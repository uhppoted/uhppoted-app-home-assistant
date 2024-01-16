from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

# Configuration constants
from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

# Attribute constants
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .config import configure_controllers
from .config import configure_doors
from .controller import ControllerInfo
from .door import ControllerDoorUnlocked
from .door import ControllerDoorOpened
from .door import ControllerDoorButtonPressed


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options

    bind = options[CONF_BIND_ADDR]
    broadcast = options[CONF_BROADCAST_ADDR]
    listen = options[CONF_LISTEN_ADDR]
    debug = options[CONF_DEBUG]

    u = uhppote.Uhppote(bind, broadcast, listen, debug)
    entities = []

    def g(controller, serial_no, door, door_no):
        entities.extend([
            ControllerDoorOpened(u, controller, serial_no, door, door_no),
            ControllerDoorButtonPressed(u, controller, serial_no, door, door_no),
            ControllerDoorUnlocked(u, controller, serial_no, door, door_no),
        ])

    configure_doors(options, g)
    async_add_entities(entities, update_before_add=True)
