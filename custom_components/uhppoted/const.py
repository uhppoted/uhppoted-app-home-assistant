"""Constants for the uhppoted integration."""

DOMAIN = 'uhppoted'

CONF_BIND_ADDR = 'bind_address'
CONF_BROADCAST_ADDR = 'broadcast_address'
CONF_LISTEN_ADDR = 'listen_address'
CONF_EVENTS_DEST_ADDR = 'events_destination_address'
CONF_TIMEZONE = 'timezone'
CONF_TIMEOUT = 'timeout'
CONF_DEBUG = 'debug'

CONF_MAX_CARDS = 'max_cards'
CONF_PREFERRED_CARDS = 'preferred_cards'
CONF_PIN_ENABLED = 'card_PINs'
CONF_POLL_CONTROLLERS = 'controllers_poll_interval'
CONF_POLL_DOORS = 'doors_poll_interval'
CONF_POLL_CARDS = 'cards_poll_interval'
CONF_POLL_EVENTS = 'events_poll_interval'

CONF_CONTROLLERS = 'controllers'
CONF_CONTROLLER_UNIQUE_ID = 'controller_unique_id'
CONF_CONTROLLER_ID = 'controller_id'
CONF_CONTROLLER_SERIAL_NUMBER = 'controller_serial_number'
CONF_CONTROLLER_ADDR = 'controller_address'
CONF_CONTROLLER_PORT = 'controller_port'
CONF_CONTROLLER_PROTOCOL = 'controller_protocol'
CONF_CONTROLLER_TIMEZONE = 'controller_timezone'
CONF_CONTROLLER_TIMEOUT = 'controller_timeout'

# controller opt-ins
CONF_CONTROLLERS_OPTINS = 'controllers_optins'
CONF_INTERLOCKS = 'interlocks'
CONF_ANTIPASSBACK = 'antipassback'
CONF_INTERLOCKS_UNIQUE_ID = 'interlocks_unique_id'
CONF_ANTIPASSBACK_UNIQUE_ID = 'antipassback_unique_id'

CONF_DOORS = 'doors'
CONF_DOOR_UNIQUE_ID = 'door_unique_id'
CONF_DOOR_ID = 'door_id'
CONF_DOOR_CONTROLLER = 'door_controller'
CONF_DOOR_NUMBER = 'door_number'

CONF_CARDS = 'cards'
CONF_CARD_UNIQUE_ID = 'card_unique_id'
CONF_CARD_NUMBER = 'card_number'
CONF_CARD_NAME = 'card_name'
CONF_CARD_STARTDATE = 'card_startdate'
CONF_CARD_ENDDATE = 'card_enddate'
CONF_CARD_DOORS = 'card_doors'

# cache expiry
CONF_CACHE_EXPIRY_CONTROLLER = 'cache.expiry.controller'
CONF_CACHE_EXPIRY_LISTENER = 'cache.expiry.listener'
CONF_CACHE_EXPIRY_DATETIME = 'cache.expiry.datetime'
CONF_CACHE_EXPIRY_DOOR = 'cache.expiry.door'
CONF_CACHE_EXPIRY_CARD = 'cache.expiry.card'
CONF_CACHE_EXPIRY_STATUS = 'cache.expiry.status'
CONF_CACHE_EXPIRY_INTERLOCK = 'cache.expiry.interlock'
CONF_CACHE_EXPIRY_ANTIPASSBACK = 'cache.expiry.antipassback'
CONF_CACHE_EXPIRY_EVENT = 'cache.expiry.event'

ATTR_AVAILABLE = 'available'
ATTR_NETMASK = 'netmask'
ATTR_GATEWAY = 'gateway'
ATTR_FIRMWARE = 'firmware'

ATTR_CONTROLLER = 'controller'
ATTR_CONTROLLER_SERIAL_NUMBER = 'serial_no'
ATTR_CONTROLLER_ADDRESS = 'address'
ATTR_CONTROLLER_PROTOCOL = 'protocol'
ATTR_CONTROLLER_DATETIME = 'date-time'
ATTR_CONTROLLER_LISTENER = 'event_listener'
ATTR_CONTROLLER_INTERLOCK = 'interlock'
ATTR_CONTROLLER_INTERLOCK_SETTING = 'interlock_setting'
ATTR_CONTROLLER_ANTIPASSBACK = 'antipassback'

ATTR_DOORS = 'doors'
ATTR_DOOR = 'door'
ATTR_DOOR_CONTROLLER = 'controller'
ATTR_DOOR_NUMBER = 'door'
ATTR_DOOR_OPEN = 'door_open'
ATTR_DOOR_BUTTON = 'door_button'
ATTR_DOOR_LOCK = 'door_lock'
ATTR_DOOR_MODE = 'door_mode'
ATTR_DOOR_DELAY = 'door_delay'

ATTR_CARDS = 'cards'
ATTR_CARD = 'card'
ATTR_CARD_HOLDER = 'cardholder'
ATTR_CARD_STARTDATE = 'start_date'
ATTR_CARD_ENDDATE = 'end_date'
ATTR_CARD_PERMISSIONS = 'permissions'
ATTR_CARD_PIN = 'PIN'

ATTR_EVENTS = 'events'
ATTR_STATUS = 'status'

