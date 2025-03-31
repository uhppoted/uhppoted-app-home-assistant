from __future__ import annotations

import concurrent.futures
import threading
from ipaddress import IPv4Address
from dataclasses import dataclass

import async_timeout
import datetime
import re
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)
_MAX_EVENTS = 16
_MASK = {
    1: 0x01,
    2: 0x02,
    3: 0x04,
    4: 0x08,
}

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote
from uhppoted import decode
from uhppoted.decode import unpack_uint8
from uhppoted.decode import unpack_bool

from ..const import CONF_LISTEN_ADDR
from ..const import CONF_EVENTS_DEST_ADDR
from ..const import ATTR_AVAILABLE
from ..const import ATTR_EVENTS
from ..const import ATTR_STATUS
from ..const import EVENT_REASON_DOOR_LOCKED
from ..const import EVENT_REASON_DOOR_UNLOCKED
from ..const import EVENT_REASON_BUTTON_RELEASED

from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_controllers_ext

from ..uhppoted import Controller


async def _listen(hass, addr, port, listener):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(lambda: listener, local_addr=(addr, port))

    _LOGGER.debug(f'UDP event listener {transport}')
    _LOGGER.debug(f'UDP event listener {protocol}')
    _LOGGER.info(f'listening for events on {addr}:{port}')


@dataclass
class Event:
    controller: int
    index: int
    event_type: int
    access_granted: bool
    door: int
    direction: int
    card: int
    timestamp: datetime.datetime
    reason: int


class EventListener:

    def __init__(self, handler):
        self._handler = handler
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def connection_lost(self, err):
        self._transport = None
        _LOGGER.error(f'event listener UDP connection lost {err}')

    def datagram_received(self, packet, addr):
        try:
            (event, relays, buttons) = self.decode(packet)
            if self._handler:
                self._handler(event, relays, buttons)
        except BaseException as err:
            _LOGGER.warning(f'Error decoding received event ({err})')

    def decode(self, packet):
        evt = decode.event(packet)

        # yapf: disable
        return (Event(evt.controller,
                      evt.event_index,
                      evt.event_type,
                      evt.event_access_granted,
                      evt.event_door,
                      evt.event_direction,
                      evt.event_card,
                      evt.event_timestamp,
                      evt.event_reason),
                evt.relays,
                {
                    1: evt.door_1_button,
                    2: evt.door_2_button,
                    3: evt.door_3_button,
                    4: evt.door_4_button,
                })
        # yapf: enable

    def close(self):
        if self._transport:
            self._transport.close()


class EventsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, options, poll, driver, db, notify):
        interval = _INTERVAL if poll == None else poll
        addr = '0.0.0.0'
        port = 60001

        super().__init__(hass, _LOGGER, name='events', update_interval=interval)

        self._options = options
        self._uhppote = driver
        self._controllers = get_configured_controllers_ext(options)
        self._db = db
        self._notify = notify
        self._listener_addr = options.get(CONF_EVENTS_DEST_ADDR, None)
        self._initialised = False
        self._state = {
            'events': {},
            'index': {},
            'relays': {},
            'buttons': {},
        }

        if CONF_LISTEN_ADDR in options:
            match = re.match(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):([0-9]+)', options[CONF_LISTEN_ADDR])
            if match:
                addr = match.group(1)
                port = int(match.group(2))

        self._listener = EventListener(self.onEvent)

        asyncio.create_task(_listen(hass, addr, port, self._listener))

        _LOGGER.info(f'events coordinator initialised ({interval.total_seconds():.0f}s)')

    def __del__(self):
        self.unload()

    def unload(self):
        try:
            if self._listener:
                self._listener.close()
        except Exception as err:
            _LOGGER.warning(f'error unloading events-coordinator ({err})')

    def onEvent(self, event, relays, inputs):
        contexts = set(self.async_contexts())
        controller = event.controller

        if controller in contexts:
            events = [event]
            events.extend(self.doorLocks(controller, relays))
            events.extend(self.doorButtons(controller, inputs))

            if not controller in self._state['index'] or self._state['index'][controller] < event.index:
                self._state['index'][controller] = event.index

            self._state['events'][controller] = {
                ATTR_AVAILABLE: True,
                ATTR_EVENTS: events,
            }

            self._db.events = self._state['events']
            self.async_set_updated_data(self._db.events)

            if self._notify:
                self._notify(event)

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            controllers = get_configured_controllers(self._options)

            if not self._initialised:
                contexts.update(controllers)
                self._initialised = True

            async with async_timeout.timeout(2.5):
                return await self._get_events(contexts)
        except Exception as err:
            raise UpdateFailed(f'uhppoted API error {err}')

    async def _get_events(self, contexts):
        lock = threading.Lock()

        controllers = []
        for controller in self._controllers:
            if controller.id in contexts:
                controllers.append(controller)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda controller: self._record_special_events(lock, controller), controllers, timeout=1)
                executor.map(lambda controller: self._set_event_listener(lock, controller), controllers, timeout=1)
                executor.map(lambda controller: self._get_controller_events(lock, controller), controllers, timeout=1)
        except Exception as err:
            _LOGGER.error(f'error retrieving event information ({err})')

        self._db.events = self._state['events']

        return self._db.events

    def _record_special_events(self, lock, controller):
        _LOGGER.debug(f'enable controller {controller.id} record special events')

        try:
            response = self._uhppote.record_special_events(controller.id, True)
            if response.controller == controller.id:
                if not response.updated:
                    _LOGGER.warning('record special events not enabled for {controller.id}')

        except Exception as err:
            _LOGGER.warning(f'error enabling controller {controller} record special events ({err})')

    def _set_event_listener(self, lock, controller):
        if self._listener_addr != None:
            _LOGGER.debug(f'check controller {controller.id} event listener')

            match = re.match(r'^[0-9.]+:[0-9]+$', f'{self._listener_addr}')
            if match == None:
                return

            try:
                response = self._uhppote.get_listener(controller.id)
                if response.controller == controller.id:
                    addr = f'{response.address}:{response.port}'
                    if addr != self._listener_addr:
                        _LOGGER.warning(f'controller {controller.id} incorrect event listener address ({addr})')
                        host, port = self._listener_addr.split(':')
                        response = self._uhppote.set_listener(controller.id, IPv4Address(host), int(port))
                        if response.controller == controller.id:
                            if response.ok:
                                _LOGGER.warning(
                                    f'controller {controller.id} event listener address updated ({self._listener_addr})'
                                )
                            else:
                                _LOGGER.warning(f'failed to set controller {controller.id} event listener address')

            except Exception as err:
                _LOGGER.warning(f'error setting controller {controller.id} event listener ({err})')

    def _get_controller_events(self, lock, controller):
        _LOGGER.debug(f'fetch controller {controller.id} events')

        info = {
            ATTR_AVAILABLE: False,
            ATTR_EVENTS: [],
        }

        try:
            response = self._uhppote.get_status(controller.id)
            if response.controller == controller.id:
                info[ATTR_STATUS] = response
                index = response.event_index
                relays = response.relays
                buttons = {
                    1: response.door_1_button,
                    2: response.door_2_button,
                    3: response.door_3_button,
                    4: response.door_4_button,
                }
                events = []

                if not controller.id in self._state['index']:
                    self._state['index'][controller.id] = index
                elif self._state['index'][controller.id] >= index:
                    self._state['index'][controller.id] = index
                else:
                    count = 0
                    ix = self._state['index'][controller.id]
                    while ix < index and count < _MAX_EVENTS:
                        count += 1
                        next = ix + 1
                        response = self._uhppote.get_event(controller.id, next)
                        if response.controller == controller.id and response.index == next:
                            event = self.decode(response, relays)
                            events.append(event)
                            ix = response.index

                    self._state['index'][controller.id] = ix

                events.extend(self.doorLocks(controller.id, relays))
                events.extend(self.doorButtons(controller.id, buttons))

                info[ATTR_EVENTS] = events
                info[ATTR_AVAILABLE] = True

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} events ({err})')

        with lock:
            self._state['events'][controller.id] = info

    def decode(self, evt, relays):
        # yapf: disable
        return Event(evt.controller,
                     evt.index,
                     evt.event_type,
                     evt.access_granted,
                     evt.door,
                     evt.direction,
                     evt.card,
                     evt.timestamp,
                     evt.reason)
        # yapf: enable

    def doorLocks(self, controller_id, relays):
        contexts = set(self.async_contexts())
        events = []

        if controller_id in contexts:
            timestamp = datetime.datetime.now()

            if controller_id in self._state['relays']:
                for door in [1, 2, 3, 4]:
                    mask = _MASK[door]
                    if self._state['relays'][controller_id] & mask != relays & mask:
                        reason = EVENT_REASON_DOOR_UNLOCKED if relays & mask == mask else EVENT_REASON_DOOR_LOCKED
                        events.append(Event(controller_id, -1, None, None, door, None, None, timestamp, reason))

            self._state['relays'][controller_id] = relays

        return events

    def doorButtons(self, controller_id, buttons):
        contexts = set(self.async_contexts())
        events = []

        if controller_id in contexts:
            timestamp = datetime.datetime.now()

            if controller_id in self._state['buttons']:
                for door in [1, 2, 3, 4]:
                    if self._state['buttons'][controller_id][door] != buttons[door] and not buttons[door]:
                        events.append(
                            Event(controller_id, -1, None, None, door, None, None, timestamp,
                                  EVENT_REASON_BUTTON_RELEASED))

            self._state['buttons'][controller_id] = buttons

        return events

    def _resolve(self, controller_id):
        for controller in self._controllers:
            if controller.id == controller_id:
                return controller

        return Controller(int(f'{controller_id}'), None, None)
