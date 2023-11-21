import logging

from homeassistant import core
from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    # print(">>>>>>>>>>>>>> awooooogahhhhhhhhhhhhhh", entry.data)
    # print(">>>>>>>>>>>>>> awooooogahhhhhhhhhhhhhh", hass.data[DOMAIN])
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))

    return True

async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    # print(">>>>>>>>>>>>>> aaaahh awooooogahhhhhhhhhhhhhh", config)
    hass.data.setdefault(DOMAIN, {})
    return True
