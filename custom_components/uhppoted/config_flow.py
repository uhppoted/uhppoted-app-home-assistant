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

_LOGGER = logging.getLogger(__name__)


def validate_controller_id(v: int) -> None:
    if not v or v.strip() == '':
        raise ValueError


def validate_controller_serial_no(v) -> None:
    controller = int(f'{v}')
    if controller < 100000000:
        raise ValueError


def validate_door_id(v: int) -> None:
    if not v or v.strip() == '':
        raise ValueError


def validate_door_controller(v: str, controllers: list[str]) -> None:
    if v not in controllers:
        raise ValueError


def validate_door_number(v) -> None:
    door = int(f'{v}')
    if door < 1 or door > 4:
        raise ValueError


class UhppotedConfigFlow(ConfigFlow, domain=DOMAIN):
    # data: Optional[Dict[str, Any]]

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

        self.data = {
            CONF_BIND_ADDR: bind,
            CONF_BROADCAST_ADDR: broadcast,
            CONF_LISTEN_ADDR: listen,
            CONF_DEBUG: debug,
        }

        self.options = {}

        return await self.async_step_IPv4()

    async def async_step_IPv4(self, user_input: Optional[Dict[str, Any]] = None):
        bind = self.data[CONF_BIND_ADDR]
        broadcast = self.data[CONF_BROADCAST_ADDR]
        listen = self.data[CONF_LISTEN_ADDR]
        debug = self.data[CONF_DEBUG]

        schema = vol.Schema({
            vol.Optional(CONF_BIND_ADDR, default=bind): str,
            vol.Optional(CONF_BROADCAST_ADDR, default=broadcast): str,
            vol.Optional(CONF_LISTEN_ADDR, default=listen): str,
            vol.Optional(CONF_DEBUG, default=debug): bool,
        })

        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.data.update(user_input)
                return await self.async_step_controller()

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        controllers = selector.SelectSelector(
            selector.SelectSelectorConfig(options=['201020304', '303986753', '405419896'],
                                          multiple=False,
                                          custom_value=True,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_ID, default='Alpha'): str,
            vol.Required(CONF_CONTROLLER_SERIAL_NUMBER, default='405419896'): controllers,
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
