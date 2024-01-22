from __future__ import annotations

import datetime
import logging
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
# from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

from .const import DOMAIN
from .const import ATTR_CONTROLLER_DATETIME

from .config import configure_controllers
from .config import configure_driver

from .controller import ControllerDateTime


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data
    options = entry.options
    u = configure_driver(options)
    entities = []

    coordinator = ControllerDateTimeCoordinator(hass, u)

    def f(unique_id, controller, serial_no, address):
        entities.extend([
            ControllerDateTime(coordinator, u['api'], unique_id, controller, serial_no),
        ])

    configure_controllers(options, f)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(entities, update_before_add=True)


class ControllerDateTimeCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, u):
        super().__init__(hass, _LOGGER, name="coordinator", update_interval=_INTERVAL)
        self.uhppote = u
        self._initialised = False
        self._state = {
            'controllers': {},
        }

    @property
    def controllers(self):
        return self._state['controllers']

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            if not self._initialised:
                for v in self.uhppote['controllers']:
                    contexts.add(v)
                self._initialised = True

            async with async_timeout.timeout(10):
                return await self._get_controllers(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_controllers(self, contexts):
        api = self.uhppote['api']
        for controller in contexts:
            _LOGGER.debug(f'update controller {controller} date/time')

            info = {
                'available': False,
                ATTR_CONTROLLER_DATETIME: None,
            }

            if controller in self._state['controllers']:
                for attr in [ATTR_CONTROLLER_DATETIME]:
                    if attr in self._state['controllers']:
                        info[attr] = self._state['controllers'][attr]

            try:
                response = self.uhppote['api'].get_time(controller)
                if response.controller == controller:
                    year = response.datetime.year
                    month = response.datetime.month
                    day = response.datetime.day
                    hour = response.datetime.hour
                    minute = response.datetime.minute
                    second = response.datetime.second
                    tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

                    info[ATTR_CONTROLLER_DATETIME] = datetime.datetime(year, month, day, hour, minute, second, 0, tz)
                    info['available'] = True

            except (Exception):
                _LOGGER.exception(f'error retrieving controller {controller} date/time')

            self._state['controllers'][controller] = info
