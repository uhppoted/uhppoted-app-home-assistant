from __future__ import annotations
from collections import deque

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import callback
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.datetime import DateTimeEntity
from homeassistant.components.event import EventEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.restore_state import ExtraStoredData
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_AVAILABLE
from .const import ATTR_CONTROLLER_ADDRESS
from .const import ATTR_CONTROLLER_PROTOCOL
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE
from .const import ATTR_CONTROLLER
from .const import ATTR_CONTROLLER_DATETIME
from .const import ATTR_CONTROLLER_LISTENER
from .const import ATTR_CONTROLLER_INTERLOCK
from .const import ATTR_CONTROLLER_ANTIPASSBACK
from .const import ATTR_EVENTS
from .const import EVENTS

INTERLOCK = {
    'NONE': 0,
    'DOORS 1&2': 1,
    'DOORS 3&4': 2,
    'DOORS 1&2,3&4': 3,
    'DOORS 1,2&3': 4,
    'DOORS 1,2,3&4': 8,
}

ANTIPASSBACK = {
    'DISABLED': 0,
    '(1:2);(3:4)': 1,
    '(1,3):(2,4)': 2,
    '1:(2,3)': 3,
    '1:(2,3,4)': 4,
}


class ControllerInfo(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:identifier'
    _attr_has_entity_name = True
    _attr_translation_key = 'controller_id'

    def __init__(self, coordinator, unique_id, controller, serial_no):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller} {serial_no}')

        self._unique_id = unique_id
        self.controller = controller
        self._serial_no = int(f'{serial_no}')
        self._name = f'uhppoted.controller.{controller}.info'.lower()
        self._state = serial_no
        self._attributes: Dict[str, Any] = {
            ATTR_CONTROLLER_ADDRESS: None,
            ATTR_CONTROLLER_PROTOCOL: None,
            ATTR_NETMASK: None,
            ATTR_GATEWAY: None,
            ATTR_FIRMWARE: None,
            ATTR_CONTROLLER_LISTENER: None,
        }
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.controller.{self._unique_id}.info'.lower()

    # NTS: remove to use name translation
    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._state != None:
            return f'{self._state}'

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
        _LOGGER.debug(f'controller:{self.controller}  update info')

        try:
            idx = self._serial_no

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._attributes[ATTR_CONTROLLER_ADDRESS] = state.get(ATTR_CONTROLLER_ADDRESS, None)
                self._attributes[ATTR_CONTROLLER_PROTOCOL] = state.get(ATTR_CONTROLLER_PROTOCOL, None)
                self._attributes[ATTR_NETMASK] = state.get(ATTR_NETMASK, None)
                self._attributes[ATTR_GATEWAY] = state.get(ATTR_GATEWAY, None)
                self._attributes[ATTR_FIRMWARE] = state.get(ATTR_FIRMWARE, None)
                self._attributes[ATTR_CONTROLLER_LISTENER] = state.get(ATTR_CONTROLLER_LISTENER, None)
                self._available = state.get(ATTR_AVAILABLE, False)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} information')


class ControllerDateTime(CoordinatorEntity, DateTimeEntity):
    _attr_icon = 'mdi:calendar-clock-outline'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller datetime:{controller}')

        self._unique_id = unique_id
        self.controller = controller
        self._serial_no = int(f'{serial_no}')
        self._name = f'uhppoted.controller.{controller}.datetime'.lower()
        self._datetime = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.controller.{self._unique_id}.datetime'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> Optional[datetime.datetime]:
        return self._datetime

    async def async_set_value(self, utc: datetime) -> None:
        try:
            controller = self._serial_no
            tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            localtime = utc.astimezone(tz)
            response = self.coordinator.set_datetime(controller, localtime)

            if response:
                await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating controller {self.controller} date/time')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update datetime')
        try:
            idx = self._serial_no

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_AVAILABLE not in self.coordinator.data[idx]:
                self._available = False
            elif ATTR_CONTROLLER_DATETIME not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._available = state.get(ATTR_AVAILABLE, False)
                self._datetime = state.get(ATTR_CONTROLLER_DATETIME, None)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} date/time')


class ControllerEvent(CoordinatorEntity, EventEntity):
    _attr_icon = 'mdi:lock-alert'
    _attr_has_entity_name: True
    _attr_event_types = list(EVENTS.values())

    def __init__(self, coordinator, unique_id, controller, serial_no):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller} event')

        self._unique_id = unique_id
        self.controller = controller
        self._serial_no = int(f'{serial_no}')
        self._name = f'uhppoted.controller.{controller}.event'.lower()
        self._events = deque([], 16)
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.controller.{self._unique_id}.event'.lower()

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
        _LOGGER.debug(f'controller:{self.controller} update event')
        try:
            idx = self._serial_no

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_EVENTS not in self.coordinator.data[idx]:
                self._available = False
            else:
                events = self.coordinator.data[idx][ATTR_EVENTS]
                for e in events:
                    if e.reason in EVENTS:
                        self._events.appendleft(EVENTS[e.reason])

                self._available = True

            # ... because Home Assistant coalesces multiple events in an update cycle
            if len(self._events) > 0:
                event = self._events.pop()
                self._trigger_event(event)

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} events')


