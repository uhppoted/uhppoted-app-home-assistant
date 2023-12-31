import logging
import datetime
import calendar
import re
import voluptuous as vol

from typing import Any
from typing import Dict
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import OptionsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import selector
from homeassistant.helpers.selector import SelectSelector
from homeassistant.helpers.selector import SelectSelectorConfig
from homeassistant.helpers.selector import SelectSelectorMode
from homeassistant.helpers import config_validation as cv

from uhppoted import uhppote

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

from .const import CONF_CONTROLLERS
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_CONTROLLER_TIMEZONE

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

from .const import DEFAULT_CONTROLLER_ID
from .const import DEFAULT_CONTROLLER_ADDR
from .const import DEFAULT_CONTROLLER_TIMEZONE

from .const import DEFAULT_DOOR1
from .const import DEFAULT_DOOR2
from .const import DEFAULT_DOOR3
from .const import DEFAULT_DOOR4

from .options_flow import UhppotedOptionsFlow

from .config import validate_controller_id
from .config import validate_door_id
from .config import validate_door_duplicates
from .config import validate_card_id
from .config import validate_all_cards
from .config import get_IPv4
from .config import get_all_controllers
from .config import get_all_cards

_LOGGER = logging.getLogger(__name__)


class UhppotedConfigFlow(ConfigFlow, domain=DOMAIN):

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> UhppotedOptionsFlow:
        return UhppotedOptionsFlow(config_entry)

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        defaults = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}

        self.data = {}
        self.options = {}
        self.controllers = []
        self.doors = []
        self.configuration = {'cards': []}

        self.options.update(get_IPv4(defaults))
        self.options.update({
            CONF_CONTROLLERS: [],
            CONF_DOORS: [],
        })

        return await self.async_step_IPv4()

    async def async_step_IPv4(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.options.update(user_input)
                return await self.async_step_controllers()

        bind = self.options[CONF_BIND_ADDR]
        broadcast = self.options[CONF_BROADCAST_ADDR]
        listen = self.options[CONF_LISTEN_ADDR]
        debug = self.options[CONF_DEBUG]

        schema = vol.Schema({
            vol.Optional(CONF_BIND_ADDR, default=bind): str,
            vol.Optional(CONF_BROADCAST_ADDR, default=broadcast): str,
            vol.Optional(CONF_LISTEN_ADDR, default=listen): str,
            vol.Optional(CONF_DEBUG, default=debug): bool,
        })

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_step_controllers(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                for v in user_input[CONF_CONTROLLERS]:
                    self.controllers.append({
                        'controller': {
                            'name': '',
                            'serial_no': v,
                            'configured': False,
                        },
                        'doors': None,
                    })

                return await self.async_step_controller()

        controllers = get_all_controllers(self.options)

        if len(controllers) < 2:
            for v in controllers:
                self.controllers.append({
                    'controller': {
                        'name': '',
                        'serial_no': v,
                        'configured': False,
                    },
                    'doors': None,
                })

            return await self.async_step_controller()

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLERS, default=[f'{v}' for v in controllers]):
            SelectSelector(
                SelectSelectorConfig(options=[f'{v}' for v in controllers],
                                     multiple=True,
                                     custom_value=False,
                                     mode=SelectSelectorMode.LIST)),
        })

        return self.async_show_form(step_id="controllers", data_schema=schema, errors=errors)

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        it = next((v for v in self.controllers if not v['controller']['configured']), None)
        if it == None:
            return await self.async_step_doors()
        else:
            controller = it['controller']

        errors: Dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_CONTROLLER_ID]
            serial_no = controller['serial_no']
            address = user_input[CONF_CONTROLLER_ADDR]
            timezone = user_input[CONF_CONTROLLER_TIMEZONE]

            try:
                validate_controller_id(serial_no, name, self.options)
            except ValueError as err:
                errors[CONF_CONTROLLER_ID] = f'{err}'

            if not errors:
                v = self.options[CONF_CONTROLLERS]

                v.append({
                    CONF_CONTROLLER_ID: name,
                    CONF_CONTROLLER_SERIAL_NUMBER: serial_no,
                    CONF_CONTROLLER_ADDR: address,
                    CONF_CONTROLLER_TIMEZONE: timezone,
                })

                self.options.update({CONF_CONTROLLERS: v})

                controller['name'] = user_input[CONF_CONTROLLER_ID]
                controller['configured'] = True

                return await self.async_step_controller()

        defaults = {
            CONF_CONTROLLER_ID: DEFAULT_CONTROLLER_ID,
            CONF_CONTROLLER_ADDR: DEFAULT_CONTROLLER_ADDR,
            CONF_CONTROLLER_TIMEZONE: DEFAULT_CONTROLLER_TIMEZONE,
        }

        if user_input is not None:
            for k in [CONF_CONTROLLER_ID, CONF_CONTROLLER_ADDR, CONF_CONTROLLER_TIMEZONE]:
                if k in user_input:
                    defaults[k] = user_input[k]

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_ID, default=defaults[CONF_CONTROLLER_ID]): str,
            vol.Optional(CONF_CONTROLLER_ADDR, default=defaults[CONF_CONTROLLER_ADDR]): str,
            vol.Optional(CONF_CONTROLLER_TIMEZONE, default=defaults[CONF_CONTROLLER_TIMEZONE]): str,
        })

        return self.async_show_form(step_id="controller",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders={
                                        "serial_no": controller['serial_no'],
                                    })

    async def async_step_doors(self, user_input: Optional[Dict[str, Any]] = None):
        it = next((v for v in self.controllers if not v['doors']), None)
        if it == None:
            return await self.async_step_door()
        else:
            controller = it['controller']

        errors: Dict[str, str] = {}
        if user_input is not None:
            if not errors:
                it['doors'] = {
                    'doors': [int(f'{v}') for v in user_input['doors']],
                    'configured': False,
                }

                return await self.async_step_doors()

        doors = []
        if re.match('^[1234].*', f"{controller['serial_no']}"):
            doors.append(1)

        if re.match('^[234].*', f"{controller['serial_no']}"):
            doors.append(2)

        if re.match('^[34].*', f"{controller['serial_no']}"):
            doors.append(3)

        if re.match('^[4].*', f"{controller['serial_no']}"):
            doors.append(4)

        select = selector.SelectSelectorConfig(options=[{ 'label': f'Door {v}', 'value': f'{v}' } for v in doors],
                                               multiple=True,
                                               custom_value=False,
                                               mode=selector.SelectSelectorMode.LIST) # yapf: disable

        schema = vol.Schema({
            vol.Required('doors', default=[f'{v}' for v in doors]): selector.SelectSelector(select),
        })

        placeholders = {
            'controller': f'{controller["name"]}',
            'serial_no': f'{controller["serial_no"]}',
        }

        return self.async_show_form(step_id="doors",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_door(self, user_input: Optional[Dict[str, Any]] = None):

        def f(v):
            return len(v['doors']) > 0 and not v['configured']

        it = next((v for v in self.controllers if f(v['doors'])), None)
        if it == None:
            return await self.async_step_cards()
        else:
            controller = it['controller']['name']
            serial_no = it['controller']['serial_no']
            doors = it['doors']['doors']

        errors: Dict[str, str] = {}
        if user_input is not None:
            l = [user_input[f'door{v}_id'] for v in doors]
            for d in doors:
                try:
                    k = f'door{d}_id'
                    v = user_input[k]
                    validate_door_id(v, self.options)
                    validate_door_duplicates(v, l)
                except ValueError as err:
                    errors[k] = f'{err}'

            if not errors:
                v = self.options[CONF_DOORS]

                if 1 in doors:
                    v.append({
                        CONF_DOOR_ID: user_input['door1_id'],
                        CONF_DOOR_CONTROLLER: controller,
                        CONF_DOOR_NUMBER: 1,
                    })

                if 2 in it['doors']['doors']:
                    v.append({
                        CONF_DOOR_ID: user_input['door2_id'],
                        CONF_DOOR_CONTROLLER: controller,
                        CONF_DOOR_NUMBER: 2,
                    })

                if 3 in it['doors']['doors']:
                    v.append({
                        CONF_DOOR_ID: user_input['door3_id'],
                        CONF_DOOR_CONTROLLER: controller,
                        CONF_DOOR_NUMBER: 3,
                    })

                if 4 in it['doors']['doors']:
                    v.append({
                        CONF_DOOR_ID: user_input['door4_id'],
                        CONF_DOOR_CONTROLLER: controller,
                        CONF_DOOR_NUMBER: 4,
                    })

                self.options.update({CONF_DOORS: v})
                it['doors']['configured'] = True

                return await self.async_step_door()

        defaults = {
            'door1_id': DEFAULT_DOOR1,
            'door2_id': DEFAULT_DOOR2,
            'door3_id': DEFAULT_DOOR3,
            'door4_id': DEFAULT_DOOR4,
        }

        if user_input is not None:
            for k in ['door1_id', 'door2_id', 'door3_id', 'door4_id']:
                if k in user_input:
                    defaults[k] = user_input[k]

        schema = vol.Schema({})

        if 1 in doors:
            schema = schema.extend({vol.Required('door1_id', default=defaults['door1_id']): str})

        if 2 in doors:
            schema = schema.extend({vol.Required('door2_id', default=defaults['door2_id']): str})

        if 3 in doors:
            schema = schema.extend({vol.Required('door3_id', default=defaults['door3_id']): str})

        if 4 in doors:
            schema = schema.extend({vol.Required('door4_id', default=defaults['door4_id']): str})

        placeholders = {
            'controller': f'{it["controller"]["name"]}',
            'serial_no': f'{it["controller"]["serial_no"]}',
        }

        return self.async_show_form(step_id="door",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_cards(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.configuration['cards'] = [{
                    'card': int(f'{v}'),
                    'configured': False,
                } for v in user_input[CONF_CARDS]]

                return await self.async_step_card()

        cards = get_all_cards(self.options)

        if len(cards) < 2:
            self.configuration['cards'] = [{
                'card': int(f'{v}'),
                'configured': False,
            } for v in cards]

            return await self.async_step_card()

        schema = vol.Schema({
            vol.Required(CONF_CARDS, default=[f'{v}' for v in cards]):
            SelectSelector(
                SelectSelectorConfig(options=[f'{v}' for v in cards],
                                     multiple=True,
                                     custom_value=False,
                                     mode=SelectSelectorMode.LIST)),
        })

        return self.async_show_form(step_id="cards", data_schema=schema, errors=errors)

    async def async_step_card(self, user_input: Optional[Dict[str, Any]] = None):

        def f(v):
            return not v['configured']

        it = next((v for v in self.configuration['cards'] if f(v)), None)
        if it == None:
            try:
                validate_all_cards(self.options)
                return self.async_create_entry(title="uhppoted", data=self.data, options=self.options)
            except ValueError as err:
                self.configuration['cards'] = []
                return await self.async_step_cards()
        else:
            card = it['card']

        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                validate_card_id(user_input[CONF_CARD_NAME])
            except ValueError as err:
                errors[CONF_CARD_NAME] = f'{err}'

            if not errors:
                v = []
                v.append({
                    CONF_CARD_NUMBER: card,
                    CONF_CARD_NAME: user_input[CONF_CARD_NAME],
                    CONF_CARD_STARTDATE: user_input[CONF_CARD_STARTDATE],
                    CONF_CARD_ENDDATE: user_input[CONF_CARD_ENDDATE],
                    CONF_CARD_DOORS: user_input[CONF_CARD_DOORS],
                })

                self.options.update({CONF_CARDS: v})
                it['configured'] = True

                return await self.async_step_card()

        today = datetime.date.today()
        start = today
        end = today + datetime.timedelta(days=180)
        end = datetime.date(end.year, end.month, calendar.monthrange(end.year, end.month)[1])

        defaults = {
            CONF_CARD_NAME: '',
            CONF_CARD_STARTDATE: start,
            CONF_CARD_ENDDATE: end,
            CONF_CARD_DOORS: [],
        }

        if user_input is not None:
            for k in [CONF_CARD_NAME, CONF_CARD_STARTDATE, CONF_CARD_ENDDATE, CONF_CARD_DOORS]:
                if k in user_input:
                    defaults[k] = user_input[k]

        doors = selector.SelectSelector(
            selector.SelectSelectorConfig(options=[f'{v[CONF_DOOR_ID]}' for v in self.options[CONF_DOORS]],
                                          multiple=True,
                                          custom_value=False,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_CARD_NAME, default=defaults[CONF_CARD_NAME]):
            str,
            vol.Required(CONF_CARD_STARTDATE, default=defaults[CONF_CARD_STARTDATE]):
            selector.DateSelector(),
            vol.Required(CONF_CARD_ENDDATE, default=defaults[CONF_CARD_ENDDATE]):
            selector.DateSelector(),
            vol.Optional(CONF_CARD_DOORS, default=defaults[CONF_CARD_DOORS]):
            doors,
        })

        placeholders = {
            'card': f'{card}',
        }

        return self.async_show_form(step_id="card",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)
