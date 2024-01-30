from __future__ import annotations

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

from .coordinators.events import EventsCoordinator

from .config import configure_controllers
from .config import configure_doors
from .config import configure_driver

from .controller import ControllerEvent
from .door import DoorUnlocked
from .door import DoorOpened
from .door import DoorButtonPressed


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    entities = []

    events = EventsCoordinator(hass, options)

    def f(unique_id, controller, serial_no, address):
        entities.extend([
            ControllerEvent(events, unique_id, controller, serial_no),
        ])

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            DoorOpened(events, unique_id, controller, serial_no, door, door_no),
            DoorButtonPressed(events, unique_id, controller, serial_no, door, door_no),
            DoorUnlocked(events, unique_id, controller, serial_no, door, door_no),
        ])

    configure_controllers(options, f)
    configure_doors(options, g)
    await events.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
