from __future__ import annotations

import datetime
import logging
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

# Attribute constants
from .const import ATTR_AVAILABLE

from .const import ATTR_CONTROLLER
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .const import ATTR_DOORS
from .const import ATTR_DOOR_OPEN
from .const import ATTR_DOOR_BUTTON
from .const import ATTR_DOOR_LOCK

from .const import ATTR_CARD
from .const import ATTR_CARD_HOLDER
from .const import ATTR_CARD_STARTDATE
from .const import ATTR_CARD_ENDDATE
from .const import ATTR_CARD_PERMISSIONS

from .coordinators.controllers import ControllerCoordinator
from .coordinators.cards import CardsCoordinator

from .config import configure_cards
from .config import configure_driver
from .card import CardStartDate
from .card import CardEndDate


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    entities = []

    cards = CardsCoordinator(hass, options)
    u = configure_driver(options)

    def f(card, name, unique_id):
        entities.extend([
            CardStartDate(cards, u, unique_id, card, name),
            CardEndDate(cards, u, unique_id, card, name),
        ])

    configure_cards(options, f)
    await cards.async_config_entry_first_refresh()
    async_add_entities(entities, update_before_add=True)


from .config import configure_controllers
from .config import configure_doors
from .config import configure_cards
from .config import configure_driver
from .config import get_configured_controllers
from .config import get_configured_cards

from .controller import ControllerInfo

from .door import Door
from .door import DoorOpen
from .door import DoorLock
from .door import DoorButton
from .door import DoorMode
from .card import CardInfo
from .card import CardHolder


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    entities = []

    controllers = ControllerCoordinator(hass, options)
    cards = CardsCoordinator(hass, options)

    def f(unique_id, controller, serial_no, address):
        entities.extend([
            ControllerInfo(controllers, unique_id, controller, serial_no),
        ])

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            Door(controllers, unique_id, controller, serial_no, door, door_no),
            DoorOpen(controllers, unique_id, controller, serial_no, door, door_no),
            DoorLock(controllers, unique_id, controller, serial_no, door, door_no),
            DoorButton(controllers, unique_id, controller, serial_no, door, door_no),
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
    await cards.async_config_entry_first_refresh()

    async_add_entities(entities, update_before_add=True)
