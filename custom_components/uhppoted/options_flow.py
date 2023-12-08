import logging

from typing import Any
from typing import Dict
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import OptionsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.data_entry_flow import FlowResult
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


def validate_controller_id(id: int, hass: HomeAssistant) -> None:
    if id < 10:
        raise ValueError


class UhppotedOptionsFlow(OptionsFlow):

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.data = dict(config_entry.data)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        return await self.async_step_IPv4()

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

        if CONF_BIND_ADDR in self.config_entry.data:
            bind = self.config_entry.data[CONF_BIND_ADDR]

        if CONF_BROADCAST_ADDR in self.config_entry.data:
            broadcast = self.config_entry.data[CONF_BROADCAST_ADDR]

        if CONF_LISTEN_ADDR in self.config_entry.data:
            listen = self.config_entry.data[CONF_LISTEN_ADDR]

        if CONF_DEBUG in self.config_entry.data:
            debug = self.config_entry.data[CONF_DEBUG]

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
                return self.async_create_entry(title="uhppoted", data=self.data)

        return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

    async def async_end(self):
        print('>>>>>>>>>>>>>>>>>>>>>>> async_end')
        # """Finalization of the ConfigEntry creation"""
        # _LOGGER.info(
        #     "Recreating entry %s due to configuration change",
        #     self.config_entry.entry_id,
        # )
        # self.hass.config_entries.async_update_entry(self.config_entry, data=self._infos)
        # return self.async_create_entry(title=None, data=None)
