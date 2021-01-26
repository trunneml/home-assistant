"""Config flow to configure Vorwerk integration."""

import logging
from typing import Any, Dict


from homeassistant import config_entries

# pylint: disable=unused-import
from .const import VORWERK_DOMAIN, VORWERK_ROBOT_NAME, VORWERK_ROBOT_SERIAL, VORWERK_ROBOT_TRAITS

DOCS_URL = "https://www.home-assistant.io/integrations/neato"

_LOGGER = logging.getLogger(__name__)


class VorwerkConfigFlow(config_entries.ConfigFlow, domain=VORWERK_DOMAIN):
    """Vorwerk integration config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_import(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Import a config flow from configuration."""
        name: str =  user_input[VORWERK_ROBOT_NAME]
        serial: str = user_input[VORWERK_ROBOT_SERIAL]

        if self.robot_exists(serial):
            _LOGGER.debug("Vorwerk robot with serial already configured", serial)
            return self.async_abort(reason="already_configured")

        _LOGGER.info("Creating new Vorwerk robot config entry: %s/%s", name, serial)
        return self.async_create_entry(
            title=f"{name} (from configuration)",
            data=user_input,
        )

    def robot_exists(self, robot_serial: str) -> bool:
        for entry in self._async_current_entries():
            if robot_serial == entry.data.get(VORWERK_ROBOT_SERIAL):
                return True
        return False
