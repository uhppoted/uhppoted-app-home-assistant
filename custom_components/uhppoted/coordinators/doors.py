from __future__ import annotations

import datetime
import logging
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

from ..const import CONF_DOOR_ID
from ..const import CONF_CONTROLLER_SERIAL_NUMBER
from ..const import CONF_DOOR_NUMBER

from ..const import ATTR_AVAILABLE
from ..const import ATTR_DOOR_DELAY
from ..const import ATTR_DOOR_MODE

from ..config import configure_driver
from ..config import get_configured_doors
from ..config import resolve_door


class DoorsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, options):
        super().__init__(hass, _LOGGER, name="coordinator", update_interval=_INTERVAL)
        self._uhppote = configure_driver(options)
        self._options = options
        self._initialised = False
        self._state = {
            'doors': {},
        }

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            doors = get_configured_doors(self._options)

            if not self._initialised:
                contexts.update(doors)
                self._initialised = True

            async with async_timeout.timeout(5):
                return await self._get_doors(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_doors(self, contexts):
        api = self._uhppote['api']

        for idx in contexts:
            info = {
                ATTR_AVAILABLE: False,
                ATTR_DOOR_MODE: None,
                ATTR_DOOR_DELAY: None,
            }

            try:
                door = resolve_door(self._options, idx)
                if door:
                    name = door[CONF_DOOR_ID]
                    controller = door[CONF_CONTROLLER_SERIAL_NUMBER]
                    door_id = door[CONF_DOOR_NUMBER]

                    _LOGGER.debug(f'update door {name}')

                    mode = None
                    delay = None

                    response = api.get_door_control(controller, door_id)
                    if response.controller == controller and response.door == door_id:
                        mode = response.mode
                        delay = response.delay

                        info = {
                            ATTR_DOOR_MODE: mode,
                            ATTR_DOOR_DELAY: delay,
                            ATTR_AVAILABLE: True,
                        }

            except (Exception):
                _LOGGER.exception(f'error retrieving door {door} information')

            self._state['doors'][idx] = info

        return self._state['doors']
