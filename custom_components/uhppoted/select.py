from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

# Configuration constants
from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

# Attribute constants
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .door import ControllerDoorMode


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options

    bind = options[CONF_BIND_ADDR]
    broadcast = options[CONF_BROADCAST_ADDR]
    listen = options[CONF_LISTEN_ADDR]
    debug = options[CONF_DEBUG]

    controller = options[CONF_CONTROLLER_ID].strip()
    serial_no = options[CONF_CONTROLLER_SERIAL_NUMBER].strip()
    address = options[CONF_CONTROLLER_ADDR].strip()

    door = options[CONF_DOOR_ID]
    # door_controller = options[CONF_DOOR_CONTROLLER] // FIXME
    door_no = options[CONF_DOOR_NUMBER]

    u = uhppote.Uhppote(bind, broadcast, listen, debug)

    controllers = [
        ControllerDoorMode(u, controller, serial_no, door, door_no),
    ]

    async_add_entities(controllers, update_before_add=True)