from __future__ import annotations

from datetime import datetime
from datetime import date
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.date import DateEntity

from .const import ATTR_CARD_HOLDER
from .const import ATTR_CARD_STARTDATE
from .const import ATTR_CARD_ENDDATE
from .const import ATTR_CARD_PERMISSIONS

from .config import default_card_start_date
from .config import default_card_end_date

_LOGGER = logging.getLogger(__name__)


class CardInfo(SensorEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, u, card, name, start_date, end_date, permissions):
        super().__init__()

        _LOGGER.debug(f'card {card}')

        self.driver = u
        self.card = int(f'{card}')
        self.cardholder = name
        self.permissions = permissions

        self._name = f'uhppoted.card.{card}.info'.lower()
        self._start_date = None
        self._end_date = None
        self._available = False

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
            today = date.today()
            state = []

            if self.cardholder.strip() != '':
                state.append(self.cardholder)

            if self._start_date and self._start_date <= today and self._end_date and self._end_date >= today:
                state.append('VALID')
            elif self._start_date and self._start_date > today:
                state.append('NOT VALID')
            elif self._end_date and self._end_date < today:
                state.append('EXPIRED')

            if len(self.permissions) < 1:
                state.append('NO ACCESS')

            return ', '.join(state)

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            ATTR_CARD_HOLDER: f'{self.cardholder}',
            ATTR_CARD_STARTDATE: f'{self._start_date}',
            ATTR_CARD_ENDDATE: f'{self._end_date}',
            ATTR_CARD_PERMISSIONS: f"{','.join(self.permissions)}",
        }

    async def async_update(self):
        _LOGGER.debug(f'card:{self.card} state')
        try:
            start_date = None
            end_date = None
            for controller in self.driver['controllers']:
                response = self.driver['api'].get_card(controller, self.card)

                if response.controller == controller and response.card_number == self.card:
                    if not start_date or response.start_date < start_date:
                        start_date = response.start_date

                    if not end_date or response.end_date > end_date:
                        end_date = response.end_date

            self._start_date = start_date
            self._end_date = end_date
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

        self.driver = u
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
        self._available = True


class CardStartDate(DateEntity):
    _attr_icon = 'mdi:calendar-clock-outline'
    _attr_has_entity_name: True

    def __init__(self, u, card, name, start_date, end_date, permissions):
        super().__init__()

        _LOGGER.debug(f'card {card} start date')

        self.driver = u
        self.card = int(f'{card}')

        self._name = f'uhppoted.card.{card}.start-date'.lower()
        self._date = datetime.strptime(f'{start_date}', '%Y-%m-%d').date()
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self.card}.start-date'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> Optional[datetime.date]:
        return self._date

    async def async_set_value(self, v: datetime.date) -> None:
        try:
            for controller in self.driver['controllers']:
                response = self.driver['api'].get_card(controller, self.card)

                card = self.card
                start = v
                end = default_card_end_date()
                door1 = 0
                door2 = 0
                door3 = 0
                door4 = 0
                PIN = 0

                if response.controller == controller and response.card_number == self.card:
                    end = response.end_date
                    door1 = response.door_1
                    door2 = response.door_2
                    door3 = response.door_3
                    door4 = response.door_4
                    PIN = response.pin

                response = self.driver['api'].put_card(controller, card, start, end, door1, door2, door3, door4, PIN)

                if not response.stored:
                    _LOGGER.warning(f'controller {controller}: card {self.card} start date not updated')
                    self._available = False

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} start date')

    async def async_update(self):
        _LOGGER.debug(f'card:{self.card}  update start date')

        try:
            start_date = None
            for controller in self.driver['controllers']:
                response = self.driver['api'].get_card(controller, self.card)

                if response.controller == controller and response.card_number == self.card:
                    if not start_date or response.start_date < start_date:
                        start_date = response.start_date

            self._date = start_date
            self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.cared} start date')


class CardEndDate(DateEntity):
    _attr_icon = 'mdi:calendar-clock-outline'
    _attr_has_entity_name: True

    def __init__(self, u, card, name, start_date, end_date, permissions):
        super().__init__()

        _LOGGER.debug(f'card {card} end date')

        self.driver = u
        self.card = int(f'{card}')

        self._name = f'uhppoted.card.{card}.end-date'.lower()
        self._date = datetime.strptime(f'{end_date}', '%Y-%m-%d').date()
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self.card}.end-date'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> Optional[datetime.date]:
        return self._date

    async def async_set_value(self, v: datetime.date) -> None:
        try:
            for controller in self.driver['controllers']:
                response = self.driver['api'].get_card(controller, self.card)

                card = self.card
                start = default_card_start_date()
                end = v
                door1 = 0
                door2 = 0
                door3 = 0
                door4 = 0
                PIN = 0

                if response.controller == controller and response.card_number == self.card:
                    start = response.start_date
                    door1 = response.door_1
                    door2 = response.door_2
                    door3 = response.door_3
                    door4 = response.door_4
                    PIN = response.pin

                response = self.driver['api'].put_card(controller, card, start, end, door1, door2, door3, door4, PIN)

                if not response.stored:
                    _LOGGER.warning(f'controller {controller}: card {self.card} end date not updated')
                    self._available = False

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} end date')

    async def async_update(self):
        _LOGGER.debug(f'card:{self.card}  update end date')

        try:
            end_date = None
            for controller in self.driver['controllers']:
                response = self.driver['api'].get_card(controller, self.card)

                if response.controller == controller and response.card_number == self.card:
                    if not end_date or response.end_date > end_date:
                        end_date = response.end_date

            self._date = end_date
            self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.cared} end date')
