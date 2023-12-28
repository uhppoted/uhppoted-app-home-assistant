import re
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

from .const import ERR_INVALID_CONTROLLER_ID
from .const import ERR_DUPLICATE_CONTROLLER_ID

_LOGGER = logging.getLogger(__name__)
MAX_CARDS = 25
MAX_CARD_INDEX = 20000
MAX_ERRORS = 5


def normalise(v):
    return re.sub(r'\s+', '', f'{v}', flags=re.UNICODE).lower()


def validate_controller_id(serial_no, name, options) -> None:
    if not name or name.strip() == '':
        raise ValueError(ERR_INVALID_CONTROLLER_ID)

    if options and CONF_CONTROLLERS in options:
        for v in options[CONF_CONTROLLERS]:
            if normalise(v[CONF_CONTROLLER_ID]) == normalise(name):
                if int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') != int(f'{serial_no}'):
                    raise ValueError(ERR_DUPLICATE_CONTROLLER_ID)


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


def get_IPv4(defaults):
    bind = '0.0.0.0'
    broadcast = '255.255.255.255:60000'
    listen = '0.0.0.0:60001'
    debug = False

    if CONF_BIND_ADDR in defaults:
        bind = defaults[CONF_BIND_ADDR]

    if CONF_BROADCAST_ADDR in defaults:
        broadcast = defaults[CONF_BROADCAST_ADDR]

    if CONF_LISTEN_ADDR in defaults:
        listen = defaults[CONF_LISTEN_ADDR]

    if CONF_DEBUG in defaults:
        debug = defaults[CONF_DEBUG]

    return {
        CONF_BIND_ADDR: bind,
        CONF_BROADCAST_ADDR: broadcast,
        CONF_LISTEN_ADDR: listen,
        CONF_DEBUG: debug,
    }


def get_all_controllers(options):
    controllers = set()
    if CONF_CONTROLLERS in options:
        for v in options[CONF_CONTROLLERS]:
            controllers.add(int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}'))

    try:
        bind = options[CONF_BIND_ADDR]
        broadcast = options[CONF_BROADCAST_ADDR]
        listen = options[CONF_LISTEN_ADDR]
        debug = options[CONF_DEBUG]
        u = uhppote.Uhppote(bind, broadcast, listen, debug)

        response = u.get_all_controllers()

        for v in response:
            controllers.add(v.controller)

    except Exception as e:
        _LOGGER.exception(f'error retrieving list of controllers ({e})')

    return sorted(list(controllers), reverse=True)


def get_all_cards(options):
    cards = set()

    bind = options[CONF_BIND_ADDR]
    broadcast = options[CONF_BROADCAST_ADDR]
    listen = options[CONF_LISTEN_ADDR]
    debug = options[CONF_DEBUG]
    u = uhppote.Uhppote(bind, broadcast, listen, debug)

    controllers = options[CONF_CONTROLLERS]

    for c in controllers:
        controller = int(f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip())

        try:
            response = u.get_cards(controller)
            _LOGGER.info(f'{controller}: {response.cards} cards')

            N = min(response.cards, MAX_CARDS)
            ix = 1
            count = 0
            errors = 0

            while count < N and ix < MAX_CARD_INDEX and len(cards) < MAX_CARDS and errors < MAX_ERRORS:
                try:
                    response = u.get_card_by_index(controller, ix)
                    count += 1
                    cards.add(response.card_number)
                    ix += 1
                except Exception as e:
                    errors += 1
                    _LOGGER.warning(f'{controller} error retrieving card at index {ix} ({e})')

        except Exception as e:
            _LOGGER.warning(f'{controller} error retrieving list of cards ({e})')

    return sorted(cards)


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
