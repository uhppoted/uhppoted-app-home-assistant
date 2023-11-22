import logging
from typing import Any
from typing import Dict
from typing import Optional

from homeassistant import core
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .const import CONF_CONTROLLER_ID
from .const import CONF_CONTROLLER_ADDR
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR

_LOGGER = logging.getLogger(__name__)

# UHPPOTE_SCHEMA = vol.Schema({
#     vol.Required(CONF_CONTROLLER_ID): int,
#     vol.Optional(CONF_BIND_ADDR, default="192.168.1.100"): str,
#     vol.Optional(CONF_BROADCAST_ADDR, default="192.168.1.255:60000"): str,
#     vol.Optional(CONF_LISTEN_ADDR, default="192.168.1.100:60001"): str,
# })


def validate_controller_id(id: int, hass: core.HomeAssistant) -> None:
    if id < 10:
        raise ValueError


class UhppotedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        data = self.hass.data[DOMAIN]

        schema = vol.Schema({
            vol.Required(CONF_CONTROLLER_ID): int,
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
        data = self.hass.data[DOMAIN]
        bind = '0.0.0.0'
        broadcast = '255.255.255.255:60000'
        listen = '0.0.0.0:60001'

        if CONF_BIND_ADDR in data:
            bind = data[CONF_BIND_ADDR]

        if CONF_BROADCAST_ADDR in data:
            broadcast = data[CONF_BROADCAST_ADDR]

        if CONF_LISTEN_ADDR in data:
            listen = data[CONF_LISTEN_ADDR]

        schema = vol.Schema({
            vol.Optional(CONF_BIND_ADDR, default=bind): str,
            vol.Optional(CONF_BROADCAST_ADDR, default=broadcast): str,
            vol.Optional(CONF_LISTEN_ADDR, default=listen): str,
        })

        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.data.update(user_input)
                return self.async_create_entry(title="uhppoted", data=self.data)

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)
