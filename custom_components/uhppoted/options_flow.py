import copy
import logging

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
import voluptuous as vol

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

from .const import DEFAULT_CONTROLLER_ID
from .const import DEFAULT_CONTROLLER_ADDR
from .const import DEFAULT_CONTROLLER_TIMEZONE

from .const import DEFAULT_DOOR1
from .const import DEFAULT_DOOR2
from .const import DEFAULT_DOOR3
from .const import DEFAULT_DOOR4

from .config import validate_controller_id
from .config import validate_all_controllers
from .config import validate_door_duplicates
from .config import validate_door_id
from .config import validate_all_doors

from .config import get_all_controllers
from .config import get_all_doors

_LOGGER = logging.getLogger(__name__)


class UhppotedOptionsFlow(OptionsFlow):

    def __init__(self, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self.data = dict(entry.data)
        # self.options = dict(entry.options)
        self.options = copy.deepcopy(dict(entry.options))
        self.controllers = []
        self.doors = []
        self.configuration = {'doors': []}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
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

        def g(v):
            if self.options and CONF_CONTROLLERS in self.options:
                for c in self.options[CONF_CONTROLLERS]:
                    if f'{c[CONF_CONTROLLER_SERIAL_NUMBER]}' == f'{v}':
                        if c[CONF_CONTROLLER_ID] != '':
                            return {
                                'label': f'{v} ({c[CONF_CONTROLLER_ID]})',
                                'value': f'{v}',
                            }
                        break
            return {
                'label': f'{v}',
                'value': f'{v}',
            }

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
        if len(controllers) < 1:
            return await self.async_step_door()

        configured = set()
        if self.options and CONF_CONTROLLERS in self.options:
            for v in self.options[CONF_CONTROLLERS]:
                configured.add(int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}'))

        configured = sorted(list(configured), reverse=True)

        try:
            validate_all_controllers(self.options)
        except ValueError as err:
            errors['base'] = f'{err}'

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLERS, default=[f'{v}' for v in configured]):
            SelectSelector(
                SelectSelectorConfig(options=[g(v) for v in controllers],
                                     multiple=True,
                                     custom_value=False,
                                     mode=SelectSelectorMode.LIST)),
        })

        return self.async_show_form(step_id="controllers", data_schema=schema, errors=errors)

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        it = next((v for v in self.controllers if not v['controller']['configured']), None)
        if it == None:
            try:
                validate_all_controllers(self.options)
                return await self.async_step_doors()
            except ValueError as err:
                return await self.async_step_controllers()
        else:
            controller = it['controller']
            serial_no = controller['serial_no']

        errors: Dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_CONTROLLER_ID]
            address = user_input[CONF_CONTROLLER_ADDR]
            timezone = user_input[CONF_CONTROLLER_TIMEZONE]

            try:
                validate_controller_id(serial_no, name, None)
            except ValueError as err:
                errors[CONF_CONTROLLER_ID] = f'{err}'

            if not errors:
                controllers = self.options[CONF_CONTROLLERS]

                for v in self.options[CONF_CONTROLLERS]:
                    if int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') == int(f'{serial_no}'):
                        v[CONF_CONTROLLER_ID] = name
                        v[CONF_CONTROLLER_SERIAL_NUMBER] = serial_no
                        v[CONF_CONTROLLER_ADDR] = address
                        v[CONF_CONTROLLER_TIMEZONE] = timezone
                        break
                else:
                    controllers.append({
                        CONF_CONTROLLER_ID: name,
                        CONF_CONTROLLER_SERIAL_NUMBER: serial_no,
                        CONF_CONTROLLER_ADDR: address,
                        CONF_CONTROLLER_TIMEZONE: timezone,
                    })

                self.options.update({CONF_CONTROLLERS: controllers})

                controller['name'] = user_input[CONF_CONTROLLER_ID]
                controller['configured'] = True

                return await self.async_step_controller()

        defaults = {
            CONF_CONTROLLER_ID: DEFAULT_CONTROLLER_ID,
            CONF_CONTROLLER_ADDR: DEFAULT_CONTROLLER_ADDR,
            CONF_CONTROLLER_TIMEZONE: DEFAULT_CONTROLLER_TIMEZONE,
        }

        if CONF_CONTROLLERS in self.options:
            for v in self.options[CONF_CONTROLLERS]:
                if int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}') == int(f'{serial_no}'):
                    for k in [CONF_CONTROLLER_ID, CONF_CONTROLLER_ADDR, CONF_CONTROLLER_TIMEZONE]:
                        if k in v:
                            defaults[k] = v[k]
                    break

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
                                        "serial_no": serial_no,
                                    })

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
                return self.async_create_entry(title="uhppoted", data=self.options)
                # return await self.async_step_cards()
            except ValueError as err:
                # for v in self.configuration['doors']:
                #     v['configured'] = False

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
                v = self.options[CONF_DOORS]

                if 1 in doors:
                    for d in v:
                        if d[CONF_DOOR_CONTROLLER] == controller and f'{d[CONF_DOOR_NUMBER]}' == '1':
                            if user_input['door1_id'].strip() == '-':
                                v.remove(d)
                            else:
                                d[CONF_DOOR_ID] = user_input['door1_id']
                            break
                    else:
                        if user_input['door1_id'].strip() != '-':
                            v.append({
                                CONF_DOOR_ID: user_input['door1_id'],
                                CONF_DOOR_CONTROLLER: controller,
                                CONF_DOOR_NUMBER: 1,
                            })

                if 2 in doors:
                    for d in v:
                        if d[CONF_DOOR_CONTROLLER] == controller and f'{d[CONF_DOOR_NUMBER]}' == '2':
                            if user_input['door2_id'].strip() == '-':
                                v.remove(d)
                            else:
                                d[CONF_DOOR_ID] = user_input['door2_id']
                            break
                    else:
                        if user_input['door2_id'].strip() != '-':
                            v.append({
                                CONF_DOOR_ID: user_input['door2_id'],
                                CONF_DOOR_CONTROLLER: controller,
                                CONF_DOOR_NUMBER: 2,
                            })

                if 3 in doors:
                    for d in v:
                        if d[CONF_DOOR_CONTROLLER] == controller and f'{d[CONF_DOOR_NUMBER]}' == '3':
                            if user_input['door3_id'].strip() == '-':
                                v.remove(d)
                            else:
                                d[CONF_DOOR_ID] = user_input['door3_id']
                            break
                    else:
                        if user_input['door3_id'].strip() != '-':
                            v.append({
                                CONF_DOOR_ID: user_input['door3_id'],
                                CONF_DOOR_CONTROLLER: controller,
                                CONF_DOOR_NUMBER: 3,
                            })

                if 4 in doors:
                    for d in v:
                        if d[CONF_DOOR_CONTROLLER] == controller and f'{d[CONF_DOOR_NUMBER]}' == '4':
                            if user_input['door4_id'].strip() == '-':
                                v.remove(d)
                            else:
                                d[CONF_DOOR_ID] = user_input['door4_id']
                            break
                    else:
                        if user_input['door4_id'].strip() != '-':
                            v.append({
                                CONF_DOOR_ID: user_input['door4_id'],
                                CONF_DOOR_CONTROLLER: controller,
                                CONF_DOOR_NUMBER: 4,
                            })

                self.options.update({CONF_DOORS: v})
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
            if v[CONF_DOOR_CONTROLLER] == controller and v[CONF_DOOR_NUMBER] == 1:
                defaults['door1_id'] = v[CONF_DOOR_ID]

            if v[CONF_DOOR_CONTROLLER] == controller and v[CONF_DOOR_NUMBER] == 2:
                defaults['door2_id'] = v[CONF_DOOR_ID]

            if v[CONF_DOOR_CONTROLLER] == controller and v[CONF_DOOR_NUMBER] == 3:
                defaults['door3_id'] = v[CONF_DOOR_ID]

            if v[CONF_DOOR_CONTROLLER] == controller and v[CONF_DOOR_NUMBER] == 4:
                defaults['door4_id'] = v[CONF_DOOR_ID]

        schema = vol.Schema({})

        if 1 in doors:
            schema = schema.extend({vol.Optional('door1_id', default=defaults['door1_id']): str})

        if 2 in doors:
            schema = schema.extend({vol.Optional('door2_id', default=defaults['door2_id']): str})

        if 3 in doors:
            schema = schema.extend({vol.Optional('door3_id', default=defaults['door3_id']): str})

        if 4 in doors:
            schema = schema.extend({vol.Optional('door4_id', default=defaults['door4_id']): str})

        placeholders = {
            'controller': f'{controller}',
            'serial_no': f'{serial_no}',
        }

        return self.async_show_form(step_id="door",
                                    data_schema=schema,
                                    errors=errors,
                                    description_placeholders=placeholders)
