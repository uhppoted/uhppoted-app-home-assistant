from __future__ import annotations
from collections import deque

import logging

_LOGGER = logging.getLogger(__name__)

from ..const import DOMAIN
from ..coordinators.coordinators import Coordinators


class Services():
    COORDINATORS = None

    @classmethod
    def initialise(clazz, hass, options):
        hass.services.async_register(DOMAIN, "unlock_door", lambda v: unlock_door(options, v))

    @classmethod
    def unload(clazz, hass):
        hass.services.async_remove(DOMAIN, 'unlock-door')


def unlock_door(options, call):
    _LOGGER.debug('service call:unlock-door', call.data)

    try:
        door = call.data.get('door', None)
        if door:
            if Coordinators.unlock_door(door):
                _LOGGER.info(f'service call:unlock door opened door {door}')
            else:
                _LOGGER.warning(f'service call:unlock door did not open door {door}')
    except Exception as err:
        _LOGGER.warning(f'error executing unlock-door service call ({err})')
