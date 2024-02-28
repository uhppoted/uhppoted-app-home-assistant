from __future__ import annotations

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

from .coordinators.coordinators import Coordinators
from .config import configure_doors
from .door import DoorUnlock


async def unlock_door(entity, service_call):
    await entity.async_unlock_door()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options
    entities = []
    doors = Coordinators.doors()

    platform = entity_platform.async_get_current_platform()

    def g(unique_id, controller, serial_no, door, door_no):
        entity = DoorUnlock(doors, unique_id, controller, serial_no, door, door_no)

        entities.extend([entity])

        platform.async_register_entity_service(
            'unlock_door',
            {
                # vol.Required('sleep_time'): cv.time_period,
            },
            unlock_door)


# component.async_register_entity_service(
#         SERVICE_SELECT_NEXT, SERVICE_SELECT_NEXT_SCHEMA,
#         lambda entity, call: entity.async_offset_index(1)
#     )

    configure_doors(options, g)
    await doors.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
