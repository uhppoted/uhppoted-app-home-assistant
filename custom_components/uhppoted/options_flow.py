import logging
import uuid
import voluptuous as vol

from copy import deepcopy
from typing import Any
from typing import Dict
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import OptionsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import SelectSelector
from homeassistant.helpers.selector import SelectSelectorConfig
from homeassistant.helpers.selector import SelectSelectorMode
from homeassistant.const import __version__ as HAVERSION

from awesomeversion import AwesomeVersion

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_EVENTS_DEST_ADDR
from .const import CONF_DEBUG
from .const import CONF_TIMEZONE
from .const import CONF_TIMEOUT

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_UNIQUE_ID
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_CONTROLLER_PORT
from .const import CONF_CONTROLLER_TIMEZONE

from .const import CONF_DOORS
from .const import CONF_DOOR_UNIQUE_ID
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

from .const import CONF_MAX_CARDS
from .const import CONF_PREFERRED_CARDS
from .const import CONF_CARDS
from .const import CONF_CARD_UNIQUE_ID
from .const import CONF_CARD_NUMBER
from .const import CONF_CARD_NAME
from .const import CONF_CARD_STARTDATE
from .const import CONF_CARD_ENDDATE
from .const import CONF_CARD_DOORS

from .const import DEFAULT_BIND_ADDRESS
from .const import DEFAULT_BROADCAST_ADDRESS
from .const import DEFAULT_LISTEN_ADDRESS
from .const import DEFAULT_EVENTS_DEST_ADDR
from .const import DEFAULT_TIMEOUT
from .const import DEFAULT_DEBUG

from .const import DEFAULT_CONTROLLER_ID
from .const import DEFAULT_CONTROLLER_ADDR
from .const import DEFAULT_CONTROLLER_TIMEZONE

from .const import DEFAULT_DOOR1
from .const import DEFAULT_DOOR2
from .const import DEFAULT_DOOR3
from .const import DEFAULT_DOOR4

from .const import DEFAULT_MAX_CARDS
from .const import DEFAULT_PREFERRED_CARDS

from .config import validate_events_addr
from .config import validate_controller_id
from .config import validate_door_duplicates
from .config import validate_door_id
from .config import validate_card_id
from .config import validate_all_controllers
from .config import validate_all_doors
from .config import validate_all_cards

from .config import get_bind_addresses
from .config import get_broadcast_addresses
from .config import get_listen_addresses
from .config import get_IPv4_addresses
from .config import get_all_doors
from .config import get_all_cards
from .config import get_card

from .flow import UhppotedFlow

_LOGGER = logging.getLogger(__name__)


