from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.data_entry_flow import FlowHandler
from homeassistant.core import callback
from homeassistant.components.sensor import (
    SensorDeviceClass
)
from homeassistant.helpers import selector
from .const.const import (
    CONF_SOURCES_TOTAL_GAS, CONF_SOURCES_TOTAL_POWER, 
    CONF_SOURCES_TOTAL_SOLAR, DOMAIN, NAME
)

def form(
    flow: FlowHandler,
    step_id: str,
    schema: dict,
    defaults: dict = None,
    template: dict = None,
    error: str = None,
):
    """Suppport:
    - overwrite schema defaults from dict (user_input or entry.options)
    - set base error code (translations > config > error > code)
    - set custom error via placeholders ("template": "{error}")
    """
    if defaults:
        for key in schema:
            if key.schema in defaults:
                key.default = vol.default_factory(defaults[key.schema])

    if template and "error" in template:
        error = {"base": "template"}
    elif error:
        error = {"base": error}

    return flow.async_show_form(
        step_id=step_id,
        data_schema=vol.Schema(schema),
        description_placeholders=template,
        errors=error,
    )

CONFIG_SCHEMA = {
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

class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    async def async_step_import(self, user_input=None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, data=None, error=None):
        if data is not None:
            entry = await self.async_set_unique_id(DOMAIN)
            if entry:
                self.hass.config_entries.async_update_entry(
                    entry, data=data, unique_id=self.unique_id
                )
                return self.async_abort(reason="reconf_successful")

            return self.async_create_entry(title=DOMAIN, data=data)
        return form(self, "user", CONFIG_SCHEMA)