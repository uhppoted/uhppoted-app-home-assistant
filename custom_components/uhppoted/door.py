from __future__ import annotations

import logging

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.event import EventEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import TIME_SECONDS

_LOGGER = logging.getLogger(__name__)

from .const import ATTR_AVAILABLE
from .const import ATTR_DOOR_CONTROLLER
from .const import ATTR_DOOR_NUMBER
from .const import ATTR_DOORS
from .const import ATTR_DOOR_OPEN
from .const import ATTR_DOOR_BUTTON
from .const import ATTR_DOOR_LOCK
from .const import ATTR_DOOR_MODE
from .const import ATTR_DOOR_DELAY


class Door(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door}')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}'.lower()
        self._locked = None
        self._open = None
        self._button = None
        self._available = False

        self._attributes: Dict[str, Any] = {
            ATTR_DOOR_CONTROLLER: f'{serial_no}',
            ATTR_DOOR_NUMBER: f'{door_id}',
        }

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}'.lower()

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

            if self._locked == False:
                s.append('UNLOCKED')
            elif self._locked == True:
                s.append('LOCKED')

            if self._open == False:
                s.append('CLOSED')
            elif self._open == True:
                s.append('OPEN')

            return ' '.join(s)

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} state')
        try:
            idx = self.serial_no

            if idx not in self.coordinator.data:
                self._available = False
            elif ATTR_DOORS not in self.coordinator.data[idx]:
                self._available = False
            elif self.door_id not in self.coordinator.data[idx][ATTR_DOORS]:
                self._available = False
            else:
                doors = self.coordinator.data[idx][ATTR_DOORS]
                self._open = doors[self.door_id][ATTR_DOOR_OPEN]
                self._button = doors[self.door_id][ATTR_DOOR_BUTTON]
                self._locked = doors[self.door_id][ATTR_DOOR_LOCK]
                self._available = doors[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} status')


class DoorOpen(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door} open')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.open'.lower()
        self._open = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.open'.lower()

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

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door}.open state')
        try:
            idx = self.serial_no

            if idx not in self.coordinator.data:
                self._available = False
            elif ATTR_DOORS not in self.coordinator.data[idx]:
                self._available = False
            elif self.door_id not in self.coordinator.data[idx][ATTR_DOORS]:
                self._available = False
            else:
                doors = self.coordinator.data[idx][ATTR_DOORS]
                self._open = doors[self.door_id][ATTR_DOOR_OPEN]
                self._available = doors[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door}.open state')


class DoorLock(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door} lock')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.lock'.lower()
        self._locked = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.lock'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            if self._locked == True:
                return 'LOCKED'
            elif self._locked == False:
                return 'UNLOCKED'

        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door}.lock state')
        try:
            idx = self.serial_no

            if idx not in self.coordinator.data:
                self._available = False
            elif ATTR_DOORS not in self.coordinator.data[idx]:
                self._available = False
            elif self.door_id not in self.coordinator.data[idx][ATTR_DOORS]:
                self._available = False
            else:
                doors = self.coordinator.data[idx][ATTR_DOORS]
                self._locked = doors[self.door_id][ATTR_DOOR_LOCK]
                self._available = doors[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} {self.door}.lock state')


class DoorButton(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door} button')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.button'.lower()
        self._pressed = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.button'.lower()

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

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} button state')
        try:
            idx = self.serial_no

            if idx not in self.coordinator.data:
                self._available = False
            elif ATTR_DOORS not in self.coordinator.data[idx]:
                self._available = False
            elif self.door_id not in self.coordinator.data[idx][ATTR_DOORS]:
                self._available = False
            else:
                doors = self.coordinator.data[idx][ATTR_DOORS]
                self._pressed = doors[self.door_id][ATTR_DOOR_BUTTON]
                self._available = doors[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} {self.door} button state')


class DoorOpened(EventEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True
    _attr_event_types = ['OPEN', 'CLOSE']

    def __init__(self, u, unique_id, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} open event')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.open.event'.lower()
        self._open = None

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.open.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door}.open.event state')
        try:
            response = self.uhppote.get_status(self.serial_no)
            last = self._open

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

                if self._open != last and self._open:
                    self._trigger_event('OPEN')
                elif self._open != last and not self._open:
                    self._trigger_event('CLOSE')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class DoorUnlocked(EventEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True
    _attr_event_types = ['LOCKED', 'UNLOCKED']

    def __init__(self, u, unique_id, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} unlocked event')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.unlocked.event'.lower()
        self._unlocked = None

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.unlocked.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller} update door {self.door}.unlocked.event state')
        try:
            response = self.uhppote.get_status(self.serial_no)
            last = self._unlocked

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

                if self._unlocked != last and self._unlocked:
                    self._trigger_event('UNLOCKED')
                elif self._unlocked != last and not self._unlocked:
                    self._trigger_event('LOCKED')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class DoorButtonPressed(EventEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True
    _attr_event_types = ['PRESSED', 'RELEASED']

    def __init__(self, u, unique_id, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} button pressed event')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.button.event'.lower()
        self._pressed = None

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.button.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller} update door {self.door}.button.event state')
        try:
            response = self.uhppote.get_status(self.serial_no)
            last = self._pressed

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

                if self._pressed != last and self._pressed:
                    self._trigger_event('PRESSED')
                elif self._pressed != last and not self._pressed:
                    self._trigger_event('RELEASED')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class DoorMode(SelectEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, unique_id, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} mode')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.mode'.lower()
        self._mode = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.mode'.lower()

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
                    _LOGGER.info(f'set door {self.door} mode  ({option})')
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


class DoorDelay(CoordinatorEntity, NumberEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    _attr_mode = 'auto'
    _attr_native_max_value = 60
    _attr_native_min_value = 1
    _attr_native_step = 1
    _attr_native_unit_of_measurement = TIME_SECONDS

    def __init__(self, coordinator, u, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} delay')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.delay'.lower()
        self._delay = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.delay'.lower()

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
                    _LOGGER.info(f'set door {self.door} delay ({delay}s)')
                    self._delay = response.delay
                    self._available = True
                else:
                    raise ValueError(f'failed to set controller {self.controller} door {self.door} delay')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} delay')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} delay')
        try:
            idx = self._unique_id

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_DOOR_DELAY not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._delay = state[ATTR_DOOR_DELAY]
                self._available = state[ATTR_AVAILABLE]
        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} delay')


class DoorUnlock(ButtonEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, u, unique_id, controller, serial_no, door, door_id):
        super().__init__()

        _LOGGER.debug(f'controller {controller}: door:{door} unlock')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self.door_id = int(f'{door_id}')

        self._name = f'uhppoted.door.{door}.unlock'.lower()
        self._available = True

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.unlock'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    async def async_press(self) -> None:
        try:
            response = self.uhppote.open_door(self.serial_no, self.door_id)
            if response.controller == self.serial_no:
                if response.opened:
                    _LOGGER.info(f'unlocked door {self.door}')
                else:
                    raise ValueError(f'failed to unlock door {self.door}')

        except (Exception):
            _LOGGER.exception(f'error unlocking door {self.door}')

    async def async_update(self):
        self._available = True
