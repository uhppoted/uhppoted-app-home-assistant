from __future__ import annotations

import datetime
import logging
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

# Attribute constants
from .const import ATTR_AVAILABLE
from .const import ATTR_CARD_STARTDATE
from .const import ATTR_CARD_ENDDATE
from .const import ATTR_CARD_PERMISSIONS

from .config import configure_driver
from .config import configure_cards
from .config import get_configured_controllers
from .config import get_configured_cards
from .config import resolve


class CardsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, options):
        super().__init__(hass, _LOGGER, name="coordinator", update_interval=_INTERVAL)
        self._uhppote = configure_driver(options)
        self._options = options
        self._initialised = False
        self._state = {
            'cards': {},
        }

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            cards = get_configured_cards(self._options)

            if not self._initialised:
                contexts.update(cards)
                self._initialised = True

            async with async_timeout.timeout(5):
                return await self._get_cards(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_cards(self, contexts):
        api = self._uhppote['api']
        controllers = self._uhppote['controllers']

        for card in contexts:
            _LOGGER.debug(f'update card {card}')

            info = {
                ATTR_AVAILABLE: False,
                ATTR_CARD_STARTDATE: None,
                ATTR_CARD_ENDDATE: None,
                ATTR_CARD_PERMISSIONS: None,
            }

            try:
                start_date = None
                end_date = None
                permissions = {}

                for controller in controllers:
                    response = api.get_card(controller, card)

                    if response.controller == controller and response.card_number == card:
                        if response.start_date and (not start_date or response.start_date < start_date):
                            start_date = response.start_date

                        if response.end_date != None and (not end_date or response.end_date > end_date):
                            end_date = response.end_date

                        permissions[controller] = []

                        if response.door_1 > 0:
                            permissions[controller].append(1)

                        if response.door_2 > 0:
                            permissions[controller].append(2)

                        if response.door_3 > 0:
                            permissions[controller].append(3)

                        if response.door_4 > 0:
                            permissions[controller].append(4)

                info = {
                    ATTR_CARD_STARTDATE: start_date,
                    ATTR_CARD_ENDDATE: end_date,
                    ATTR_CARD_PERMISSIONS: resolve(self._options, permissions),
                    ATTR_AVAILABLE: True,
                }

            except (Exception):
                _LOGGER.exception(f'error retrieving card {card} information')

            self._state['cards'][card] = info

        return self._state['cards']
