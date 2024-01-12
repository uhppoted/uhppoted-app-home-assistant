"""Constants for the uhppoted integration."""

DOMAIN = 'uhppoted'

CONF_BIND_ADDR = 'bind_address'
CONF_BROADCAST_ADDR = 'broadcast_address'
CONF_LISTEN_ADDR = 'listen_address'
CONF_DEBUG = 'debug'

CONF_CONTROLLERS = 'controllers'
CONF_CONTROLLER_ID = 'controller_id'
CONF_CONTROLLER_SERIAL_NUMBER = 'controller_serial_number'
CONF_CONTROLLER_ADDR = 'controller_address'
CONF_CONTROLLER_TIMEZONE = 'controller_timezone'

CONF_DOORS = 'doors'
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

ATTR_ADDRESS = 'address'
ATTR_NETMASK = 'netmask'
ATTR_GATEWAY = 'gateway'
ATTR_FIRMWARE = 'firmware'

ATTR_CONTROLLER_SERIAL_NUMBER = 'serial_no'

ATTR_DOOR_CONTROLLER = 'controller'
ATTR_DOOR_NUMBER = 'door'

ATTR_CARD_HOLDER = 'cardholder'
ATTR_CARD_STARTDATE = 'start_date'
ATTR_CARD_ENDDATE = 'end_date'
ATTR_CARD_PERMISSIONS = 'permissions'

DEFAULT_CONTROLLER_ID = 'Alpha'
DEFAULT_CONTROLLER_ADDR = '192.168.1.100'
DEFAULT_CONTROLLER_TIMEZONE = 'LOCAL'

DEFAULT_DOOR1 = 'Gryffindor'
DEFAULT_DOOR2 = 'Ravenclaw'
DEFAULT_DOOR3 = 'Hufflepuff'
DEFAULT_DOOR4 = 'Slytherin'

ERR_INVALID_CONTROLLER_ID = 'invalid_controller_id'
ERR_DUPLICATE_CONTROLLER_ID = 'duplicate_controller_id'
ERR_DUPLICATE_CONTROLLER_IDS = 'duplicate_controller_ids'
ERR_INVALID_DOOR_ID = 'invalid_door_id'
ERR_DUPLICATE_DOOR_ID = 'duplicate_door_id'
ERR_DUPLICATE_DOOR_IDS = 'duplicate_door_ids'
ERR_INVALID_CARD_ID = 'invalid_card_id'
