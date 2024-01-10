import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    defaults = {
        CONF_BIND_ADDR: '0.0.0.0',
        CONF_BROADCAST_ADDR: '255.255.255.255:60000',
        CONF_LISTEN_ADDR: '0.0.0.0:60001',
        CONF_DEBUG: False,
    }

    if 'uhppoted' in config:
        c = config['uhppoted']
        for v in [CONF_BIND_ADDR, CONF_BROADCAST_ADDR, CONF_LISTEN_ADDR, CONF_DEBUG]:
            if v in c:
                defaults[v] = c[v]

    _LOGGER.info(f'default bind address {defaults[CONF_BIND_ADDR]}')
    _LOGGER.info(f'default broadcast address {defaults[CONF_BROADCAST_ADDR]}')
    _LOGGER.info(f'default listen address {defaults[CONF_LISTEN_ADDR]}')
    _LOGGER.info(f'default debug {defaults[CONF_DEBUG]}')

    hass.data.setdefault(DOMAIN, defaults)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "datetime"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "select"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "number"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "button"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "event"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "date"))

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    platforms = [
        Platform.SENSOR,
        Platform.DATETIME,
        Platform.SELECT,
        Platform.NUMBER,
        Platform.BUTTON,
        Platform.EVENT,
        Platform.DATE,
    ]

    # TODO pre-unload cleanup (if any)
    ok = await hass.config_entries.async_unload_platforms(entry, platforms)
    # TODO post-unload cleanup (if any)

    return ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
