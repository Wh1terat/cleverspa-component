"""Platform for CleverSpa sensor integration."""
from __future__ import annotations
from homeassistant.components.switch import (
        SwitchEntity,
        DEVICE_CLASS_SWITCH
)
from . import CleverSpaEntity
from .const import DOMAIN, CONF_DEVICE_INFO, MAP_NAMES

SWITCHES = {
        'filter': {
            'name': 'Filter',
            'icon': 'mdi:air-filter',
            'device_class': DEVICE_CLASS_SWITCH
        },
        'bubbles': {
            'name': 'Bubbles',
            'icon': 'mdi:chart-bubble',
            'device_class': DEVICE_CLASS_SWITCH,
        },
        'heater': {
            'name': 'Heater',
            'icon': 'mdi:fire',
            'device_class': DEVICE_CLASS_SWITCH,
        }
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config_entry.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    switch_list = []
    for switch in SWITCHES:
        switch_list.append(CleverSpaSwitchEntity(coordinator, device, switch))

    async_add_entities(switch_list, True)


class CleverSpaSwitchEntity(CleverSpaEntity, SwitchEntity):
    """Switch representing CleverSpa buttons."""

    @property
    def name(self) -> str | None:
        """Return the name of the particular component."""
        return f"CleverSpa {SWITCHES[self.info_type]['name']}"

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return SWITCHES[self.info_type]["icon"]

    @property
    def is_on(self) -> bool | None:
        """State of the sensor."""
        return self.coordinator.data[MAP_NAMES[self.info_type]]

    async def async_turn_on(self):
        """Turn on."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            {MAP_NAMES[self.info_type]: 1}
        )

    async def async_turn_off(self):
        """Turn off."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            {MAP_NAMES[self.info_type]: 0}
        )
