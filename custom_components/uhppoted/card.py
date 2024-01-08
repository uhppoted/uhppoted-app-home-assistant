from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)


class Card(SensorEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, u, card, name, start_date, end_date, permissions):
        super().__init__()

        _LOGGER.debug(f'card {card}')

        self.uhppote = u
        self.card = int(f'{card}')
        self.cardholder = name
        self.start_date = start_date
        self.end_date = end_date

        self._name = f'uhppoted.card.{card}'.lower()
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self.card}'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            if self.cardholder.strip() != '':
                return f'{self.cardholder}'
            else:
                return f'{self.card}'

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes

    async def async_update(self):
        _LOGGER.debug(f'card:{self.card} state')
        try:
            self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} state')
