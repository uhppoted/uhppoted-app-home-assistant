from __future__ import annotations
from collections import deque

import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.event import EventEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTime

from .const import ATTR_AVAILABLE
from .const import ATTR_DOOR_CONTROLLER
from .const import ATTR_DOOR_NUMBER
from .const import ATTR_DOORS
from .const import ATTR_DOOR_OPEN
from .const import ATTR_DOOR_BUTTON
from .const import ATTR_DOOR_LOCK
from .const import ATTR_DOOR_MODE
from .const import ATTR_DOOR_DELAY
from .const import EVENT_REASON_DOOR_LOCKED
from .const import EVENT_REASON_DOOR_UNLOCKED
from .const import EVENT_REASON_BUTTON_RELEASED

from .const import ATTR_EVENTS
from .const import ATTR_STATUS

_REASON_BUTTON_PRESSED = 20
_REASON_DOOR_OPEN = 23
_REASON_DOOR_CLOSED = 24
_REASON_DOOR_LOCKED = EVENT_REASON_DOOR_LOCKED
_REASON_DOOR_UNLOCKED = EVENT_REASON_DOOR_UNLOCKED
_REASON_BUTTON_RELEASED = EVENT_REASON_BUTTON_RELEASED


class DoorInfo(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}  door:{door}')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')
        self._name = f'uhppoted.door.{door}.info'.lower()
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
        return f'uhppoted.door.{self._unique_id}.info'.lower()

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
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} info')
        try:
            if self.coordinator.data:
                idx = self._unique_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif ATTR_AVAILABLE not in self.coordinator.data[idx]:
                    self._available = False
                else:
                    state = self.coordinator.data[idx]

                    self._available = state[ATTR_AVAILABLE]
                    self._open = state.get(ATTR_DOOR_OPEN, None)
                    self._button = state.get(ATTR_DOOR_BUTTON, None)
                    self._locked = state.get(ATTR_DOOR_LOCK, None)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} info')


class DoorOpen(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} open')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')
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
            if self.coordinator.data:
                idx = self._unique_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif ATTR_AVAILABLE not in self.coordinator.data[idx]:
                    self._available = False
                elif ATTR_DOOR_OPEN not in self.coordinator.data[idx]:
                    self._available = False
                else:
                    state = self.coordinator.data[idx]
                    self._open = state[ATTR_DOOR_OPEN]
                    self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door}.open state')


class DoorLock(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} lock')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')
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
            if self.coordinator.data:
                idx = self._unique_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif ATTR_AVAILABLE not in self.coordinator.data[idx]:
                    self._available = False
                elif ATTR_DOOR_LOCK not in self.coordinator.data[idx]:
                    self._available = False
                else:
                    state = self.coordinator.data[idx]
                    self._locked = state[ATTR_DOOR_LOCK]
                    self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} {self.door}.lock state')


class DoorButton(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} button')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')

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
            if self.coordinator.data:
                idx = self._unique_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif ATTR_AVAILABLE not in self.coordinator.data[idx]:
                    self._available = False
                elif ATTR_DOOR_BUTTON not in self.coordinator.data[idx]:
                    self._available = False
                else:
                    state = self.coordinator.data[idx]
                    self._pressed = state[ATTR_DOOR_BUTTON]
                    self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} {self.door} button state')


class DoorOpened(CoordinatorEntity, EventEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True
    _attr_event_types = ['OPENED', 'CLOSED']

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door} open event')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self._name = f'uhppoted.door.{door}.open.event'.lower()
        self._door_id = int(f'{door_id}')
        self._events = deque([], 16)
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.open.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door}.open.event')
        try:
            if self.coordinator.data:
                idx = self.serial_no
                door = self._door_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif ATTR_EVENTS not in self.coordinator.data[idx]:
                    self._available = False
                elif not self.coordinator.data[idx][ATTR_AVAILABLE]:
                    self._available = False
                else:
                    events = self.coordinator.data[idx][ATTR_EVENTS]
                    for e in events:
                        if e.door == door and e.reason == _REASON_DOOR_OPEN:
                            self._events.appendleft('OPENED')
                        if e.door == door and e.reason == _REASON_DOOR_CLOSED:
                            self._events.appendleft('CLOSED')

                    self._available = True

                # ... because Home Assistant coalesces multiple events in an update cycle
                if len(self._events) > 0:
                    event = self._events.pop()
                    self._trigger_event(event)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} events')


