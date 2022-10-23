"""Config flow for Subaru integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from subarulink import (
    Controller as SubaruAPI,
    InvalidCredentials,
    InvalidPIN,
    SubaruException,
)
from subarulink.const import COUNTRY_CAN, COUNTRY_USA
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import CONF_COUNTRY, CONF_NOTIFICATION_OPTION, CONF_POLLING_OPTION, DOMAIN
from .options import NotificationOptions, PollingOptions

_LOGGER = logging.getLogger(__name__)

CONF_CONTACT_METHOD = "contact_method"
CONF_VALIDATION_CODE = "validation_code"


class SubaruConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Subaru."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    controller: SubaruAPI

    def __init__(self) -> None:
        """Initialize config flow."""
        self.config_data = {CONF_PIN: None}
        self.controller = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the start of the config flow."""
        error = None

        if user_input:
            if user_input[CONF_USERNAME] in [
                entry.data[CONF_USERNAME] for entry in self._async_current_entries()
            ]:
                return self.async_abort(reason="already_configured")

            try:
                await self.validate_login_creds(user_input)
            except InvalidCredentials:
                error = {"base": "invalid_auth"}
            except SubaruException as ex:
                _LOGGER.error("Unable to communicate with Subaru API: %s", ex.message)
                return self.async_abort(reason="cannot_connect")
            else:
                if not self.controller.device_registered:
                    _LOGGER.debug("2FA validation is required")
                    return await self.async_step_two_factor()
                if self.controller.is_pin_required():
                    return await self.async_step_pin()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=self.config_data
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=user_input.get(CONF_USERNAME) if user_input else "",
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=user_input.get(CONF_PASSWORD) if user_input else "",
                    ): str,
                    vol.Required(
                        CONF_COUNTRY,
                        default=user_input.get(CONF_COUNTRY)
                        if user_input
                        else COUNTRY_USA,
                    ): vol.In([COUNTRY_CAN, COUNTRY_USA]),
                }
            ),
            errors=error,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def validate_login_creds(self, data: dict[str, Any]) -> None:
        """Validate the user input allows us to connect.

        data: contains values provided by the user.
        """
        websession = aiohttp_client.async_get_clientsession(self.hass)
        now = datetime.now()
        if not data.get(CONF_DEVICE_ID):
            data[CONF_DEVICE_ID] = int(now.timestamp())
        date = now.strftime("%Y-%m-%d")
        device_name = "Home Assistant: Added " + date

        self.controller = SubaruAPI(
            websession,
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
            device_id=data[CONF_DEVICE_ID],
            pin=None,
            device_name=device_name,
            country=data[CONF_COUNTRY],
        )
        _LOGGER.debug("Setting up first time connection to Subaru API.")
        if await self.controller.connect():
            _LOGGER.debug("Successfully authenticated with Subaru API")
            self.config_data.update(data)

    async def async_step_two_factor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select contact method and request 2FA code from Subaru."""
        error = None
        if user_input:
            selected_method = next(
                k
                for k, v in self.controller.contact_methods.items()
                if v == user_input[CONF_CONTACT_METHOD]
            )
            if await self.controller.request_auth_code(selected_method):
                return await self.async_step_two_factor_validate()
            raise SubaruException("2FA request failed")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CONTACT_METHOD): vol.In(
                    list(self.controller.contact_methods.values())
                )
            }
        )
        return self.async_show_form(
            step_id="two_factor", data_schema=data_schema, errors=error
        )

    async def async_step_two_factor_validate(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Validate received 2FA code with Subaru."""
        error = None
        if user_input:
            try:
                vol.Match(r"^[0-9]{6}$")(user_input[CONF_VALIDATION_CODE])
                if await self.controller.submit_auth_code(
                    user_input[CONF_VALIDATION_CODE]
                ):
                    if self.controller.is_pin_required():
                        return await self.async_step_pin()
                    return self.async_create_entry(
                        title=self.config_data[CONF_USERNAME], data=self.config_data
                    )
                error = {"base": "incorrect_validation_code"}
            except vol.Invalid:
                error = {"base": "bad_validation_code_format"}

        data_schema = vol.Schema({vol.Required(CONF_VALIDATION_CODE): str})
        return self.async_show_form(
            step_id="two_factor_validate", data_schema=data_schema, errors=error
        )

    async def async_step_pin(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle second part of config flow, if required."""
        error = None
        if user_input:
            if self.controller.update_saved_pin(user_input[CONF_PIN]):
                try:
                    await self.controller.test_pin()
                    _LOGGER.debug("PIN successfully tested")
                    self.config_data.update(user_input)
                except InvalidPIN:
                    error = {"base": "incorrect_pin"}
                else:
                    return self.async_create_entry(
                        title=self.config_data[CONF_USERNAME], data=self.config_data
                    )
        data_schema = vol.Schema({vol.Required(CONF_PIN): str})
        return self.async_show_form(
            step_id="pin", data_schema=data_schema, errors=error
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an option flow for Subaru."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POLLING_OPTION,
                    default=self.config_entry.options.get(
                        CONF_POLLING_OPTION, PollingOptions.DISABLE.value
                    ),
                ): vol.In(sorted(PollingOptions.list())),
                vol.Required(
                    CONF_NOTIFICATION_OPTION,
                    default=self.config_entry.options.get(
                        CONF_NOTIFICATION_OPTION, NotificationOptions.DISABLE.value
                    ),
                ): vol.In(sorted(NotificationOptions.list())),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