DEFAULT_BIND_ADDRESS = '0.0.0.0'
DEFAULT_BROADCAST_ADDRESS = '255.255.255.255:60000'
DEFAULT_LISTEN_ADDRESS = '0.0.0.0:60001'
DEFAULT_EVENTS_DEST_ADDR = ''
DEFAULT_TIMEOUT = 2.5  # seconds
DEFAULT_DEBUG = False

DEFAULT_POLL_CONTROLLERS = 30  # seconds
DEFAULT_POLL_DOORS = 30  # seconds
DEFAULT_POLL_CARDS = 30  # seconds
DEFAULT_POLL_EVENTS = 30  # seconds

DEFAULT_CONTROLLER_ID = ''
DEFAULT_CONTROLLER_ADDR = ''
DEFAULT_CONTROLLER_TIMEZONE = 'LOCAL'

DEFAULT_INTERLOCKS = False
DEFAULT_ANTIPASSBACK = False

DEFAULT_DOOR1 = ''
DEFAULT_DOOR2 = ''
DEFAULT_DOOR3 = ''
DEFAULT_DOOR4 = ''

DEFAULT_MAX_CARDS = 10
DEFAULT_MAX_CARD_INDEX = 20000
DEFAULT_MAX_CARD_ERRORS = 5
DEFAULT_PREFERRED_CARDS = []

DEFAULT_CACHE_EXPIRY_CONTROLLER = 300  # 5 minutes
DEFAULT_CACHE_EXPIRY_LISTENER = 600  # 10 minutes
DEFAULT_CACHE_EXPIRY_DATETIME = 300  # 5 minutes
DEFAULT_CACHE_EXPIRY_DOOR = 600  # 10 minutes
DEFAULT_CACHE_EXPIRY_CARD = 900  # 15 minutes
DEFAULT_CACHE_EXPIRY_STATUS = 120  # 2 minutes
DEFAULT_CACHE_EXPIRY_INTERLOCK = 900  # 15 minutes
DEFAULT_CACHE_EXPIRY_ANTIPASSBACK = 900  # 15 minutes
DEFAULT_CACHE_EXPIRY_EVENT = 1800  # 30 minutes

ERR_INVALID_CONTROLLER_ID = 'invalid_controller_id'
ERR_DUPLICATE_CONTROLLER_ID = 'duplicate_controller_id'
ERR_DUPLICATE_CONTROLLER_IDS = 'duplicate_controller_ids'
ERR_INVALID_DOOR_ID = 'invalid_door_id'
ERR_DUPLICATE_DOOR_ID = 'duplicate_door_id'
ERR_DUPLICATE_DOOR_IDS = 'duplicate_door_ids'
ERR_INVALID_CARD_ID = 'invalid_card_id'

EVENT_REASON_DOOR_LOCKED = 256
EVENT_REASON_DOOR_UNLOCKED = 257
EVENT_REASON_BUTTON_RELEASED = 258

EVENTS = {
    1: 'Card swipe',
    2: 'Event #2',
    3: 'Event #3',
    4: 'Event #4',
    5: 'Swipe: access denied (PC control)',
    6: 'Swipe: access denied (not allowed)',
    7: 'Swipe: access denied (invalid password)',
    8: 'Swipe: access denied (anti-passback)',
    9: 'Swipe: access denied (more cards)',
    10: 'Swipe: access denied (first card open)',
    11: 'Swipe: access denied (normally closed)',
    12: 'Swipe: access denied (interlock)',
    13: 'Swipe: access denied (time profile)',
    14: 'Event #14',
    15: 'Swipe: access denied (invalid timezone)',
    16: 'Event #16',
    17: 'Event #17',
    18: 'Swipe: access denied',
    19: 'Event #18',
    20: 'Push Button',
    21: 'Event #21',
    22: 'Event #22',
    23: 'Door open',
    24: 'Door closed',
    25: 'Supervisor passcode override',
    26: 'Event #26',
    27: 'Event #27',
    28: 'Power On',
    29: 'Controller reset',
    30: 'Push Button: disabled by task',
    31: 'Push Button: forced lock',
    32: 'Push Button: offline',
    33: 'Push Button: interLock',
    34: 'Threat',
    35: 'Event #35',
    36: 'Event #36',
    37: 'Door open too long',
    38: 'Door forced open',
    39: 'Fire',
    40: 'Dopor forced close',
    41: 'Tamper alert',
    42: '7x24Hour Zone',
    43: 'Emergency call',
    44: 'Remote open door',
    45: 'Remote open door (USB reader)',
    EVENT_REASON_DOOR_LOCKED: 'Door locked',  # synthesized event
    EVENT_REASON_DOOR_UNLOCKED: 'Door unlocked',  # synthesized event
}

CARD_EVENTS = {
    1: 'Access Granted',
    5: 'Access Denied (PC control)',
    6: 'Access Denied (not allowed)',
    7: 'Access Denied (invalid password)',
    8: 'Access Denied (anti-passback)',
    9: 'Access Denied (more cards)',
    10: 'Access Denied (first card open)',
    11: 'Access Denied (normally closed)',
    12: 'Access Denied (interlock)',
    13: 'Access Denied (time profile)',
    15: 'Access Denied (invalid timezone)',
    18: 'Access Denied',
}
