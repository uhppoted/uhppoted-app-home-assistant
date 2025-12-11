from __future__ import annotations
from collections import namedtuple

import concurrent.futures
import asyncio
import datetime
import logging
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.const import __version__ as HAVERSION

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

from ..const import DOMAIN
from ..const import CONF_RETRY_DELAY
from ..const import CONF_DOOR_ID
from ..const import CONF_CONTROLLER_SERIAL_NUMBER
from ..const import CONF_DOOR_NUMBER

from ..const import ATTR_AVAILABLE
from ..const import ATTR_DOOR_DELAY
from ..const import ATTR_DOOR_MODE
from ..const import ATTR_DOOR_BUTTON
from ..const import ATTR_DOOR_LOCK
from ..const import ATTR_DOOR_OPEN

from ..config import get_configured_controllers_ext
from ..config import get_configured_doors
from ..config import resolve_door
from ..config import resolve_door_by_name

from ..uhppoted import Controller


class DoorsCoordinator(DataUpdateCoordinator):
    _state: Dict[str, Dict]

    def __init__(self, hass, options, poll, driver, db):
        interval = _INTERVAL if poll == None else poll

        super().__init__(hass, _LOGGER, name="doors", update_interval=interval)

        self._options = options
        self._controllers = get_configured_controllers_ext(options)
        self._uhppote = driver
        self._retry_delay = hass.data[DOMAIN].get(CONF_RETRY_DELAY, 300)
        self._db = db
        self._state = {}
        self._initialised = False

        _LOGGER.info(f'doors coordinator initialised ({interval.total_seconds():.0f}s)')

    def __del__(self):
        self.unload()

    def unload(self):
        pass

    async def set_door_mode(self, controller_id, door, mode):
        controller = self._resolve(controller_id)
        response = await self._uhppote.get_door(controller.id, door)

        if response and response.controller == controller.id and response.door == door:
            delay = response.delay
            response = await self._uhppote.set_door(controller.id, door, mode, delay)

            if response.controller != controller.id or response.door != door:
                raise ValueError(f'invalid response to set-door-mode')
            else:
                return response

        return None

    async def set_door_delay(self, controller_id, door, delay):
        controller = self._resolve(controller_id)
        response = await self._uhppote.get_door(controller.id, door)

        if response and response.controller == controller.id and response.door == door:
            mode = response.mode
            response = await self._uhppote.set_door(controller.id, door, mode, delay)

            if response.controller != controller.id or response.door != door:
                raise ValueError(f'invalid response to set-door-delay')
            else:
                return response

        return None

    async def unlock_door(self, controller_id, door) -> None:
        controller = self._resolve(controller_id)
        response = await self._uhppote.open_door(controller.id, door)

        if response.controller != controller.id:
            raise ValueError(f'invalid response to open-door')
        else:
            return response

    async def unlock_door_by_name(self, door):
        record = resolve_door_by_name(self._options, door)
        if record:
            controller = self._resolve(record[CONF_CONTROLLER_SERIAL_NUMBER])
            doorno = record[CONF_DOOR_NUMBER]
            response = await self.unlock_door(controller.id, doorno)

            return response.opened

        return False

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            doors = get_configured_doors(self._options)

            if not self._initialised:
                contexts.update(doors)
                self._initialised = True

            return await self._get_doors(contexts)
        except Exception as exc:
            try:
                raise UpdateFailed(retry_after=self._retry_delay) from exc  # HA 2025.12+
            except TypeError:
                raise UpdateFailed() from exc

    async def _get_doors(self, contexts):
        lock = asyncio.Lock()
        tasks = []
        gathered = []

        try:
            for idx in contexts:
                if not idx in self._state:
                    self._state[idx] = {
                        ATTR_AVAILABLE: False,
                    }

            doors = {}
            controllers = {}

            for idx in contexts:
                if door := resolve_door(self._options, idx):
                    doors[idx] = door
                    if controller := door.get(CONF_CONTROLLER_SERIAL_NUMBER):
                        controllers.setdefault(controller, []).append((idx, door))

            for controller in self._controllers:
                if controller.id in controllers:
                    if _doors := controllers.get(controller.id, []):
                        tasks.append(self._get_controller(lock, controller, _doors))

            for idx in contexts:
                if door := doors.get(idx):
                    tasks.append(self._get_door(lock, idx, door))

            gathered = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller door information ({err})')
            for task in tasks:
                task.close()

        if all(r is not None for r in gathered):
            raise UpdateFailed(f"general failure retrieving doors")

        self._db.doors = self._state

        return self._db.doors

    async def _get_controller(self, lock, controller, doors):
        state = {}
        for (idx, door) in doors:
            state[idx] = {
                ATTR_DOOR_OPEN: None,
                ATTR_DOOR_BUTTON: None,
                ATTR_DOOR_LOCK: None,
            }

        def g(idx, open, button, relay):
            state[idx].update({
                ATTR_DOOR_OPEN: open == True,
                ATTR_DOOR_BUTTON: button == True,
                ATTR_DOOR_LOCK: relay == 0x00,
            })

        def h(idx, door, response):
            if door == 1:
                g(idx, response.door_1_open, response.door_1_button, response.relays & 0x01)
            elif door == 2:
                g(idx, response.door_2_open, response.door_2_button, response.relays & 0x02)
            elif door == 3:
                g(idx, response.door_3_open, response.door_3_button, response.relays & 0x04)
            elif door == 4:
                g(idx, response.door_4_open, response.door_4_button, response.relays & 0x08)

        async def callback(response):
            try:
                _LOGGER.debug(f'get-controller {controller.id} {response}')
                if response and response.controller == controller.id:
                    for (idx, door) in doors:
                        if door_number := door.get('door_number'):
                            h(idx, door_number, response)

                    async with lock:
                        for (idx, door) in doors:
                            self._state[idx].update(state.get(idx, {}))

            except Exception as err:
                _LOGGER.error(f'error updating controller {controller.id} door state ({err})')

        try:
            response = await self._uhppote.get_status(controller.id, callback)
            if response and response.controller == controller.id:
                for (idx, door) in doors:
                    if door_number := door.get('door_number'):
                        h(idx, door_number, response)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} door state ({err})')

        async with lock:
            for (idx, door) in doors:
                self._state[idx].update(state.get(idx, {}))

    async def _get_door(self, lock, idx, door):
        _LOGGER.debug(f'fetch door info {door}')

        name = door[CONF_DOOR_ID]
        controller_id = door[CONF_CONTROLLER_SERIAL_NUMBER]
        door_id = door[CONF_DOOR_NUMBER]

        available = False,
        mode = None
        delay = None

        async def callback(response):
            try:
                _LOGGER.debug(f'get-door::callback {door} {response}')
                if response and response.controller == controller_id and response.door == door_id:
                    changed = False
                    async with lock:
                        old = {
                            ATTR_DOOR_MODE: self._state[idx][ATTR_DOOR_MODE],
                            ATTR_DOOR_DELAY: self._state[idx][ATTR_DOOR_DELAY],
                            ATTR_AVAILABLE: self._state[idx][ATTR_AVAILABLE],
                        }

                        updated = {
                            ATTR_DOOR_MODE: response.mode,
                            ATTR_DOOR_DELAY: response.delay,
                            ATTR_AVAILABLE: True,
                        }

                        if any(old.get(k) != v for k, v in updated.items()):
                            changed = True

                        self._state[idx].update(updated)

                    if changed:
                        self.async_set_updated_data(self._state)

            except Exception as err:
                _LOGGER.error(f'error updating internal controller {controller.id} information ({err})')

        try:
            controller = Controller(controller_id, None, None)
            for v in self._controllers:
                if int(f'{v.id}') == int(f'{controller_id}'):
                    controller = v

            _LOGGER.debug(f'fetch door {name} information')

            response = await self._uhppote.get_door(controller.id, door_id, callback)
            if response and response.controller == controller.id and response.door == door_id:
                mode = response.mode
                delay = response.delay
                available = True

        except Exception as err:
            _LOGGER.error(f'error retrieving door {door["door_id"]} information ({err})')

        async with lock:
            self._state[idx].update({
                ATTR_DOOR_MODE: mode,
                ATTR_DOOR_DELAY: delay,
                ATTR_AVAILABLE: available,
            })

    def _resolve(self, controller_id):
        for controller in self._controllers:
            if controller.id == controller_id:
                return controller

        return Controller(int(f'{controller_id}'), None, None)
