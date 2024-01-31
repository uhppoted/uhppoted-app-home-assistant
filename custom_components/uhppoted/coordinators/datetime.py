from __future__ import annotations

import datetime
import logging
import async_timeout

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

from ..const import ATTR_AVAILABLE
from ..const import ATTR_CONTROLLER_DATETIME

from ..config import configure_driver
from ..config import get_configured_controllers


class ControllerDateTimeCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, options):
        super().__init__(hass, _LOGGER, name="coordinator", update_interval=_INTERVAL)
        self._uhppote = configure_driver(options)
        self._options = options
        self._initialised = False
        self._state = {
            'controllers': {},
        }

    def set_datetime(self, controller, time):
        api = self._uhppote['api']
        response = api.set_time(controller, time)

        if response.controller == controller:
            return response

        return None

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            controllers = get_configured_controllers(self._options)

            if not self._initialised:
                contexts.update(controllers)
                self._initialised = True

            async with async_timeout.timeout(10):
                return await self._get_controllers(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_controllers(self, contexts):
        api = self._uhppote['api']
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
                response = api.get_time(controller)
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

        return self._state['controllers']
