"""Config flow for CleverSpa integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from requests.exceptions import HTTPError, Timeout

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import (
    DOMAIN,
    CONF_TOKEN,
    CONF_DEVICE_INFO,
    CONF_DID,
    CONF_DEVICE,
    DEFAULT_NAME
)

from .cleverspa.auth import auth as cleverspa_auth
from .cleverspa.control import control as cleverspa_control
from .cleverspa.errors import AuthError

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CleverSpa."""

    VERSION = 1

    _email: str | None = None
    _password: str | None = None
    _token: str | None = None
    _device: str | None = None
    _devices: list | None = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self._show_setup_form()

        self._email = user_input[CONF_EMAIL]
        self._password = user_input[CONF_PASSWORD]

        errors = {}
        if not self._token:
            try:
                self._token = await self.hass.async_add_executor_job(
                    cleverspa_auth.login,
                    self._email,
                    self._password
                )
            except (HTTPError, AuthError):
                errors["base"] = 'invalid_auth'
            except (Timeout, ConnectionError):
                errors["base"] = 'cannot_connect'
            if not errors and not self._token:
                errors["base"] = 'invalid_token'
            if errors:
                return self._show_setup_form(errors)

        controller = cleverspa_control(self._token)
        devices = await self.hass.async_add_executor_job(controller.get_devices)

        # If multiple spas found (rare case), ask the user to choose one in a select box.
        if len(devices) > 1:
            self._devices = devices
            return await self.async_step_devices()
        self._device = devices[0]

        # Check if already configured
        await self.async_set_unique_id(self._device[CONF_DID])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._device['dev_alias'] or DEFAULT_NAME,
            data={
                CONF_TOKEN: self._token,
                CONF_DEVICE_INFO: self._device
            },
        )

    def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str
                }
            ),
            errors=errors,
        )

    async def async_step_devices(self, user_input=None):
        """Handle the device selection step."""
        if not user_input:
            device_list = ['{product_name}-{did}'.format(**device) for device in self._devices]

            return self.async_show_form(
                step_id='devices',
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE) : vol.In(device_list)
                    }
                ),
            )

        # Get chosen device.
        self._device = next(
            device
            for device in self._devices
            if user_input[CONF_DEVICE].endswith(device[CONF_DID])
        )

        # Check if already configured
        await self.async_set_unique_id(self._device[CONF_DID])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._device['dev_alias'] or DEFAULT_NAME,
            data={
                CONF_TOKEN: self._token,
                CONF_DEVICE_INFO: self._device
            },
        )
 
