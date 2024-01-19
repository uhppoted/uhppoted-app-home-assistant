from __future__ import annotations

import datetime
import logging

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.datetime import DateTimeEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .const import ATTR_AVAILABLE
from .const import ATTR_CONTROLLER
from .const import ATTR_CONTROLLER_DATETIME


class ControllerInfo(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:identifier'
    _attr_has_entity_name: True
    _attr_translation_key = 'controller_id'

    def __init__(self, coordinator, unique_id, controller, serial_no):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller {controller} {serial_no}')

        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self._name = f'uhppoted.controller.{controller}.info'.lower()
        self._state = serial_no
        self._attributes: Dict[str, Any] = {
            ATTR_ADDRESS: None,
            ATTR_NETMASK: None,
            ATTR_GATEWAY: None,
            ATTR_FIRMWARE: None,
        }
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.controller.{self._unique_id}.info'.lower()

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
            idx = self.serial_no

            if idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CONTROLLER not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx][ATTR_CONTROLLER]
                self._attributes[ATTR_ADDRESS] = state[ATTR_ADDRESS]
                self._attributes[ATTR_NETMASK] = state[ATTR_NETMASK]
                self._attributes[ATTR_GATEWAY] = state[ATTR_GATEWAY]
                self._attributes[ATTR_FIRMWARE] = state[ATTR_FIRMWARE]
                self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} information')


class ControllerDateTime(CoordinatorEntity, DateTimeEntity):
    _attr_icon = 'mdi:calendar-clock-outline'
    _attr_has_entity_name: True

    def __init__(self, coordinator, u, unique_id, controller, serial_no):
        super().__init__(coordinator, context=int(f'{serial_no}'))

        _LOGGER.debug(f'controller datetime:{controller}')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
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
            tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            local = utc.astimezone(tz)
            response = self.uhppote.set_time(self.serial_no, local)

            if response.controller == self.serial_no:
                year = response.datetime.year
                month = response.datetime.month
                day = response.datetime.day
                hour = response.datetime.hour
                minute = response.datetime.minute
                second = response.datetime.second
                self._datetime = datetime.datetime(year, month, day, hour, minute, second, 0, tz)
                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} date/time')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'controller:{self.controller}  update datetime')
        try:
            controllers = self.coordinator.controllers
            serial_no = self.serial_no

            if serial_no in controllers:
                state = controllers[serial_no]
                self._available = state['available']
                self._datetime = state[ATTR_CONTROLLER_DATETIME]
            else:
                self._available = False

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} date/time')
