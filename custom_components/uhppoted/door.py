from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity

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

        self._name = f'{name}.door.{door}'
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

        self._name = f'{name}.door.{door}.open'
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

        self._name = f'{name}.door.{door}.locked'
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

        self._name = f'{name}.door.{door}.button'
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
