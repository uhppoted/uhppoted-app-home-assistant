import logging

from typing import Any
from typing import Dict
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import OptionsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
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


class UhppotedOptionsFlow(OptionsFlow):

    def __init__(self, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self.data = dict(entry.data)
        self.options = dict(entry.options)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
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
                return await self.async_step_controller()

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_step_controller(self, user_input: Optional[Dict[str, Any]] = None):
        name = self.options[CONF_CONTROLLER_ID]
        controller = self.options[CONF_CONTROLLER_SERIAL_NUMBER]
        address = self.options[CONF_CONTROLLER_ADDR]

        controllers = selector.SelectSelector(
            selector.SelectSelectorConfig(options=['201020304', '303986753', '405419896'],
                                          multiple=False,
                                          custom_value=True,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

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
                self.options.update(user_input)
                return await self.async_step_door()

        return self.async_show_form(step_id="controller", data_schema=schema, errors=errors)

    async def async_step_door(self, user_input: Optional[Dict[str, Any]] = None):
        name = self.options[CONF_DOOR_ID]
        controller = self.options[CONF_DOOR_CONTROLLER]
        door = self.options[CONF_DOOR_NUMBER]

        controllers = selector.SelectSelector(
            selector.SelectSelectorConfig(options=['Alpha', 'Beta', 'Gamma', 'Delta'],
                                          multiple=False,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        doors = selector.SelectSelector(
            selector.SelectSelectorConfig(options=['1', '2', '3', '4'],
                                          multiple=False,
                                          mode=selector.SelectSelectorMode.DROPDOWN))

        schema = vol.Schema({
            vol.Required(CONF_DOOR_ID, default=name): str,
            vol.Required(CONF_DOOR_CONTROLLER, default=controller): controllers,
            vol.Required(CONF_DOOR_NUMBER, default=door): doors,
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
                return self.async_create_entry(title="uhppoted", data=self.options)

        return self.async_show_form(step_id="door", data_schema=schema, errors=errors)
