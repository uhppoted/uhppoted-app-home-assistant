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
        return [v['controller'] for v in self._controllers]

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

    def set_listener(self, controller, addr, port):
        return self._api.set_listener(controller, addr, port)

    def get_door_control(self, controller, door):
        return self._api.get_door_control(controller, door)

    def set_door_control(self, controller, door, mode, delay):
        return self._api.set_door_control(controller, door, mode, delay)

    def open_door(self, controller, door):
        return self._api.open_door(controller, door)

    def get_status(self, controller):
        return self._api.get_status(controller)

    def get_card(self, controller, card):
        return self._api.get_card(controller, card)

    def put_card(self, controller, card, start_date, end_date, door1, door2, door3, door4, PIN):
        return self._api.put_card(controller, card, start_date, end_date, door1, door2, door3, door4, PIN)

    def delete_card(self, controller, card):
        return api.delete_card(controller, card)

    def record_special_events(self, controller, enable):
        return self._api.record_special_events(controller, enable)

    def get_event(self, controller, index):
        return self._api.get_event(controller, index)
