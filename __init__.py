"""The CleverSpa integration."""
import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import (
    DOMAIN,
    CONF_TOKEN,
    CONF_DID,
    CONF_DEVICE_INFO,
    CONF_MODEL,
    CONF_SWVER,
    DEFAULT_NAME,
    MANUFACTURER,
    MAP_NAMES
)
from .cleverspa.control import control as cleverspa_control

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ['sensor', 'binary_sensor', 'switch', 'water_heater']

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
        self.token = entry.data[CONF_TOKEN]
        self.device_id = entry.data[CONF_DEVICE_INFO][CONF_DID]
        self.client = cleverspa_control(self.token)
        #self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=f"CleverSpa data measure for {self.device_id}",
            update_interval=timedelta(seconds=15),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        return await self.hass.async_add_executor_job(
            self.client.get_data, self.device_id
        )


class CleverSpaEntity(CoordinatorEntity):
    """Implements a common class elements representing the CleverSpa component."""

    def __init__(self, coordinator, device, info_type):
        """Initialize CleverSpa sensor."""
        super().__init__(coordinator)
        self.hass = coordinator.hass
        self.device_id = device[CONF_DID]
        self.info_type = info_type
        self._attr_unique_id = f'{self.device_id}-{self.info_type}'
        self.entity_id = f'{DOMAIN}.{DOMAIN}_{self.device_id}_{self.info_type}'
        self._attr_device_info = {
            "name": DEFAULT_NAME,
            "identifiers": {
                (DOMAIN, self.device_id)
            },
            "manufacturer": MANUFACTURER,
            "model": device[CONF_MODEL],
            "sw_version": device[CONF_SWVER]
        }
