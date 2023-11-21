import logging
from typing import Any
from typing import Dict
from typing import Optional

from homeassistant import core
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN

CONF_CONTROLLER_ID = 'controller_id'
CONF_BIND_ADDR = 'bind_address'
CONF_BROADCAST_ADDR = 'broadcast_address'
CONF_LISTEN_ADDR = 'listen_address'

_LOGGER = logging.getLogger(__name__)

UHPPOTE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONTROLLER_ID): int,
        vol.Optional(CONF_BIND_ADDR, default="0.0.0.0:0"): str,
        vol.Optional(CONF_BROADCAST_ADDR, default="255.255.255.255:60000"): str,
        vol.Optional(CONF_LISTEN_ADDR, default="0.0.0.0:60001"): str,
    })


def validate_controller_id(id: int, hass: core.HomeAssistant) -> None:
    if id < 10:
        raise ValueError

class UhppotedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                validate_controller_id(user_input[CONF_CONTROLLER_ID], self.hass)
            except ValueError:
                errors["base"] = f'Invalid controller ID ({user_input[CONF_CONTROLLER_ID]})'
            if not errors:
                self.data = user_input

                # return await self.async_step_repo()
                return self.async_create_entry(title="uhppoted", data=self.data)

        return self.async_show_form(step_id="user", data_schema=UHPPOTE_SCHEMA, errors=errors)

    # async def async_step_repo(self, user_input: Optional[Dict[str, Any]] = None):
    #     """Second step in config flow to add a repo to watch."""
    #     errors: Dict[str, str] = {}
    #     if user_input is not None:
    #         # Validate the path.
    #         try:
    #             validate_path(user_input[CONF_PATH])
    #         except ValueError:
    #             errors["base"] = "invalid_path"
    #
    #         if not errors:
    #             # Input is valid, set data.
    #             self.data[CONF_REPOS].append(
    #                 {
    #                     "path": user_input[CONF_PATH],
    #                     "name": user_input.get(CONF_NAME, user_input[CONF_PATH]),
    #                 }
    #             )
    #             # If user ticked the box show this form again so they can add an
    #             # additional repo.
    #             if user_input.get("add_another", False):
    #                 return await self.async_step_repo()
    #
    #             # User is done adding repos, create the config entry.
    #             return self.async_create_entry(title="GitHub Custom", data=self.data)
    #
    #     return self.async_show_form(
    #         step_id="repo", data_schema=REPO_SCHEMA, errors=errors
    #     )
