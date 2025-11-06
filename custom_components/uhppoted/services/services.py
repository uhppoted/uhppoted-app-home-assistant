from __future__ import annotations
from collections import deque

import logging
import re

_LOGGER = logging.getLogger(__name__)

from ..const import DOMAIN
from ..coordinators.coordinators import Coordinators


class Services():
    SERVICES = dict()

    @classmethod
    def initialise(clazz, hass, id, options):
        if not Services.SERVICES:
            hass.services.async_register(DOMAIN, "unlock_door", unlock_door)
            hass.services.async_register(DOMAIN, "add_card", add_card)
            hass.services.async_register(DOMAIN, "delete_card", delete_card)

            Services.SERVICES[id] = True

    @classmethod
    def unload(clazz, hass, id):
        Services.SERVICES.pop(id, None)

        if not Services.SERVICES:
            hass.services.async_remove(DOMAIN, 'unlock_door')
            hass.services.async_remove(DOMAIN, 'add_card')
            hass.services.async_remove(DOMAIN, 'delete_card')


async def unlock_door(call):
    _LOGGER.debug('service call:unlock-door', call.data)

    try:
        door = call.data.get('door', None)
        if door:
            if await Coordinators.unlock_door(door):
                _LOGGER.info(f'service call:unlock-door opened door {door}')
            else:
                _LOGGER.warning(f'service call:unlock-door did not open door {door}')
    except Exception as err:
        _LOGGER.warning(f'error executing unlock-door service call ({err})')


async def add_card(call):
    _LOGGER.debug('service call:add-card', call.data)

    try:
        card = call.data.get('card', None)
        if card and re.compile("^[0-9]+$").match(f'{card}'):
            if await Coordinators.add_card(card):
                _LOGGER.info(f'service call:add-card  added card {card}')
            else:
                _LOGGER.info(f'service call:add-card  failed to add card {card}')

    except Exception as err:
        _LOGGER.warning(f'error executing add-card service call ({err})')


async def delete_card(call):
    _LOGGER.debug('service call:delete-card', call.data)

    try:
        card = call.data.get('card', None)
        if card and re.compile("^[0-9]+$").match(f'{card}'):
            if await Coordinators.delete_card(card):
                _LOGGER.info(f'service call:delete-card  deleted card {card}')
            else:
                _LOGGER.info(f'service call:delete-card  failed to delete card {card}')
    except Exception as err:
        _LOGGER.warning(f'error executing delete-card service call ({err})')
