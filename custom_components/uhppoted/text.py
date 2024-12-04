from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

from .const import DOMAIN
from .const import CONF_PIN_ENABLED

from .coordinators.coordinators import Coordinators
from .config import configure_cards
from .card import CardPIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    defaults = hass.data[DOMAIN] if DOMAIN in hass.data else {}

    PIN = False
    if CONF_PIN_ENABLED in defaults:
        PIN = defaults[CONF_PIN_ENABLED] == True

    options = entry.options
    cards = Coordinators.cards(entry.entry_id)
    entities = []

    def h(card, name, unique_id):
        if PIN:
            entities.extend([
                CardPIN(cards, unique_id, card, name),
            ])

    configure_cards(options, h)
    async_add_entities(entities, update_before_add=True)
