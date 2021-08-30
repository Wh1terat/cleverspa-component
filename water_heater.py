"""Platform for CleverSpa water_heater integration."""
from __future__ import annotations
from homeassistant.const import (
    ATTR_TEMPERATURE,
    STATE_OFF,
    STATE_ON,
    TEMP_CELSIUS,
    PRECISION_WHOLE
)
from homeassistant.components.water_heater import (
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.util.temperature import convert as convert_temperature

from . import CleverSpaEntity
from .const import DOMAIN, CONF_DEVICE_INFO, MAP_NAMES, MIN_TEMP, MAX_TEMP

WATERHEATERS = {
        'water_heater': {
            'name': 'Hot Tub',
            'icon': 'mdi:hot-tub',
        }
}

STATES = [STATE_ON, STATE_OFF]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    device = config_entry.data[CONF_DEVICE_INFO]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    waterheater_list = []
    for waterheater in WATERHEATERS:
        waterheater_list.append(CleverSpaWaterHeater(coordinator, device, waterheater))

    async_add_entities(waterheater_list, True)


class CleverSpaWaterHeater(CleverSpaEntity, WaterHeaterEntity):
    """Sensor representing CleverSpa data."""

    #def __init__(self, coordinator, device, info_type):
    #    super().__init__(coordinator, device, info_type)
    #    self._supported_features = SUPPORT_TARGET_TEMPERATURE

    @property
    def name(self) -> str | None:
        """Return the name of the particular component."""
        return f"CleverSpa {WATERHEATERS[self.info_type]['name']}"

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return WATERHEATERS[self.info_type]['icon']

    @property
    def precision(self) -> float | None:
        """Return the precision of the system."""
        return PRECISION_WHOLE

    @property
    def current_operation(self) -> str | None:
        """Return the current operating mode (On, or Off)."""
        state = self.coordinator.data[MAP_NAMES['heater']]
        return STATE_ON if state else STATE_OFF

    @property
    def operation_list(self) -> list[str] | None:
        """Return the list of available operations."""
        return STATES

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        temp = self.coordinator.data[MAP_NAMES['current_temperature']]
        return convert_temperature(
            temp, TEMP_CELSIUS, self.temperature_unit
        )

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        temp = self.coordinator.data[MAP_NAMES['target_temperature']]
        return convert_temperature(
            temp, TEMP_CELSIUS, self.temperature_unit
        )

    @property
    def min_temp(self) -> float | None:
        """Return the minimum temperature."""
        return convert_temperature(
            MIN_TEMP, TEMP_CELSIUS, self.temperature_unit
        )

    @property
    def max_temp(self) -> float | None:
        """Return the maximum temperature."""
        return convert_temperature(
            MAX_TEMP, TEMP_CELSIUS, self.temperature_unit
        )

    @property
    def temperature_unit(self) -> float:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> list[str]:
        """Return supported features"""
        return SUPPORT_TARGET_TEMPERATURE

    async def async_set_temperature(self, **kwargs):
        """Set a new target temperature for this zone."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_temp,
            self.coordinator.device_id,
            int(kwargs[ATTR_TEMPERATURE])
        )

    async def async_turn_on(self):
        """Turn on."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_heater_on,
            self.coordinator.device_id
        )

    async def async_turn_off(self):
        """Turn off."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_heater_off,
            self.coordinator.device_id
        )
