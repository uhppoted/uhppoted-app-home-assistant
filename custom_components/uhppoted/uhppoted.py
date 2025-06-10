import asyncio
import logging

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from asyncio import Queue

from uhppoted import uhppote
from uhppoted.structs import GetTimeResponse
from uhppoted.structs import GetListenerResponse

from . import const
from .const import CONF_CACHE_EXPIRY_CONTROLLER
from .const import CONF_CACHE_EXPIRY_LISTENER
from .const import CONF_CACHE_EXPIRY_DATETIME
from .const import CONF_CACHE_EXPIRY_INTERLOCK

_LOGGER = logging.getLogger(__name__)

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

_DEFAULT_CACHE_EXPIRY = {
    CONF_CACHE_EXPIRY_CONTROLLER: const.DEFAULT_CACHE_EXPIRY_CONTROLLER,
    CONF_CACHE_EXPIRY_LISTENER: const.DEFAULT_CACHE_EXPIRY_LISTENER,
    CONF_CACHE_EXPIRY_DATETIME: const.DEFAULT_CACHE_EXPIRY_DATETIME,
    CONF_CACHE_EXPIRY_INTERLOCK: const.DEFAULT_CACHE_EXPIRY_INTERLOCK,
}


class uhppoted:

    def __init__(self, bind, broadcast, listen, controllers, timeout, debug):
        self._broadcast = broadcast
        self._api = uhppote.Uhppote(bind, broadcast, listen, debug)
        self._timeout = timeout
        self._controllers = controllers
        self.queue = Queue()
        self._caching = {}

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

    async def worker(self):
        while True:
            task = await self.queue.get()
            try:
                await task()
            except Exception as exc:
                _LOGGER.warning(f"{exc}")
            finally:
                self.queue.task_done()

    def start(self, hass):
        self._thread = hass.loop.create_task(self.worker())

    def stop(self, hass):
        if self._thread:
            self._thread.cancel()

    async def ye_olde_taskke(self, g, key, message, callback=None):
        try:
            if response := g():
                _LOGGER.info(f"{message} ok")

                _CACHE[key] = {
                    'response': response,
                    'touched': datetime.now(),
                }

                if callback:
                    callback(response)
        except Exception as exc:
            _LOGGER.warning(f"{message} ({exc})")

    def get(self, key, expiry_key):
        if record := _CACHE.get(key, None):
            expiry = self.caching.get(expiry_key, _DEFAULT_CACHE_EXPIRY.get(expiry_key, 60))
            now = datetime.now()
            dt = now - record['touched']
            if dt.total_seconds() < expiry:
                return record.get('response')

        return None

    def get_controller(self, controller, callback):
        key = f'controller.{controller}.controller'
        (c, timeout) = self._lookup(controller)

        g = lambda: self._api.get_controller(c, timeout=timeout)

        self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key, f"{'get-controller':<15} {controller}", callback))

        return self.get(key, CONF_CACHE_EXPIRY_CONTROLLER)

    def get_time(self, controller, callback=None):
        key = f'controller.{controller}.datetime'
        (c, timeout) = self._lookup(controller)
        g = lambda: self._api.get_time(c, timeout=timeout)

        self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key, f"{'get-time':<15} {controller}", callback))

        return self.get(key, CONF_CACHE_EXPIRY_DATETIME)

    def set_time(self, controller, time):
        key = f'controller.{controller}.datetime'
        (c, timeout) = self._lookup(controller)

        response = self._api.set_time(c, time, timeout=timeout)
        if response is None:
            del _CACHE[key]
        else:
            _CACHE[key] = {
                'response': GetTimeResponse(response.controller, response.datetime),
                'touched': datetime.now(),
            }

        return response

    def get_listener(self, controller, callback=None):
        key = f'controller.{controller}.listener'
        (c, timeout) = self._lookup(controller)
        g = lambda: self._api.get_listener(c, timeout=timeout)

        self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key, f"{'get_listener':<15} {controller}", callback))

        return self.get(key, CONF_CACHE_EXPIRY_LISTENER)

    def set_listener(self, controller, address, port):
        key = f'controller.{controller}.listener'
        (c, timeout) = self._lookup(controller)

        response = self._api.set_listener(c, address, port, interval=0, timeout=timeout)
        if response is None or not response.ok:
            del _CACHE[key]
        else:
            _CACHE[key] = {
                'response': GetListenerResponse(response.controller, address, port, 0),
                'touched': datetime.now(),
            }

        return response

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

        return self.get(key, CONF_CACHE_EXPIRY_INTERLOCK)

    def set_interlock(self, controller, interlock):
        key = f'controller.{controller}.interlock'

        (c, timeout) = self._lookup(controller)
        response = self._api.set_interlock(c, interlock, timeout=timeout)

        if response and not response.ok:
            del _CACHE[key]
        else:
            _CACHE[key] = {
                'response': GetInterlockResponse(controller, interlock),
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
