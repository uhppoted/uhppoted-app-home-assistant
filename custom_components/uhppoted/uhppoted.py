import logging

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from uhppoted import uhppote

from .const import CONF_CACHE_EXPIRY_INTERLOCK

_LOGGER = logging.getLogger(__name__)
_CACHE_EXPIRY_INTERLOCK = 900 # 15 minutes

Controller = namedtuple('Controller', 'id address protocol')

@dataclass
class GetInterlockResponse:
    controller: int
    interlock: int


#FIXME remove when uhppoted-lib is published
@dataclass
class GetAntiPassbackResponse:
    controller: int
    antipassback: int


#FIXME remove when uhppoted-lib is published
@dataclass
class SetAntiPassbackResponse:
    controller: int
    ok: bool


_CACHE = {}

class uhppoted:

    def __init__(self, bind, broadcast, listen, controllers, timeout, debug):
        self._broadcast = broadcast
        self._api = uhppote.Uhppote(bind, broadcast, listen, debug)
        self._timeout = timeout
        self._controllers = controllers
        self._caching = {
           CONF_CACHE_EXPIRY_INTERLOCK: _CACHE_EXPIRY_INTERLOCK,
        }

    @property
    def api(self):
        return self._api

    @property
    def controllers(self):
        return [v['controller'] for v in self._controllers]

    @property
    def caching(self) -> int:
        return self._caching

    @caching.setter
    def caching(self, expiry: {}) -> None:
        self._caching |= expiry

    @staticmethod
    def get_all_controllers(bind, broadcast, listen, debug):
        return uhppote.Uhppote(bind, broadcast, listen, debug).get_all_controllers()

    def get_controller(self, controller):
        (c, timeout) = self._lookup(controller)
        return self._api.get_controller(c, timeout=timeout)

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

    def get_interlock(self, controller):
        key = f'controller.{controller}.interlock'

        if record := _CACHE.get(key, None):
            now = datetime.now()
            dt = now - record['touched']
            expiry = self.caching.get(CONF_CACHE_EXPIRY_INTERLOCK, _CACHE_EXPIRY_INTERLOCK)
            if dt.total_seconds() < expiry:
                return GetInterlockResponse(controller, record.get('interlock', -1))

        return GetInterlockResponse(controller, -1)

    def set_interlock(self, controller, interlock):
        key = f'controller.{controller}.interlock'

        (c, timeout) = self._lookup(controller)
        response = self._api.set_interlock(c, interlock, timeout=timeout)

        if response and not response.ok:
            del _CACHE[key]
        else:
            _CACHE[key] = {
                'interlock': interlock,
                'touched': datetime.now(),
            }

        return response

    def get_antipassback(self, controller):
        # FIXME
        # (c, timeout) = self._lookup(controller)
        # return self._api.get_antipassback(c, timeout=timeout)

        if record := _CACHE.get(f'controller.{controller}.antipassback', None):
            return GetAntiPassbackResponse(controller, record.get('antipassback', -1))

        return GetAntiPassbackResponse(controller, 0)

    def set_antipassback(self, controller, antipassback):
        # FIXME
        # (c, timeout) = self._lookup(controller)
        # return self._api.set_antipassback(c, antipassback, timeout=timeout)

        _CACHE[f'controller.{controller}.antipassback'] = {
            'antipassback': antipassback,
            'touched': datetime.now(),
        }

        return SetAntiPassbackResponse(controller, True)

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
