from __future__ import annotations

import concurrent.futures
import threading
import datetime
import logging
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)
_INTERVAL = datetime.timedelta(seconds=30)

from ..const import CONF_CONTROLLER_SERIAL_NUMBER
from ..const import CONF_DOOR_NUMBER

from ..const import ATTR_AVAILABLE
from ..const import ATTR_CARD_STARTDATE
from ..const import ATTR_CARD_ENDDATE
from ..const import ATTR_CARD_PERMISSIONS
from ..const import ATTR_CARD_PIN

from ..config import configure_driver
from ..config import configure_cards
from ..config import get_configured_controllers
from ..config import get_configured_cards
from ..config import resolve_permissions
from ..config import default_card_start_date
from ..config import default_card_end_date


class CardsCoordinator(DataUpdateCoordinator):
    _state: Dict[int, Dict]

    def __init__(self, hass, options, poll, db):
        interval = _INTERVAL if poll == None else poll

        super().__init__(hass, _LOGGER, name="cards", update_interval=interval)

        self._uhppote = configure_driver(options)
        self._options = options
        self._db = db
        self._state = {}
        self._initialised = False

        _LOGGER.info(f'cards coordinator initialised ({interval.total_seconds():.0f}s)')

    def __del__(self):
        self.unload()

    def unload(self):
        pass

    def add_card(self, card):
        api = self._uhppote['api']
        controllers = get_configured_controllers(self._options)
        cardno = int(f'{card}')
        errors = []

        for controller in controllers:
            try:
                response = api.get_card(controller, cardno)
                if response.controller == controller and response.card_number == cardno:
                    _LOGGER.info(f'card {card} already exists on controller {controller}')
                elif response.controller == controller and response.card_number == 0:
                    start_date = default_card_start_date()
                    end_date = default_card_end_date()
                    door1 = 0
                    door2 = 0
                    door3 = 0
                    door4 = 0
                    PIN = 0

                    response = api.put_card(controller, card, start_date, end_date, door1, door2, door3, door4, PIN)
                    if response.stored:
                        _LOGGER.info(f'card {card} added to controller {controller}')
                    else:
                        errors.append(f'{controller}')
                        _LOGGER.warning(f'card {card} not added to controller {controller}')
                else:
                    errors.append(f'{controller}')
                    _LOGGER.error(f'invalid get-card response for {card} from {controller} ({response})')

            except Exception as e:
                errors.append(f'{controller}')
                _LOGGER.exception(f'error adding card {card} to controller {controller} ({e})')

        if errors and len(errors) > 1:
            raise ValueError(f'error adding card {card} to controllers {",".join(errors)}')

        if errors and len(errors) > 0:
            raise ValueError(f'error adding card {card} to controller {errors[0]}')

        return True

    def delete_card(self, card):
        api = self._uhppote['api']
        controllers = get_configured_controllers(self._options)
        cardno = int(f'{card}')
        errors = []

        for controller in controllers:
            try:
                response = api.delete_card(controller, cardno)
                if response.controller == controller:
                    if response.deleted:
                        _LOGGER.info(f'card {card} deleted from controller {controller}')
                    else:
                        _LOGGER.warning(f'card {card} not deleted from controller {controller}')

            except Exception as e:
                errors.append(f'{controller}')
                _LOGGER.exception(f'error deleting card {card} from controller {controller} ({e})')

        if errors and len(errors) > 1:
            raise ValueError(f'error deleting card {card} from controllers {",".join(errors)}')

        if errors and len(errors) > 0:
            raise ValueError(f'error deleting card {card} from controller {errors[0]}')

        return True

    def set_card_start_date(self, card, start_date):
        api = self._uhppote['api']
        controllers = get_configured_controllers(self._options)
        errors = []

        for controller in controllers:
            try:
                end_date = default_card_end_date()
                door1 = 0
                door2 = 0
                door3 = 0
                door4 = 0
                PIN = 0

                response = api.get_card(controller, card)
                if response.controller == controller and response.card_number == card:
                    end_date = response.end_date if response.end_date else end_date
                    door1 = response.door_1
                    door2 = response.door_2
                    door3 = response.door_3
                    door4 = response.door_4
                    PIN = response.pin

                response = api.put_card(controller, card, start_date, end_date, door1, door2, door3, door4, PIN)
                if not response.stored:
                    errors.append(f'{controller}')

            except Exception as e:
                errors.append(f'{controller}')
                _LOGGER.exception(f'error updating card {card} start date on controller {controller} ({e})')

        if errors and len(errors) > 1:
            _LOGGER.exception(f'error updating card {card} start date on controllers {",".join(errors)}')
            return False

        if errors and len(errors) > 0:
            _LOGGER.exception(f'error updating card {card} start date on controller {errors[0]}')
            return False

        return True

    def set_card_end_date(self, card, end_date):
        api = self._uhppote['api']
        controllers = get_configured_controllers(self._options)
        errors = []

        for controller in controllers:
            try:
                start_date = default_card_start_date()
                door1 = 0
                door2 = 0
                door3 = 0
                door4 = 0
                PIN = 0

                response = api.get_card(controller, card)
                if response.controller == controller and response.card_number == card:
                    start_date = response.start_date if response.end_date else start_date
                    door1 = response.door_1
                    door2 = response.door_2
                    door3 = response.door_3
                    door4 = response.door_4
                    PIN = response.pin

                response = api.put_card(controller, card, start_date, end_date, door1, door2, door3, door4, PIN)
                if not response.stored:
                    errors.append(f'{controller}')

            except Exception as e:
                errors.append(f'{controller}')
                _LOGGER.exception(f'error updating card {card} end date on controller {controller} ({e})')

        if errors and len(errors) > 1:
            _LOGGER.exception(f'error updating card {card} end date on controllers {",".join(errors)}')
            return False

        if errors and len(errors) > 0:
            _LOGGER.exception(f'error updating card {card} end date on controller {errors[0]}')
            return False

        return True

    def set_card_PIN(self, card, PIN):
        api = self._uhppote['api']
        controllers = get_configured_controllers(self._options)
        errors = []

        for controller in controllers:
            try:
                start = default_card_start_date()
                end = default_card_end_date()
                door1 = 0
                door2 = 0
                door3 = 0
                door4 = 0

                response = api.get_card(controller, card)
                if response.controller == controller and response.card_number == card:
                    if response.start_date:
                        start = response.start_date

                    if response.end_date:
                        end = response.end_date

                    door1 = response.door_1
                    door2 = response.door_2
                    door3 = response.door_3
                    door4 = response.door_4

                response = api.put_card(controller, card, start, end, door1, door2, door3, door4, PIN)
                if not response.stored:
                    errors.append(f'{controller}')

            except (Exception):
                self._available = False
                _LOGGER.exception(f'error updating card {self.card} PIN')

        if errors and len(errors) > 1:
            _LOGGER.exception(f'error updating card {card} end date on controllers {",".join(errors)}')
            return False

        if errors and len(errors) > 0:
            _LOGGER.exception(f'error updating card {card} end date on controller {errors[0]}')
            return False

        return True

    def set_card_permission(self, card, door, allowed):
        api = self._uhppote['api']
        controller = int(f'{door[CONF_CONTROLLER_SERIAL_NUMBER]}')
        doorno = int(f'{door[CONF_DOOR_NUMBER]}')
        permission = 1 if allowed else 0

        start = default_card_start_date()
        end = default_card_end_date()
        door1 = permission if doorno == 1 else 0
        door2 = permission if doorno == 2 else 0
        door3 = permission if doorno == 3 else 0
        door4 = permission if doorno == 4 else 0
        PIN = 0

        response = api.get_card(controller, card)
        if response.controller == controller and response.card_number == card:
            if response.start_date:
                start = response.start_date

            if response.end_date:
                end = response.end_date

            door1 = permission if doorno == 1 else response.door_1
            door2 = permission if doorno == 2 else response.door_2
            door3 = permission if doorno == 3 else response.door_3
            door4 = permission if doorno == 4 else response.door_4

            PIN = response.pin

        response = api.put_card(controller, card, start, end, door1, door2, door3, door4, PIN)
        if not response.stored:
            raise ValueError(f'controller {controller}, card {card} door {door[CONF_DOOR_ID]} permission not updated')

    async def _async_update_data(self):
        try:
            contexts = set(self.async_contexts())
            cards = get_configured_cards(self._options)

            if not self._initialised:
                contexts.update(cards)
                self._initialised = True

            for v in contexts:
                if not v in self._state:
                    self._state[v] = {
                        ATTR_AVAILABLE: False,
                    }

            async with async_timeout.timeout(2.5):
                return await self._get_cards(contexts)
        except Exception as err:
            raise UpdateFailed(f"uhppoted API error {err}")

    async def _get_cards(self, contexts):
        api = self._uhppote['api']
        controllers = self._uhppote['controllers']
        lock = threading.Lock()

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda card: self._get_card(api, controllers, lock, card), contexts, timeout=1)
        except Exception as err:
            _LOGGER.error(f'error retrieving controller {controller} information ({err})')

        self._db.cards = self._state

        return self._db.cards

    def _get_card(self, api, controllers, lock, card):
        _LOGGER.debug(f'fetch card {card} information')

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
            PIN = None

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

                    if response.pin > 0:
                        PIN = response.pin

            info = {
                ATTR_CARD_STARTDATE: start_date,
                ATTR_CARD_ENDDATE: end_date,
                ATTR_CARD_PERMISSIONS: resolve_permissions(self._options, permissions),
                ATTR_CARD_PIN: PIN,
                ATTR_AVAILABLE: True,
            }

        except Exception as err:
            _LOGGER.error(f'error retrieving card {card} information ({err})')

        with lock:
            self._state[card].update(info)
