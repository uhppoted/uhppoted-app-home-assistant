from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

from .coordinators.coordinators import Coordinators
from .config import configure_cards
from .card import CardPIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options
    cards = Coordinators.cards()
    entities = []

    def h(card, name, unique_id):
        entities.extend([
            CardPIN(cards, unique_id, card, name),
        ])

    configure_cards(options, h)
    await cards.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
