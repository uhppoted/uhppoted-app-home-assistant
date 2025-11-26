import re
import logging
import datetime
import calendar
import socket
import uuid
import urllib
import netifaces

from typing import Any

from uhppoted import uhppote

from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_TIMEOUT
from .const import CONF_DEBUG

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_UNIQUE_ID
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_CONTROLLER_PORT
from .const import CONF_CONTROLLER_PROTOCOL
from .const import CONF_CONTROLLER_TIMEOUT

from .const import CONF_INTERLOCKS
from .const import CONF_ANTIPASSBACK

from .const import CONF_DOORS
from .const import CONF_DOOR_UNIQUE_ID
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

from .const import CONF_CARDS
from .const import CONF_CARD_UNIQUE_ID
from .const import CONF_CARD_NUMBER
from .const import CONF_CARD_NAME
from .const import CONF_CARD_STARTDATE
from .const import CONF_CARD_ENDDATE
from .const import CONF_CARD_DOORS

from .const import CONF_CACHE_ENABLED
from .const import CONF_CACHE_EXPIRY_CONTROLLER
from .const import CONF_CACHE_EXPIRY_LISTENER
from .const import CONF_CACHE_EXPIRY_DATETIME
from .const import CONF_CACHE_EXPIRY_DOOR
from .const import CONF_CACHE_EXPIRY_CARD
from .const import CONF_CACHE_EXPIRY_STATUS
from .const import CONF_CACHE_EXPIRY_INTERLOCK
from .const import CONF_CACHE_EXPIRY_ANTIPASSBACK
from .const import CONF_CACHE_EXPIRY_EVENT

from .const import DEFAULT_TIMEOUT
from .const import DEFAULT_MAX_CARDS
from .const import DEFAULT_MAX_CARD_INDEX
from .const import DEFAULT_MAX_CARD_ERRORS
from .const import DEFAULT_PREFERRED_CARDS

from .const import DEFAULT_CACHE_ENABLED
from .const import DEFAULT_CACHE_EXPIRY_CONTROLLER
from .const import DEFAULT_CACHE_EXPIRY_LISTENER
from .const import DEFAULT_CACHE_EXPIRY_DATETIME
from .const import DEFAULT_CACHE_EXPIRY_DOOR
from .const import DEFAULT_CACHE_EXPIRY_CARD
from .const import DEFAULT_CACHE_EXPIRY_STATUS
from .const import DEFAULT_CACHE_EXPIRY_INTERLOCK
from .const import DEFAULT_CACHE_EXPIRY_ANTIPASSBACK
from .const import DEFAULT_CACHE_EXPIRY_EVENT

from .const import ERR_INVALID_CONTROLLER_ID
from .const import ERR_DUPLICATE_CONTROLLER_ID
from .const import ERR_DUPLICATE_CONTROLLER_IDS
from .const import ERR_INVALID_DOOR_ID
from .const import ERR_DUPLICATE_DOOR_ID
from .const import ERR_DUPLICATE_DOOR_IDS
from .const import ERR_INVALID_CARD_ID

from .uhppoted import uhppoted
from .uhppoted import Controller

_LOGGER = logging.getLogger(__name__)


def normalise(v):
    return re.sub(r'\s+', '', f'{v}', flags=re.UNICODE).lower()


def validate_events_addr(addr):
    if addr == '':
        pass
    else:
        try:
            host, port = addr.split(':')
            socket.inet_pton(socket.AF_INET, host)
            if 0 > int(port) > 65535:
                raise ValueError(f'invalid port ({port})')
        except Exception as err:
            _LOGGER.warning(f'Invalid controller event listener address {addr} ({err}')
            raise ValueError(f'Invalid controller event listener address {addr}')


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


def get_bind_addresses():
    addresses = ['0.0.0.0']
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if addrs:
            for addr_info in addrs:
                if 'addr' in addr_info and addr_info['addr'] != '127.0.0.1':
                    addresses.append(addr_info['addr'])

    return addresses


def get_broadcast_addresses():
    addresses = ['255.255.255.255']
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if addrs:
            for addr_info in addrs:
                if 'broadcast' in addr_info:
                    addresses.append(addr_info['broadcast'])

    return addresses


def get_listen_addresses():
    addresses = ['0.0.0.0']
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if addrs:
            for addr_info in addrs:
                if 'addr' in addr_info and addr_info['addr'] != '127.0.0.1':
                    addresses.append(addr_info['addr'])

    return addresses


def get_IPv4_addresses():
    addresses = []
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if addrs:
            for addr_info in addrs:
                addresses.append(addr_info['addr'])

    return addresses


