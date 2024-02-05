from __future__ import annotations
from collections import deque

from datetime import datetime
from datetime import date
import logging

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.date import DateEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.text import TextEntity
from homeassistant.components.event import EventEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_AVAILABLE
from .const import ATTR_CONTROLLER_SERIAL_NUMBER
from .const import ATTR_DOOR_CONTROLLER
from .const import ATTR_DOOR_NUMBER
from .const import ATTR_CARD_HOLDER
from .const import ATTR_CARD_STARTDATE
from .const import ATTR_CARD_ENDDATE
from .const import ATTR_CARD_PERMISSIONS
from .const import ATTR_CARD_PIN
from .const import ATTR_EVENTS

from .const import CONF_DOOR_ID
from .const import CONF_DOOR_NUMBER
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CARD_EVENTS

from .config import default_card_start_date
from .config import default_card_end_date

_LOGGER = logging.getLogger(__name__)


class CardInfo(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, card, name):
        super().__init__(coordinator, context=int(f'{card}'))

        _LOGGER.debug(f'card {card}')

        self.card = int(f'{card}')

        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.info'.lower()
        self._cardholder = name
        self._start_date = None
        self._end_date = None
        self._permissions = None
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.info'.lower()

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

            if self._cardholder.strip() != '':
                state.append(self._cardholder)

            if self._start_date and self._start_date <= today and self._end_date and self._end_date >= today:
                state.append('VALID')
            elif self._start_date and self._start_date > today:
                state.append('NOT VALID')
            elif self._end_date and self._end_date < today:
                state.append('EXPIRED')

            if self._permissions and len(self._permissions) < 1:
                state.append('NO ACCESS')

            return ', '.join(state)

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        permissions = ','.join(self._permissions) if self._permissions else None
        return {
            ATTR_CARD_HOLDER: self._cardholder,
            ATTR_CARD_STARTDATE: self._start_date,
            ATTR_CARD_ENDDATE: self._end_date,
            ATTR_CARD_PERMISSIONS: permissions,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card} state')
        try:
            idx = self.card

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._start_date = state[ATTR_CARD_STARTDATE]
                self._end_date = state[ATTR_CARD_ENDDATE]
                self._permissions = state[ATTR_CARD_PERMISSIONS]
                self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} state')


class CardHolder(CoordinatorEntity, SensorEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, card, name):
        super().__init__(coordinator, context=int(f'{card}'))

        _LOGGER.debug(f'card {card}')

        self.card = int(f'{card}')

        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.cardholder'.lower()
        self._cardholder = name
        self._available = True
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.cardholder'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        if self._available:
            return self._cardholder

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card} cardholder')
        self._available = True


class CardStartDate(CoordinatorEntity, DateEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, card, name):
        super().__init__(coordinator, context=int(f'{card}'))

        _LOGGER.debug(f'card {card} start date')

        self.card = int(f'{card}')
        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.start-date'.lower()
        self._date = None
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.start-date'.lower()

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
            if self.coordinator.set_card_start_date(self.card, v):
                _LOGGER.info(f'card {self.card} start date updated')
            else:
                _LOGGER.warning(f' card {self.card} start date not updated')
                self._available = False

            await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} start date')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card}  update start date')

        try:
            idx = self.card

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CARD_STARTDATE not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._date = state[ATTR_CARD_STARTDATE]
                self._available = state[ATTR_AVAILABLE]
        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} start date')


class CardEndDate(CoordinatorEntity, DateEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, coordinator, unique_id, card, name):
        super().__init__(coordinator, context=int(f'{card}'))

        _LOGGER.debug(f'card {card} end date')

        self.card = int(f'{card}')
        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.end-date'.lower()
        self._date = None
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.end-date'.lower()

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
            if self.coordinator.set_card_end_date(self.card, v):
                _LOGGER.info(f'card {self.card} end date updated')
            else:
                _LOGGER.warning(f' card {self.card} end date not updated')
                self._available = False

            await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} end date')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card}  update end date')

        try:
            idx = self.card

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CARD_ENDDATE not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._date = state[ATTR_CARD_ENDDATE]
                self._available = state[ATTR_AVAILABLE]

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} end date')


