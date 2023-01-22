from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant.const import CONF_NAME
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)
from homeassistant.components.sensor import (
    SensorDeviceClass
)
from homeassistant.helpers import selector
from .const.const import (
    CONF_SOURCES_TOTAL_GAS, CONF_SOURCES_TOTAL_POWER, 
    CONF_SOURCES_TOTAL_SOLAR, DOMAIN
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCES_TOTAL_POWER): selector.EntitySelector(
            selector.EntitySelectorConfig(
                device_class=SensorDeviceClass.ENERGY, multiple=True)
        ),
        vol.Optional(CONF_SOURCES_TOTAL_SOLAR, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(
                device_class=SensorDeviceClass.ENERGY, multiple=True)
        ),
        vol.Required(CONF_SOURCES_TOTAL_GAS): selector.EntitySelector(
            selector.EntitySelectorConfig(
                device_class=SensorDeviceClass.GAS, multiple=True)
        )
    }
)

CONFIG_FLOW = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA)
}

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(CONFIG_SCHEMA),
}

class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for the Prijsplafond sensor."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""

        return DOMAIN