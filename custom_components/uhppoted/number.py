from __future__ import annotations

import datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

# Configuration constants
from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

from .coordinators.doors import DoorsCoordinator

from .config import configure_doors
from .config import configure_driver
from .door import DoorDelay


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    entities = []

    doors = DoorsCoordinator(hass, options)
    u = configure_driver(options)

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            DoorDelay(doors, u['api'], unique_id, controller, serial_no, door, door_no),
        ])

    configure_doors(options, g)
    await doors.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
