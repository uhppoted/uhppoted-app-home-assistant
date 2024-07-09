import asyncio
import datetime

from ..const import DOMAIN
from ..const import CONF_POLL_CONTROLLERS
from ..const import CONF_POLL_DOORS
from ..const import CONF_POLL_CARDS
from ..const import CONF_POLL_EVENTS

from ..config import configure_driver

from .controllers import ControllersCoordinator
from .doors import DoorsCoordinator
from .cards import CardsCoordinator
from .events import EventsCoordinator
from .db import DB


class Coordinators():
    COORDINATORS = dict()

    @classmethod
    def initialise(clazz, hass, id, options):
        Coordinators.COORDINATORS[id] = Coordinators(hass, options)

    @classmethod
    def unload(clazz, id):
        coordinators = Coordinators.COORDINATORS.pop(id, None)
        if coordinators:
            coordinators._unload()

    @classmethod
    def controllers(clazz, id):
        coordinators = Coordinators.COORDINATORS.get(id)
        if coordinators:
            return coordinators._controllers

        return None

    @classmethod
    def doors(clazz, id):
        coordinators = Coordinators.COORDINATORS.get(id)
        if coordinators:
            return coordinators._doors

        return None

    @classmethod
    def cards(clazz, id):
        coordinators = Coordinators.COORDINATORS.get(id)
        if coordinators:
            return coordinators._cards

        return None

    @classmethod
    def events(clazz, id):
        coordinators = Coordinators.COORDINATORS.get(id)
        if coordinators:
            return coordinators._events

        return None

    @classmethod
    def unlock_door(clazz, door):
        unlocked = False

        for coordinators in Coordinators.COORDINATORS.values():
            if coordinators and coordinators._doors:
                if coordinators._doors.unlock_door_by_name(door):
                    unlocked = True

        return unlocked

    @classmethod
    def add_card(clazz, card):
        added = False

        for coordinators in Coordinators.COORDINATORS.values():
            if coordinators and coordinators._cards:
                if coordinators._cards.add_card(card):
                    added = True

        return added

    @classmethod
    def delete_card(clazz, card):
        deleted = False

        for coordinators in Coordinators.COORDINATORS.values():
            if coordinators and coordinators._cards:
                if coordinators._cards.delete_card(card):
                    deleted = True
        return deleted

    def __init__(self, hass, options):
        poll_controllers = None
        poll_doors = None
        poll_cards = None
        poll_events = None

        listen_addr = '0.0.0.0:60001'

        defaults = hass.data[DOMAIN] if DOMAIN in hass.data else {}

        if CONF_POLL_CONTROLLERS in defaults:
            poll_controllers = datetime.timedelta(seconds=defaults[CONF_POLL_CONTROLLERS])

        if CONF_POLL_DOORS in defaults:
            poll_doors = datetime.timedelta(seconds=defaults[CONF_POLL_DOORS])

        if CONF_POLL_CARDS in defaults:
            poll_cards = datetime.timedelta(seconds=defaults[CONF_POLL_CARDS])

        if CONF_POLL_EVENTS in defaults:
            poll_events = datetime.timedelta(seconds=defaults[CONF_POLL_EVENTS])

        self._db = DB()
        self._driver = configure_driver(options, defaults)
        self._controllers = ControllersCoordinator(hass, options, poll_controllers, self._driver, self._db)
        self._doors = DoorsCoordinator(hass, options, poll_doors, self._driver, self._db)
        self._cards = CardsCoordinator(hass, options, poll_cards, self._driver, self._db)
        self._events = EventsCoordinator(hass, options, poll_events, self._driver, self._db,
                                         lambda evt: self._on_event(hass, evt))

    def __del__(self):
        self.unload()

    def _unload(self):
        self._controllers.unload()
        self._doors.unload()
        self._cards.unload()
        self._events.unload()

    def _on_event(self, hass, event):
        asyncio.run_coroutine_threadsafe(self._async_on_event(event), hass.loop)

    async def _async_on_event(self, event):
        await self._doors.async_request_refresh()
