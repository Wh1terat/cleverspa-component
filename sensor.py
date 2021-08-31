"""Platform for CleverSpa sensor integration."""
from __future__ import annotations
from homeassistant.components.sensor import (
        SensorEntity,
)
from . import CleverSpaEntity
from .const import DOMAIN, CONF_DEVICE_INFO, MAP_NAMES

# STATE_CLASS_TOTAL_INCREASING only added recently.
#try:
#    from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
#except ModuleNotFoundError as err:
#    STATE_CLASS_TOTAL_INCREASING = None

SENSORS = {
        'filter_time': {
            'name': 'Filter Age',
            'icon': 'mdi:history',
            'unit': 'Minutes',
            'device_class': None,
            #'state_class': STATE_CLASS_TOTAL_INCREASING
        }
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config_entry.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors_list = []
    for sensor in SENSORS:
        sensors_list.append(CleverSpaSensor(coordinator, device, sensor))

    async_add_entities(sensors_list, True)


class CleverSpaSensor(CleverSpaEntity, SensorEntity):
    """Sensor representing CleverSpa data."""

    @property
    def name(self) -> str | None:
        """Return the name of the particular component."""
        return f"CleverSpa {SENSORS[self.info_type]['name']}"

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return SENSORS[self.info_type]['icon']

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return SENSORS[self.info_type]['device_class']

    @property
    def native_value(self) -> str:
        """State of the sensor."""
        return self.coordinator.data[MAP_NAMES[self.info_type]]

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        return SENSORS[self.info_type]['unit']
