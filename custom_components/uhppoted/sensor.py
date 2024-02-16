from __future__ import annotations

import async_timeout
import datetime
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

from .config import configure_controllers
from .config import configure_doors
from .config import configure_cards
from .config import configure_driver

from .coordinators.coordinators import Coordinators

from .controller import ControllerInfo
from .door import DoorInfo
from .door import DoorOpen
from .door import DoorLock
from .door import DoorButton
from .card import CardInfo
from .card import CardHolder


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options
    controllers = Coordinators.controllers()
    doors = Coordinators.doors()
    cards = Coordinators.cards()
    entities = []

    def f(unique_id, controller, serial_no, address):
        entities.extend([
            ControllerInfo(controllers, unique_id, controller, serial_no),
        ])

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            DoorInfo(doors, unique_id, controller, serial_no, door, door_no),
            DoorOpen(doors, unique_id, controller, serial_no, door, door_no),
            DoorLock(doors, unique_id, controller, serial_no, door, door_no),
            DoorButton(doors, unique_id, controller, serial_no, door, door_no),
        ])

    def h(card, name, unique_id):
        entities.extend([
            CardInfo(cards, unique_id, card, name),
            CardHolder(cards, unique_id, card, name),
        ])

    configure_controllers(options, f)
    configure_doors(options, g)
    configure_cards(options, h)

    await controllers.async_config_entry_first_refresh()
    await doors.async_config_entry_first_refresh()
    await cards.async_config_entry_first_refresh()

    async_add_entities(entities, update_before_add=True)
