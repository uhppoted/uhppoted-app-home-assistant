from __future__ import annotations

from datetime import datetime
from datetime import date
import logging

from homeassistant.components.sensor import SensorEntity

from .const import ATTR_CARD_HOLDER
from .const import ATTR_CARD_STARTDATE
from .const import ATTR_CARD_ENDDATE
from .const import ATTR_CARD_PERMISSIONS

_LOGGER = logging.getLogger(__name__)


class CardInfo(SensorEntity):
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
        self.permissions = permissions

        self._name = f'uhppoted.card.{card}.info'.lower()
        self._valid = None
        self._available = False
        self._attributes: Dict[str, Any] = {
            ATTR_CARD_HOLDER: f'{name}',
            ATTR_CARD_STARTDATE: f'{start_date}',
            ATTR_CARD_ENDDATE: f'{end_date}',
            ATTR_CARD_PERMISSIONS: f"{','.join(permissions)}",
        }

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self.card}.info'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            state = []

            if self.cardholder.strip() != '':
                state.append(self.cardholder)

            if self._valid:
                state.append(self._valid)

            if len(self.permissions) < 1:
                state.append('NO ACCESS')

            return ', '.join(state)

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes

    async def async_update(self):
        _LOGGER.debug(f'card:{self.card} state')
        try:
            start_date = datetime.strptime(f'{self.start_date}', '%Y-%m-%d').date()
            end_date = datetime.strptime(f'{self.end_date}', '%Y-%m-%d').date()
            today = date.today()

            if start_date <= today and end_date >= today:
                self._valid = 'VALID'
            elif start_date > today:
                self._valid = 'NOT VALID'
            elif end_date < today:
                self._valid = 'EXPIRED'

            self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} state')


class CardHolder(SensorEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, u, card, name, start_date, end_date, permissions):
        super().__init__()

        _LOGGER.debug(f'card {card}')

        self.uhppote = u
        self.card = int(f'{card}')
        self.cardholder = name

        self._name = f'uhppoted.card.{card}.cardholder'.lower()
        self._available = True
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self.card}.cardholder'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            return self.cardholder

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes

    async def async_update(self):
        _LOGGER.debug(f'card:{self.card} cardholder')
        try:
            self._available = True
        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} card holder')
