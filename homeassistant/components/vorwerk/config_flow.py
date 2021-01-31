"""Config flow to configure Vorwerk integration."""
import logging
from typing import Any, Dict

from pybotvac.exceptions import NeatoException
from requests.models import HTTPError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_CODE, CONF_EMAIL, CONF_TOKEN

from . import authsession

# pylint: disable=unused-import
from .const import (
    VORWERK_DOMAIN,
    VORWERK_ROBOT_ENDPOINT,
    VORWERK_ROBOT_NAME,
    VORWERK_ROBOT_SECRET,
    VORWERK_ROBOT_SERIAL,
    VORWERK_ROBOT_TRAITS,
    VORWERK_ROBOTS,
)

DOCS_URL = "https://www.home-assistant.io/integrations/vorwerk"

_LOGGER = logging.getLogger(__name__)


class VorwerkConfigFlow(config_entries.ConfigFlow, domain=VORWERK_DOMAIN):
    """Vorwerk integration config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._session = authsession.VorwerkSession()

    async def async_step_user(self, user_input=None):
        """Step when user initializes a integration."""

        errors = {}

        if user_input is not None:
            email = user_input.get(CONF_EMAIL)
            if email:
                await self.async_set_unique_id(email)
                self._abort_if_unique_id_configured()

                code = user_input.get(CONF_CODE)
                if code:
                    try:
                        self._session.fetch_token_passwordless(email, code)
                        robots = [
                            {
                                VORWERK_ROBOT_NAME: robot["name"],
                                VORWERK_ROBOT_SERIAL: robot["serial"],
                                VORWERK_ROBOT_SECRET: robot["secret_key"],
                                VORWERK_ROBOT_TRAITS: robot["traits"],
                                VORWERK_ROBOT_ENDPOINT: robot["nucleo_url"],
                            }
                            for robot in self._session.get("users/me/robots").json()
                        ]
                        data = {
                            CONF_EMAIL: email,
                            CONF_TOKEN: self._session.token,
                            VORWERK_ROBOTS: robots,
                        }
                        return self.async_create_entry(
                            title=email,
                            data=data,
                        )
                    except (HTTPError, NeatoException):
                        errors["base"] = "invalid_auth"

                self._session.send_email_otp(email)

                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_EMAIL, default=email): str,
                            vol.Required(CONF_CODE): str,
                        }
                    ),
                    description_placeholders={"docs_url": DOCS_URL},
                    errors=errors,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                }
            ),
            description_placeholders={"docs_url": DOCS_URL},
            errors=errors,
        )

    async def async_step_import(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Import a config flow from configuration."""
        unique_id = "from configuration"
        data = {VORWERK_ROBOTS: user_input}

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(data)

        _LOGGER.info("Creating new Vorwerk robot config entry")
        return self.async_create_entry(
            title="from configuration",
            data=data,
        )
