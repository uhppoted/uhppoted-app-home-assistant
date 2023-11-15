"""Platform for sensor integration."""
from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_CONTROLLER_ID = 'controller_id'
CONF_CONTROLLER_ADDRESS = 'controller_address'


def setup_platform(hass: HomeAssistant,
                   config: ConfigType,
                   add_entities: AddEntitiesCallback,
                   discovery_info: DiscoveryInfoType | None = None) -> None:
    id = config[CONF_CONTROLLER_ID]
    address = config[CONF_CONTROLLER_ADDRESS]

    add_entities([
        ControllerID(id),
        ControllerAddress(id, address),
        ControllerDateTime(id, address),
    ])


class ControllerID(SensorEntity):
    _attr_name = "serial number"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, id):
        super().__init__()

        _LOGGER.info(f'>> controller ID:{id}')

        self._name = "Controller ID"
        self.id = id

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.ID'

    def update(self) -> None:
        _LOGGER.info(f'>> controller::update ID:{self.id}')

        self._attr_native_value = self.id


class ControllerAddress(SensorEntity):
    _attr_name = "address"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, id, address):
        super().__init__()

        _LOGGER.info(f'>> controller address:{id}  address:{address}')

        self._name = "Controller Address"
        self.id = id
        self.address = address

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.address'

    def update(self) -> None:
        _LOGGER.info(f'>> controller::update address:{self.id}')

        self._attr_native_value = self.address


class ControllerDateTime(SensorEntity):
    _attr_name = "datetime"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, id, address):
        super().__init__()

        _LOGGER.info(f'>> controller datetime:{id}  address:{address}')

        self._name = "Controller Date/Time"
        self.id = id
        self.address = address

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.datetime'

    def update(self) -> None:
        _LOGGER.info(f'>> controller::update datetime:{self.id}')

        dt = datetime.datetime.now()

        self._attr_native_value = f'{dt:%Y-%m-%d %H:%M:%S}'
