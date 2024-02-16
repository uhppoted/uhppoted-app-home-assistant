from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)


from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_DOORS
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_NUMBER
from .const import CONF_DOOR_CONTROLLER

from .coordinators.coordinators import Coordinators
from .config import configure_cards
from .card import CardPermission


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    options = entry.options
    cards = Coordinators.cards()
    entities = []

    doors = []
    if CONF_CONTROLLERS in options and CONF_DOORS in options:
        for c in options[CONF_CONTROLLERS]:
            controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
            serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()

            for d in options[CONF_DOORS]:
                door = f'{d[CONF_DOOR_ID]}'.strip()
                door_no = f'{d[CONF_DOOR_NUMBER]}'.strip()
                door_controller = f'{d[CONF_DOOR_CONTROLLER]}'.strip()

                if door_controller == controller:
                    doors.append({
                        CONF_DOOR_ID: door,
                        CONF_DOOR_NUMBER: door_no,
                        CONF_DOOR_CONTROLLER: controller,
                        CONF_CONTROLLER_SERIAL_NUMBER: serial_no,
                    })

    def h(card, name, unique_id):
        for d in doors:
            entities.extend([
                CardPermission(cards, unique_id, card, name, d),
            ])

    configure_cards(options, h)
    await cards.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)
