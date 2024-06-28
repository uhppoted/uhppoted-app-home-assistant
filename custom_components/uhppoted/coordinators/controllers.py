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

from ..const import CONF_CONTROLLERS
from ..const import CONF_CONTROLLER_SERIAL_NUMBER
from ..const import CONF_CONTROLLER_PROTOCOL

from ..const import ATTR_AVAILABLE
from ..const import ATTR_CONTROLLER
from ..const import ATTR_CONTROLLER_ADDRESS
from ..const import ATTR_CONTROLLER_PROTOCOL
from ..const import ATTR_NETMASK
from ..const import ATTR_GATEWAY
from ..const import ATTR_FIRMWARE
from ..const import ATTR_CONTROLLER_DATETIME
from ..const import ATTR_CONTROLLER_LISTENER

from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_cards


class ControllersCoordinator(DataUpdateCoordinator):
    _state: Dict[int, Dict]

    def __init__(self, hass, options, poll, driver, db):
        interval = _INTERVAL if poll == None else poll

        super().__init__(hass, _LOGGER, name="controllers", update_interval=poll)

        self._options = options
        self._uhppote = driver
        self._db = db
        self._state = {}
        self._initialised = False

        _LOGGER.info(f'controllers coordinator initialised ({interval.total_seconds():.0f}s)')

    def __del__(self):
        self.unload()

    def unload(self):
        pass

    def set_datetime(self, controller, time):
        response = self._uhppote.set_time(controller, time)

        if response.controller == controller:
            return response
        else:
            return None

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
        lock = threading.Lock()

        for v in contexts:
            if not v in self._state:
                self._state[v] = {
                    ATTR_AVAILABLE: False,
                }

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda controller: self._get_controller(lock, controller), contexts, timeout=1)
                executor.map(lambda controller: self._get_datetime(lock, controller), contexts, timeout=1)
                executor.map(lambda controller: self._get_listener(lock, controller), contexts, timeout=1)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} information ({err})')

        self._db.controllers = self._state

        return self._db.controllers

    def _get_controller(self, lock, controller):
        _LOGGER.debug(f'fetch controller info {controller}')

        available = False

        address = None
        protocol = None
        netmask = None
        gateway = None
        firmware = None

        controllers = self._options.get(CONF_CONTROLLERS,[])
        for v in controllers:
            if int(f'{v.get(CONF_CONTROLLER_SERIAL_NUMBER,0)}') == int(f'{controller}'):
                protocol = f'{v.get(CONF_CONTROLLER_PROTOCOL,"UDP")}'

        try:
            response = self._uhppote.get_controller(controller)
            if response.controller == controller:
                address = f'{response.ip_address}'
                protocol = protocol
                netmask = f'{response.subnet_mask}'
                gateway = f'{response.gateway}'
                firmware = f'{response.version} {response.date:%Y-%m-%d}'
                available = True

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} information ({err})')

        with lock:
            self._state[controller].update({
                ATTR_CONTROLLER_ADDRESS: address,
                ATTR_CONTROLLER_PROTOCOL: protocol,
                ATTR_NETMASK: netmask,
                ATTR_GATEWAY: gateway,
                ATTR_FIRMWARE: firmware,
                ATTR_AVAILABLE: available,
            })

    def _get_datetime(self, lock, controller):
        _LOGGER.debug(f'fetch controller datetime {controller}')

        sysdatetime = None

        try:
            response = self._uhppote.get_time(controller)
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
            _LOGGER.error(f'error retrieving controller {controller} date/time ({err})')

        with lock:
            self._state[controller].update({
                ATTR_CONTROLLER_DATETIME: sysdatetime,
            })

    def _get_listener(self, lock, controller):
        _LOGGER.debug(f'fetch controller event listener {controller}')

        listener = None

        try:
            response = self._uhppote.get_listener(controller)
            if response.controller == controller:
                listener = f'{response.address}:{response.port}'

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} event listener ({err})')

        with lock:
            self._state[controller].update({
                ATTR_CONTROLLER_LISTENER: listener,
            })
