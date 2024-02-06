from __future__ import annotations

import async_timeout
import datetime
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)
_MAX_EVENTS = 16

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

from ..const import ATTR_AVAILABLE
from ..const import ATTR_EVENTS
from ..const import ATTR_STATUS

from ..config import configure_driver
from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_cards


async def _listen(hass, listener):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(lambda: listener, local_addr=('192.168.1.100', 60001))

    _LOGGER.debug(f'UDP event listener {transport}')
    _LOGGER.debug(f'UDP event listener {protocol}')


class EventListener:

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data, addr):
        print(f'>>>>>>>>>>>>>>>>>>>>>>>> EVENT {len(data)} bytes')

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
        }

        self._listener = EventListener()

        asyncio.create_task(_listen(hass, self._listener))

    def __del__(self):
        self.unload()

    def unload(self):
        print(">>>>>>>> awooooooooogah ...")
        if self._listener:
            self._listener.close()

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
                                info[ATTR_EVENTS].append(response)
                                ix = response.index

                        self._state['index'][controller] = ix

                    info[ATTR_AVAILABLE] = True

            except (Exception):
                _LOGGER.exception(f'error retrieving controller {controller} events')

            self._state['events'][controller] = info

        return self._state['events']
