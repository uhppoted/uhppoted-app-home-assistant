from uhppoted import uhppote


class uhppoted:

    def __init__(self, bind, broadcast, listen, controllers, debug):
        self._api = uhppote.Uhppote(bind, broadcast, listen, debug)
        self._controllers = controllers

    @property
    def api(self):
        return self._api

    @property
    def controllers(self):
        return self._controllers

    @staticmethod
    def get_all_controllers(bind, broadcast, listen, debug):
        return uhppote.Uhppote(bind, broadcast, listen, debug).get_all_controllers()

    def get_controller(self, controller):
        return self._api.get_controller(controller)

    def get_time(self, controller):
        return self._api.get_time(controller)

    def set_time(self, controller, time):
        return self._api.set_time(controller, time)

    def get_listener(self, controller):
        return self._api.get_listener(controller)
