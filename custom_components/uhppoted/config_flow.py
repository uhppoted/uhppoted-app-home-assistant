import logging

from typing import Any
from typing import Dict
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import OptionsFlow
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_NAME
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_DOOR_ID
from .const import CONF_DOOR_NAME

from .options_flow import UhppotedOptionsFlow

_LOGGER = logging.getLogger(__name__)


def validate_controller_id(id: int, hass: HomeAssistant) -> None:
    if id < 10:
        raise ValueError


class UhppotedConfigFlow(ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return UhppotedOptionsFlow(config_entry)        

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        data = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_ID): int,
            vol.Optional(CONF_CONTROLLER_NAME, default=''): str,
            vol.Optional(CONF_CONTROLLER_ADDR, default=''): str,
        })

        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                validate_controller_id(user_input[CONF_CONTROLLER_ID], self.hass)
            except ValueError:
                errors["base"] = f'Invalid controller ID ({user_input[CONF_CONTROLLER_ID]})'

            if not errors:
                self.data = user_input
                return await self.async_step_IPv4()

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_IPv4(self, user_input: Optional[Dict[str, Any]] = None):
        data = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}
        bind = '0.0.0.0'
        broadcast = '255.255.255.255:60000'
        listen = '0.0.0.0:60001'
        debug = False

        if CONF_BIND_ADDR in data:
            bind = data[CONF_BIND_ADDR]

        if CONF_BROADCAST_ADDR in data:
            broadcast = data[CONF_BROADCAST_ADDR]

        if CONF_LISTEN_ADDR in data:
            listen = data[CONF_LISTEN_ADDR]

        if CONF_DEBUG in data:
            debug = data[CONF_DEBUG]

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
                return await self.async_step_door()

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_step_door(self, user_input: Optional[Dict[str, Any]] = None):
        data = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}

        schema = vol.Schema({
            vol.Required(CONF_DOOR_ID, default=1): int,
            vol.Optional(CONF_DOOR_NAME, default=''): str,
        })

        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.data.update(user_input)
                return self.async_create_entry(title="uhppoted", data=self.data)

        return self.async_show_form(step_id="door", data_schema=schema, errors=errors)

