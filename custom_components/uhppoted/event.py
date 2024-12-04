from __future__ import annotations

import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

from .coordinators.coordinators import Coordinators
from .config import configure_controllers
from .config import configure_doors
from .config import configure_cards

from .controller import ControllerEvent
from .door import DoorUnlocked
from .door import DoorOpened
from .door import DoorButtonPressed
from .card import CardSwiped


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options
    events = Coordinators.events(entry.entry_id)
    entities = []

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

    def h(card, name, unique_id):
        entities.extend([
            CardSwiped(events, unique_id, card, name),
        ])

    configure_controllers(options, f)
    configure_doors(options, g)
    configure_cards(options, h)
    # await events.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
