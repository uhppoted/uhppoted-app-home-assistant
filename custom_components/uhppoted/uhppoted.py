import asyncio
import logging

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from asyncio import Queue
from typing import Any

from uhppoted import uhppote
from uhppoted.structs import GetTimeResponse
from uhppoted.structs import GetListenerResponse
from uhppoted.structs import GetDoorControlResponse
from uhppoted.structs import GetCardResponse

from . import const
from .const import CONF_CACHE_EXPIRY_CONTROLLER
from .const import CONF_CACHE_EXPIRY_LISTENER
from .const import CONF_CACHE_EXPIRY_DATETIME
from .const import CONF_CACHE_EXPIRY_DOOR
from .const import CONF_CACHE_EXPIRY_CARD
from .const import CONF_CACHE_EXPIRY_STATUS
from .const import CONF_CACHE_EXPIRY_INTERLOCK
from .const import CONF_CACHE_EXPIRY_ANTIPASSBACK
from .const import CONF_CACHE_EXPIRY_EVENT

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


@dataclass
class CacheEntry:
    response: Any
    expires: datetime


_CACHE = {}

_DEFAULT_CACHE_EXPIRY = {
    CONF_CACHE_EXPIRY_CONTROLLER: const.DEFAULT_CACHE_EXPIRY_CONTROLLER,
    CONF_CACHE_EXPIRY_LISTENER: const.DEFAULT_CACHE_EXPIRY_LISTENER,
    CONF_CACHE_EXPIRY_DATETIME: const.DEFAULT_CACHE_EXPIRY_DATETIME,
    CONF_CACHE_EXPIRY_DOOR: const.DEFAULT_CACHE_EXPIRY_DOOR,
    CONF_CACHE_EXPIRY_CARD: const.DEFAULT_CACHE_EXPIRY_CARD,
    CONF_CACHE_EXPIRY_STATUS: const.DEFAULT_CACHE_EXPIRY_STATUS,
    CONF_CACHE_EXPIRY_INTERLOCK: const.DEFAULT_CACHE_EXPIRY_INTERLOCK,
    CONF_CACHE_EXPIRY_ANTIPASSBACK: const.DEFAULT_CACHE_EXPIRY_ANTIPASSBACK,
    CONF_CACHE_EXPIRY_EVENT: const.DEFAULT_CACHE_EXPIRY_EVENT,
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

    def start(self, hass):
        self._thread = hass.loop.create_task(self._worker())
        self.queue.put_nowait(lambda: self._flush())

    def stop(self, hass):
        if self._thread:
            self._thread.cancel()

    async def _worker(self):
        while True:
            task = await self.queue.get()
            try:
                await task()
            except Exception as exc:
                _LOGGER.warning(f"{exc}")
            finally:
                self.queue.task_done()

    async def ye_olde_taskke(self, g, key, expiry, message, callback=None):
        try:
            if response := g():
                _LOGGER.info(f"{message} ok")

                self._put(response, key, expiry)

                if callback:
                    callback(response)
        except Exception as exc:
            _LOGGER.warning(f"{message} ({exc})")

    async def _flush(self):
        now = datetime.now()
        expired = [key for key, record in _CACHE.items() if record.expires < now]

        if len(expired) > 0:
            _LOGGER.warning(f'flushing cache - cached:{len(_CACHE)} expired:{len(expired)}')
            for key in expired:
                del _CACHE[key]

        await asyncio.sleep(60)
        self.queue.put_nowait(lambda: self._flush())

    def _put(self, response, key, expiry):
        lifetime = self.caching.get(expiry, _DEFAULT_CACHE_EXPIRY.get(expiry, 60))
        now = datetime.now()
        expires = now + timedelta(seconds=lifetime)

        _CACHE[key] = CacheEntry(response, expires)

    def _get(self, key):
        if record := _CACHE.get(key, None):
            now = datetime.now()
            if now < record.expires:
                return record.response

        return None

    def _delete(self, key):
        del _CACHE[key]

    def get_controller(self, controller, callback):
        key = f'controller.{controller}.controller'
        (c, timeout) = self._lookup(controller)

        g = lambda: self._api.get_controller(c, timeout=timeout)

        self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key, CONF_CACHE_EXPIRY_CONTROLLER,
                                                          f"{'get-controller':<16} {controller}", callback))

        return self._get(key)

    def get_listener(self, controller, callback=None):
        key = f'controller.{controller}.listener'
        (c, timeout) = self._lookup(controller)
        g = lambda: self._api.get_listener(c, timeout=timeout)

        self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key, CONF_CACHE_EXPIRY_LISTENER,
                                                          f"{'get_listener':<16} {controller}", callback))

        return self._get(key)

    def set_listener(self, controller, address, port):
        key = f'controller.{controller}.listener'
        (c, timeout) = self._lookup(controller)

        response = self._api.set_listener(c, address, port, interval=0, timeout=timeout)

        if response is None or not response.ok:
            self._delete(key)
        else:
            self._put(GetListenerResponse(response.controller, address, port, 0), key, CONF_CACHE_EXPIRY_LISTENER)

        return response

    def get_time(self, controller, callback=None):
        key = f'controller.{controller}.datetime'
        (c, timeout) = self._lookup(controller)
        g = lambda: self._api.get_time(c, timeout=timeout)

        self.queue.put_nowait(
            lambda: self.ye_olde_taskke(g, key, CONF_CACHE_EXPIRY_DATETIME, f"{'get-time':<16} {controller}", callback))

        return self._get(key)

    def set_time(self, controller, time):
        key = f'controller.{controller}.datetime'
        (c, timeout) = self._lookup(controller)

        response = self._api.set_time(c, time, timeout=timeout)

        if response is None:
            self._delete(key)
        else:
            self._put(GetTimeResponse(response.controller, response.datetime), key, CONF_CACHE_EXPIRY_DATETIME)

        return response

    def get_door_control(self, controller, door, callback=None):
        key = f'controller.{controller}.door.{door}'
        (c, timeout) = self._lookup(controller)
        g = lambda: self._api.get_door_control(c, door, timeout=timeout)

        self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key, CONF_CACHE_EXPIRY_DOOR,
                                                          f"{'get_door_control':<16} {controller} {door}", callback))

        return self._get(key)

    def set_door_control(self, controller, door, mode, delay):
        key = f'controller.{controller}.door.{door}'
        (c, timeout) = self._lookup(controller)

        response = self._api.set_door_control(c, door, mode, delay, timeout=timeout)
        if response is None:
            self._delete(key)
        else:
            self._put(GetDoorControlResponse(response.controller, response.door, response.mode, response.delay), key,
                      CONF_CACHE_EXPIRY_DOOR)

        return response

    def open_door(self, controller, door):
        (c, timeout) = self._lookup(controller)
        return self._api.open_door(c, door, timeout=timeout)

    def get_status(self, controller, callback=None):
        key = f'controller.{controller}.status'
        (c, timeout) = self._lookup(controller)
        g = lambda: self._api.get_status(c, timeout=timeout)

        self.queue.put_nowait(
            lambda: self.ye_olde_taskke(g, key, CONF_CACHE_EXPIRY_STATUS, f"{'get_status':<16} {controller}", callback))

        return self._get(key)

    def get_cards(self, controller):
        (c, timeout) = self._lookup(controller)
        return self._api.get_cards(c, timeout=timeout)

    def get_card(self, controller, card):
        key = f'controller.{controller}.card.{card}'
        (c, timeout) = self._lookup(controller)

        try:
            response = self._api.get_card(c, card, timeout=timeout)
            if response is None:
                self._delete(key)
            else:
                self._put(response, key, CONF_CACHE_EXPIRY_CARD)
        except Exception as exc:
            _LOGGER.error(f'error retrieving card {card} from controller {controller} ({exc})')

        return self._get(key)

    def get_card_by_index(self, controller, index):
        (c, timeout) = self._lookup(controller)
        return self._api.get_card_by_index(c, index, timeout=timeout)

    def put_card(self, controller, card, start_date, end_date, door1, door2, door3, door4, PIN):
        key = f'controller.{controller}.card.{card}'
        (c, timeout) = self._lookup(controller)
        response = self._api.put_card(c, card, start_date, end_date, door1, door2, door3, door4, PIN, timeout=timeout)

        if response is not None and response.stored:
            self._put(GetCardResponse(response.controller, card, start_date, end_date, door1, door2, door3, door4, PIN),
                      key, CONF_CACHE_EXPIRY_CARD)

        return response

    def delete_card(self, controller, card):
        (c, timeout) = self._lookup(controller)
        return self.api.delete_card(c, card, timeout=timeout)

    def record_special_events(self, controller, enable):
        (c, timeout) = self._lookup(controller)
        return self._api.record_special_events(c, enable, timeout=timeout)

    def get_event(self, controller, index):
        key = f'controller.{controller}.event.{index}'
        (c, timeout) = self._lookup(controller)

        try:
            response = self._api.get_event(c, index, timeout=timeout)
            if response is not None:  # events are never deleted
                self._put(response, key, CONF_CACHE_EXPIRY_EVENT)
        except Exception as exc:
            _LOGGER.error(f'error retrieving event {index} from controller {controller} ({exc})')

        return self._get(key)

    def get_interlock(self, controller):
        key = f'controller.{controller}.interlock'

        return self._get(key)

    def set_interlock(self, controller, interlock):
        key = f'controller.{controller}.interlock'

        (c, timeout) = self._lookup(controller)
        response = self._api.set_interlock(c, interlock, timeout=timeout)

        if response is None or not response.ok:
            self._delete(key)
        else:
            self._put(GetInterlockResponse(controller, interlock), key, CONF_CACHE_EXPIRY_INTERLOCK)

        return response

    def get_antipassback(self, controller, callback=None):
        key = f'controller.{controller}.antipassback'

        # FIXME
        # (c, timeout) = self._lookup(controller)
        # g = lambda: self._api.get_antipassback(c, timeout=timeout)
        #
        # self.queue.put_nowait(lambda: self.ye_olde_taskke(g, key,CONF_CACHE_EXPIRY_ANTIPASSBACK, f"{'get_antipassback':<16} {controller}", callback))

        if response := self._get(key):
            return response
        else:
            return GetAntiPassbackResponse(controller, 0)

    def set_antipassback(self, controller, antipassback):
        key = f'controller.{controller}.antipassback'
        # FIXME
        # (c, timeout) = self._lookup(controller)
        # response = self._api.set_antipassback(c, antipassback, timeout=timeout)
        #
        # if response is None or not response.ok:
        #     self._delete(key)
        # else:
        #     self._put(GetAntiPassbackResponse(controller, antipassback),
        #               key,
        #               CONF_CACHE_EXPIRY_ANTIPASSBACK)

        self._put(GetAntiPassbackResponse(controller, antipassback), key, CONF_CACHE_EXPIRY_ANTIPASSBACK)

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
