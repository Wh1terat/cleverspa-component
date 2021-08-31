"""Platform for CleverSpa binary_sensor integration."""
from __future__ import annotations
from homeassistant.components.binary_sensor import (
        BinarySensorEntity,
        DEVICE_CLASS_PROBLEM
)
from . import CleverSpaEntity
from .const import DOMAIN, CONF_DEVICE_INFO, MAP_NAMES

BINARY_SENSORS = {
    'filter_warning': {
        'name': 'Replace Filter Warning',
        'icon': 'mdi:sync-alert',
        'device_class': DEVICE_CLASS_PROBLEM
    },
    'freeze_warning': {
        'name': 'Freeze Warning',
        'icon': 'mdi:snowflake-alert',
        'device_class': DEVICE_CLASS_PROBLEM,
    },
    'overheat_warning': {
        'name': 'Overheat Warning',
        'icon': 'mdi:fire-alert',
        'device_class': DEVICE_CLASS_PROBLEM,
    }
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config_entry.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors_list = []
    for sensor in BINARY_SENSORS:
        sensors_list.append(CleverSpaBinarySensor(coordinator, device, sensor))

    async_add_entities(sensors_list, True)


class CleverSpaBinarySensor(CleverSpaEntity, BinarySensorEntity):
    """Sensor representing CleverSpa data."""

    @property
    def name(self) -> str | None:
        """Return the name of the particular component."""
        return f"CleverSpa {BINARY_SENSORS[self.info_type]['name']}"

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return BINARY_SENSORS[self.info_type]['icon']

    @property
    def is_on(self) -> bool:
        """State of the sensor."""
        return self.coordinator.data[MAP_NAMES[self.info_type]]

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return BINARY_SENSORS[self.info_type]['device_class']
