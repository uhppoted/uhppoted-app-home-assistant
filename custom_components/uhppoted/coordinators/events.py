from __future__ import annotations
from dataclasses import dataclass

import async_timeout
import datetime
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

from ..const import ATTR_AVAILABLE
from ..const import ATTR_EVENTS
from ..const import ATTR_STATUS
from ..const import EVENT_REASON_DOOR_LOCKED
from ..const import EVENT_REASON_DOOR_UNLOCKED

from ..config import configure_driver
from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_cards


async def _listen(hass, listener):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(lambda: listener, local_addr=('192.168.1.100', 60001))

    _LOGGER.debug(f'UDP event listener {transport}')
    _LOGGER.debug(f'UDP event listener {protocol}')


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

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, packet, addr):
        try:
            (event, relays) = self.decode(packet)
            if self._handler:
                self._handler(event, relays)
        except BaseException as err:
            _LOGGER.warning(f'Error decoding received event ({err})')

    def decode(self, packet):
        evt = decode.event(packet)

        # FIXME interim workaround for bug in uhppoted-python::decode.event
        # evt.door_1_open = unpack_bool(packet, 28)
        # evt.door_2_open = unpack_bool(packet, 29)
        # evt.door_3_open = unpack_bool(packet, 30)
        # evt.door_4_open = unpack_bool(packet, 31)
        # evt.door_1_button = unpack_bool(packet, 32)
        # evt.door_2_button = unpack_bool(packet, 33)
        # evt.door_3_button = unpack_bool(packet, 34)
        # evt.door_4_button = unpack_bool(packet, 35)
        relays = unpack_uint8(packet, 49)
        # evt.inputs = unpack_uint8(packet, 50)
        # evt.system_error = unpack_uint8(packet, 36)
        # # END FIXME

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
                relays)
        # yapf: enable

    def close(self):
        if self.transport:
            self._transport.close()


class EventsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, options):
        super().__init__(hass, _LOGGER, name="events", update_interval=_INTERVAL)
        self._uhppote = configure_driver(options)
        self._options = options
        self._initialised = False
        self._state = {
            'events': {},
            'index': {},
            'relays': {},
        }

        self._listener = EventListener(self.onEvent)

        asyncio.create_task(_listen(hass, self._listener))

    def __del__(self):
        self.unload()

    def unload(self):
        if self._listener:
            self._listener.close()

    def onEvent(self, event, relays):
        contexts = set(self.async_contexts())
        controller = event.controller

        if controller in contexts:
            events = [event]
            events.extend(self.doorLocks(controller, relays))

            if not controller in self._state['index'] or self._state['index'][controller] < event.index:
                self._state['index'][controller] = event.index

            self._state['events'][controller] = {
                ATTR_AVAILABLE: True,
                ATTR_EVENTS: events,
            }

            self.async_set_updated_data(self._state['events'])

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            controllers = get_configured_controllers(self._options)

            if not self._initialised:
                contexts.update(controllers)
                self._initialised = True

            async with async_timeout.timeout(5):
                return await self._get_events(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_events(self, contexts):
        api = self._uhppote['api']

        for controller in contexts:
            _LOGGER.debug(f'update controller {controller}')

            info = {
                ATTR_AVAILABLE: False,
                ATTR_EVENTS: [],
            }

            try:
                response = api.record_special_events(controller, True)
                if response.controller == controller:
                    if not response.updated:
                        _LOGGER.warning('record special events not enabled for {controller}')

                response = api.get_status(controller)
                if response.controller == controller:
                    info[ATTR_STATUS] = response
                    index = response.event_index
                    relays = response.relays
                    events = []

                    if not controller in self._state['index']:
                        self._state['index'][controller] = index
                    elif self._state['index'][controller] >= index:
                        self._state['index'][controller] = index
                    else:
                        count = 0
                        ix = self._state['index'][controller]
                        while ix < index and count < _MAX_EVENTS:
                            count += 1
                            next = ix + 1
                            response = api.get_event(controller, next)
                            if response.controller == controller and response.index == next:
                                event = self.decode(response, relays)
                                events.append(event)
                                ix = response.index

                        self._state['index'][controller] = ix

                    events.extend(self.doorLocks(controller, relays))

                    info[ATTR_EVENTS] = events
                    info[ATTR_AVAILABLE] = True

            except (Exception):
                _LOGGER.exception(f'error retrieving controller {controller} events')

            self._state['events'][controller] = info

        return self._state['events']

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

    def doorLocks(self, controller, relays):
        contexts = set(self.async_contexts())
        events = []

        if controller in contexts:
            timestamp = datetime.datetime.now()

            if controller in self._state['relays']:
                for door in [1, 2, 3, 4]:
                    mask = _MASK[door]
                    if self._state['relays'][controller] & mask != relays & mask:
                        reason = EVENT_REASON_DOOR_UNLOCKED if relays & mask == mask else EVENT_REASON_DOOR_LOCKED
                        events.append(Event(controller, -1, None, None, door, None, None, timestamp, reason))

            self._state['relays'][controller] = relays

        return events
