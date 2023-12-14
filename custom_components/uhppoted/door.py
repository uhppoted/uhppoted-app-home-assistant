from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.number import NumberEntity
from homeassistant.const import TIME_SECONDS

_LOGGER = logging.getLogger(__name__)


class ControllerDoor(SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door}')

        self.uhppote = u
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.{controller}.door.{door}'.lower()
        self._unlocked = None
        self._open = None
        self._button = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'{self.controller}.door.{self.door}'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            s = []
            if self._button == True:
                s.append('PRESSED')

            if self._unlocked == False:
                s.append('LOCKED')
            elif self._unlocked == True:
                s.append('UNLOCKED')

            if self._open == False:
                s.append('CLOSED')
            elif self._open == True:
                s.append('OPEN')

            return ' '.join(s)

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} state')
        try:
            response = self.uhppote.get_status(self.serial_no)

            if response.controller == self.serial_no:
                if self.door_id == 1:
                    self._open = response.door_1_open == True
                    self._button = response.door_1_button == True
                    self._unlocked = response.relays & 0x01 == 0x01
                elif self.door_id == 2:
                    self._open = response.door_2_open == True
                    self._button = response.door_2_button == True
                    self._unlocked = response.relays & 0x02 == 0x02
                elif self.door_id == 3:
                    self._open = response.door_3_open == True
                    self._button = response.door_3_button == True
                    self._unlocked = response.relays & 0x04 == 0x04
                elif self.door_id == 4:
                    self._open = response.door_4_open == True
                    self._button = response.door_4_button == True
                    self._unlocked = response.relays & 0x08 == 0x08
                else:
                    self._open = None
                    self._button = None
                    self._unlocked = None

                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class ControllerDoorOpen(SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} open')

        self.uhppote = u
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.{controller}.door.{door}.open'.lower()
        self._open = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'{self.controller}.door.{self.door}.open'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            if self._open == False:
                return 'CLOSED'
            elif self._open == True:
                return 'OPEN'

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door}.open state')
        try:
            response = self.uhppote.get_status(self.serial_no)

            if response.controller == self.serial_no:
                if self.door_id == 1:
                    self._open = response.door_1_open == True
                elif self.door_id == 2:
                    self._open = response.door_2_open == True
                elif self.door_id == 3:
                    self._open = response.door_3_open == True
                elif self.door_id == 4:
                    self._open = response.door_4_open == True
                else:
                    self._open = None

                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class ControllerDoorLock(SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} lock')

        self.uhppote = u
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.{controller}.door.{door}.lock'.lower()
        self._unlocked = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'{self.controller}.door.{self.door}.lock'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            if self._unlocked == False:
                return 'LOCKED'
            elif self._unlocked == True:
                return 'UNLOCKED'

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door}.lock state')
        try:
            response = self.uhppote.get_status(self.serial_no)

            if response.controller == self.serial_no:
                if self.door_id == 1:
                    self._unlocked = response.relays & 0x01 == 0x01
                elif self.door_id == 2:
                    self._unlocked = response.relays & 0x02 == 0x02
                elif self.door_id == 3:
                    self._unlocked = response.relays & 0x04 == 0x04
                elif self.door_id == 4:
                    self._unlocked = response.relays & 0x08 == 0x08
                else:
                    self._unlocked = None

                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class ControllerDoorButton(SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} button')

        self.uhppote = u
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.{controller}.door.{door}.button'.lower()
        self._pressed = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'{self.controller}.door.{self.door}.button'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            if self._pressed == True:
                return 'PRESSED'
            elif self._pressed == False:
                return 'RELEASED'

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} button state')
        try:
            response = self.uhppote.get_status(self.serial_no)

            if response.controller == self.serial_no:
                if self.door_id == 1:
                    self._pressed = response.door_1_button == True
                elif self.door_id == 2:
                    self._pressed = response.door_2_button == True
                elif self.door_id == 3:
                    self._pressed = response.door_3_button == True
                elif self.door_id == 4:
                    self._pressed = response.door_4_button == True
                else:
                    self._pressed = None

                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class ControllerDoorMode(SelectEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} mode')

        self.uhppote = u
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.{controller}.door.{door}.mode'.lower()
        self._mode = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'{self.controller}.door.{self.door}.mode'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def options(self):
        return ['CONTROLLED', 'LOCKED', 'UNLOCKED']

    @property
    def current_option(self) -> Optional[str]:
        if self._available:
            if self._mode == 1:
                return 'UNLOCKED'
            elif self._mode == 2:
                return 'LOCKED'
            elif self._mode == 3:
                return 'CONTROLLED'
            else:
                return 'UNKNOWN'

        return None

    async def async_select_option(self, option):
        if option == 'UNLOCKED':
            self._mode = 1
        elif option == 'LOCKED':
            self._mode = 2
        elif option == 'CONTROLLED':
            self._mode = 3

        try:
            response = self.uhppote.get_door_control(self.serial_no, self.door_id)
            if response.controller == self.serial_no and response.door == self.door_id:
                mode = self._mode
                delay = response.delay
                response = self.uhppote.set_door_control(self.serial_no, self.door_id, mode, delay)

                if response.controller == self.serial_no and response.door == self.door_id:
                    _LOGGER.debug(f'controller {self.controller} door {self.door}: door mode updated')
                    self._mode = response.mode
                    self._available = True
                else:
                    raise ValueError(f'failed to set controller {self.controller} door {self.door} mode')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} mode')

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} mode')
        try:
            response = self.uhppote.get_door_control(self.serial_no, self.door_id)

            if response.controller == self.serial_no and response.door == self.door_id:
                self._mode = response.mode
                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} mode')


class ControllerDoorDelay(NumberEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    _attr_mode = 'auto'
    _attr_native_max_value = 60
    _attr_native_min_value = 1
    _attr_native_step = 1
    _attr_native_unit_of_measurement = TIME_SECONDS

    def __init__(self, u, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} delay')

        self.uhppote = u
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.{controller}.door.{door}.delay'.lower()
        self._delay = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'{self.controller}.door.{self.door}.delay'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> Optional[float]:
        return self._delay

    async def async_set_native_value(self, value):
        try:
            response = self.uhppote.get_door_control(self.serial_no, self.door_id)
            if response.controller == self.serial_no and response.door == self.door_id:
                mode = response.mode
                delay = int(value)
                response = self.uhppote.set_door_control(self.serial_no, self.door_id, mode, delay)

                if response.controller == self.serial_no and response.door == self.door_id:
                    _LOGGER.debug(f'controller {self.controller} door {self.door}: door delay updated')
                    self._delay = response.delay
                    self._available = True
                else:
                    raise ValueError(f'failed to set controller {self.controller} door {self.door} delay')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} delay')

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} delay')
        try:
            response = self.uhppote.get_door_control(self.serial_no, self.door_id)

            if response.controller == self.serial_no and response.door == self.door_id:
                self._delay = response.delay
                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} delay')
