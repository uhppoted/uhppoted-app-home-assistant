import logging

from typing import Any

from uhppoted import uhppote

from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_ID

_LOGGER = logging.getLogger(__name__)


def validate_controller_id(v: int) -> None:
    if not v or v.strip() == '':
        raise ValueError


def validate_controller_serial_no(v) -> None:
    controller = int(f'{v}')
    if controller < 100000000:
        raise ValueError


def validate_door_id(v: int) -> None:
    if not v or v.strip() == '':
        raise ValueError


def validate_door_controller(v: str, controllers: list[Any]) -> None:
    for controller in controllers:
        if v == controller[CONF_CONTROLLER_ID]:
            return

    raise ValueError


def validate_door_number(v) -> None:
    door = int(f'{v}')
    if door < 1 or door > 4:
        raise ValueError


def validate_card_number(v: int) -> None:
    card = int(f'{v}')
    if card < 1:
        raise ValueError


def list_controllers(options):
    return [v[CONF_CONTROLLER_ID] for v in options[CONF_CONTROLLERS]]


def get_all_controllers(options):
    controllers = []

    try:
        bind = options[CONF_BIND_ADDR]
        broadcast = options[CONF_BROADCAST_ADDR]
        listen = options[CONF_LISTEN_ADDR]
        debug = options[CONF_DEBUG]
        u = uhppote.Uhppote(bind, broadcast, listen, debug)

        response = u.get_all_controllers()

        for v in response:
            controllers.append(v.controller)

    except Exception as e:
        _LOGGER.exception(f'error retrieving list of controllers ({e})')

    return controllers
