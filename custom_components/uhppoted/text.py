from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

# Configuration constants
from .const import DOMAIN

from .config import configure_cards
from .config import configure_driver
from .card import CardPIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    u = configure_driver(options)
    entities = []

    def h(card, name, unique_id):
        entities.extend([
            CardPIN(u, unique_id, card, name),
        ])

    configure_cards(options, h)
    async_add_entities(entities, update_before_add=True)
