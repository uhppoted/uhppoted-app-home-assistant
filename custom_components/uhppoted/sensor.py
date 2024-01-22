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

# Configuration constants
from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

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

from .config import configure_controllers
from .config import configure_doors
from .config import configure_cards
from .config import configure_driver

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
    u = configure_driver(options)
    entities = []

    coordinator = ControllerCoordinator(hass, u)

    def f(unique_id, controller, serial_no, address):
        entities.extend([
            ControllerInfo(coordinator, unique_id, controller, serial_no),
        ])

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            Door(coordinator, unique_id, controller, serial_no, door, door_no),
            DoorOpen(coordinator, unique_id, controller, serial_no, door, door_no),
            DoorLock(coordinator, unique_id, controller, serial_no, door, door_no),
            DoorButton(coordinator, unique_id, controller, serial_no, door, door_no),
        ])

    def h(card, name, unique_id):
        entities.extend([
            CardInfo(u, unique_id, card, name),
            CardHolder(u, unique_id, card, name),
        ])

    configure_controllers(options, f)
    configure_doors(options, g)
    configure_cards(options, h)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(entities, update_before_add=True)


class ControllerCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, u):
        super().__init__(hass, _LOGGER, name="coordinator", update_interval=_INTERVAL)
        self.uhppote = u
        self._state = {
            'controllers': {},
        }

    # FIXME remove and use data attribute
    @property
    def controllers(self):
        return self._state['controllers']

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            async with async_timeout.timeout(5):
                return await self._get_controllers(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_controllers(self, contexts):
        api = self.uhppote['api']

        for controller in contexts:
            _LOGGER.debug(f'update controller {controller}')

            info = {
                ATTR_CONTROLLER: {
                    ATTR_AVAILABLE: False,
                    ATTR_ADDRESS: None,
                    ATTR_NETMASK: None,
                    ATTR_GATEWAY: None,
                    ATTR_FIRMWARE: None,
                },
                ATTR_DOORS: {
                    ATTR_AVAILABLE: False,
                }
            }

            try:
                response = api.get_controller(controller)
                if response.controller == controller:
                    info[ATTR_CONTROLLER] = {
                        ATTR_ADDRESS: f'{response.ip_address}',
                        ATTR_NETMASK: f'{response.subnet_mask}',
                        ATTR_GATEWAY: f'{response.gateway}',
                        ATTR_FIRMWARE: f'{response.version} {response.date:%Y-%m-%d}',
                        ATTR_AVAILABLE: True,
                    }

                response = api.get_status(controller)
                if response.controller == controller:
                    info[ATTR_DOORS] = {
                        ATTR_AVAILABLE: True,
                        1: {
                            ATTR_DOOR_OPEN: response.door_1_open == True,
                            ATTR_DOOR_BUTTON: response.door_1_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x01 == 0x00,
                        },
                        2: {
                            ATTR_DOOR_OPEN: response.door_2_open == True,
                            ATTR_DOOR_BUTTON: response.door_2_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x02 == 0x00,
                        },
                        3: {
                            ATTR_DOOR_OPEN: response.door_3_open == True,
                            ATTR_DOOR_BUTTON: response.door_3_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x04 == 0x00,
                        },
                        4: {
                            ATTR_DOOR_OPEN: response.door_4_open == True,
                            ATTR_DOOR_BUTTON: response.door_4_button == True,
                            ATTR_DOOR_LOCK: response.relays & 0x08 == 0x00,
                        },
                    }

            except (Exception):
                _LOGGER.exception(f'error retrieving controller {controller} information')

            self._state['controllers'][controller] = info

        return self._state['controllers']
