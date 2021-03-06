"""Config flow for CleverSpa integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from requests.exceptions import HTTPError, Timeout

from homeassistant import config_entries
from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_DEVICE,
    CONF_DEVICE_ID,
    CONF_FRIENDLY_NAME,
    CONF_TOKEN,
    CONF_AUTHENTICATION,
    ATTR_MODEL
)
from .const import (
    DOMAIN,
    CONF_DEVICE_INFO,
    CONF_TOKEN_EXPIRY,
    MAP_KEYS,
    DEFAULT_NAME
)

from .cleverspa.auth import auth as cleverspa_auth
from .cleverspa.control import control as cleverspa_control
from .cleverspa.errors import AuthError

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CleverSpa."""

    _email: str | None = None
    _password: str | None = None
    _auth: dict | None = None
    _reauth: bool | None = None
    _device: str | None = None
    _devices: list | None = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self._show_setup_form()

        self._email = user_input[CONF_EMAIL]
        self._password = user_input[CONF_PASSWORD]

        errors = {}
        if not self._auth:
            try:
                self._auth = await self.hass.async_add_executor_job(
                    cleverspa_auth.login,
                    self._email,
                    self._password
                )
            except (HTTPError, AuthError):
                errors["base"] = 'invalid_auth'
            except (Timeout, ConnectionError):
                errors["base"] = 'cannot_connect'
            if not errors and not self._auth:
                errors["base"] = 'unknown'            
            if errors:
                return self._show_setup_form(errors)

        controller = cleverspa_control(self._auth[CONF_TOKEN])
        raw_devices = await self.hass.async_add_executor_job(controller.get_devices)
        devices = [
            {MAP_KEYS.get(k, k): v for k, v in device.items()}
            for device in raw_devices
        ]

        # If multiple devices are found (unusual for this component)
        # ask the user to choose one in a select box.
        if len(devices) > 1:
            self._devices = devices
            return await self.async_step_devices()
        else:
            self._device = devices[0]

        # Check if already configured
        existing_entry = await self.async_set_unique_id(self._device[CONF_DEVICE_ID])
        if existing_entry:
            if self._reauth:
                self.hass.config_entries.async_update_entry(
                    existing_entry,
                    data={
                        CONF_AUTHENTICATION: self._auth
                    }
                )
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            else:
                self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._device[CONF_FRIENDLY_NAME] or DEFAULT_NAME,
            data={
                CONF_AUTHENTICATION: self._auth,
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
            device_label = f'{ATTR_MODEL}-{CONF_DEVICE_ID}'
            device_list = [device_label.format(**device) for device in self._devices]
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
            if user_input[CONF_DEVICE].endswith(device[CONF_DEVICE_ID])
        )
        return await self.async_step_user(user_input)

        
        async def async_step_reauth(self, user_input=None):
            """Perform reauth upon an token expiry."""
            self._auth = None
            self._reauth = True
            return await self.async_step_reauth_confirm()


        async def async_step_reauth_confirm(self, user_input=None):
            """Dialog that informs the user that reauth is required."""
            if user_input is None:
                return self.async_show_form(
                    step_id='reauth_configm',
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_EMAIL): str,
                            vol.Required(CONF_PASSWORD): str
                        }
                    ),
                    errors=errors,
                )
            return await self.async_step_user(user_input)        