class InterlockExtraStoredData(ExtraStoredData):

    @classmethod
    def from_dict(cls, restored: dict[str, Any]) -> "InterlockExtraStoredData":
        interlock = restored.get("interlock", -1)
        return cls(interlock)

    def __init__(self, interlock: int):
        self._interlock = interlock

    def as_dict(self) -> dict:
        return {'interlock': self._interlock}

    @property
    def interlock(self) -> int:
        return self._interlock

    @interlock.setter
    def interlock(self, interlock: int) -> None:
        if interlock == 0 or interlock == 1 or interlock == 2 or interlock == 3 or interlock == 4:
            self._interlock = interlock
        else:
            self._interlock = -1


class Interlock(CoordinatorEntity, SelectEntity, RestoreEntity):
    _attr_icon = 'mdi:lock-plus'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'interlock {controller}')

        self._unique_id = unique_id
        self._controller = controller
        self._serial_no = int(f'{serial_no}')

        self._name = f'uhppoted.controller.{controller}.interlock'.lower()
        self._mode = -1
        self._extra = InterlockExtraStoredData(-1)
        self._available = False

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def options(self):
        return list(INTERLOCK.keys())

    @property
    def current_option(self) -> Optional[str]:
        lookup = {v: k for k, v in INTERLOCK.items()}
        if self._available:
            return lookup.get(self._mode, 'UNKNOWN')

        return None

    @property
    def extra_restore_state_data(self) -> ExtraStoredData | None:
        return self._extra

    # Sets the controller door interlock mode on startup
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        # if state := await self.async_get_last_state():
        #     self._mode = INTERLOCK.get(state.state, -1)

        if v := await self.async_get_last_extra_data():
            self._extra = InterlockExtraStoredData.from_dict(v.as_dict())
            if self._extra.interlock in INTERLOCK.values():
                controller = self._serial_no
                mode = self._extra.interlock
                self.hass.async_create_background_task(
                    self._background_set_timeout(controller, mode),
                    name='uhppoted::set controller door interlock on startup')

    async def async_select_option(self, option):
        _LOGGER.debug(f'controller:{self._controller}  set interlock {option}')

        try:
            if mode := INTERLOCK.get(option, None):
                self._extra.interlock = mode

                controller = self._serial_no
                if response := self.coordinator.set_interlock(controller, mode):
                    if response.ok:
                        self._mode = mode

                    self._available = True
                    await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error setting controller {self._controller} interlock mode')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self._controller} update door interlock mode')
        try:
            idx = self._serial_no

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CONTROLLER_INTERLOCK not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._mode = state[ATTR_CONTROLLER_INTERLOCK]
                self._available = state[ATTR_AVAILABLE]

                if self._available and self._mode not in INTERLOCK.values() and self._extra.interlock in INTERLOCK.values():
                    controller = self._serial_no
                    mode = self._extra.interlock
                    self.hass.async_create_background_task(
                        self._background_set_timeout(controller, mode), 
                        name='uhppoted::set controller door interlock on startup')

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self._controller} interlock mode')

    async def _background_set_timeout(self, controller, mode):
        try:
            self.coordinator.set_interlock(controller, mode)
        except Exception as err:
            _LOGGER.warning(f'set-interlock on startup failed ({err})')


class AntiPassback(CoordinatorEntity, SelectEntity):
    _attr_icon = 'mdi:lock-plus'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'antipassback {controller}')

        self._unique_id = unique_id
        self._controller = controller
        self._serial_no = int(f'{serial_no}')

        self._name = f'uhppoted.controller.{controller}.antipassback'.lower()
        self._mode = -1
        self._available = False

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def options(self):
        return list(ANTIPASSBACK.keys())

    @property
    def current_option(self) -> Optional[str]:
        lookup = {v: k for k, v in ANTIPASSBACK.items()}
        if self._available:
            return lookup.get(self._mode, 'UNKNOWN')

        return None

    async def async_select_option(self, option):
        _LOGGER.debug(f'controller:{self._controller}  set anti-passback {option}')

        try:
            if mode := ANTIPASSBACK.get(option, None):
                controller = self._serial_no
                if response := self.coordinator.set_antipassback(controller, mode):
                    if response.ok:
                        self._mode = mode
                    else:
                        self._mode = -1

                    self._available = True
                    await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error setting controller {self._controller} anti-passback mode')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self._controller} update anti-passback mode')
        try:
            idx = self._serial_no

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CONTROLLER_ANTIPASSBACK not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._mode = state[ATTR_CONTROLLER_ANTIPASSBACK]
                self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self._controller} anti-passback mode')
