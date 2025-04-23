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
from ..const import ATTR_CONTROLLER_INTERLOCK

from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_controllers_ext
from ..config import get_configured_cards

from ..uhppoted import Controller


class ControllersCoordinator(DataUpdateCoordinator):
    _state: Dict[int, Dict]

    def __init__(self, hass, options, poll, driver, db):
        interval = _INTERVAL if poll == None else poll

        super().__init__(hass, _LOGGER, name="controllers", update_interval=poll)

        self._options = options
        self._controllers = get_configured_controllers_ext(options)
        self._uhppote = driver
        self._db = db
        self._lock = threading.Lock()
        self._state = {}
        self._initialised = False

        _LOGGER.info(f'controllers coordinator initialised ({interval.total_seconds():.0f}s)')

    def __del__(self):
        self.unload()

    def unload(self):
        pass

    def set_datetime(self, controller_id, time):
        controller = self._resolve(controller_id)
        response = self._uhppote.set_time(controller.id, time)

        if response.controller == controller.id:
            return response
        else:
            return None

    def set_interlock(self, controller_id, interlock):
        controller = self._resolve(controller_id)
        response = self._uhppote.set_interlock(controller.id, interlock)

        if response.controller == controller.id:
            if response.ok and controller.id in self._state:
                with self._lock:
                    self._state[controller.id].update({ATTR_CONTROLLER_INTERLOCK: interlock})

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
        lock = self._lock # threading.Lock()

        for v in contexts:
            if not v in self._state:
                self._state[v] = {
                    ATTR_AVAILABLE: False,
                }

        controllers = []
        for controller in self._controllers:
            if controller.id in contexts:
                controllers.append(controller)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda controller: self._get_controller(lock, controller), controllers, timeout=1)
                executor.map(lambda controller: self._get_datetime(lock, controller), controllers, timeout=1)
                executor.map(lambda controller: self._get_listener(lock, controller), controllers, timeout=1)
                executor.map(lambda controller: self._get_interlock(lock, controller), controllers, timeout=1)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller information ({err})')

        self._db.controllers = self._state

        return self._db.controllers

    def _get_controller(self, lock, controller):
        _LOGGER.debug(f'fetch controller info {controller.id}')

        available = False

        address = None
        protocol = controller.protocol
        netmask = None
        gateway = None
        firmware = None

        try:
            response = self._uhppote.get_controller(controller.id)
            if response.controller == controller.id:
                address = f'{response.ip_address}'
                netmask = f'{response.subnet_mask}'
                gateway = f'{response.gateway}'
                firmware = f'{response.version} {response.date:%Y-%m-%d}'
                available = True

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} information ({err})')

        with lock:
            self._state[controller.id].update({
                ATTR_CONTROLLER_ADDRESS: address,
                ATTR_CONTROLLER_PROTOCOL: protocol,
                ATTR_NETMASK: netmask,
                ATTR_GATEWAY: gateway,
                ATTR_FIRMWARE: firmware,
                ATTR_AVAILABLE: available,
            })

    def _get_datetime(self, lock, controller):
        _LOGGER.debug(f'fetch controller datetime {controller.id}')

        sysdatetime = None

        try:
            response = self._uhppote.get_time(controller.id)
            if response.controller == controller.id:
                year = response.datetime.year
                month = response.datetime.month
                day = response.datetime.day
                hour = response.datetime.hour
                minute = response.datetime.minute
                second = response.datetime.second
                tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

                sysdatetime = datetime.datetime(year, month, day, hour, minute, second, 0, tz)

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} date/time ({err})')

        with lock:
            self._state[controller.id].update({
                ATTR_CONTROLLER_DATETIME: sysdatetime,
            })

    def _get_listener(self, lock, controller):
        _LOGGER.debug(f'fetch controller event listener {controller.id}')

        listener = None

        try:
            response = self._uhppote.get_listener(controller.id)
            if response.controller == controller.id:
                listener = f'{response.address}:{response.port}'

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} event listener ({err})')

        with lock:
            self._state[controller.id].update({
                ATTR_CONTROLLER_LISTENER: listener,
            })

    def _get_interlock(self, lock, controller):
        _LOGGER.debug(f'fetch controller interlock {controller.id}')

        interlock = -1

        try:
            if state := self._state.get(controller.id):
                interlock = state.get(ATTR_CONTROLLER_INTERLOCK,-1)

        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} interlock ({err})')

        with lock:
            self._state[controller.id].update({
                ATTR_CONTROLLER_INTERLOCK: interlock,
            })

    def _resolve(self, controller_id):
        for controller in self._controllers:
            if controller.id == controller_id:
                return controller

        return Controller(int(f'{controller_id}'), None, None)
