from __future__ import annotations

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from uhppoted import uhppote

from .coordinators.coordinators import Coordinators
from .config import configure_controllers
from .controller import ControllerDateTime


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    entities = []

    controllers = Coordinators.controllers(entry.entry_id)

    def f(unique_id, controller, serial_no, address):
        entities.extend([
            ControllerDateTime(controllers, unique_id, controller, serial_no),
        ])

    configure_controllers(options, f)
    await controllers.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