class CardPermission(CoordinatorEntity, SwitchEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    def __init__(self, coordinator, u, unique_id, card, name, door):
        super().__init__(coordinator, context=int(f'{card}'))

        _LOGGER.debug(f'card {card} permission for door {door[CONF_DOOR_ID]}')

        self.driver = u
        self.card = int(f'{card}')
        self.door = door

        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.{door[CONF_DOOR_ID]}'.lower()
        self._allowed = None
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.{self.door[CONF_DOOR_ID]}'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def is_on(self):
        if self._available:
            return self._allowed

        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            ATTR_DOOR_CONTROLLER: self.door[CONF_DOOR_CONTROLLER],
            ATTR_CONTROLLER_SERIAL_NUMBER: self.door[CONF_CONTROLLER_SERIAL_NUMBER],
            ATTR_DOOR_NUMBER: self.door[CONF_DOOR_NUMBER],
        }

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(f'card:{self.card} enable access for door {self.door[CONF_DOOR_ID]}')
        try:
            controller = int(f'{self.door[CONF_CONTROLLER_SERIAL_NUMBER]}')
            door = int(f'{self.door[CONF_DOOR_NUMBER]}')
            card = self.card

            start = default_card_start_date()
            end = default_card_end_date()
            door1 = 1 if door == 1 else 0
            door2 = 1 if door == 2 else 0
            door3 = 1 if door == 3 else 0
            door4 = 1 if door == 4 else 0
            PIN = 0

            response = self.driver['api'].get_card(controller, self.card)
            if response.controller == controller and response.card_number == self.card:
                if response.start_date:
                    start = response.start_date

                if response.end_date:
                    end = response.start_date

                door1 = 1 if door == 1 else response.door_1
                door2 = 1 if door == 2 else response.door_2
                door3 = 1 if door == 3 else response.door_3
                door4 = 1 if door == 4 else response.door_4
                PIN = response.pin

            response = self.driver['api'].put_card(controller, card, start, end, door1, door2, door3, door4, PIN)
            if response.stored:
                _LOGGER.info(
                    f'controller {self.door[CONF_DOOR_CONTROLLER]}, card {self.card} door {self.door[CONF_DOOR_ID]} permission updated'
                )
            else:
                _LOGGER.warning(
                    f'controller {self.door[CONF_DOOR_CONTROLLER]}, card {self.card} door {self.door[CONF_DOOR_ID]} permission not updated'
                )
                self._available = False

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} access for door {self.door[CONF_DOOR_ID]}')

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(f'card:{self.card} remove access for door {self.door[CONF_DOOR_ID]}')
        try:
            controller = int(f'{self.door[CONF_CONTROLLER_SERIAL_NUMBER]}')
            door = int(f'{self.door[CONF_DOOR_NUMBER]}')
            card = self.card

            start = default_card_start_date()
            end = default_card_end_date()
            door1 = 1 if door == 1 else 0
            door2 = 1 if door == 2 else 0
            door3 = 1 if door == 3 else 0
            door4 = 1 if door == 4 else 0
            PIN = 0

            response = self.driver['api'].get_card(controller, self.card)
            if response.controller == controller and response.card_number == self.card:
                if response.start_date:
                    start = response.start_date

                if response.end_date:
                    end = response.start_date

                door1 = 0 if door == 1 else response.door_1
                door2 = 0 if door == 2 else response.door_2
                door3 = 0 if door == 3 else response.door_3
                door4 = 0 if door == 4 else response.door_4
                PIN = response.pin

            response = self.driver['api'].put_card(controller, card, start, end, door1, door2, door3, door4, PIN)
            if response.stored:
                _LOGGER.info(
                    f'controller {self.door[CONF_DOOR_CONTROLLER]}, card {self.card} door {self.door[CONF_DOOR_ID]} permission updated'
                )
            else:
                _LOGGER.warning(
                    f'controller {self.door[CONF_DOOR_CONTROLLER]}, card {self.card} door {self.door[CONF_DOOR_ID]} permission not updated'
                )
                self._available = False

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} access for door {self.door[CONF_DOOR_ID]}')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card} update door {self.door[CONF_DOOR_ID]} access')
        try:
            idx = self.card
            door = self.door[CONF_DOOR_ID]

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CARD_PERMISSIONS not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._allowed = door in state[ATTR_CARD_PERMISSIONS]
                self._available = state[ATTR_AVAILABLE]
        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} access for door {self.door}')


