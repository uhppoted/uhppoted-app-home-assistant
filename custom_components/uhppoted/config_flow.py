import logging

from typing import Any
from typing import Dict
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import OptionsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import selector
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from uhppoted import uhppote

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_SERIAL_NUMBER
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_CONTROLLER
from .const import CONF_DOOR_NUMBER

from .options_flow import UhppotedOptionsFlow

from .config import validate_controller_id
from .config import validate_controller_serial_no
from .config import validate_door_id
from .config import validate_door_controller
from .config import validate_door_number
from .config import get_all_controllers

_LOGGER = logging.getLogger(__name__)


class UhppotedConfigFlow(ConfigFlow, domain=DOMAIN):

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> UhppotedOptionsFlow:
        return UhppotedOptionsFlow(config_entry)

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        defaults = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}
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

        self.data = {}

        self.options = {
            CONF_BIND_ADDR: bind,
            CONF_BROADCAST_ADDR: broadcast,
            CONF_LISTEN_ADDR: listen,
            CONF_DEBUG: debug,
        }

        return await self.async_step_IPv4()

    async def async_step_IPv4(self, user_input: Optional[Dict[str, Any]] = None):
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

        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.options.update(user_input)
                self.controllers = get_all_controllers(self.options)
                return await self.async_step_controller()

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        controllers = selector.SelectSelector(
            selector.SelectSelectorConfig(options=[f'{v}' for v in self.controllers],
                                          multiple=False,
                                          custom_value=True,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_SERIAL_NUMBER): controllers,
            vol.Required(CONF_CONTROLLER_ID, default='Alpha'): str,
            vol.Optional(CONF_CONTROLLER_ADDR, default='192.168.1.100'): str,
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
                self.options.update(user_input)
                return await self.async_step_door()

        return self.async_show_form(step_id="controller", data_schema=schema, errors=errors)

    async def async_step_door(self, user_input: Optional[Dict[str, Any]] = None):
        controllers = selector.SelectSelector(
            selector.SelectSelectorConfig(options=['Alpha', 'Beta', 'Gamma', 'Delta'],
                                          multiple=False,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        doors = selector.SelectSelector(
            selector.SelectSelectorConfig(options=['1', '2', '3', '4'],
                                          multiple=False,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_DOOR_ID, default='Dungeon'): str,
            vol.Required(CONF_DOOR_CONTROLLER, default='Alpha'): controllers,
            vol.Required(CONF_DOOR_NUMBER, default='1'): doors,
        })

        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                validate_door_id(user_input[CONF_DOOR_ID])
            except ValueError:
                errors["base"] = f'Invalid door ID ({user_input[CONF_DOOR_ID]})'

            try:
                validate_door_controller(user_input[CONF_DOOR_CONTROLLER], [self.options[CONF_CONTROLLER_ID]])
            except ValueError:
                errors["base"] = f'Invalid door controller ({user_input[CONF_DOOR_CONTROLLER]})'

            try:
                validate_door_number(user_input[CONF_DOOR_NUMBER])
            except ValueError:
                errors["base"] = f'Invalid door number ({user_input[CONF_DOOR_NUMBER]})'

            if not errors:
                self.options.update(user_input)
                return self.async_create_entry(title="uhppoted", data=self.data, options=self.options)

        return self.async_show_form(step_id="door", data_schema=schema, errors=errors)