def get_all_controllers(predefined, options):
    controllers = dict()

    for v in predefined:
        serial_no = v.get('controller', 0)
        address = v.get('address', '')
        port = v.get('port', 60000)
        protocol = v.get('protocol', 'UDP')

        if serial_no > 0 and address != '':
            k = serial_no
            controllers[k] = {
                'controller': serial_no,
                'address': address,
                'port': port,
                'protocol': protocol,
            }

    if CONF_CONTROLLERS in options:
        for v in options[CONF_CONTROLLERS]:
            serial_no = int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}')
            address = v.get(CONF_CONTROLLER_ADDR, '')
            port = v.get(CONF_CONTROLLER_PORT, 60000)
            protocol = v.get(CONF_CONTROLLER_PROTOCOL, 'UDP')
            k = serial_no
            controllers[k] = {
                'controller': serial_no,
                'address': address,
                'port': port,
                'protocol': protocol,
            }

    try:
        bind = options[CONF_BIND_ADDR]
        broadcast = options[CONF_BROADCAST_ADDR]
        listen = options[CONF_LISTEN_ADDR]
        debug = options[CONF_DEBUG]

        response = uhppoted.get_all_controllers(bind, broadcast, listen, debug)

        for v in response:
            protocol = 'UDP'
            if v.controller in controllers:
                protocol = controllers[v.controller].get('protocol', protocol)

            controllers[v.controller] = {
                'controller': v.controller,
                'address': f'{v.ip_address}',
                'port': 60000,
                'protocol': protocol,
            }

    except Exception as e:
        _LOGGER.exception(f'error retrieving list of controllers ({e})')

    return sorted(controllers.values(), key=lambda v: v['controller'], reverse=True)


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

            if re.match('^[1-9].*', f'{serial_no}'):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 1),
                    CONF_DOOR_NUMBER: 1,
                })

            if re.match('^[2-9].*', f'{serial_no}'):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 2),
                    CONF_DOOR_NUMBER: 2,
                })

            if re.match('^[3-9].*', f'{serial_no}'):
                doors.append({
                    CONF_DOOR_ID: lookup(controller, 3),
                    CONF_DOOR_NUMBER: 3,
                })

            if re.match('^[4-9].*', f'{serial_no}'):
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


