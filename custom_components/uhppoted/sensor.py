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

from .controller import ControllerID
from .controller import ControllerAddress

from .door import ControllerDoor
from .door import ControllerDoorOpen
from .door import ControllerDoorLocked
from .door import ControllerDoorButton
from .door import ControllerDoorMode


async def async_setup_entry(hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry,
                            async_add_entities: AddEntitiesCallback):
    config = hass.data[DOMAIN][config_entry.entry_id]

    print('>>>>>>>>>>>>>>> sensor', config)
    print('>>>>>>>>>>>>>>> sensor/data', config_entry.data)
    print('>>>>>>>>>>>>>>> sensor/options', config_entry.options)

    id = config[CONF_CONTROLLER_ID]
    name = f'{id}'
    address = ''
    bind = '0.0.0.0'
    broadcast = '255.255.255.255'
    listen = '0.0.0.0:60001'
    debug = False

    door = {'id': 'Dungeon', 'controller': 'Alpha', 'number': 1}

    if CONF_CONTROLLER_ID in config and not config[CONF_CONTROLLER_ID].strip() == '':
        name = config[CONF_CONTROLLER_ID].strip()

    if CONF_CONTROLLER_ADDR in config:
        address = config[CONF_CONTROLLER_ADDR]

    if CONF_BIND_ADDR in config:
        bind = config[CONF_BIND_ADDR]

    if CONF_BROADCAST_ADDR in config:
        broadcast = config[CONF_BROADCAST_ADDR]

    if CONF_LISTEN_ADDR in config:
        listen = config[CONF_LISTEN_ADDR]

    if CONF_DEBUG in config:
        debug = config[CONF_DEBUG]

    if CONF_DOOR_ID in config:
        door['id'] = config[CONF_DOOR_ID]
        door['controller'] = config[CONF_DOOR_CONTROLLER]
        door['number'] = config[CONF_DOOR_NUMBER]

    u = uhppote.Uhppote(bind, broadcast, listen, debug)

    controller = [
        ControllerID(u, id, name),
        ControllerAddress(u, id, name, address),
        ControllerDoor(u, id, name, door['id'], door['name']),
        ControllerDoorOpen(u, id, name, door['id'], door['name']),
        ControllerDoorLocked(u, id, name, door['id'], door['name']),
        ControllerDoorButton(u, id, name, door['id'], door['name']),
    ]

    async_add_entities(controller, update_before_add=True)
