from __future__ import annotations

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

from .coordinators.coordinators import Coordinators
from .config import configure_doors
from .config import configure_interlocks
from .config import configure_antipassback

from .door import DoorMode
from .controller import Interlock


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options
    controllers = Coordinators.controllers(entry.entry_id)
    doors = Coordinators.doors(entry.entry_id)
    entities = []

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            DoorMode(doors, unique_id, controller, serial_no, door, door_no),
        ])

    def h(unique_id, controller, serial_no):
        entities.extend([
            Interlock(controllers, unique_id, controller, serial_no),
        ])

    # def i(unique_id, controller, serial_no):
    #       entities.extend([
    #             AntiPassback(controllers, unique_id, controller, serial_no),
    #       ])

    configure_doors(options, g)
    configure_interlocks(options, h)
    # configure_antipassback(options,i)

    async_add_entities(entities, update_before_add=True)
