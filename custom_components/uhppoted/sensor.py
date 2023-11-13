"""Platform for sensor integration."""
from __future__ import annotations

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

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None:
    id = config[CONF_CONTROLLER_ID]
    address = config[CONF_CONTROLLER_ADDRESS]

    add_entities([Controller(id, address)])


class Controller(SensorEntity):
    _attr_name = "UHPPOTE"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, id, address):
        super().__init__()

        _LOGGER.info(f'>> controller ID:{id}  address:{address}')

        self._name = "UHPPOTE"
        self.id = id
        self.address = address

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self.id

    def update(self) -> None:
        _LOGGER.info(f'>> controller::update ID:{self.id}')

        self._attr_native_value = self.id