async def get_all_cards(options, max_cards=DEFAULT_MAX_CARDS, preferred_cards=DEFAULT_PREFERRED_CARDS):
    cards = dict()
    u = configure_driver(options)

    # ... build 'preferred' cards list
    preferred = set()
    if preferred_cards:
        if isinstance(preferred_cards, list):
            preferred = {int(f'{v}') for v in preferred_cards}
        elif isinstance(preferred_cards, str):
            preferred = {int(v) for v in re.findall(r'[0-9]+', f'{preferred_cards}')}

    # ... get preferred cards
    for controller in u.controllers:
        for card in sorted(list(preferred)):
            try:
                if response := await u.get_card(controller, card):
                    if response.card_number == card:
                        cards[response.card_number] = {
                            CONF_CARD_NUMBER: response.card_number,
                            CONF_CARD_UNIQUE_ID: uuid.uuid4(),
                            CONF_CARD_NAME: None,
                        }
            except Exception as e:
                _LOGGER.warning(f'{controller} error retrieving preferred card {card} ({e})')

    # ... get controller cards
    for controller in u.controllers:
        try:
            response = await u.get_cards(controller)
            _LOGGER.info(f'{controller}: {response.cards} cards')

            N = min(response.cards, max_cards)
            ix = 1
            count = 0
            errors = 0

            while count < N and ix < DEFAULT_MAX_CARD_INDEX and len(cards) < max_cards and errors < DEFAULT_MAX_CARD_ERRORS: # yapf: disable
                try:
                    response = await u.get_card_by_index(controller, ix)
                    cards[response.card_number] = {
                        CONF_CARD_NUMBER: response.card_number,
                        CONF_CARD_UNIQUE_ID: uuid.uuid4(),
                        CONF_CARD_NAME: None,
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
            k = int(f'{v[CONF_CARD_NUMBER]}')
            cards[k] = v

    # ... convert cards list to records

    return [cards[k] for k in sorted(cards.keys())]


def get_card(card_number, options):
    if options and CONF_CARDS in options:
        for v in options[CONF_CARDS]:
            if int(f'{v[CONF_CARD_NUMBER]}') == int(f'{card_number}'):
                return v

    return {
        CONF_CARD_NUMBER: int(f'{card_number}'),
        CONF_CARD_UNIQUE_ID: uuid.uuid4(),
        CONF_CARD_NAME: f'{card_number}',
    }


def configure_controllers(options, f):
    if CONF_CONTROLLERS in options:
        controllers = options[CONF_CONTROLLERS]

        for c in controllers:
            unique_id = f'{c[CONF_CONTROLLER_UNIQUE_ID]}'.strip()
            controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
            serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
            address = f'{c[CONF_CONTROLLER_ADDR]}'.strip()

            f(unique_id, controller, serial_no, address)


def configure_doors(options, g):
    if CONF_CONTROLLERS in options and CONF_DOORS in options:
        controllers = options[CONF_CONTROLLERS]
        doors = options[CONF_DOORS]

        for c in controllers:
            controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
            serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
            address = f'{c[CONF_CONTROLLER_ADDR]}'.strip()

            for d in doors:
                unique_id = f'{d[CONF_DOOR_UNIQUE_ID]}'.strip()
                door = f'{d[CONF_DOOR_ID]}'.strip()
                door_no = f'{d[CONF_DOOR_NUMBER]}'.strip()
                door_controller = f'{d[CONF_DOOR_CONTROLLER]}'.strip()

                if door_controller == controller:
                    g(unique_id, controller, serial_no, door, door_no)


def configure_cards(options, f):
    if CONF_CARDS in options:
        cards = options[CONF_CARDS]
        for c in cards:
            card = f'{c[CONF_CARD_NUMBER]}'.strip()
            name = f'{c[CONF_CARD_NAME]}'.strip()
            unique_id = f'{c[CONF_CARD_UNIQUE_ID]}'.strip()

            f(card, name, unique_id)


def configure_driver(options, defaults={}):
    bind = options[CONF_BIND_ADDR]
    broadcast = options[CONF_BROADCAST_ADDR]
    listen = options[CONF_LISTEN_ADDR]
    debug = options[CONF_DEBUG]

    # NTS: timeout is not configured in either config-flow or options-flow
    # timeout = options.get(CONF_TIMEOUT, defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
    timeout = defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    timeouts = dict([[v['controller'], v.get('timeout', timeout)] for v in defaults.get(CONF_CONTROLLERS, [])])

    def f(v):
        controller = int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}')
        address = f'{v[CONF_CONTROLLER_ADDR]}'
        port = int(f'{v.get(CONF_CONTROLLER_PORT,60000)}')
        protocol = f"{v.get(CONF_CONTROLLER_PROTOCOL,'UDP')}"

        return {
            'controller': controller,
            'address': address,
            'port': port,
            'protocol': protocol,
            'timeout': timeouts.get(controller, timeout),
        }

    if CONF_CONTROLLERS in options:
        controllers = [f(v) for v in options[CONF_CONTROLLERS]]
    else:
        controllers = []

    driver = uhppoted(bind, broadcast, listen, controllers, timeout, debug)

    driver.cache_enabled = defaults.get(CONF_CACHE_ENABLED, DEFAULT_CACHE_ENABLED)
    driver.cache_expiry = {
        CONF_CACHE_EXPIRY_CONTROLLER: defaults.get(CONF_CACHE_EXPIRY_CONTROLLER, DEFAULT_CACHE_EXPIRY_CONTROLLER),
        CONF_CACHE_EXPIRY_LISTENER: defaults.get(CONF_CACHE_EXPIRY_LISTENER, DEFAULT_CACHE_EXPIRY_LISTENER),
        CONF_CACHE_EXPIRY_DATETIME: defaults.get(CONF_CACHE_EXPIRY_DATETIME, DEFAULT_CACHE_EXPIRY_DATETIME),
        CONF_CACHE_EXPIRY_DOOR: defaults.get(CONF_CACHE_EXPIRY_DOOR, DEFAULT_CACHE_EXPIRY_DOOR),
        CONF_CACHE_EXPIRY_CARD: defaults.get(CONF_CACHE_EXPIRY_CARD, DEFAULT_CACHE_EXPIRY_CARD),
        CONF_CACHE_EXPIRY_STATUS: defaults.get(CONF_CACHE_EXPIRY_STATUS, DEFAULT_CACHE_EXPIRY_STATUS),
        CONF_CACHE_EXPIRY_INTERLOCK: defaults.get(CONF_CACHE_EXPIRY_INTERLOCK, DEFAULT_CACHE_EXPIRY_INTERLOCK),
        CONF_CACHE_EXPIRY_ANTIPASSBACK: defaults.get(CONF_CACHE_EXPIRY_ANTIPASSBACK, DEFAULT_CACHE_EXPIRY_ANTIPASSBACK),
        CONF_CACHE_EXPIRY_EVENT: defaults.get(CONF_CACHE_EXPIRY_EVENT, DEFAULT_CACHE_EXPIRY_EVENT),
    }

    return driver


