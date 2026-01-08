# from __future__ import annotations
from collections import namedtuple

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

from .const import DOMAIN
from .const import CONF_EVENTS_CARDS_ENABLED
from .const import CONF_EVENTS_DOORS_ENABLED
from .const import CONF_EVENTS_CONTROLLERS_ENABLED
from .const import DEFAULT_EVENTS_CARDS_ENABLED
from .const import DEFAULT_EVENTS_DOORS_ENABLED
from .const import DEFAULT_EVENTS_CONTROLLERS_ENABLED


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    defaults = hass.data[DOMAIN] if DOMAIN in hass.data else {}
    options = entry.options
    events = Coordinators.events(entry.entry_id)
    entities = []

    opt_in = namedtuple('opt_in', ['cards', 'doors', 'controllers'])(defaults.get(CONF_EVENTS_CARDS_ENABLED,
                                                                                  DEFAULT_EVENTS_CARDS_ENABLED),
                                                                     defaults.get(CONF_EVENTS_DOORS_ENABLED,
                                                                                  DEFAULT_EVENTS_DOORS_ENABLED),
                                                                     defaults.get(CONF_EVENTS_CONTROLLERS_ENABLED,
                                                                                  DEFAULT_EVENTS_CONTROLLERS_ENABLED))

    def f(unique_id, controller, serial_no, address):
        if opt_in.controllers != False:
            entities.extend([
                ControllerEvent(events, unique_id, controller, serial_no),
            ])

    def g(unique_id, controller, serial_no, door, door_no):
        if opt_in.doors != False:
            entities.extend([
                DoorOpened(events, unique_id, controller, serial_no, door, door_no),
                DoorButtonPressed(events, unique_id, controller, serial_no, door, door_no),
                DoorUnlocked(events, unique_id, controller, serial_no, door, door_no),
            ])

    def h(card, name, unique_id):
        if opt_in.cards != False:
            entities.extend([CardSwiped(events, unique_id, card, name, options)])

    configure_controllers(options, f)
    configure_doors(options, g)
    configure_cards(options, h)

    async_add_entities(entities, update_before_add=True)
