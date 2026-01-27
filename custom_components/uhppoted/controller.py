from __future__ import annotations
from collections import deque

import datetime
import logging
import asyncio

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
from .const import ATTR_CONTROLLER_SERIAL_NUMBER
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

from .const import STORAGE_VERSION
from .const import STORAGE_KEY_INTERLOCK

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
            ATTR_CONTROLLER_SERIAL_NUMBER: serial_no,
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
            response = await self.coordinator.set_datetime(controller, localtime)

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
        interlock = restored.get('interlock', None)
        modified = restored.get('modified', None)

        return cls(interlock, modified)

    def __init__(self, interlock: str = '', modified: str = ''):
        self._interlock = interlock if interlock else ''
        self._modified = modified if modified else ''

    def as_dict(self) -> dict:
        return {
            'interlock': self._interlock,
            'modified': self._modified,
        }

    @property
    def interlock(self) -> str:
        return self._interlock

    @interlock.setter
    def interlock(self, interlock: str) -> None:
        if interlock in list(INTERLOCK.keys()):
            self._interlock = interlock
        else:
            self._interlock = ''

    @property
    def modified(self) -> str:
        return self._modified

    @modified.setter
    def modified(self, modified: str) -> None:
        self._modified = modified if modified else ''


class Interlock(CoordinatorEntity, SelectEntity, RestoreEntity):
    _attr_icon = 'mdi:lock-plus'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, controller, serial_no, store, persist):
        super().__init__(coordinator, context=unique_id)

        _LOGGER.debug(f'interlock {controller}')

        self._unique_id = unique_id
        self._controller = controller
        self._serial_no = int(f'{serial_no}')
        self._store = store
        self._persist = persist
        self._pending = None

        self._name = f'uhppoted.controller.{controller}.interlock'.lower()
        self._mode = -1
        self._extra = InterlockExtraStoredData(None, None)
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

    # Restores the controller door interlock mode on startup
    #
    # There is no 'get_interlock' controller API so the interlock state is the last 'set interlock'. The interlock
    # state is only restored if:
    #      - uhppoted.controller.{name}.interlock is listed in the persisted.entities in the configuration.yaml file
    #      - the 'last state' has a valid interlock mode
    #      - the 'last state' matches the 'persisted' state set in async_select_option
    #      - the 'last state' matches the 'extra' state set in async_select_option
    #      - the 'extra' state matches the 'persisted' state set in async_select_option
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        # restore persisted data
        if self._persist:
            persisted = {}
            extra = self._extra

            if self._store:
                if interlocks := self._store.get('interlocks'):
                    if record := interlocks.get(self._name):
                        persisted['interlock'] = record.get('interlock', None)
                        persisted['modified'] = record.get('modified', None)

            # restore 'extra' data
            if v := await self.async_get_last_extra_data():
                extra = InterlockExtraStoredData.from_dict(v.as_dict())

            # restore door interlocks
            try:
                if state := await self.async_get_last_state():
                    if mode := INTERLOCK.get(state.state, None):
                        if state.state != persisted.get('interlock', None):
                            _LOGGER.warning(f"{self._controller}: inconsistent interlock 'persisted' state (state:{state.state}, stored:{persisted})") # yapf: disable
                        elif state.state != extra.interlock:
                            _LOGGER.warning(f"{self._controller}: inconsistent interlock 'extra' state (state:{state.state}, stored:{extra.interlock})") # yapf: disable
                        elif extra.modified != persisted.get('modified', None):
                            _LOGGER.warning(f"{self._controller}: inconsistent interlock 'extra' state (state:{extra.modified}, stored:{persisted.get('modified')})") # yapf: disable
                        else:
                            self._extra = extra
                            await self._set_interlock(self._serial_no, mode)
                            _LOGGER.info(f'{self._controller}: restored door interlock mode ({state.state})')

            except Exception as err:
                _LOGGER.warning(f'{self._controller}: error initialising door interlock mode ({err})')

    async def async_select_option(self, option):
        _LOGGER.debug(f'controller:{self._controller}  set interlock {option}')

        if mode := INTERLOCK.get(option, None):
            try:
                await self._set_interlock(self._serial_no, mode)

                modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self._extra.interlock = option
                self._extra.modified = modified

                if self._store:
                    if store := self._store.get('store'):
                        interlocks = self._store.get('interlocks', {})

                        interlocks[self.name] = {
                            'interlock': option,
                            'modified': modified,
                        }

                        await store.async_save(interlocks)

            except Exception as err:
                _LOGGER.exception(f'error setting controller {self._controller} interlock mode ({err})')

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

                # refresh controller door interlock mode if expired
                if self._available and self._mode not in INTERLOCK.values() and self._extra.interlock in INTERLOCK.keys(): # yapf: disable
                    if mode := INTERLOCK.get(self._extra.interlock, None):
                        if self._pending is None or self._pending.done():
                            self._pending = self.hass.async_create_task(self._refresh_interlock(self._serial_no, mode))

        except Exception as err:
            self._available = False
            _LOGGER.exception(f'{self._controller}: error updating controller door interlock mode {err}')

    async def _set_interlock(self, controller, mode):
        lookup = {v: k for k, v in INTERLOCK.items()}

        try:
            if response := await self.coordinator.set_interlock(controller, mode):
                if response.ok == True:
                    self._mode = mode
                    self._available = True
                    self.async_write_ha_state()

                    _LOGGER.info(f"{self._controller}: set door interlock mode {lookup.get(mode, 'UNKNOWN')} ({mode})")

        except Exception as err:
            self._available = False
            raise err

    # NTS: Because of the way coordinators + callbacks work it's quite possible for a _refresh_interlock task to complete
    #      before a previous callback has updated the state. The 100ms just keeps the task alive to prevent another refresh
    #      being scheduled almost immediately.
    async def _refresh_interlock(self, controller, mode):
        try:
            _LOGGER.warning(f'{self._controller}: refreshing expired door interlock mode ({mode}) [{self._mode}]')
            if self._mode != mode:
                await self._set_interlock(controller, mode)

            await asyncio.sleep(0.1)
        except Exception as err:
            _LOGGER.exception(f'{self._controller}: error refreshing expired door interlock mode ({err})')


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
        _LOGGER.debug(f'controller:{self._controller}  set card anti-passback {option}')

        try:
            mode = ANTIPASSBACK.get(option, None)
            if mode is not None:
                controller = self._serial_no
                if response := await self.coordinator.set_antipassback(controller, mode):
                    if response.ok:
                        self._mode = mode
                        _LOGGER.info(f'set card anti-passback mode {mode}')
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
