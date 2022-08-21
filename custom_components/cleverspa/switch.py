"""Platform for CleverSpa sensor integration."""
from __future__ import annotations
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_SWITCH
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    CONF_ICON,
    CONF_DEVICE_CLASS,
    CONF_COMMAND_ON,
    CONF_COMMAND_OFF,
)
from .const import DOMAIN, CONF_DEVICE_INFO, MAP_KEYS_INV
from . import CleverSpaEntity

SWITCHES = [
    {
        CONF_ID: "filter",
        CONF_NAME: "Filter",
        CONF_ICON: "mdi:air-filter",
        CONF_DEVICE_CLASS: DEVICE_CLASS_SWITCH,
        CONF_COMMAND_ON: [{MAP_KEYS_INV["filter"]: 1}],
        CONF_COMMAND_OFF: [{MAP_KEYS_INV["filter"]: 0}],
    },
    {
        CONF_ID: "bubbles",
        CONF_NAME: "Bubbles",
        CONF_ICON: "mdi:chart-bubble",
        CONF_DEVICE_CLASS: DEVICE_CLASS_SWITCH,
        CONF_COMMAND_ON: [{MAP_KEYS_INV["bubbles"]: 1}],
        CONF_COMMAND_OFF: [{MAP_KEYS_INV["bubbles"]: 0}],
    },
]


async def async_setup_entry(hass, config, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config.entry_id]

    switch_list = []
    for switch in SWITCHES:
        switch_list.append(CleverSpaSwitchEntity(coordinator, device, switch))

    async_add_entities(switch_list, True)


class CleverSpaSwitchEntity(CleverSpaEntity, SwitchEntity):
    """Switch representing CleverSpa buttons."""

    @property
    def is_on(self) -> bool | None:
        """State of the sensor."""
        return self.coordinator.data[self.info_type[CONF_ID]]

    async def async_turn_on(self):
        """Turn on."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            self.info_type[CONF_COMMAND_ON],
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        """Turn off."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            self.info_type[CONF_COMMAND_OFF],
        )
        await self.coordinator.async_request_refresh()
