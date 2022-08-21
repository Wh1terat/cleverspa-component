"""Platform for CleverSpa binary_sensor integration."""
from __future__ import annotations
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_PROBLEM,
)
from homeassistant.const import CONF_ID, CONF_NAME, CONF_ICON, CONF_DEVICE_CLASS
from .const import (
    DOMAIN,
    CONF_DEVICE_INFO,
)
from . import CleverSpaEntity

BINARY_SENSORS = [
    {
        CONF_ID: "filter_warning",
        CONF_NAME: "Replace Filter Warning",
        CONF_ICON: "mdi:sync-alert",
        CONF_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
    },
    {
        CONF_ID: "freeze_warning",
        CONF_NAME: "Freeze Warning",
        CONF_ICON: "mdi:snowflake-alert",
        CONF_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
    },
    {
        CONF_ID: "overheat_warning",
        CONF_NAME: "Overheat Warning",
        CONF_ICON: "mdi:fire-alert",
        CONF_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
    },
]


async def async_setup_entry(hass, config, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config.entry_id]

    sensors_list = []
    for sensor in BINARY_SENSORS:
        sensors_list.append(CleverSpaBinarySensor(coordinator, device, sensor))

    async_add_entities(sensors_list, True)


class CleverSpaBinarySensor(CleverSpaEntity, BinarySensorEntity):
    """Sensor representing CleverSpa data."""

    @property
    def is_on(self) -> bool:
        """State of the sensor."""
        return self.coordinator.data[self.info_type[CONF_ID]]

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return self.info_type[CONF_DEVICE_CLASS]
