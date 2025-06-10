import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN
from .const import CONF_BIND_ADDR
from .const import CONF_BROADCAST_ADDR
from .const import CONF_LISTEN_ADDR
from .const import CONF_DEBUG
from .const import CONF_TIMEZONE
from .const import CONF_TIMEOUT
from .const import CONF_MAX_CARDS
from .const import CONF_PREFERRED_CARDS
from .const import CONF_PIN_ENABLED
from .const import CONF_POLL_CONTROLLERS
from .const import CONF_POLL_DOORS
from .const import CONF_POLL_CARDS
from .const import CONF_POLL_EVENTS
from .const import CONF_CONTROLLERS

from .const import CONF_CACHE_EXPIRY_CONTROLLER
from .const import CONF_CACHE_EXPIRY_LISTENER
from .const import CONF_CACHE_EXPIRY_DATETIME
from .const import CONF_CACHE_EXPIRY_DOORS
from .const import CONF_CACHE_EXPIRY_INTERLOCK

from .const import CONF_INTERLOCKS
from .const import CONF_ANTIPASSBACK

from .const import DEFAULT_TIMEOUT
from .const import DEFAULT_POLL_CONTROLLERS
from .const import DEFAULT_POLL_DOORS
from .const import DEFAULT_POLL_CARDS
from .const import DEFAULT_POLL_EVENTS
from .const import DEFAULT_MAX_CARDS
from .const import DEFAULT_PREFERRED_CARDS

from .const import DEFAULT_CACHE_EXPIRY_CONTROLLER
from .const import DEFAULT_CACHE_EXPIRY_LISTENER
from .const import DEFAULT_CACHE_EXPIRY_DATETIME
from .const import DEFAULT_CACHE_EXPIRY_DOORS
from .const import DEFAULT_CACHE_EXPIRY_INTERLOCK

from .coordinators.coordinators import Coordinators
from .services.services import Services
from .config import get_all_doors

