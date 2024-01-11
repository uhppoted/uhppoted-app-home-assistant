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
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_SERIAL_NUMBER

# Attribute constants
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .config import configure_driver
from .config import configure_cards
from .card import CardStartDate
from .card import CardEndDate


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    u = configure_driver(options)
    entities = []

    def f(card, name, unique_id):
        entities.extend([
            CardStartDate(u, card, name, unique_id),
            CardEndDate(u, card, name, unique_id),
        ])

    configure_cards(options, f)
    async_add_entities(entities, update_before_add=True)
