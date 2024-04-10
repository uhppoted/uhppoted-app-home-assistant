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
