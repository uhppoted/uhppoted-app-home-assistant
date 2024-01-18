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
from .const import ATTR_ADDRESS
from .const import ATTR_NETMASK
from .const import ATTR_GATEWAY
from .const import ATTR_FIRMWARE

from .config import configure_controllers
from .config import configure_doors
from .config import configure_cards
from .config import configure_driver

from .controller import ControllerInfo
from .door import ControllerDoor
from .door import ControllerDoorOpen
from .door import ControllerDoorLock
from .door import ControllerDoorButton
from .door import ControllerDoorMode
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
            ControllerInfo(coordinator, u['api'], unique_id, controller, serial_no),
        ])

    def g(unique_id, controller, serial_no, door, door_no):
        entities.extend([
            ControllerDoor(u['api'], unique_id, controller, serial_no, door, door_no),
            ControllerDoorOpen(u['api'], unique_id, controller, serial_no, door, door_no),
            ControllerDoorLock(u['api'], unique_id, controller, serial_no, door, door_no),
            ControllerDoorButton(u['api'], unique_id, controller, serial_no, door, door_no),
        ])

    def h(card, name, unique_id):
        entities.extend([
            CardInfo(u, card, name, unique_id),
            CardHolder(u, card, name, unique_id),
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

    @property
    def controllers(self):
        return self._state['controllers']

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                return await self._get_controllers()
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_controllers(self):
        api = self.uhppote['api']
        for controller in self.uhppote['controllers']:
            _LOGGER.info(f'update controller {controller} info')

            info = {
                'available': False,
                ATTR_ADDRESS: '',
                ATTR_NETMASK: '',
                ATTR_GATEWAY: '',
                ATTR_FIRMWARE: '',
            }

            if controller in self._state['controllers']:
                for attr in [ATTR_ADDRESS, ATTR_NETMASK, ATTR_GATEWAY, ATTR_FIRMWARE]:
                    if attr in self._state['controllers']:
                        info[attr] = self._state['controllers'][attr]

            try:

                response = self.uhppote['api'].get_controller(controller)
                if response.controller == controller:
                    info['available'] = True
                    info[ATTR_ADDRESS] = f'{response.ip_address}'
                    info[ATTR_NETMASK] = f'{response.subnet_mask}'
                    info[ATTR_GATEWAY] = f'{response.gateway}'
                    info[ATTR_FIRMWARE] = f'{response.version} {response.date:%Y-%m-%d}'

            except (Exception):
                _LOGGER.exception(f'error retrieving controller {controller} information')

            self._state['controllers'][controller] = info
