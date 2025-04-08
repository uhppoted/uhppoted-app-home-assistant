from dataclasses import dataclass

import logging

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER

from .const import CONF_DOORS
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

from .const import CONF_CARDS
from .const import CONF_CARD_NUMBER
from .const import CONF_CARD_NAME


@dataclass
class Controller:
    controller: int
    name: str


@dataclass
class Card:
    card: int
    name: str


@dataclass
class Door:
    door: int
    name: str


@dataclass
class Event:
    reason: str


_REASONS = {
    '1': 'swipe valid',
    '2': 'swipe open',
    '3': 'swipe close',
    '5': 'swipe:denied (system)',
    '6': 'no access rights',
    '7': 'incorrect password',
    '8': 'anti-passback',
    '9': 'more cards',
    '10': 'first card open',
    '11': 'door is normally closed',
    '12': 'interlock',
    '13': 'not in allowed time period',
    '15': 'invalid timezone',
    '18': 'access denied',
    '20': 'push button ok',
    '23': 'door opened',
    '24': 'door closed',
    '25': 'door opened (supervisor password)',
    '28': 'controller power on',
    '29': 'controller reset',
    '31': 'pushbutton invalid (door locked)',
    '32': 'pushbutton invalid (offline)',
    '33': 'pushbutton invalid (interlock)',
    '34': 'pushbutton invalid (threat)',
    '37': 'door open too long',
    '38': 'forced open',
    '39': 'fire',
    '40': 'forced closed',
    '41': 'theft prevention',
    '42': '24x7 zone',
    '43': 'emergency',
    '44': 'remote open door',
    '45': 'remote open door (USB reader)',
}

_LOGGER = logging.getLogger(__name__)


def lookup_controller(options, controller):
    if CONF_CONTROLLERS in options:
        controllers = options[CONF_CONTROLLERS]
        for c in controllers:
            if f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}' == f'{controller}':
                name = f'{c[CONF_CONTROLLER_ID]}'
                return Controller(controller, name)

    return None


def lookup_door(options, key):
    if CONF_CONTROLLERS in options and CONF_DOORS in options:
        controllers = options[CONF_CONTROLLERS]
        doors = options[CONF_DOORS]

        for controller in controllers:
            if f'{key}'.startswith(f'{controller[CONF_CONTROLLER_SERIAL_NUMBER]}.'):
                for d in doors:
                    if f'{d[CONF_DOOR_CONTROLLER]}' == f'{controller[CONF_CONTROLLER_ID]}':
                        if f'{controller[CONF_CONTROLLER_SERIAL_NUMBER]}.{d[CONF_DOOR_NUMBER]}' == f'{key}':
                            door = d[CONF_DOOR_NUMBER]
                            name = f'{d[CONF_DOOR_ID]}'
                            return Door(door, name)

    return None


def lookup_card(options, card):
    if CONF_CARDS in options:
        cards = options[CONF_CARDS]

        for c in cards:
            if f'{c[CONF_CARD_NUMBER]}' == f'{card}':
                name = f'{c[CONF_CARD_NAME]}'
                return Card(card, name)

    return None


def lookup_event(options, code):
    reason = _REASONS.get(f'{code}', '(unknown)')

    return Event(reason)
