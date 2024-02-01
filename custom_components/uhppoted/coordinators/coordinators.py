from .controllers import ControllersCoordinator
from .doors import DoorsCoordinator


class Coordinators():
    COORDINATORS = None

    @classmethod
    def initialise(clazz, hass, options):
        Coordinators.COORDINATORS = Coordinators(hass, options)

    @classmethod
    def unload(clazz, hass, options):
        Coordinators.COORDINATORS = None

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

    def __init__(self, hass, options):
        self._controllers = ControllersCoordinator(hass, options)
        self._doors = DoorsCoordinator(hass, options)
