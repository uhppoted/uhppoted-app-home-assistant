"""Platform for sensor integration."""
from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_BIND_ADDR = 'bind_address'
CONF_BROADCAST_ADDR = 'broadcast_address'
CONF_LISTEN_ADDR = 'listen_address'
CONF_DEBUG = 'debug'

CONF_CONTROLLER_ID = 'controller_id'
CONF_CONTROLLER_ADDRESS = 'controller_address'


async def async_setup_platform(hass: HomeAssistantType,
                               config: ConfigType,
                               async_add_entities: Callable,
                               discovery_info: DiscoveryInfoType | None = None) -> None:
    bind = config[CONF_BIND_ADDR]
    broadcast = config[CONF_BROADCAST_ADDR]
    listen = config[CONF_LISTEN_ADDR]
    debug = config[CONF_DEBUG]

    if bind == '':
        bind = '0.0.0.0'

    if broadcast == '':
        broadcast = '255.255.255.255:60000'

    if listen == '':
        listen = '0.0.0.0:60001'

    u = uhppote.Uhppote(bind, broadcast, listen, debug)
    id = config[CONF_CONTROLLER_ID]
    address = config[CONF_CONTROLLER_ADDRESS]

    sensors = [
        ControllerID(u, id),
        ControllerAddress(u, id, address),
        ControllerDateTime(u, id, address),
    ]

    async_add_entities(sensors, update_before_add=True)


class ControllerID(SensorEntity):
    _attr_name = "serial number"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id):
        super().__init__()

        _LOGGER.debug(f'controller ID:{id}')

        self.uhppote = u
        self.id = id
        self._name = "Controller ID"
        self._available = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.ID'

    @property
    def available(self) -> bool:
        return self._available

    def update(self) -> None:
        _LOGGER.info(f'controller::update ID:{self.id}')

        self._attr_native_value = self.id


class ControllerAddress(SensorEntity):
    _attr_name = "address"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, address):
        super().__init__()

        _LOGGER.debug(f'controller address:{id}  address:{address}')

        self.uhppote = u
        self.id = id
        self.address = address
        self._name = "Controller Address"
        self._available = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.address'

    @property
    def available(self) -> bool:
        return self._available

    def update(self) -> None:
        _LOGGER.info(f'controller::update address:{self.id}')

        self._attr_native_value = self.address


class ControllerDateTime(SensorEntity):
    _attr_name = "datetime"
    _attr_device_class = None
    _attr_last_reset = None
    _attr_native_unit_of_measurement = None
    _attr_state_class = None

    def __init__(self, u, id, address):
        super().__init__()

        _LOGGER.debug(f'controller datetime:{id}  address:{address}')

        self.uhppote = u
        self.id = id
        self.address = address
        self._name = "Controller Date/Time"
        self._state = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.id}.datetime'

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._state != None:
            return f'{self._state:%Y-%m-%d %H:%M:%S}'

        return None

    async def async_update(self):
        _LOGGER.debug(f'controller::update datetime:{self.id}')
        try:
            controller = self.id
            response = self.uhppote.get_time(controller)

            if response.controller == self.id:
                self._state = response.datetime
                self._available = True

            # clones_data = await self.github.getitem(clones_url)
            # views_url = f"{repo_url}/traffic/views"
            # views_data = await self.github.getitem(views_url)
            # self.attrs[ATTR_VIEWS] = views_data["count"]
            # self.attrs[ATTR_VIEWS_UNIQUE] = views_data["uniques"]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving controller {self.id} date/time')