class CardPIN(CoordinatorEntity, TextEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True

    _attr_mode = 'password'
    _attr_pattern = '[0-9]{0,6}'
    _attr_native_max_value = 6
    _attr_native_min_value = 0

    def __init__(self, coordinator, unique_id, card, name):
        super().__init__(coordinator, context=int(f'{card}'))

        _LOGGER.debug(f'card {card} PIN code')

        self.card = int(f'{card}')
        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.PIN'.lower()
        self._pin = None
        self._allowed = None
        self._available = False
        self._attributes: Dict[str, Any] = {}

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.PIN'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def native_value(self) -> Optional[float]:
        if self._pin and int(f'{self._pin}') > 0:
            return f'{self._pin}'
        else:
            return ''

    async def async_set_value(self, value):
        try:
            if self.coordinator.set_card_PIN(self.card, int(f'{value}')):
                _LOGGER.info(f'card {self.card} PIN updated')
            else:
                _LOGGER.warning(f' card {self.card} PIN not updated')
                self._available = False

            await self.coordinator.async_request_refresh()

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error updating card {self.card} end date')

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card} update PIN')
        try:
            idx = self.card

            if not self.coordinator.data or idx not in self.coordinator.data:
                self._available = False
            elif ATTR_CARD_PIN not in self.coordinator.data[idx]:
                self._available = False
            else:
                state = self.coordinator.data[idx]
                self._pin = state[ATTR_CARD_PIN]
                self._available = state[ATTR_AVAILABLE]
        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} PIN')


class CardSwiped(CoordinatorEntity, EventEntity):
    _attr_icon = 'mdi:card-account-details'
    _attr_has_entity_name: True
    _attr_event_types = list(CARD_EVENTS.values())

    def __init__(self, coordinator, unique_id, card, name):
        super().__init__(coordinator)

        _LOGGER.debug(f'card {card} swipe event')

        self.card = int(f'{card}')

        self._unique_id = unique_id
        self._name = f'uhppoted.card.{card}.swipe.event'.lower()
        self._events = deque([], 16)
        self._available = False

    @property
    def unique_id(self) -> str:
        return f'uhppoted.card.{self._unique_id}.swipe.event'.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update()
        self.async_write_ha_state()

    async def async_update(self):
        self._update()

    def _update(self):
        _LOGGER.debug(f'card:{self.card} swipe event')
        try:
            for idx in self.coordinator.data:
                if ATTR_EVENTS not in self.coordinator.data[idx]:
                    pass
                elif not self.coordinator.data[idx][ATTR_AVAILABLE]:
                    pass
                else:
                    events = self.coordinator.data[idx][ATTR_EVENTS]
                    for e in events:
                        if e.card == self.card and e.reason in CARD_EVENTS:
                            self._events.appendleft(CARD_EVENTS[e.reason])

            # ... because Home Assistant coalesces multiple events in an update cycle
            if len(self._events) > 0:
                event = self._events.pop()
                self._trigger_event(event)

            self._available = True

        except (Exception):
            self._available = False
            _LOGGER.exception(f'error retrieving card {self.card} swipe event')
