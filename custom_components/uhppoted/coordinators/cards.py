from __future__ import annotations
from collections import namedtuple

import concurrent.futures
import threading
import asyncio
import datetime
import logging
import async_timeout
import traceback

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

from ..config import configure_cards
from ..config import get_configured_controllers_ext
from ..config import get_configured_controllers
from ..config import get_configured_cards
from ..config import resolve_permissions
from ..config import resolve_door_by_name
from ..config import default_card_start_date
from ..config import default_card_end_date

from ..uhppoted import Controller


class CardsCoordinator(DataUpdateCoordinator):
    _state: Dict[int, Dict]

    def __init__(self, hass, options, poll, driver, db):
        interval = _INTERVAL if poll == None else poll

        super().__init__(hass, _LOGGER, name="cards", update_interval=interval)

        self._options = options
        self._controllers = get_configured_controllers_ext(options)
        self._uhppote = driver
        self._db = db
        self._state = {}
        self._initialised = False

        _LOGGER.info(f'cards coordinator initialised ({interval.total_seconds():.0f}s)')

    def __del__(self):
        self.unload()

    def unload(self):
        pass

    async def add_card(self, card):
        controllers = self._controllers
        cardno = int(f'{card}')
        errors = []

        for controller in controllers:
            try:
                response = await self._uhppote.get_card(controller.id, cardno)
                if response.controller == controller.id and response.card_number == cardno:
                    _LOGGER.info(f'card {card} already exists on controller {controller.id}')
                elif response.controller == controller.id and response.card_number == 0:
                    start_date = default_card_start_date()
                    end_date = default_card_end_date()
                    door1 = 0
                    door2 = 0
                    door3 = 0
                    door4 = 0
                    PIN = 0

                    response = await self._uhppote.put_card(controller.id, card, start_date, end_date, door1, door2,
                                                            door3, door4, PIN)
                    if response.stored:
                        _LOGGER.info(f'card {card} added to controller {controller.id}')
                    else:
                        errors.append(f'{controller.id}')
                        _LOGGER.warning(f'card {card} not added to controller {controller.id}')
                else:
                    errors.append(f'{controller.id}')
                    _LOGGER.error(f'invalid get-card response for {card} from {controller.id} ({response})')

            except Exception as e:
                errors.append(f'{controller.id}')
                _LOGGER.exception(f'error adding card {card} to controller {controller.id} ({e})')

        if errors and len(errors) > 1:
            raise ValueError(f'error adding card {card} to controllers {",".join(errors)}')

        if errors and len(errors) > 0:
            raise ValueError(f'error adding card {card} to controller {errors[0]}')

        return True

    async def delete_card(self, card):
        controllers = self._controllers
        cardno = int(f'{card}')
        errors = []

        for controller in controllers:
            try:
                response = await self._uhppote.delete_card(controller.id, cardno)
                if response.controller == controller.id:
                    if response.deleted:
                        _LOGGER.info(f'card {card} deleted from controller {controller.id}')
                    else:
                        _LOGGER.warning(f'card {card} not deleted from controller {controller.id}')

            except Exception as e:
                errors.append(f'{controller.id}')
                _LOGGER.exception(f'error deleting card {card} from controller {controller.id} ({e})')

        if errors and len(errors) > 1:
            raise ValueError(f'error deleting card {card} from controllers {",".join(errors)}')

        if errors and len(errors) > 0:
            raise ValueError(f'error deleting card {card} from controller {errors[0]}')

        return True

    async def set_card_start_date(self, card, date):
        return await self._put_card(card, start_date=date)

    async def set_card_end_date(self, card, date):
        return await self._put_card(card, end_date=date)

    async def set_card_PIN(self, card, PIN):
        return await self._put_card(card, PIN=PIN)

    async def set_card_permission(self, card, door, allowed):
        permission = 1 if allowed else 0

        return await self._put_card(card, door=door, permission=permission)

    async def _put_card(self, card, **kwargs):
        errors = []
        doors = []

        record = self._state.get(card)
        if record is not None:
            for p in record.get('permissions', []):
                door = resolve_door_by_name(self._options, p)
                if door is not None:
                    doors.append(door)

        controllers = self._controllers
        for controller in controllers:
            try:
                start_date = default_card_start_date()
                end_date = default_card_end_date()
                door1 = 0
                door2 = 0
                door3 = 0
                door4 = 0
                PIN = 0

                if record is not None:
                    if date := record.get('start_date'):
                        start_date = date

                    if date := record.get('end_date'):
                        end_date = date

                    if pin := record.get('PIN'):
                        PIN = pin

                    for door in doors:
                        if door.get(CONF_CONTROLLER_SERIAL_NUMBER) == controller.id:
                            if door.get(CONF_DOOR_NUMBER) == 1:
                                door1 = 1
                            elif door.get(CONF_DOOR_NUMBER) == 2:
                                door2 = 1
                            elif door.get(CONF_DOOR_NUMBER) == 3:
                                door3 = 1
                            elif door.get(CONF_DOOR_NUMBER) == 4:
                                door4 = 1

                for k, v in kwargs.items():
                    if k == 'start_date':
                        start_date = v
                    elif k == 'end_date':
                        end_date = v
                    elif k == 'PIN':
                        PIN = v
                    elif k == 'door':
                        if f'{v.get(CONF_CONTROLLER_SERIAL_NUMBER)}' == str(controller.id):
                            d = f'{v.get(CONF_DOOR_NUMBER)}'
                            if d == str(1):
                                door1 = kwargs.get('permission', door1)
                            elif d == str(2):
                                door2 = kwargs.get('permission', door2)
                            elif d == str(3):
                                door3 = kwargs.get('permission', door3)
                            elif d == str(4):
                                door4 = kwargs.get('permission', door4)

                if response := await self._uhppote.put_card(controller.id, card, start_date, end_date, door1, door2,
                                                            door3, door4, PIN):
                    if response.stored:
                        permissions = []
                        if door1 > 0: permissions.append(1)
                        if door2 > 0: permissions.append(2)
                        if door3 > 0: permissions.append(3)
                        if door4 > 0: permissions.append(4)

                        self._state[card].update({
                            ATTR_CARD_STARTDATE:
                            start_date,
                            ATTR_CARD_ENDDATE:
                            end_date,
                            ATTR_CARD_PERMISSIONS:
                            resolve_permissions(self._options, {controller.id: permissions}),
                            ATTR_CARD_PIN:
                            PIN,
                            ATTR_AVAILABLE:
                            True,
                        })

                        self.async_set_updated_data(self._state)
                    else:
                        errors.append(f'{controller.id}')
                else:
                    errors.append(f'{controller.id}')

            except Exception as e:
                errors.append(f'{controller.id}')
                _LOGGER.exception(f'error updating card {card} on controller {controller.id} ({e})')

        if errors and len(errors) > 1:
            _LOGGER.exception(f'error updating card {card} on controllers {",".join(errors)}')
            return False

        if errors and len(errors) > 0:
            _LOGGER.exception(f'error updating card {card} on controller {errors[0]}')
            return False

        return True

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
        lock = threading.Lock()
        controllers = self._controllers

        try:
            tasks = [self._get_card(controllers, lock, card) for card in contexts]

            await asyncio.gather(*tasks)
        except Exception as err:
            _LOGGER.error(f'error retrieving card information ({err})')

        self._db.cards = self._state

        return self._db.cards

    async def _get_card(self, controllers, lock, card):
        _LOGGER.debug(f'fetch card {card} information')

        def callback(response):
            try:
                if response and response.card_number == card:
                    with lock:
                        record = self._state.setdefault(card, {
                            ATTR_AVAILABLE: False,
                            ATTR_CARD_STARTDATE: None,
                            ATTR_CARD_ENDDATE: None,
                            ATTR_CARD_PERMISSIONS: None,
                        })
                   
                        _LOGGER.warning(f'>>>>>> >>>>> >>>>> WOOOT {response.controller} {response.start_date} {record.get(ATTR_CARD_STARTDATE)}')

                        start_date = record.get(ATTR_CARD_STARTDATE)
                        end_date = record.get(ATTR_CARD_ENDDATE)

                        if response.start_date is not None and (not start_date or response.start_date < start_date):
                            _LOGGER.warning(f'>>>>>> >>>>> >>>>> YEEEEEAHHHHHHHHHAAAAA/1')
                            start_date = response.start_date

                        if response.end_date is not None and (not end_date or response.end_date > end_date):
                            _LOGGER.warning(f'>>>>>> >>>>> >>>>> YEEEEEAHHHHHHHHHAAAAA/2')
                            end_date = response.end_date

                        self._state[card].update({
                            ATTR_CARD_STARTDATE: start_date,
                            ATTR_CARD_ENDDATE: end_date,
                            # ATTR_CARD_PERMISSIONS: update_permissions(......),
                            ATTR_AVAILABLE: True,
                        })
                
                    # self.async_set_updated_data(self._state)
            except Exception as exc:
                _LOGGER.error(f'error updating internal controller {controller.id} information ({exc})')

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
                response = await self._uhppote.get_card(controller.id, card, callback)
                if response and response.controller == controller.id and response.card_number == card:
                    if response.start_date is not None and (not start_date or response.start_date < start_date):
                        start_date = response.start_date

                    if response.end_date is not None and (not end_date or response.end_date > end_date):
                        end_date = response.end_date

                    permissions[controller.id] = []
                    if response.door_1 > 0: permissions[controller.id].append(1)
                    if response.door_2 > 0: permissions[controller.id].append(2)
                    if response.door_3 > 0: permissions[controller.id].append(3)
                    if response.door_4 > 0: permissions[controller.id].append(4)

                    if response.pin > 0:
                        PIN = response.pin

            info = {
                ATTR_CARD_STARTDATE: start_date,
                ATTR_CARD_ENDDATE: end_date,
                ATTR_CARD_PERMISSIONS: resolve_permissions(self._options, permissions),
                ATTR_CARD_PIN: PIN,
                ATTR_AVAILABLE: True,
            }

        except Exception as exc:
            _LOGGER.error(f'error retrieving card {card} information ({exc})')

        with lock:
            self._state[card].update(info)

    def _resolve(self, controller_id):
        for controller in self._controllers:
            if controller.id == controller_id:
                return controller

        return Controller(int(f'{controller_id}'), None, None)
