from .controllers import ControllersCoordinator


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

    def __init__(self, hass, options):
        self._controllers = ControllersCoordinator(hass, options)
