"""The CleverSpa integration."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    CONF_ICON,
    CONF_TOKEN,
    CONF_DEVICE_ID,
    CONF_UNIQUE_ID,
    CONF_AUTHENTICATION,
    ATTR_IDENTIFIERS,
    ATTR_NAME,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_SW_VERSION,
)
from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_DEVICE_INFO,
    CONF_TOKEN_EXPIRY,
    DEFAULT_NAME,
    MANUFACTURER,
    MAP_KEYS,
    MAP_KEYS_INV,
)
from .cleverspa.control import control as cleverspa_control

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CleverSpa from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = CleverSpaDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class CleverSpaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to hold CleverSpa data retrieval."""

    def __init__(self, hass, entry):
        """Initialize."""
        self._auth = entry.data[CONF_AUTHENTICATION]
        #_LOGGER.warn(entry)
        #_LOGGER.warn(entry.data)
        #self.device_id = entry.data[CONF_DEVICE_INFO][CONF_DEVICE_ID]
        self.device_id = entry.unique_id
        self.client = cleverspa_control(self._auth[CONF_TOKEN])

        super().__init__(
            hass,
            _LOGGER,
            name=f"CleverSpa data measure for {self.device_id}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        if self._auth[CONF_TOKEN_EXPIRY] < int(datetime.now().timestamp()):
            raise ConfigEntryAuthFailed('Token Expired')

        data = await self.hass.async_add_executor_job(
            self.client.get_data, self.device_id
        )
        return {MAP_KEYS.get(k, k): v for k, v in data.items()}


class CleverSpaEntity(CoordinatorEntity):
    """Implements a common class elements representing the CleverSpa component."""

    def __init__(self, coordinator, device, info_type):
        """Initialize CleverSpa sensor."""
        super().__init__(coordinator)
        self.hass = coordinator.hass
        self.device = device
        self.info_type = info_type
        self.entity_id = (
            f"{DOMAIN}.{DOMAIN}_{self.device[CONF_DEVICE_ID]}_{self.info_type[CONF_ID]}"
        )

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the particular component."""
        return f"{self.device[CONF_DEVICE_ID]}-{self.info_type[CONF_ID]}"

    @property
    def name(self) -> str | None:
        """Return the name of the particular component."""
        return f"{DEFAULT_NAME} {self.info_type[CONF_NAME]}"

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return self.info_type[CONF_ICON]

    @property
    def device_info(self) -> dict | None:
        """Return information about the device,"""
        return {
            ATTR_NAME: DEFAULT_NAME,
            ATTR_IDENTIFIERS: {(DOMAIN, self.device[CONF_DEVICE_ID])},
            ATTR_MANUFACTURER: MANUFACTURER,
            ATTR_MODEL: self.device[ATTR_MODEL],
            ATTR_SW_VERSION: self.device[ATTR_SW_VERSION],
        }