class UhppotedOptionsFlow(UhppotedFlow, OptionsFlow):

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__()

        self._bind = DEFAULT_BIND_ADDRESS
        self._broadcast = DEFAULT_BROADCAST_ADDRESS
        self._listen = DEFAULT_LISTEN_ADDRESS
        self._events_dest_addr = DEFAULT_EVENTS_DEST_ADDR
        self._debug = DEFAULT_DEBUG
        self._timezone = DEFAULT_CONTROLLER_TIMEZONE
        self._timeout = DEFAULT_TIMEOUT
        self._max_cards = DEFAULT_MAX_CARDS
        self._preferred_cards = DEFAULT_PREFERRED_CARDS

        if AwesomeVersion(HAVERSION) < '2024.11.99':
            self.config_entry = config_entry

        self.data = dict(entry.data)
        self.options = deepcopy(dict(entry.options))
        self.doors = []
        self.configuration = {'doors': []}
        self.cache = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        defaults = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}

        super().initialise(defaults)

        self._bind = defaults.get(CONF_BIND_ADDR, self._bind)
        self._broadcast = defaults.get(CONF_BROADCAST_ADDR, self._broadcast)
        self._listen = defaults.get(CONF_LISTEN_ADDR, self._listen)
        self._events_dest_addr = defaults.get(CONF_EVENTS_DEST_ADDR, self._events_dest_addr)
        self._debug = defaults.get(CONF_DEBUG, self._debug)
        self._timezone = defaults.get(CONF_TIMEZONE, DEFAULT_CONTROLLER_TIMEZONE)
        self._timeout = defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        self._max_cards = defaults.get(CONF_MAX_CARDS, DEFAULT_MAX_CARDS)
        self._preferred_cards = defaults.get(CONF_PREFERRED_CARDS, DEFAULT_PREFERRED_CARDS)

        self.options.update({
            CONF_TIMEOUT: self._timeout,
        })

        return self.async_show_menu(step_id="init",
                                    menu_options=['IPv4', 'controllers', 'doors', 'cards'],
                                    description_placeholders={})

    async def async_step_IPv4(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.options.update(user_input)
                return await self.async_step_events_listener()

        bind = self.options.get(CONF_BIND_ADDR, self._bind)
        broadcast = self.options.get(CONF_BROADCAST_ADDR, self._broadcast)
        listen = self.options.get(CONF_LISTEN_ADDR, self._listen)
        debug = self.options.get(CONF_DEBUG, self._debug)

        binds = SelectSelectorConfig(options=[{ 'label': f'{v}', 'value': f'{v}' } for v in get_bind_addresses()],
                                     multiple=False,
                                     custom_value=True,
                                     mode=SelectSelectorMode.LIST) # yapf: disable

        broadcasts = SelectSelectorConfig(options=[{ 'label': f'{v}:60000', 'value': f'{v}:60000' } for v in get_broadcast_addresses()],
                                          multiple=False,
                                          custom_value=True,
                                          mode=SelectSelectorMode.LIST) # yapf: disable

        listens = SelectSelectorConfig(options=[{ 'label': f'{v}:60001', 'value': f'{v}:60001' } for v in get_listen_addresses()],
                                       multiple=False,
                                       custom_value=True,
                                       mode=SelectSelectorMode.LIST) # yapf: disable

        schema = vol.Schema({
            vol.Optional(CONF_BIND_ADDR, default=bind): SelectSelector(binds),
            vol.Optional(CONF_BROADCAST_ADDR, default=broadcast): SelectSelector(broadcasts),
            vol.Optional(CONF_LISTEN_ADDR, default=listen): SelectSelector(listens),
            vol.Optional(CONF_DEBUG, default=debug): bool,
        })

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_step_events_listener(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            address = user_input.get(CONF_EVENTS_DEST_ADDR, '')

            try:
                validate_events_addr(address)
            except ValueError as err:
                errors[CONF_EVENTS_DEST_ADDR] = f'{err}'

            if not errors:
                self.options.update([[CONF_EVENTS_DEST_ADDR, address]])

                return await self.async_step_controllers()

        addr = self.options.get(CONF_EVENTS_DEST_ADDR, self._events_dest_addr)
        addresses = [v for v in get_IPv4_addresses() if v != '127.0.0.1']

        select = SelectSelectorConfig(options=[{ 'label': f'{v}:60001', 'value': f'{v}:60001' } for v in addresses],
                                      multiple=False,
                                      custom_value=True,
                                      mode=SelectSelectorMode.LIST) # yapf: disable

        schema = vol.Schema({
            vol.Optional(CONF_EVENTS_DEST_ADDR, default=addr): SelectSelector(select),
        })

        return self.async_show_form(step_id="events_listener", data_schema=schema, errors=errors)

    async def async_step_controllers(self, user_input: Optional[Dict[str, Any]] = None):
        controllers = self._get_all_controllers(self.options)
        if len(controllers) < 1:
            return await self.async_step_door()

        self.cache['controllers'] = controllers

        configured = set()
        if self.options and CONF_CONTROLLERS in self.options:
            for v in self.options[CONF_CONTROLLERS]:
                configured.add(int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}'))

        configured = sorted(list(configured), reverse=True)

        (schema, placeholders, errors) = super().step_controllers(controllers, configured, self.options, user_input,
                                                                  self.cache)

        # NTS: errors are for display only
        if user_input is None:
            return self.async_show_form(step_id="controllers",
                                        data_schema=schema,
                                        errors=errors,
                                        description_placeholders=placeholders)
        else:
            return await self.async_step_controller()

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        it = next((v for v in self._controllers if not v['controller']['configured']), None)
        if it == None:
            try:
                validate_all_controllers(self.options)
                return await self.async_step_doors()
            except ValueError as err:
                return await self.async_step_controllers()
        else:
            controller = it['controller']

            (schema, placeholders, errors) = super().step_controller(controller, self.options, user_input)

            if user_input is None or errors:
                return self.async_show_form(step_id="controller",
                                            data_schema=schema,
                                            errors=errors,
                                            description_placeholders=placeholders)
            else:
                return await self.async_step_controller()

    async def async_step_doors(self, user_input: Optional[Dict[str, Any]] = None):

        def f(v):
            return v[CONF_CONTROLLER_ID] in [u['controller'] for u in self.configuration['doors']]

        def g(d):
            door = d[CONF_DOOR_ID]
            no = d[CONF_DOOR_NUMBER]
            return {
                'label': f'Door {no} ({door})' if door else f'Door {no}',
                'value': f'{no}',
            }

        all_doors = get_all_doors(self.options)
        it = next((v for v in all_doors if not f(v)), None)
        if it == None:
            return await self.async_step_door()
        else:
            controller = it[CONF_CONTROLLER_ID]
            serial_no = it[CONF_CONTROLLER_SERIAL_NUMBER]
            doors = it['doors']

        errors: Dict[str, str] = {}
        try:
            validate_all_doors(self.options)
        except ValueError as err:
            errors['base'] = f'{err}'

        if user_input is not None:
            self.configuration['doors'].append({
                'controller': controller,
                'serial_no': serial_no,
                'doors': [int(f'{v}') for v in user_input['doors']],
                'configured': False,
            })

            return await self.async_step_doors()

        select = SelectSelectorConfig(options=[g(v) for v in doors],
                                      multiple=True,
                                      custom_value=False,
                                      mode=SelectSelectorMode.LIST) # yapf: disable

        schema = vol.Schema({
            vol.Required('doors', default=[f'{v[CONF_DOOR_NUMBER]}' for v in doors if v[CONF_DOOR_ID]]):
            SelectSelector(select),
        })

        placeholders = {
            'controller': f'{controller}',
            'serial_no': f'{serial_no}',
        }

        return self.async_show_form(step_id="doors",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_door(self, user_input: Optional[Dict[str, Any]] = None):

        def f(v):
            return len(v['doors']) > 0 and not v['configured']

        it = next((v for v in self.configuration['doors'] if f(v)), None)
        if it == None:
            try:
                validate_all_doors(self.options)
                return await self.async_step_cards()
            except ValueError as err:
                self.configuration['doors'] = []

                return await self.async_step_doors()

        else:
            controller = it['controller']
            serial_no = it['serial_no']
            doors = it['doors']

        errors: Dict[str, str] = {}
        if user_input is not None:
            l = [user_input[f'door{v}_id'] for v in doors]
            for d in doors:
                try:
                    k = f'door{d}_id'
                    v = user_input[k]
                    validate_door_id(v, None)
                    validate_door_duplicates(v, l)
                except ValueError as err:
                    errors[k] = f'{err}'

            if not errors:
                l = self.options[CONF_DOORS]

                for door in doors:
                    k = f'door{door}_id'
                    for d in l:
                        if d[CONF_DOOR_CONTROLLER] == controller and f'{d[CONF_DOOR_NUMBER]}' == f'{door}':
                            if user_input[k].strip() == '-':
                                l.remove(d)
                            else:
                                d[CONF_DOOR_ID] = user_input[k]
                            break
                    else:
                        if user_input[k].strip() != '-':
                            l.append({
                                CONF_DOOR_UNIQUE_ID: f'{uuid.uuid4()}',
                                CONF_DOOR_ID: user_input[k],
                                CONF_DOOR_CONTROLLER: controller,
                                CONF_DOOR_NUMBER: door,
                            })

                self.options.update({CONF_DOORS: l})
                it['configured'] = True

                return await self.async_step_door()

        defaults = {
            'door1_id': DEFAULT_DOOR1,
            'door2_id': DEFAULT_DOOR2,
            'door3_id': DEFAULT_DOOR3,
            'door4_id': DEFAULT_DOOR4,
        }

        if user_input is not None:
            for v in ['door1_id', 'door2_id', 'door3_id', 'door4_id']:
                if k in user_input:
                    defaults[k] = user_input[k]

        for v in self.options[CONF_DOORS]:
            for d in [1, 2, 3, 4]:
                if v[CONF_DOOR_CONTROLLER] == controller and int(f'{v[CONF_DOOR_NUMBER]}') == d:
                    defaults[f'door{d}_id'] = v[CONF_DOOR_ID]

        schema = vol.Schema({})

        for d in [1, 2, 3, 4]:
            if d in doors:
                key = f'door{d}_id'
                schema = schema.extend({vol.Optional(key, default=defaults[key]): str})

        placeholders = {
            'controller': f'{controller}',
            'serial_no': f'{serial_no}',
        }

        return self.async_show_form(step_id="door",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_cards(self, user_input: Optional[Dict[str, Any]] = None):

        def g(c):
            card = c[CONF_CARD_NUMBER]
            cardholder = c[CONF_CARD_NAME]
            return {
                'label': f'{card} ({cardholder})' if cardholder and cardholder.strip() != '' else f'{card}',
                'value': f'{card}',
            }

        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                l = [{
                    'card': get_card(v, self.options),
                    'configured': False,
                } for v in user_input[CONF_CARDS]]

                self.configuration['cards'] = sorted(l, key=lambda v: v['card'][CONF_CARD_NUMBER])

                return await self.async_step_card()

        cards = get_all_cards(self.options, self._max_cards, self._preferred_cards)
        defaults = [f'{v[CONF_CARD_NUMBER]}' for v in self.options.get(CONF_CARDS, [])]

        select = SelectSelectorConfig(options=[g(v) for v in cards],
                                      multiple=True,
                                      custom_value=False,
                                      mode=SelectSelectorMode.LIST) # yapf: disable

        schema = vol.Schema({
            vol.Required(CONF_CARDS, default=defaults): SelectSelector(select),
        })

        return self.async_show_form(step_id="cards", data_schema=schema, errors=errors)

    async def async_step_card(self, user_input: Optional[Dict[str, Any]] = None):

        def f(v):
            return not v['configured']

        it = (v for v in self.configuration['cards'] if f(v))
        item = next(it, None)
        if item == None:
            try:
                validate_all_cards(self.options)
                return self.async_create_entry(title="uhppoted", data=self.options)
            except ValueError as err:
                self.configuration['cards'] = []
                return await self.async_step_cards()

        cards = []
        while item != None and len(cards) < 4:
            cards.append(item)
            item = next(it, None)

        errors: Dict[str, str] = {}
        if user_input is not None:
            for ix, item in enumerate(cards):
                k = f'card{ix+1}_name'
                try:
                    validate_card_id(user_input[k])
                except ValueError as err:
                    errors[k] = f'{err}'

            if not errors:
                v = self.options.get(CONF_CARDS, [])

                for ix, item in enumerate(cards):
                    k = f'card{ix+1}_name'
                    card = item['card']
                    name = user_input[k]
                    if name == '-':
                        for c in v:
                            if c[CONF_CARD_UNIQUE_ID] == card[CONF_CARD_UNIQUE_ID]:
                                v.remove(c)
                    else:
                        for c in v:
                            if int(f'{c[CONF_CARD_NUMBER]}') == int(f'{card[CONF_CARD_NUMBER]}'):
                                c[CONF_CARD_NAME] = name
                                break
                        else:
                            v.append({
                                CONF_CARD_UNIQUE_ID: uuid.uuid4(),
                                CONF_CARD_NUMBER: card[CONF_CARD_NUMBER],
                                CONF_CARD_NAME: name,
                            })

                    item['configured'] = True

                self.options.update({CONF_CARDS: v})

                return await self.async_step_card()

        defaults = {}
        for ix, item in enumerate(cards):
            card = item['card']
            defaults[f'card{ix+1}_name'] = f'{card[CONF_CARD_NAME]}'

        if user_input is not None:
            for ix, items in enumerate(cards):
                card = item['card']
                k = f'card{ix+1}_name'
                if k in user_input:
                    defaults[k] = user_input[k]

        placeholders = {}
        for ix, item in enumerate(cards):
            card = item['card']
            placeholders[f'card{ix+1}'] = f'{card[CONF_CARD_NUMBER]}'
            placeholders[f'cardholder{ix+1}'] = f"{card[CONF_CARD_NAME]}"

        schema = vol.Schema({})
        for ix, item in enumerate(cards):
            k = f'card{ix+1}_name'
            card = item['card']
            schema = schema.extend({vol.Required(k, default=defaults[k]): str})

        return self.async_show_form(step_id="card",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)
