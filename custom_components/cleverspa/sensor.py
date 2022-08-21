"""Platform for CleverSpa sensor integration."""
from __future__ import annotations
from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    CONF_ICON,
    CONF_DEVICE_CLASS,
    CONF_UNIT_OF_MEASUREMENT,
    TIME_MINUTES,
)
from .const import (
    DOMAIN,
    CONF_DEVICE_INFO,
)
from . import CleverSpaEntity

SENSORS = [
    {
        CONF_ID: "filter_time",
        CONF_NAME: "Filter Age",
        CONF_ICON: "mdi:history",
        CONF_UNIT_OF_MEASUREMENT: TIME_MINUTES,
        CONF_DEVICE_CLASS: None,
    }
]


async def async_setup_entry(hass, config, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config.entry_id]

    sensors_list = []
    for sensor in SENSORS:
        sensors_list.append(CleverSpaSensor(coordinator, device, sensor))

    async_add_entities(sensors_list, True)


class CleverSpaSensor(CleverSpaEntity, SensorEntity):
    """Sensor representing CleverSpa data."""

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return self.info_type[CONF_DEVICE_CLASS]

    @property
    def native_value(self) -> str:
        """State of the sensor."""
        return self.coordinator.data[self.info_type[CONF_ID]]

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        return self.info_type[CONF_UNIT_OF_MEASUREMENT]
