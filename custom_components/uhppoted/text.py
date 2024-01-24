from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

from .coordinators import CardsCoordinator
from .config import configure_cards
from .config import configure_driver
from .card import CardPIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    entities = []

    cards = CardsCoordinator(hass, options)
    u = configure_driver(options)

    def h(card, name, unique_id):
        entities.extend([
            CardPIN(cards, u, unique_id, card, name),
        ])

    configure_cards(options, h)
    await cards.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
