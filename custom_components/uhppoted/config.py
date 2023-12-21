import logging

from typing import Any

from uhppoted import uhppote

from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_DOORS
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

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

        controllers.sort(reverse=True)

    except Exception as e:
        _LOGGER.exception(f'error retrieving list of controllers ({e})')

    return controllers


def configure_controllers(options, f):
    controllers = options[CONF_CONTROLLERS]

    for c in controllers:
        controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
        serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
        address = f'{c[CONF_CONTROLLER_ADDR]}'.strip()

        f(controller, serial_no, address)


def configure_doors(options, g):
    controllers = options[CONF_CONTROLLERS]
    doors = options[CONF_DOORS]

    for c in controllers:
        controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
        serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
        address = f'{c[CONF_CONTROLLER_ADDR]}'.strip()

        for d in doors:
            door = f'{d[CONF_DOOR_ID]}'.strip()
            door_no = f'{d[CONF_DOOR_NUMBER]}'.strip()
            door_controller = f'{d[CONF_DOOR_CONTROLLER]}'.strip()

            if door_controller == controller:
                g(controller, serial_no, door, door_no)
