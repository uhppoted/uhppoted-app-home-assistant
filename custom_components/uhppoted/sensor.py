from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
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

from .controller import ControllerInfo

from .door import ControllerDoor
from .door import ControllerDoorOpen
from .door import ControllerDoorLocked
from .door import ControllerDoorButton
from .door import ControllerDoorMode


async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry,
                            async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options

    bind = config[CONF_BIND_ADDR]
    broadcast = config[CONF_BROADCAST_ADDR]
    listen = config[CONF_LISTEN_ADDR]
    debug = config[CONF_DEBUG]

    controller = options[CONF_CONTROLLER_ID].strip()
    serial_no = options[CONF_CONTROLLER_SERIAL_NUMBER].strip()
    address = options[CONF_CONTROLLER_ADDR].strip()

    # door = {'id': 'Dungeon', 'controller': 'Alpha', 'number': 1}

    # if CONF_DOOR_ID in config:
    #     door['id'] = config[CONF_DOOR_ID]
    #     door['controller'] = config[CONF_DOOR_CONTROLLER]
    #     door['number'] = config[CONF_DOOR_NUMBER]

    u = uhppote.Uhppote(bind, broadcast, listen, debug)

    controllers = [
        ControllerInfo(u, controller, serial_no),
        #     ControllerDoor(u, id, name, door['id'], door['name']),
        #     ControllerDoorOpen(u, id, name, door['id'], door['name']),
        #     ControllerDoorLocked(u, id, name, door['id'], door['name']),
        #     ControllerDoorButton(u, id, name, door['id'], door['name']),
    ]

    async_add_entities(controllers, update_before_add=True)
