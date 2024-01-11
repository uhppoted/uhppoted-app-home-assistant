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
from .config import configure_cards
from .config import configure_driver

from .controller import ControllerInfo
from .door import ControllerDoor
from .door import ControllerDoorOpen
from .door import ControllerDoorLock
from .door import ControllerDoorButton
from .door import ControllerDoorMode
from .card import CardInfo
from .card import CardHolder


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    u = configure_driver(options)
    entities = []

    def f(controller, serial_no, address):
        entities.extend([
            ControllerInfo(u['api'], controller, serial_no),
        ])

    def g(controller, serial_no, door, door_no):
        entities.extend([
            ControllerDoor(u['api'], controller, serial_no, door, door_no),
            ControllerDoorOpen(u['api'], controller, serial_no, door, door_no),
            ControllerDoorLock(u['api'], controller, serial_no, door, door_no),
            ControllerDoorButton(u['api'], controller, serial_no, door, door_no),
        ])

    def h(card, name, unique_id):
        entities.extend([
            CardInfo(u, card, name, unique_id),
            CardHolder(u, card, name, unique_id),
        ])

    configure_controllers(options, f)
    configure_doors(options, g)
    configure_cards(options, h)
    async_add_entities(entities, update_before_add=True)
