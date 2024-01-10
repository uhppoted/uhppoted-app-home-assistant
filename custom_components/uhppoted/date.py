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

from .config import configure_cards
from .card import CardStartDate


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options

    bind = options[CONF_BIND_ADDR]
    broadcast = options[CONF_BROADCAST_ADDR]
    listen = options[CONF_LISTEN_ADDR]
    debug = options[CONF_DEBUG]

    controllers = [int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}')
                   for v in options[CONF_CONTROLLERS]] if CONF_CONTROLLERS in options else []

    u = {
        'api': uhppote.Uhppote(bind, broadcast, listen, debug),
        'controllers': controllers,
    }

    entities = []

    def f(card, name, start_date, end_date, permissions):
        entities.extend([
            CardStartDate(u, card, name, start_date, end_date, permissions),
        ])

    configure_cards(options, f)
    async_add_entities(entities, update_before_add=True)
