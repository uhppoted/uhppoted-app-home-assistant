import logging

from collections import namedtuple
from uhppoted import uhppote

_LOGGER = logging.getLogger(__name__)

Controller = namedtuple('Controller', 'id address protocol')


class uhppoted:

    def __init__(self, bind, broadcast, listen, controllers, timeout, debug):
        self._broadcast = broadcast
        self._api = uhppote.Uhppote(bind, broadcast, listen, debug)
        self._timeout = timeout
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
        (c, timeout) = self._lookup(controller)
        return self._api.get_controller(c, timeout=self._timeout)

    def get_time(self, controller):
        (c, timeout) = self._lookup(controller)
        return self._api.get_time(c, timeout=timeout)

    def set_time(self, controller, time):
        (c, timeout) = self._lookup(controller)
        return self._api.set_time(c, time, timeout=timeout)

    def get_listener(self, controller):
        (c, timeout) = self._lookup(controller)
        return self._api.get_listener(c, timeout=timeout)

    def set_listener(self, controller, address, port):
        (c, timeout) = self._lookup(controller)
        return self._api.set_listener(c, address, port, interval=0, timeout=timeout)

    def get_door_control(self, controller, door):
        (c, timeout) = self._lookup(controller)
        return self._api.get_door_control(c, door, timeout=timeout)

    def set_door_control(self, controller, door, mode, delay):
        (c, timeout) = self._lookup(controller)
        return self._api.set_door_control(c, door, mode, delay, timeout=timeout)

    def open_door(self, controller, door):
        (c, timeout) = self._lookup(controller)
        return self._api.open_door(c, door, timeout=timeout)

    def get_status(self, controller):
        (c, timeout) = self._lookup(controller)
        return self._api.get_status(c, timeout=timeout)

    def get_cards(self, controller):
        (c, timeout) = self._lookup(controller)
        return self._api.get_cards(c, timeout=timeout)

    def get_card(self, controller, card):
        (c, timeout) = self._lookup(controller)
        return self._api.get_card(c, card, timeout=timeout)

    def get_card_by_index(self, controller, index):
        (c, timeout) = self._lookup(controller)
        return self._api.get_card_by_index(c, index, timeout=timeout)

    def put_card(self, controller, card, start_date, end_date, door1, door2, door3, door4, PIN):
        (c, timeout) = self._lookup(controller)
        return self._api.put_card(c, card, start_date, end_date, door1, door2, door3, door4, PIN, timeout=timeout)

    def delete_card(self, controller, card):
        (c, timeout) = self._lookup(controller)
        return self.api.delete_card(c, card, timeout=timeout)

    def record_special_events(self, controller, enable):
        (c, timeout) = self._lookup(controller)
        return self._api.record_special_events(c, enable, timeout=timeout)

    def get_event(self, controller, index):
        (c, timeout) = self._lookup(controller)
        return self._api.get_event(c, index, timeout=timeout)

    def _lookup(self, controller):
        for v in self._controllers:
            if controller == v['controller']:
                addr = v.get('address', None)
                port = v.get('port', 60000)
                timeout = v.get('timeout', self._timeout)
                protocol = v.get('protocol', 'udp')

                if addr is None:
                    return ((controller, None, 'udp'), timeout)
                elif f'{addr}:{port}' == self._broadcast:
                    return ((controller, None, 'udp'), timeout)
                else:
                    return ((controller, f'{addr}:{port}', protocol), timeout)

        return ((controller, None, 'udp'), self._timeout)