def configure_interlocks(options, g):
    interlocks = options.get(CONF_INTERLOCKS, False)
    controllers = options[CONF_CONTROLLERS]

    if interlocks:
        for c in controllers:
            controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
            serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
            unique_id = f'{c.get("controller_unique_id")}.interlock'.strip()

            g(unique_id, controller, serial_no)


def configure_antipassback(options, g):
    antipassback = options.get(CONF_ANTIPASSBACK, False)
    controllers = options[CONF_CONTROLLERS]

    if antipassback:
        for c in controllers:
            controller = f'{c[CONF_CONTROLLER_ID]}'.strip()
            serial_no = f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}'.strip()
            unique_id = f'{c.get("controller_unique_id")}.antipassback'.strip()

            g(unique_id, controller, serial_no)


def default_card_start_date():
    return datetime.date.today()


def default_card_end_date():
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=180)
    year = end_date.year
    month = end_date.month
    day = calendar.monthrange(end_date.year, end_date.month)[1]

    return datetime.date(year, month, day)


def get_configured_controllers(options):
    if CONF_CONTROLLERS in options:
        return [int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') for v in options[CONF_CONTROLLERS]]
    else:
        return []


def get_configured_controllers_ext(options):

    def g(v):
        id = int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}')
        address = v.get(CONF_CONTROLLER_ADDR, '')
        port = int(f'{v.get(CONF_CONTROLLER_PORT,60000)}')
        addr = f'{address}:{port}'
        protocol = v.get(CONF_CONTROLLER_PROTOCOL, 'UDP')

        return Controller(id, addr, protocol)

    return [g(v) for v in options.get(CONF_CONTROLLERS, [])]


def get_configured_doors(options):
    if CONF_DOORS in options:
        return [v[CONF_DOOR_UNIQUE_ID] for v in options[CONF_DOORS]]
    else:
        return []


def get_configured_cards(options):
    if CONF_CARDS in options:
        return [int(f'{v[CONF_CARD_NUMBER]}') for v in options[CONF_CARDS]]
    else:
        return []


def resolve_permissions(options, acl):
    controllers = options[CONF_CONTROLLERS]
    doors = options[CONF_DOORS]
    permissions = set()

    for u in controllers:
        controller = u[CONF_CONTROLLER_ID]
        serial_no = int(f'{u[CONF_CONTROLLER_SERIAL_NUMBER]}')
        if serial_no in acl:
            for d in doors:
                door = d[CONF_DOOR_ID]
                door_no = int(f'{d[CONF_DOOR_NUMBER]}')
                if d[CONF_DOOR_CONTROLLER] == controller and door_no in acl[serial_no]:
                    permissions.add(door)

    return sorted(list(permissions))


def resolve_door(options, unique_id):
    if CONF_CONTROLLERS in options and CONF_DOORS in options:
        controllers = options[CONF_CONTROLLERS]
        doors = options[CONF_DOORS]

        for door in doors:
            if door[CONF_DOOR_UNIQUE_ID] == unique_id:
                for controller in controllers:
                    if controller[CONF_CONTROLLER_ID] == door[CONF_DOOR_CONTROLLER]:
                        return {
                            CONF_DOOR_ID: door[CONF_DOOR_ID],
                            CONF_CONTROLLER_SERIAL_NUMBER: int(f'{controller[CONF_CONTROLLER_SERIAL_NUMBER]}'),
                            CONF_DOOR_NUMBER: door[CONF_DOOR_NUMBER],
                        }

    return None


def resolve_door_by_name(options, name):

    def normalise(v):
        return re.sub('[^a-zA-z0-9]', '', f'{v}'.strip().lower())

    if CONF_CONTROLLERS in options and CONF_DOORS in options:
        controllers = options[CONF_CONTROLLERS]
        doors = options[CONF_DOORS]

        for door in doors:
            if normalise(door[CONF_DOOR_ID]) == normalise(name):
                for controller in controllers:
                    if controller[CONF_CONTROLLER_ID] == door[CONF_DOOR_CONTROLLER]:
                        return {
                            CONF_DOOR_ID: door[CONF_DOOR_ID],
                            CONF_CONTROLLER_SERIAL_NUMBER: int(f'{controller[CONF_CONTROLLER_SERIAL_NUMBER]}'),
                            CONF_DOOR_NUMBER: door[CONF_DOOR_NUMBER],
                        }

    return None


def resolve_door_by_id(options, controller_id, door_id):
    if CONF_CONTROLLERS in options and CONF_DOORS in options:
        controllers = options[CONF_CONTROLLERS]
        doors = options[CONF_DOORS]

        for controller in controllers:
            if controller['controller_serial_number'] == f'{controller_id}':
                for door in doors:
                    if door['door_controller'] == controller['controller_id'] and door['door_number'] == door_id:
                        return door

    return None
