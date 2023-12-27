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

from .const import CONF_DOORS
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

from .config import validate_controller_id
from .config import validate_controller_serial_no
from .config import validate_door_id
from .config import validate_door_controller
from .config import validate_door_number
from .config import get_all_controllers

_LOGGER = logging.getLogger(__name__)


class UhppotedOptionsFlow(OptionsFlow):

    def __init__(self, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self.data = dict(entry.data)
        self.options = dict(entry.options)
        self.controllers = []
        self.doors = []

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

        configured = set()
        if self.options and CONF_CONTROLLERS in self.options:
            for v in self.options[CONF_CONTROLLERS]:
                configured.add(int(f'{v[CONF_CONTROLLER_SERIAL_NUMBER]}'))

        configured = sorted(list(configured), reverse=True)

        # if len(controllers) < 2:
        #     for v in controllers:
        #         self.controllers.append({
        #             'controller': {
        #                 'name': '',
        #                 'serial_no': v,
        #                 'configured': False,
        #             },
        #             'doors': None,
        #         })
        #
        #     return await self.async_step_controller()

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLERS, default=[f'{v}' for v in configured]):
            SelectSelector(
                SelectSelectorConfig(options=[f'{v}' for v in controllers],
                                     multiple=True,
                                     custom_value=False,
                                     mode=SelectSelectorMode.LIST)),
        })

        return self.async_show_form(step_id="controllers", data_schema=schema, errors=errors)

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        name = ''
        controller = ''
        address = ''

        if CONF_CONTROLLERS in self.options:
            for v in self.options[CONF_CONTROLLERS]:
                name = v[CONF_CONTROLLER_ID]
                controller = v[CONF_CONTROLLER_SERIAL_NUMBER]
                address = v[CONF_CONTROLLER_ADDR]
                break

        controllers = SelectSelector(
            SelectSelectorConfig(options=[f'{v}' for v in self.controllers],
                                 multiple=False,
                                 custom_value=True,
                                 mode=SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_ID, default=name): str,
            vol.Required(CONF_CONTROLLER_SERIAL_NUMBER, default=controller): controllers,
            vol.Optional(CONF_CONTROLLER_ADDR, default=address): str,
        })

        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                validate_controller_id(user_input[CONF_CONTROLLER_ID])
            except ValueError:
                errors["base"] = f'Invalid controller ID ({user_input[CONF_CONTROLLER_ID]})'

            try:
                validate_controller_serial_no(user_input[CONF_CONTROLLER_SERIAL_NUMBER])
            except ValueError:
                errors["base"] = f'Invalid controller serial number ({user_input[CONF_CONTROLLER_SERIAL_NUMBER]})'

            if not errors:
                v = []
                v.append({
                    CONF_CONTROLLER_ID: user_input[CONF_CONTROLLER_ID],
                    CONF_CONTROLLER_SERIAL_NUMBER: user_input[CONF_CONTROLLER_SERIAL_NUMBER],
                    CONF_CONTROLLER_ADDR: user_input[CONF_CONTROLLER_ADDR],
                })

                self.options.update({CONF_CONTROLLERS: v})

                return await self.async_step_door()

        return self.async_show_form(step_id="controller", data_schema=schema, errors=errors)

    async def async_step_door(self, user_input: Optional[Dict[str, Any]] = None):
        name = ''
        controller = ''
        door_no = ''

        if CONF_DOORS in self.options:
            for v in self.options[CONF_DOORS]:
                name = v[CONF_DOOR_ID]
                controller = v[CONF_DOOR_CONTROLLER]
                door_no = v[CONF_DOOR_NUMBER]
                break

        controllers = SelectSelector(
            SelectSelectorConfig(options=['Alpha', 'Beta', 'Gamma', 'Delta'],
                                 multiple=False,
                                 mode=SelectSelectorMode.DROPDOWN))

        doors = SelectSelector(
            SelectSelectorConfig(options=['1', '2', '3', '4'],
                                 multiple=False,
                                 mode=selector.SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_DOOR_ID, default=name): str,
            vol.Required(CONF_DOOR_CONTROLLER, default=controller): controllers,
            vol.Required(CONF_DOOR_NUMBER, default=door_no): doors,
        })

        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                validate_door_id(user_input[CONF_DOOR_ID])
            except ValueError:
                errors["base"] = f'Invalid door ID ({user_input[CONF_DOOR_ID]})'

            try:
                validate_door_controller(user_input[CONF_DOOR_CONTROLLER], self.options[CONF_CONTROLLERS])
            except ValueError:
                errors["base"] = f'Invalid door controller ({user_input[CONF_DOOR_CONTROLLER]})'

            try:
                validate_door_number(user_input[CONF_DOOR_NUMBER])
            except ValueError:
                errors["base"] = f'Invalid door number ({user_input[CONF_DOOR_NUMBER]})'

            if not errors:
                v = []
                v.append({
                    CONF_DOOR_ID: user_input[CONF_DOOR_ID],
                    CONF_DOOR_CONTROLLER: user_input[CONF_DOOR_CONTROLLER],
                    CONF_DOOR_NUMBER: user_input[CONF_DOOR_NUMBER],
                })

                self.options.update({CONF_DOORS: v})

                return self.async_create_entry(title="uhppoted", data=self.options)

        return self.async_show_form(step_id="door", data_schema=schema, errors=errors)
