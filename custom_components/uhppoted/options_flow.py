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
        return await self.async_step_controller()

    async def async_step_IPv4(self, user_input: Optional[Dict[str, Any]] = None):
        pass
    #     data = self.hass.data[DOMAIN] if DOMAIN in self.hass.data else {}
    #     bind = '0.0.0.0'
    #     broadcast = '255.255.255.255:60000'
    #     listen = '0.0.0.0:60001'
    #     debug = False
    # 
    #     if CONF_BIND_ADDR in data:
    #         bind = data[CONF_BIND_ADDR]
    # 
    #     if CONF_BROADCAST_ADDR in data:
    #         broadcast = data[CONF_BROADCAST_ADDR]
    # 
    #     if CONF_LISTEN_ADDR in data:
    #         listen = data[CONF_LISTEN_ADDR]
    # 
    #     if CONF_DEBUG in data:
    #         debug = data[CONF_DEBUG]
    # 
    #     if CONF_BIND_ADDR in self.config_entry.data:
    #         bind = self.config_entry.data[CONF_BIND_ADDR]
    # 
    #     if CONF_BROADCAST_ADDR in self.config_entry.data:
    #         broadcast = self.config_entry.data[CONF_BROADCAST_ADDR]
    # 
    #     if CONF_LISTEN_ADDR in self.config_entry.data:
    #         listen = self.config_entry.data[CONF_LISTEN_ADDR]
    # 
    #     if CONF_DEBUG in self.config_entry.data:
    #         debug = self.config_entry.data[CONF_DEBUG]
    # 
    #     schema = vol.Schema({
    #         vol.Optional(CONF_BIND_ADDR, default=bind): str,
    #         vol.Optional(CONF_BROADCAST_ADDR, default=broadcast): str,
    #         vol.Optional(CONF_LISTEN_ADDR, default=listen): str,
    #         vol.Optional(CONF_DEBUG, default=debug): bool,
    #     })
    # 
    #     errors: Dict[str, str] = {}
    # 
    #     if user_input is not None:
    #         if not errors:
    #             self.data.update(user_input)
    #             return self.async_create_entry(title="uhppoted", data=self.data)
    # 
    #     return self.async_show_form(step_id="IPv4", data_schema=schema, errors=errors)

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
                # return await self.async_step_door()
                return self.async_create_entry(title="uhppoted", data=self.options)

        return self.async_show_form(step_id="controller", data_schema=schema, errors=errors)

    async def async_end(self):
        print('>>>>>>>>>>>>>>>>>>>>>>> async_end')
        # """Finalization of the ConfigEntry creation"""
        # _LOGGER.info(
        #     "Recreating entry %s due to configuration change",
        #     self.config_entry.entry_id,
        # )
        # self.hass.config_entries.async_update_entry(self.config_entry, data=self._infos)
        # return self.async_create_entry(title=None, data=None)
