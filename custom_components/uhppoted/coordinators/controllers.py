from __future__ import annotations

import datetime
import logging
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

# Attribute constants
from ..const import ATTR_AVAILABLE
from ..const import ATTR_CONTROLLER
from ..const import ATTR_ADDRESS
from ..const import ATTR_NETMASK
from ..const import ATTR_GATEWAY
from ..const import ATTR_FIRMWARE
from ..const import ATTR_DOOR_BUTTON
from ..const import ATTR_DOOR_LOCK
from ..const import ATTR_DOOR_OPEN
from ..const import ATTR_DOORS

from ..config import configure_driver
from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_cards


class ControllersCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, options):
        super().__init__(hass, _LOGGER, name="controllers", update_interval=_INTERVAL)
        self._uhppote = configure_driver(options)
        self._options = options
        self._initialised = False
        self._state = {
            'controllers': {},
        }

    def set_datetime(self, controller, time):
        api = self._uhppote['api']
        response = api.set_time(controller, time)

        if response.controller == controller:
            return response

        return None

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            controllers = get_configured_controllers(self._options)

            if not self._initialised:
                contexts.update(controllers)
                self._initialised = True

            async with async_timeout.timeout(5):
                return await self._get_controllers(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_controllers(self, contexts):
        api = self._uhppote['api']

        for controller in contexts:
            _LOGGER.debug(f'update controller {controller}')

            info = {
                ATTR_CONTROLLER: {
                    ATTR_AVAILABLE: False,
                    ATTR_ADDRESS: None,
                    ATTR_NETMASK: None,
                    ATTR_GATEWAY: None,
                    ATTR_FIRMWARE: None,
                },
                ATTR_DOORS: {
                    ATTR_AVAILABLE: False,
                }
            }

            try:
                response = api.get_controller(controller)
                if response.controller == controller:
                    info[ATTR_CONTROLLER] = {
                        ATTR_ADDRESS: f'{response.ip_address}',
                        ATTR_NETMASK: f'{response.subnet_mask}',
                        ATTR_GATEWAY: f'{response.gateway}',
                        ATTR_FIRMWARE: f'{response.version} {response.date:%Y-%m-%d}',
                        ATTR_AVAILABLE: True,
                    }

                response = api.get_status(controller)
                if response.controller == controller:
                    info[ATTR_DOORS] = {
                        ATTR_AVAILABLE: True,
                        1: {
                            ATTR_DOOR_OPEN: response.door_1_open == True,
                            ATTR_DOOR_BUTTON: response.door_1_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x01 == 0x00,
                        },
                        2: {
                            ATTR_DOOR_OPEN: response.door_2_open == True,
                            ATTR_DOOR_BUTTON: response.door_2_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x02 == 0x00,
                        },
                        3: {
                            ATTR_DOOR_OPEN: response.door_3_open == True,
                            ATTR_DOOR_BUTTON: response.door_3_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x04 == 0x00,
                        },
                        4: {
                            ATTR_DOOR_OPEN: response.door_4_open == True,
                            ATTR_DOOR_BUTTON: response.door_4_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x08 == 0x00,
                        },
                    }

            except (Exception):
                _LOGGER.exception(f'error retrieving controller {controller} information')

            self._state['controllers'][controller] = info

        return self._state['controllers']
