"""Config flow to configure Vorwerk integration."""

from enum import unique
import logging
from typing import Any, Dict


from homeassistant import config_entries

# pylint: disable=unused-import
from .const import VORWERK_DOMAIN, VORWERK_ROBOTS, VORWERK_ROBOT_NAME, VORWERK_ROBOT_SERIAL, VORWERK_ROBOT_TRAITS

DOCS_URL = "https://www.home-assistant.io/integrations/neato"

_LOGGER = logging.getLogger(__name__)


class VorwerkConfigFlow(config_entries.ConfigFlow, domain=VORWERK_DOMAIN):
    """Vorwerk integration config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_import(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Import a config flow from configuration."""
        unique_id = "from configuration"
        data = {
            VORWERK_ROBOTS: user_input
        }

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(data)

        _LOGGER.info("Creating new Vorwerk robot config entry")
        return self.async_create_entry(
            title="from configuration",
            data=data,
        )
