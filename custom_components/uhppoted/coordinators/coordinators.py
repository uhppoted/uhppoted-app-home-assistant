from .controllers import ControllersCoordinator
from .doors import DoorsCoordinator
from .cards import CardsCoordinator
from .events import EventsCoordinator


class Coordinators():
    COORDINATORS = None

    @classmethod
    def initialise(clazz, hass, options):
        Coordinators.COORDINATORS = Coordinators(hass, options)

    @classmethod
    def unload(clazz):
        coordinators = Coordinators.COORDINATORS
        Coordinators.COORDINATORS = None

        if coordinators:
            coordinators._unload()

    @classmethod
    def controllers(clazz):
        coordinators = Coordinators.COORDINATORS
        if coordinators:
            return coordinators._controllers

        return None

    @classmethod
    def doors(clazz):
        coordinators = Coordinators.COORDINATORS
        if coordinators:
            return coordinators._doors

        return None

    @classmethod
    def cards(clazz):
        coordinators = Coordinators.COORDINATORS
        if coordinators:
            return coordinators._cards

        return None

    @classmethod
    def events(clazz):
        coordinators = Coordinators.COORDINATORS
        if coordinators:
            return coordinators._events

        return None

    def __init__(self, hass, options):
        self._controllers = ControllersCoordinator(hass, options)
        self._doors = DoorsCoordinator(hass, options)
        self._cards = CardsCoordinator(hass, options)
        self._events = EventsCoordinator(hass, options)

    def __del__(self):
        self.unload()

    def _unload(self):
        self._controllers.unload()
        self._doors.unload()
        self._cards.unload()
        self._events.unload()
