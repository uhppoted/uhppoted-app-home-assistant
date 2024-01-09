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
from .const import CONF_CARDS
from .const import CONF_CARD_NUMBER
from .const import CONF_CARD_NAME
from .const import CONF_CARD_STARTDATE
from .const import CONF_CARD_ENDDATE
from .const import CONF_CARD_DOORS

from .const import ERR_INVALID_CONTROLLER_ID
from .const import ERR_DUPLICATE_CONTROLLER_ID
from .const import ERR_DUPLICATE_CONTROLLER_IDS
from .const import ERR_INVALID_DOOR_ID
from .const import ERR_DUPLICATE_DOOR_ID
from .const import ERR_DUPLICATE_DOOR_IDS
from .const import ERR_INVALID_CARD_ID

_LOGGER = logging.getLogger(__name__)
MAX_CARDS = 25
MAX_CARD_INDEX = 20000
MAX_ERRORS = 5


def normalise(v):
    return re.sub(r'\s+', '', f'{v}', flags=re.UNICODE).lower()


def validate_controller_id(serial_no, name, options):
    if not name or name.strip() == '':
        raise ValueError(ERR_INVALID_CONTROLLER_ID)

    if options and CONF_CONTROLLERS in options:
        for v in options[CONF_CONTROLLERS]:
            if normalise(v[CONF_CONTROLLER_ID]) == normalise(name):
                if int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') != int(f'{serial_no}'):
                    raise ValueError(ERR_DUPLICATE_CONTROLLER_ID)


def validate_all_controllers(options):
    if options and CONF_CONTROLLERS in options:
        controllers = [normalise(v[CONF_CONTROLLER_ID]) for v in options[CONF_CONTROLLERS]]
        if len(controllers) != len(set(controllers)):
            raise ValueError(ERR_DUPLICATE_CONTROLLER_IDS)


def validate_door_id(name, options):
    if not name or name.strip() == '':
        raise ValueError(ERR_INVALID_DOOR_ID)

    if name.strip() != '-' and options and CONF_DOORS in options:
        for v in options[CONF_DOORS]:
            if normalise(v[CONF_DOOR_ID]) == normalise(name):
                raise ValueError(ERR_DUPLICATE_DOOR_ID)


def validate_door_duplicates(name, doors):
    normalised = [normalise(v) for v in doors]
    normalised = [v for v in normalised if v != '']

    if normalised.count(normalise(name)) > 1:
        raise ValueError(ERR_DUPLICATE_DOOR_ID)


def validate_all_doors(options):
    if options and CONF_DOORS in options:
        doors = [normalise(v[CONF_DOOR_ID]) for v in options[CONF_DOORS]]
        if len(doors) != len(set(doors)):
            raise ValueError(ERR_DUPLICATE_DOOR_IDS)


def validate_card_id(name):
    if not name or name.strip() == '':
        raise ValueError(ERR_INVALID_CARD_ID)


def validate_all_cards(options):
    pass


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


def get_all_doors(options):
    controllers = []

    def lookup(controller, door):
        for v in options[CONF_DOORS]:
            if v[CONF_DOOR_CONTROLLER] == controller and int(f'{v[CONF_DOOR_NUMBER]}') == int(f'{door}'):
                return v[CONF_DOOR_ID]
        return None

    if CONF_CONTROLLERS in options:
        for v in options[CONF_CONTROLLERS]:
            controller = v[CONF_CONTROLLER_ID]
            serial_no = v[CONF_CONTROLLER_SERIAL_NUMBER]
            doors = []

            if re.match('^[1234].*', f"{serial_no}"):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 1),
                    CONF_DOOR_NUMBER: 1,
                })

            if re.match('^[234].*', f"{serial_no}"):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 2),
                    CONF_DOOR_NUMBER: 2,
                })

            if re.match('^[34].*', f"{serial_no}"):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 3),
                    CONF_DOOR_NUMBER: 3,
                })

            if re.match('^[4].*', f"{serial_no}"):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 4),
                    CONF_DOOR_NUMBER: 4,
                })

            controllers.append({
                CONF_CONTROLLER_ID: controller,
                CONF_CONTROLLER_SERIAL_NUMBER: serial_no,
                'doors': doors,
            })

    return sorted(list(controllers), key=lambda v: v[CONF_CONTROLLER_SERIAL_NUMBER], reverse=True)


def get_all_cards(options):
    cards = dict()

    # ... get controller cards
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
                    cards[response.card_number] = {
                        CONF_CARD_NUMBER: response.card_number,
                        CONF_CARD_NAME: None,
                        CONF_CARD_STARTDATE: None,
                        CONF_CARD_ENDDATE: None,
                        CONF_CARD_DOORS: [],
                    }
                    count += 1
                    ix += 1
                except Exception as e:
                    errors += 1
                    _LOGGER.warning(f'{controller} error retrieving card at index {ix} ({e})')

        except Exception as e:
            _LOGGER.warning(f'{controller} error retrieving list of cards ({e})')

    # ... add cards from options
    if options and CONF_CARDS in options:
        for v in options[CONF_CARDS]:
            k = v[CONF_CARD_NUMBER]
            cards[k] = v

    # ... convert cards list to records

    return [cards[k] for k in sorted(cards.keys())]


def configure_controllers(options, f):
    if CONF_CONTROLLERS in options:
        controllers = options[CONF_CONTROLLERS]

        for c in controllers:
            controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
            serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
            address = f'{c[CONF_CONTROLLER_ADDR]}'.strip()

            f(controller, serial_no, address)


def configure_doors(options, g):
    if CONF_CONTROLLERS in options and CONF_DOORS in options:
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


def configure_cards(options, f):
    if CONF_CARDS in options:
        cards = options[CONF_CARDS]

        for c in cards:
            card = f'{c[CONF_CARD_NUMBER]}'.strip()
            name = f'{c[CONF_CARD_NAME]}'.strip()
            start_date = f'{c[CONF_CARD_STARTDATE]}'.strip()
            end_date = f'{c[CONF_CARD_ENDDATE]}'.strip()
            permissions = c[CONF_CARD_DOORS]

            f(card, name, start_date, end_date, permissions)
