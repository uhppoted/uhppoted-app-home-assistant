from __future__ import annotations

import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.datetime import DateTimeEntity

_LOGGER = logging.getLogger(__name__)

# Attribute constants
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE


class ControllerInfo(SensorEntity):
    _attr_icon = 'mdi:identifier'
    _attr_has_entity_name: True
    _attr_translation_key = 'controller_id'

    def __init__(self, u, unique_id, controller, serial_no):
        super().__init__()

        _LOGGER.debug(f'controller {controller} {serial_no}')

        self.uhppote = u
        self._unique_id = unique_id
        self.controller = controller
        self.serial_no = int(f'{serial_no}')
        self._name = f'uhppoted.controller.{controller}.info'.lower()
        self._state = None
        self._attributes: Dict[str, Any] = {
            ATTR_ADDRESS: '',
            ATTR_NETMASK: '',
            ATTR_GATEWAY: '',
            ATTR_FIRMWARE: '',
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

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update info')
        try:
            response = self.uhppote.get_controller(self.serial_no)

            if response.controller == self.serial_no:
                self._state = response.controller
                self._available = True
                self._attributes[ATTR_ADDRESS] = f'{response.ip_address}'
                self._attributes[ATTR_NETMASK] = f'{response.subnet_mask}'
                self._attributes[ATTR_GATEWAY] = f'{response.gateway}'
                self._attributes[ATTR_FIRMWARE] = f'{response.version} {response.date:%Y-%m-%d}'

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} information')


class ControllerDateTime(DateTimeEntity):
    _attr_icon = 'mdi:calendar-clock-outline'
    _attr_has_entity_name: True

    def __init__(self, u, unique_id, controller, serial_no):
        super().__init__()

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

    async def async_update(self):
        _LOGGER.debug(f'controller:{self.controller}  update datetime')
        try:
            response = self.uhppote.get_time(self.serial_no)

            if response.controller == self.serial_no:
                year = response.datetime.year
                month = response.datetime.month
                day = response.datetime.day
                hour = response.datetime.hour
                minute = response.datetime.minute
                second = response.datetime.second
                tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

                self._datetime = datetime.datetime(year, month, day, hour, minute, second, 0, tz)
                self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.controller} date/time')
