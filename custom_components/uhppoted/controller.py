from __future__ import annotations
from collections import deque

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.datetime import DateTimeEntity
from homeassistant.components.event import EventEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_AVAILABLE
from .const import ATTR_CONTROLLER_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE
from .const import ATTR_CONTROLLER
from .const import ATTR_CONTROLLER_DATETIME
from .const import ATTR_CONTROLLER_LISTENER
from .const import ATTR_EVENTS
from .const import EVENTS


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
            ATTR_NETMASK: None,
            ATTR_GATEWAY: None,
            ATTR_FIRMWARE: None,
            ATTR_CONTROLLER_LISTENER: None,
        }
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.controller.{self._unique_id}.info'.lower()

    # @property
    # def name(self) -> str:
    #     return self._name

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
            elif ATTR_CONTROLLER not in self.coordinator.data[idx]:
                self._available = False
            elif ATTR_AVAILABLE not in self.coordinator.data[idx]:
                self._available = False
            else:
                data = self.coordinator.data[idx]
                state = data[ATTR_CONTROLLER]
                self._attributes[ATTR_CONTROLLER_ADDRESS] = state[ATTR_CONTROLLER_ADDRESS]
                self._attributes[ATTR_NETMASK] = state[ATTR_NETMASK]
                self._attributes[ATTR_GATEWAY] = state[ATTR_GATEWAY]
                self._attributes[ATTR_FIRMWARE] = state[ATTR_FIRMWARE]
                self._attributes[ATTR_CONTROLLER_LISTENER] = data.get(ATTR_CONTROLLER_LISTENER, None)
                self._available = self.coordinator.data[idx][ATTR_AVAILABLE]

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
                self._available = state[ATTR_AVAILABLE]
                self._datetime = state[ATTR_CONTROLLER_DATETIME]

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
