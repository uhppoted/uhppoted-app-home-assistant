from uhppoted import uhppote


class uhppoted:

    def __init__(self, bind, broadcast, listen, controllers, debug):
        self._broadcast = broadcast
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
        addr = self._lookup(controller)
        return self._api.get_controller(controller, dest_addr=addr)

    def get_time(self, controller):
        addr = self._lookup(controller)
        return self._api.get_time(controller, dest_addr=addr)

    def set_time(self, controller, time):
        addr = self._lookup(controller)
        return self._api.set_time(controller, time, dest_addr=addr)

    def get_listener(self, controller):
        addr = self._lookup(controller)
        return self._api.get_listener(controller, dest_addr=addr)

    def set_listener(self, controller, addr, port):
        addr = self._lookup(controller)
        return self._api.set_listener(controller, addr, port, dest_addr=addr)

    def get_door_control(self, controller, door):
        addr = self._lookup(controller)
        return self._api.get_door_control(controller, door, dest_addr=addr)

    def set_door_control(self, controller, door, mode, delay):
        addr = self._lookup(controller)
        return self._api.set_door_control(controller, door, mode, delay, dest_addr=addr)

    def open_door(self, controller, door):
        addr = self._lookup(controller)
        return self._api.open_door(controller, door, dest_addr=addr)

    def get_status(self, controller):
        addr = self._lookup(controller)
        return self._api.get_status(controller, dest_addr=addr)

    def get_card(self, controller, card):
        addr = self._lookup(controller)
        return self._api.get_card(controller, card)

    def put_card(self, controller, card, start_date, end_date, door1, door2, door3, door4, PIN):
        addr = self._lookup(controller)
        return self._api.put_card(controller, card, start_date, end_date, door1, door2, door3, door4, PIN, dest_addr=addr)

    def delete_card(self, controller, card):
        addr = self._lookup(controller)
        return api.delete_card(controller, card, dest_addr=addr)

    def record_special_events(self, controller, enable):
        addr = self._lookup(controller)
        return self._api.record_special_events(controller, enable, dest_addr=addr)

    def get_event(self, controller, index):
        addr = self._lookup(controller)
        return self._api.get_event(controller, index, dest_addr=addr)

    def _lookup(self, controller):
        for v in self._controllers:
            if controller == v['controller']:
                addr = v.get('address', self._broadcast)
                port = v.get('port', 60000)
                return f'{addr}:{port}'

        return None
