"""Platform for CleverSpa water_heater integration."""
from __future__ import annotations
from homeassistant.util.temperature import convert as convert_temperature
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
    CONF_ICON,
    CONF_COMMAND_ON,
    CONF_COMMAND_OFF,
    ATTR_TEMPERATURE,
    STATE_OFF,
    TEMP_CELSIUS,
    PRECISION_WHOLE
)
from homeassistant.components.water_heater import (
    STATE_ELECTRIC,        
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from .const import (
    DOMAIN,
    CONF_DEVICE_INFO,
    MAP_KEYS_INV,
    MIN_TEMP,
    MAX_TEMP,
    COOLDOWN_TIME
)
from . import CleverSpaEntity

WATERHEATER = {
    CONF_ID: 'water_heater',
    CONF_NAME: 'Hot Tub',
    CONF_ICON: 'mdi:hot-tub',
    CONF_COMMAND_ON: [
        {MAP_KEYS_INV['heater']: 1}
    ],
    CONF_COMMAND_OFF: [
        {MAP_KEYS_INV['heater']: 0},
        {MAP_KEYS_INV['filter']: 1}
    ],
}

HEATER_ATTRS = [
    'filter_warning',
    'freeze_warning',
    'overheat_warning',
    'filter_time'
]

STATES = [STATE_ELECTRIC, STATE_OFF]

async def async_setup_entry(hass, config, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config.entry_id]
    async_add_entities(
        [CleverSpaWaterHeater(coordinator, device, WATERHEATER)], True
    )


class CleverSpaWaterHeater(CleverSpaEntity, WaterHeaterEntity):
    """Sensor representing CleverSpa data."""

    @property
    def precision(self) -> float | None:
        """Return the precision of the system."""
        return PRECISION_WHOLE

    @property
    def current_operation(self) -> str | None:
        """Return the current operating mode (On, or Off)."""
        state = self.coordinator.data['heater']
        return STATE_ELECTRIC if state else STATE_OFF

    @property
    def operation_list(self) -> list[str] | None:
        """Return the list of available operations."""
        return STATES

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data['current_temperature']

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data['target_temperature']

    @property
    def min_temp(self) -> float | None:
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self) -> float | None:
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def temperature_unit(self) -> float:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> list[str]:
        """Return supported features"""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes of the CleverSpa sensor."""
        return {
            k: v
            for k, v in self.coordinator.data.items()
            if k in HEATER_ATTRS
        }

    async def async_set_temperature(self, **kwargs):
        """Set a new target temperature for the tub."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            {MAP_KEYS_INV['target_temperature']: int(kwargs[ATTR_TEMPERATURE])}
        )

    async def async_turn_on(self):
        """Turn heater and filter on."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            self.info_type[CONF_COMMAND_ON]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        """Turn heater off and filter 30 secs later."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            self.info_type[CONF_COMMAND_OFF]
        )
        # Not sure if this is 'naughty' or not
        self.hass.loop.call_later(
            COOLDOWN_TIME,
            self.hass.async_add_executor_job,
            self.coordinator.client.set_data,
            self.coordinator.device_id,
            {MAP_KEYS_INV['filter']: 0}
        )
        await self.coordinator.async_request_refresh()
