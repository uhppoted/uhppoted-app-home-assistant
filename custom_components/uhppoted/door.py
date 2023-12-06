from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.number import NumberEntity

_LOGGER = logging.getLogger(__name__)


class ControllerDoor(SensorEntity):
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, name, door_id, door):
        super().__init__()

        _LOGGER.debug(f'controller {id}: door:{door_id}')

        self.uhppote = u
        self.id = id
        self.door_id = door_id
        self.door = door

        self._name = f'uhppoted.{name}.door.{door}'
        self._icon = 'mdi:door'
        self._unlocked = None
        self._open = None
        self._button = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.door.{self.door_id}'

    @property
    def icon(self) -> str:
        return f'{self._icon}'

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

            return ','.join(s)

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.id}  update door {self.door_id} state')
        try:
            controller = self.id
            response = self.uhppote.get_status(controller)

            if response.controller == self.id:
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
            _LOGGER.exception(f'error retrieving controller {self.id} status')


class ControllerDoorOpen(SensorEntity):
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, name, door_id, door):
        super().__init__()

        _LOGGER.debug(f'controller {id}: door:{door_id} open')

        self.uhppote = u
        self.id = id
        self.door_id = door_id
        self.door = door

        self._name = f'uhppoted.{name}.door.{door}.open'
        self._icon = 'mdi:door'
        self._open = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.door.{self.door_id}.open'

    @property
    def icon(self) -> str:
        return f'{self._icon}'

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
        _LOGGER.debug(f'controller:{self.id}  update door {self.door_id}.open state')
        try:
            controller = self.id
            response = self.uhppote.get_status(controller)

            if response.controller == self.id:
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
            _LOGGER.exception(f'error retrieving controller {self.id} status')


class ControllerDoorLocked(SensorEntity):
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, name, door_id, door):
        super().__init__()

        _LOGGER.debug(f'controller {id}: door:{door_id} locked')

        self.uhppote = u
        self.id = id
        self.door_id = door_id
        self.door = door

        self._name = f'uhppoted.{name}.door.{door}.locked'
        self._icon = 'mdi:door'
        self._unlocked = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.door.{self.door_id}.locked'

    @property
    def icon(self) -> str:
        return f'{self._icon}'

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
        _LOGGER.debug(f'controller:{self.id}  update door {self.door_id}.locked state')
        try:
            controller = self.id
            response = self.uhppote.get_status(controller)

            if response.controller == self.id:
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
            _LOGGER.exception(f'error retrieving controller {self.id} status')


class ControllerDoorButton(SensorEntity):
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, name, door_id, door):
        super().__init__()

        _LOGGER.debug(f'controller {id}: door:{door_id} button')

        self.uhppote = u
        self.id = id
        self.door_id = door_id
        self.door = door

        self._name = f'uhppoted.{name}.door.{door}.button'
        self._icon = 'mdi:door'
        self._button = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.door.{self.door_id}.button'

    @property
    def icon(self) -> str:
        return f'{self._icon}'

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            if self._button == True:
                return 'PRESSED'
            elif self._button == False:
                return 'RELEASED'

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.id}  update door {self.door_id} button state')
        try:
            controller = self.id
            response = self.uhppote.get_status(controller)

            if response.controller == self.id:
                if self.door_id == 1:
                    self._button = response.door_1_button == True
                elif self.door_id == 2:
                    self._button = response.door_2_button == True
                elif self.door_id == 3:
                    self._button = response.door_3_button == True
                elif self.door_id == 4:
                    self._button = response.door_4_button == True
                else:
                    self._button = None

                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.id} status')


class ControllerDoorMode(SelectEntity):
    _attr_device_class = ''
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, name, door_id, door):
        super().__init__()

        _LOGGER.debug(f'controller {id}: door:{door_id} mode')

        self.uhppote = u
        self.id = id
        self.door_id = door_id
        self.door = door

        self._name = f'uhppoted.{name}.door.{door}.mode'
        self._icon = 'mdi:door'
        self._mode = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.door.{self.door_id}.mode'

    @property
    def icon(self) -> str:
        return f'{self._icon}'

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
            controller = self.id
            door = self.door_id

            response = self.uhppote.get_door_control(controller, door)
            if response.controller == self.id and response.door == self.door_id:
                mode = self._mode
                delay = response.delay
                response = self.uhppote.set_door_control(controller, door, mode, delay)

                if response.controller == self.id and response.door == self.door_id:
                    _LOGGER.debug(f'controller {self.id} door {self.door}: door mode updated')
                    self._mode = response.mode
                    self._available = True
                else:
                    raise ValueError(f'failed to set controller {self.id} door {self.door} mode')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.id} door {self.door} mode')

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.id}  update door {self.door_id} mode')
        try:
            controller = self.id
            door = self.door_id

            response = self.uhppote.get_door_control(controller, door)

            if response.controller == self.id and response.door == self.door_id:
                self._mode = response.mode
                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.id} door {self.door} mode')


class ControllerDoorDelay(NumberEntity):
    _attr_device_class = ''
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None
    _attr_mode = 'auto'
    _attr_native_max_value = 60
    _attr_native_min_value = 1
    _attr_native_step = 1

    def __init__(self, u, id, name, door_id, door):
        super().__init__()

        _LOGGER.debug(f'controller {id}: door:{door_id} delay')

        self.uhppote = u
        self.id = id
        self.door_id = door_id
        self.door = door

        self._name = f'uhppoted.{name}.door.{door}.delay'
        self._icon = 'mdi:door'
        self._delay = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.door.{self.door_id}.delay'

    @property
    def icon(self) -> str:
        return f'{self._icon}'

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> Optional[float]:
        return self._delay

    async def async_set_native_value(self, value):
        try:
            controller = self.id
            door = self.door_id

            response = self.uhppote.get_door_control(controller, door)
            if response.controller == self.id and response.door == self.door_id:
                mode = response.mode
                delay = int(value)
                response = self.uhppote.set_door_control(controller, door, mode, delay)

                if response.controller == self.id and response.door == self.door_id:
                    _LOGGER.debug(f'controller {self.id} door {self.door}: door delay updated')
                    self._delay = response.delay
                    self._available = True
                else:
                    raise ValueError(f'failed to set controller {self.id} door {self.door} delay')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.id} door {self.door} delay')

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.id}  update door {self.door_id} delay')
        try:
            controller = self.id
            door = self.door_id

            response = self.uhppote.get_door_control(controller, door)

            if response.controller == self.id and response.door == self.door_id:
                self._delay = response.delay
                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.id} door {self.door} delay')