class DoorButtonPressed(CoordinatorEntity, EventEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True
    _attr_event_types = ['PRESSED', 'RELEASED']

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door} button pressed event')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self._name = f'uhppoted.door.{door}.button.event'.lower()
        self._door_id = int(f'{door_id}')
        self._events = deque([], 16)
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.button.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller} update door {self.door}.button.event state')
        try:
            if self.coordinator.data:
                idx = self.serial_no
                door = self._door_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif not self.coordinator.data[idx][ATTR_AVAILABLE]:
                    self._available = False
                else:
                    if ATTR_EVENTS in self.coordinator.data[idx]:
                        events = self.coordinator.data[idx][ATTR_EVENTS]
                        for e in events:
                            if e.door == door and e.reason == _REASON_BUTTON_PRESSED:
                                self._events.appendleft('PRESSED')

                            if e.door == door and e.reason == _REASON_BUTTON_RELEASED:
                                self._events.appendleft('RELEASED')

                    self._available = True

                # ... because Home Assistant coalesces multiple events in an update cycle
                if len(self._events) > 0:
                    event = self._events.pop()
                    self._trigger_event(event)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} events')


class DoorUnlocked(CoordinatorEntity, EventEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True
    _attr_event_types = ['LOCKED', 'UNLOCKED']

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller}: door:{door} unlocked event')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self.door = door
        self._name = f'uhppoted.door.{door}.unlocked.event'.lower()
        self._door_id = int(f'{door_id}')
        self._events = deque([], 16)
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.door.{self._unique_id}.unlocked.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller} update door {self.door}.unlocked.event state')
        try:
            if self.coordinator.data:
                idx = self.serial_no
                door = self._door_id

                if idx not in self.coordinator.data:
                    self._available = False
                elif not self.coordinator.data[idx][ATTR_AVAILABLE]:
                    self._available = False
                else:
                    if ATTR_EVENTS in self.coordinator.data[idx]:
                        events = self.coordinator.data[idx][ATTR_EVENTS]
                        for e in events:
                            if e.door == door and e.reason == _REASON_DOOR_LOCKED:
                                self._events.appendleft('LOCKED')
                            elif e.door == door and e.reason == _REASON_DOOR_UNLOCKED:
                                self._events.appendleft('UNLOCKED')

                    self._available = True

                # ... because Home Assistant coalesces multiple events in an update cycle
                if len(self._events) > 0:
                    event = self._events.pop()
                    self._trigger_event(event)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} status')


class DoorMode(CoordinatorEntity, SelectEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} mode')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')

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
            controller = self._serial_no
            door = self._door_id
            mode = self._mode
            response = await self.coordinator.set_door_mode(controller, door, mode)

            if response:
                await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} door {self.door} mode')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update door {self.door} mode')
        try:
            idx = self._unique_id

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_DOOR_DELAY not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._mode = state[ATTR_DOOR_MODE]
                self._available = state[ATTR_AVAILABLE]

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
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} delay')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')

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
            controller = self._serial_no
            door = self._door_id
            delay = int(value)
            response = await self.coordinator.set_door_delay(controller, door, delay)

            if response:
                await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error setting controller {self.controller} door {self.door} delay')

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


class DoorUnlock(CoordinatorEntity, ButtonEntity):
    _attr_icon = 'mdi:door'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, door, door_id):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'controller {controller}: door:{door} unlock')

        self._unique_id = unique_id
        self.controller = controller
        self.door = door
        self._serial_no = int(f'{serial_no}')
        self._door_id = int(f'{door_id}')
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
            controller = self._serial_no
            door = self._door_id
            response = self.coordinator.unlock_door(controller, door)

            if response:
                if response.opened:
                    _LOGGER.info(f'unlocked door {self.door}')
                else:
                    _LOGGER.info(f'unable to unlock door {self.door}')

                await self.coordinator.async_request_refresh()

        except (Exception):
            _LOGGER.exception(f'error unlocking door {self.door}')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        self._available = True