PLATFORMS = [
    Platform.DATETIME,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.DATE,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.EVENT,
    Platform.SENSOR,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    defaults = {
        CONF_BIND_ADDR: '0.0.0.0',
        CONF_BROADCAST_ADDR: '255.255.255.255:60000',
        CONF_LISTEN_ADDR: '0.0.0.0:60001',
        CONF_DEBUG: False,
        CONF_TIMEZONE: 'Local',
        CONF_TIMEOUT: DEFAULT_TIMEOUT,  # 2.5s
        CONF_MAX_CARDS: DEFAULT_MAX_CARDS,  # 10
        CONF_PREFERRED_CARDS: DEFAULT_PREFERRED_CARDS,
        CONF_PIN_ENABLED: False,
        CONF_POLL_CONTROLLERS: DEFAULT_POLL_CONTROLLERS,  # 30s
        CONF_POLL_DOORS: DEFAULT_POLL_DOORS,  # 30s
        CONF_POLL_CARDS: DEFAULT_POLL_CARDS,  # 30s
        CONF_POLL_EVENTS: DEFAULT_POLL_EVENTS,  # 30s
        CONF_CONTROLLERS: [],

        # caching
        CONF_CACHE_EXPIRY_CONTROLLER: DEFAULT_CACHE_EXPIRY_CONTROLLER,
        CONF_CACHE_EXPIRY_LISTENER: DEFAULT_CACHE_EXPIRY_LISTENER,
        CONF_CACHE_EXPIRY_DATETIME: DEFAULT_CACHE_EXPIRY_DATETIME,
        CONF_CACHE_EXPIRY_DOORS: DEFAULT_CACHE_EXPIRY_DOORS,
        CONF_CACHE_EXPIRY_INTERLOCK: DEFAULT_CACHE_EXPIRY_INTERLOCK,
    }

    if 'uhppoted' in config:
        c = config['uhppoted']
        topics = [
            CONF_BIND_ADDR,
            CONF_BROADCAST_ADDR,
            CONF_LISTEN_ADDR,
            CONF_DEBUG,
            CONF_TIMEZONE,
            CONF_TIMEOUT,
            CONF_MAX_CARDS,
            CONF_PREFERRED_CARDS,
            CONF_PIN_ENABLED,
            CONF_POLL_CONTROLLERS,
            CONF_POLL_DOORS,
            CONF_POLL_CARDS,
            CONF_POLL_EVENTS,
            CONF_CONTROLLERS,

            # caching
            CONF_CACHE_EXPIRY_CONTROLLER,
            CONF_CACHE_EXPIRY_LISTENER,
            CONF_CACHE_EXPIRY_DATETIME,
            CONF_CACHE_EXPIRY_DOORS,
            CONF_CACHE_EXPIRY_INTERLOCK,
        ]

        for v in topics:
            if v in c:
                defaults[v] = c[v]

        if caching := c.get('cache', None):
            if expiry := caching.get('expiry', None):
                defaults[CONF_CACHE_EXPIRY_CONTROLLER] = expiry.get('controller', DEFAULT_CACHE_EXPIRY_CONTROLLER)
                defaults[CONF_CACHE_EXPIRY_LISTENER] = expiry.get('listener', DEFAULT_CACHE_EXPIRY_LISTENER)
                defaults[CONF_CACHE_EXPIRY_DATETIME] = expiry.get('datetime', DEFAULT_CACHE_EXPIRY_DATETIME)
                defaults[CONF_CACHE_EXPIRY_DOORS] = expiry.get('doors', DEFAULT_CACHE_EXPIRY_DOORS)
                defaults[CONF_CACHE_EXPIRY_INTERLOCK] = expiry.get('interlock', DEFAULT_CACHE_EXPIRY_INTERLOCK)

    _LOGGER.info(f'default bind address:        {defaults[CONF_BIND_ADDR]}')
    _LOGGER.info(f'default broadcast address:   {defaults[CONF_BROADCAST_ADDR]}')
    _LOGGER.info(f'default listen address:      {defaults[CONF_LISTEN_ADDR]}')
    _LOGGER.info(f'default debug:               {defaults[CONF_DEBUG]}')
    _LOGGER.info(f'default timezone:            {defaults[CONF_TIMEZONE]}')
    _LOGGER.info(f'default timeout:             {defaults[CONF_TIMEOUT]}s')
    _LOGGER.info(f'max. cards:                  {defaults[CONF_MAX_CARDS]}')
    _LOGGER.info(f'preferred cards:             {defaults[CONF_PREFERRED_CARDS]}')
    _LOGGER.info(f'PIN enabled:                 {defaults[CONF_PIN_ENABLED]}')
    _LOGGER.info(f'poll interval - controllers: {defaults[CONF_POLL_CONTROLLERS]}')
    _LOGGER.info(f'poll interval - doors:       {defaults[CONF_POLL_DOORS]}s')
    _LOGGER.info(f'poll interval - cards:       {defaults[CONF_POLL_CARDS]}s')
    _LOGGER.info(f'poll interval - events:      {defaults[CONF_POLL_EVENTS]}s')
    _LOGGER.info(f'controllers:                 {defaults[CONF_CONTROLLERS]}')

    # caching
    _LOGGER.info(f'cache.expiry - controller:   {defaults[CONF_CACHE_EXPIRY_CONTROLLER]}')
    _LOGGER.info(f'cache.expiry - listener:     {defaults[CONF_CACHE_EXPIRY_LISTENER]}')
    _LOGGER.info(f'cache.expiry - date/time:    {defaults[CONF_CACHE_EXPIRY_DATETIME]}')
    _LOGGER.info(f'cache.expiry - doors:        {defaults[CONF_CACHE_EXPIRY_DOORS]}')
    _LOGGER.info(f'cache.expiry - interlock:    {defaults[CONF_CACHE_EXPIRY_INTERLOCK]}')

    hass.data.setdefault(DOMAIN, defaults)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # ... pre-load: start data coordinators
    Coordinators.initialise(hass, entry.entry_id, entry.options)

    await Coordinators.controllers(entry.entry_id).async_config_entry_first_refresh()
    await Coordinators.doors(entry.entry_id).async_config_entry_first_refresh()
    await Coordinators.cards(entry.entry_id).async_config_entry_first_refresh()
    await Coordinators.events(entry.entry_id).async_config_entry_first_refresh()

    # ... load entities
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # ... post-load: start services and register unload listener
    Services.initialise(hass, entry.entry_id, entry.options)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # ... pre-unload: remove service endpoints
    Services.unload(hass, entry.entry_id)

    # ... unload
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # ... post-unload: shut down data-coordinators
    Coordinators.unload(entry.entry_id)

    return ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
