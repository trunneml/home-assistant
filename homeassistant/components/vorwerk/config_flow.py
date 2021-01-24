"""Config flow to configure Vorwerk integration."""

import logging

from pybotvac import Account, Vorwerk
from pybotvac.exceptions import NeatoLoginException, NeatoRobotException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

# pylint: disable=unused-import
from .const import VORWERK_DOMAIN

DOCS_URL = "https://www.home-assistant.io/integrations/neato"

_LOGGER = logging.getLogger(__name__)


class VorwerkConfigFlow(config_entries.ConfigFlow, domain=VORWERK_DOMAIN):
    """Vorwerk integration config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize flow."""
        self._username = vol.UNDEFINED
        self._password = vol.UNDEFINED

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            self._username = user_input["username"]
            self._password = user_input["password"]
            error = await self.hass.async_add_executor_job(
                self.try_login, self._username, self._password
            )
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                    description_placeholders={"docs_url": DOCS_URL},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            description_placeholders={"docs_url": DOCS_URL},
            errors=errors,
        )

    async def async_step_import(self, user_input):
        """Import a config flow from configuration."""

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]
        error = await self.hass.async_add_executor_job(
            self.try_login, username, password
        )
        if error is not None:
            _LOGGER.error(error)
            return self.async_abort(reason=error)

        return self.async_create_entry(
            title=f"{username} (from configuration)",
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
            },
        )

    @staticmethod
    def try_login(username, password):
        """Try logging in to device and return any errors."""
        try:
            # TODO: Passwordless Auth is needed here
            Account(username, password, Vorwerk())
        except NeatoLoginException:
            return "invalid_auth"
        except NeatoRobotException:
            return "unknown"

        return None
