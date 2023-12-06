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
from .const import CONF_CONTROLLER_NAME
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_NAME

# Attribute constants
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .door import ControllerDoorMode


async def async_setup_entry(hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry,
                            async_add_entities: AddEntitiesCallback):
    config = hass.data[DOMAIN][config_entry.entry_id]

    id = config[CONF_CONTROLLER_ID]
    name = f'{id}'
    address = ''
    bind = '0.0.0.0'
    broadcast = '255.255.255.255'
    listen = '0.0.0.0:60001'
    debug = False

    door = {'id': 1, 'name': '1'}

    if CONF_CONTROLLER_NAME in config and not config[CONF_CONTROLLER_NAME].strip() == '':
        name = config[CONF_CONTROLLER_NAME].strip()

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
        door['name'] = f"{door['id']}"

    if CONF_DOOR_NAME in config:
        door['name'] = config[CONF_DOOR_NAME]

    u = uhppote.Uhppote(bind, broadcast, listen, debug)

    controller = [
        ControllerDoorMode(u, id, name, door['id'], door['name']),
    ]

    async_add_entities(controller, update_before_add=True)
