from __future__ import annotations
from collections import namedtuple

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
        response = self._uhppote.get_door_control(controller.id, door)

        if response and response.controller == controller.id and response.door == door:
            delay = response.delay
            response = await self._uhppote.set_door(controller.id, door, mode, delay)

            if response.controller != controller.id or response.door != door:
                raise ValueError(f'invalid response to set-door-control')
            else:
                return response

        return None

    async def set_door_delay(self, controller_id, door, delay):
        controller = self._resolve(controller_id)
        response = self._uhppote.get_door_control(controller.id, door)

        if response and response.controller == controller.id and response.door == door:
            mode = response.mode
            response = await self._uhppote.set_door(controller.id, door, mode, delay)

            if response.controller != controller.id or response.door != door:
                raise ValueError(f'invalid response to set-door-control')
            else:
                return response

        return None

    def unlock_door(self, controller_id, door) -> None:
        controller = self._resolve(controller_id)
        response = self._uhppote.open_door(controller.id, door)

        if response.controller != controller.id:
            raise ValueError(f'invalid response to open-door')
        else:
            return response

    def unlock_door_by_name(self, door):
        record = resolve_door_by_name(self._options, door)
        if record:
            controller = self._resolve(record[CONF_CONTROLLER_SERIAL_NUMBER])
            doorno = record[CONF_DOOR_NUMBER]
            response = self.unlock_door(controller.id, doorno)
            return response.opened

        return False

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            doors = get_configured_doors(self._options)

            if not self._initialised:
                contexts.update(doors)
                self._initialised = True

            async with async_timeout.timeout(2.5):
                return await self._get_doors(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_doors(self, contexts):
        lock = threading.Lock()

        for v in contexts:
            if not v in self._state:
                self._state[v] = {
                    ATTR_AVAILABLE: False,
                }

        _controllers = set()
        doors = {}
        for idx in contexts:
            door = resolve_door(self._options, idx)
            if door:
                _controllers.add(door[CONF_CONTROLLER_SERIAL_NUMBER])
                doors[idx] = door

        controllers = []
        for controller in self._controllers:
            if controller.id in _controllers:
                controllers.append(controller)

        state = {}
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda controller: self._get_controller(lock, state, controller), controllers, timeout=1)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda idx: self._get_door(lock, idx, doors[idx], state), contexts, timeout=1)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller door information ({err})')

        self._db.doors = self._state

        return self._db.doors

    def _get_controller(self, lock, state, controller):

        def g(response):
            if response and response.controller == controller.id:
                info = {
                    1: {
                        'open': response.door_1_open == True,
                        'button': response.door_1_button == True,
                        'locked': response.relays & 0x01 == 0x00,
                    },
                    2: {
                        'open': response.door_2_open == True,
                        'button': response.door_2_button == True,
                        'locked': response.relays & 0x02 == 0x00,
                    },
                    3: {
                        'open': response.door_3_open == True,
                        'button': response.door_3_button == True,
                        'locked': response.relays & 0x04 == 0x00,
                    },
                    4: {
                        'open': response.door_4_open == True,
                        'button': response.door_4_button == True,
                        'locked': response.relays & 0x08 == 0x00,
                    }
                }

                return namedtuple('reply', ['info'])(info)

            return None

        def callback(response):
            try:
                if reply := g(response):
                    _LOGGER.debug(f'get-controller {controller.id} {reply}')
                    with lock:
                        state[controller.id] = reply.info

            except Exception as err:
                _LOGGER.error(f'error updating controller {controller.id} door state ({err})')

        info = None

        try:
            response = self._uhppote.get_status(controller.id, callback)
            if reply := g(response):
                info = reply.info
        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller.id} door state ({err})')

        with lock:
            state[controller.id] = info

    def _get_door(self, lock, idx, door, state):
        name = door[CONF_DOOR_ID]
        controller_id = door[CONF_CONTROLLER_SERIAL_NUMBER]
        door_id = door[CONF_DOOR_NUMBER]

        def g(response):
            if response and response.controller == controller.id and response.door == door_id:
                mode = response.mode
                delay = response.delay
                open = None
                button = None
                locked = None

                if controller.id in state and state[controller.id] != None:
                    open = state[controller.id][door_id]['open']
                    button = state[controller.id][door_id]['button']
                    locked = state[controller.id][door_id]['locked']

                return namedtuple('reply', ['mode', 'delay', 'open', 'button', 'locked'])(mode, delay, open, button,
                                                                                          locked)

            return None

        def callback(response):
            try:
                if reply := g(response):
                    with lock:
                        self._state[idx].update({
                            ATTR_DOOR_MODE: reply.mode,
                            ATTR_DOOR_DELAY: reply.delay,
                            ATTR_DOOR_OPEN: reply.open,
                            ATTR_DOOR_BUTTON: reply.button,
                            ATTR_DOOR_LOCK: reply.locked,
                            ATTR_AVAILABLE: True,
                        })

                    self.async_set_updated_data(self._state)

            except Exception as err:
                _LOGGER.error(f'error updating internal controller {controller.id} information ({err})')

        info = {
            ATTR_AVAILABLE: False,
            ATTR_DOOR_MODE: None,
            ATTR_DOOR_DELAY: None,
            ATTR_DOOR_OPEN: None,
            ATTR_DOOR_BUTTON: None,
            ATTR_DOOR_LOCK: None,
        }

        try:
            controller = Controller(controller_id, None, None)
            for v in self._controllers:
                if int(f'{v.id}') == int(f'{controller_id}'):
                    controller = v

            _LOGGER.debug(f'fetch door {name} information')

            mode = None
            delay = None

            response = self._uhppote.get_door_control(controller.id, door_id, callback)
            if reply := g(response):
                info = {
                    ATTR_DOOR_MODE: reply.mode,
                    ATTR_DOOR_DELAY: reply.delay,
                    ATTR_DOOR_OPEN: reply.open,
                    ATTR_DOOR_BUTTON: reply.button,
                    ATTR_DOOR_LOCK: reply.locked,
                    ATTR_AVAILABLE: True,
                }

        except Exception as err:
            _LOGGER.error(f'error retrieving door {door["door_id"]} information ({err})')

        with lock:
            self._state[idx].update(info)

    def _resolve(self, controller_id):
        for controller in self._controllers:
            if controller.id == controller_id:
                return controller

        return Controller(int(f'{controller_id}'), None, None)
