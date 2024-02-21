from __future__ import annotations

import concurrent.futures
import threading
import datetime
import logging
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

from ..const import ATTR_AVAILABLE
from ..const import ATTR_CONTROLLER
from ..const import ATTR_CONTROLLER_ADDRESS
from ..const import ATTR_NETMASK
from ..const import ATTR_GATEWAY
from ..const import ATTR_FIRMWARE
from ..const import ATTR_CONTROLLER_DATETIME

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

    def __del__(self):
        self.unload()

    def unload(self):
        pass

    def set_datetime(self, controller, time):
        api = self._uhppote['api']
        response = api.set_time(controller, time)

        return response if response.controller == controller else None

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            controllers = get_configured_controllers(self._options)

            if not self._initialised:
                contexts.update(controllers)
                self._initialised = True

            async with async_timeout.timeout(2.5):
                return await self._get_controllers(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_controllers(self, contexts):
        api = self._uhppote['api']
        lock = threading.Lock()

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda controller: self._get_controller(api, lock, controller), contexts, timeout=1)
                executor.map(lambda controller: self._get_datetime(api, lock, controller), contexts, timeout=1)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} information ({err})')

        return self._state['controllers']

    def _get_controller(self, api, lock, controller):
        _LOGGER.debug(f'update controller {controller}')

        available = False
        info = {
            ATTR_CONTROLLER_ADDRESS: None,
            ATTR_NETMASK: None,
            ATTR_GATEWAY: None,
            ATTR_FIRMWARE: None,
        }

        try:
            response = api.get_controller(controller)
            if response.controller == controller:
                info = {
                    ATTR_CONTROLLER_ADDRESS: f'{response.ip_address}',
                    ATTR_NETMASK: f'{response.subnet_mask}',
                    ATTR_GATEWAY: f'{response.gateway}',
                    ATTR_FIRMWARE: f'{response.version} {response.date:%Y-%m-%d}',
                }

                available = True

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} information ({err})')

        with lock:
            if controller in self._state['controllers']:
                self._state['controllers'][controller][ATTR_CONTROLLER] = info
                self._state['controllers'][controller][ATTR_AVAILABLE] = available
            else:
                self._state['controllers'][controller] = {ATTR_CONTROLLER: info, ATTR_AVAILABLE: available}

    def _get_datetime(self, api, lock, controller):
        _LOGGER.debug(f'update controller datetime {controller}')

        sysdatetime = None

        try:
            response = api.get_time(controller)
            if response.controller == controller:
                year = response.datetime.year
                month = response.datetime.month
                day = response.datetime.day
                hour = response.datetime.hour
                minute = response.datetime.minute
                second = response.datetime.second
                tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

                sysdatetime = datetime.datetime(year, month, day, hour, minute, second, 0, tz)

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} information ({err})')

        with lock:
            if controller in self._state['controllers']:
                self._state['controllers'][controller][ATTR_CONTROLLER_DATETIME] = sysdatetime
            else:
                self._state['controllers'][controller] = {ATTR_CONTROLLER_DATETIME: sysdatetime}
