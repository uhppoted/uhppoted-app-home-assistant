import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers import entity_platform

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG
from .const import CONF_TIMEZONE
from .const import CONF_MAX_CARDS
from .const import CONF_PREFERRED_CARDS
from .const import CONF_PIN_ENABLED
from .const import CONF_POLL_CONTROLLERS
from .const import CONF_POLL_DOORS
from .const import CONF_POLL_CARDS
from .const import CONF_POLL_EVENTS

from .const import DEFAULT_MAX_CARDS
from .const import DEFAULT_PREFERRED_CARDS

from .coordinators.coordinators import Coordinators


def unlock_door(call):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UNLOCK DOOR', call.data)
    # name = call.data.get(ATTR_NAME, DEFAULT_NAME)
    #
    # hass.states.set("hello_service.hello", name)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    defaults = {
        CONF_BIND_ADDR: '0.0.0.0',
        CONF_BROADCAST_ADDR: '255.255.255.255:60000',
        CONF_LISTEN_ADDR: '0.0.0.0:60001',
        CONF_DEBUG: False,
        CONF_TIMEZONE: 'Local',
        CONF_MAX_CARDS: DEFAULT_MAX_CARDS,
        CONF_PREFERRED_CARDS: DEFAULT_PREFERRED_CARDS,
        CONF_PIN_ENABLED: False,
        CONF_POLL_CONTROLLERS: 30,
        CONF_POLL_DOORS: 30,
        CONF_POLL_CARDS: 30,
        CONF_POLL_EVENTS: 30,
    }

    if 'uhppoted' in config:
        c = config['uhppoted']
        for v in [
                CONF_BIND_ADDR, CONF_BROADCAST_ADDR, CONF_LISTEN_ADDR, CONF_DEBUG, CONF_TIMEZONE, CONF_MAX_CARDS,
                CONF_PREFERRED_CARDS, CONF_PIN_ENABLED, CONF_POLL_CONTROLLERS, CONF_POLL_DOORS, CONF_POLL_CARDS,
                CONF_POLL_EVENTS
        ]:
            if v in c:
                defaults[v] = c[v]

    _LOGGER.info(f'default bind address:        {defaults[CONF_BIND_ADDR]}')
    _LOGGER.info(f'default broadcast address:   {defaults[CONF_BROADCAST_ADDR]}')
    _LOGGER.info(f'default listen address:      {defaults[CONF_LISTEN_ADDR]}')
    _LOGGER.info(f'default debug:               {defaults[CONF_DEBUG]}')
    _LOGGER.info(f'default timezone:            {defaults[CONF_TIMEZONE]}')
    _LOGGER.info(f'max. cards:                  {defaults[CONF_MAX_CARDS]}')
    _LOGGER.info(f'preferred cards:             {defaults[CONF_PREFERRED_CARDS]}')
    _LOGGER.info(f'PIN enabled:                 {defaults[CONF_PIN_ENABLED]}')
    _LOGGER.info(f'poll interval - controllers: {defaults[CONF_POLL_CONTROLLERS]}s')
    _LOGGER.info(f'poll interval - doors:       {defaults[CONF_POLL_DOORS]}s')
    _LOGGER.info(f'poll interval - cards:       {defaults[CONF_POLL_CARDS]}s')
    _LOGGER.info(f'poll interval - events:      {defaults[CONF_POLL_EVENTS]}s')

    hass.data.setdefault(DOMAIN, defaults)

    hass.services.async_register(DOMAIN, "unlock_door", unlock_door)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    Coordinators.initialise(hass, entry.options)

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "datetime"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "select"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "number"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "button"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "event"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "date"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "switch"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "text"))

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
        Platform.SWITCH,
        Platform.TEXT,
    ]

    # TODO pre-unload cleanup (if any)
    ok = await hass.config_entries.async_unload_platforms(entry, platforms)

    # ... post-unload cleanup (if any)
    Coordinators.unload()

    return ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
