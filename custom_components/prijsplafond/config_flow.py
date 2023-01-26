from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.data_entry_flow import FlowHandler
from homeassistant.core import callback
from homeassistant.components.sensor import (
    SensorDeviceClass
)
from homeassistant.helpers import selector
from .const.const import (
    _LOGGER, CONF_SOURCES_TOTAL_GAS, CONF_SOURCES_TOTAL_POWER, 
    CONF_SOURCES_TOTAL_SOLAR, DOMAIN, NAME
)

SOURCES_TOTAL_POWER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCES_TOTAL_POWER): selector.EntitySelector(
            selector.EntitySelectorConfig(
                device_class=SensorDeviceClass.ENERGY, multiple=True)
        )
    }
)

SOURCES_TOTAL_SOLAR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SOURCES_TOTAL_SOLAR, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(
                device_class=SensorDeviceClass.ENERGY, multiple=True)
        )
    }
)

SOURCES_TOTAL_GAS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCES_TOTAL_GAS): selector.EntitySelector(
            selector.EntitySelectorConfig(
                device_class=SensorDeviceClass.GAS, multiple=True)
        )
    }
)

class PrijsplafondConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._sources_total_power = []
        self._sources_total_solar = []
        self._sources_total_gas = []

    # Method called when an user adds the integration for the first time.
    # Also when deleted and 're-added'.
    async def async_step_user(self, info):
        return await self.async_step_power_consumers()
    
    async def async_step_power_consumers(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._sources_total_power = user_input.get(CONF_SOURCES_TOTAL_POWER, [])
            if not self._sources_total_power:
                errors["base"] = "invalid_sources_total_power"
            else:
                # If we got all power consumers defined, we go to the next step.
                return self.async_show_form(
                    step_id="power_producers", 
                    data_schema=SOURCES_TOTAL_SOLAR_SCHEMA,
                    last_step=False
                )

        # Show the power consumers form.
        return self.async_show_form(
            step_id="power_consumers", 
            data_schema=SOURCES_TOTAL_POWER_SCHEMA, 
            errors=errors,
            last_step=False
        )

    async def async_step_power_producers(self, user_input=None):
        if user_input is not None:
            self._sources_total_solar = user_input.get(CONF_SOURCES_TOTAL_SOLAR, [])

            # If we got all power producers defined, we go to the next step.
            return self.async_show_form(
                step_id="gas_consumers", 
                data_schema=SOURCES_TOTAL_GAS_SCHEMA,
                last_step=True
            )

        # Show the power producers form.
        return self.async_show_form(
            step_id="power_producers", 
            data_schema=SOURCES_TOTAL_SOLAR_SCHEMA,
            last_step=False
        )
        
    async def async_step_gas_consumers(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._sources_total_gas = user_input.get(CONF_SOURCES_TOTAL_GAS, [])
            if not self._sources_total_power:
                errors["base"] = "invalid_sources_total_gas"
            else:
                # If we have all data provided it's time to save to config.
                return self.async_create_entry(title=DOMAIN, data=self._get_data())

        # Show the power consumers form.
        return self.async_show_form(
            step_id="gas_consumers", 
            data_schema=SOURCES_TOTAL_GAS_SCHEMA, 
            errors=errors,
            last_step=True
        )

    def _get_data(self):
        return {
            CONF_SOURCES_TOTAL_POWER: self._sources_total_power,
            CONF_SOURCES_TOTAL_SOLAR: self._sources_total_solar,
            CONF_SOURCES_TOTAL_GAS: self._sources_total_gas
        }


class PrijplafondOptionsFlow(OptionsFlow):

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.updated_config: dict[str, Any] = {}

    # Method called when an user clicks on the configure button. Which can be
    # found on the integrations page. This option can be used to reconfigure 
    # the configuration provided earlier by the async_step_user method.
    async def async_step_init(self, user_input=None):
        return await self.async_step_power_consumers()

    async def async_step_power_consumers(self, user_input=None):
        errors = {}
        current_config = self.config_entry.data

        if user_input is not None:
            sources_total_power = user_input.get(CONF_SOURCES_TOTAL_POWER, [])
            if not sources_total_power:
                errors["base"] = "invalid_sources_total_power"
            else:
                self.updated_config = dict(current_config)
                self.updated_config[CONF_SOURCES_TOTAL_POWER] = sources_total_power

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=self.updated_config
                )

                # If we got all power consumers defined, we go to the next step.
                return self.async_show_form(
                    step_id="power_producers", 
                    data_schema=SOURCES_TOTAL_SOLAR_SCHEMA,
                    last_step=False
                )

        # Show the power consumers form.
        return self.async_show_form(
            step_id="power_consumers", 
            data_schema=SOURCES_TOTAL_POWER_SCHEMA, 
            errors=errors,
            last_step=False
        )

    async def async_step_power_producers(self, user_input=None):
        if user_input is not None:
            self.updated_config[CONF_SOURCES_TOTAL_SOLAR] = user_input.get(CONF_SOURCES_TOTAL_SOLAR, [])

            self.hass.config_entries.async_update_entry(
                self.config_entry, data=self.updated_config
            )

            # If we got all power producers defined, we go to the next step.
            return self.async_show_form(
                step_id="gas_consumers", 
                data_schema=SOURCES_TOTAL_GAS_SCHEMA,
                last_step=True
            )

        # Show the power producers form.
        return self.async_show_form(
            step_id="power_producers", 
            data_schema=SOURCES_TOTAL_SOLAR_SCHEMA,
            last_step=False
        )

    async def async_step_gas_consumers(self, user_input=None):
        errors = {}
        if user_input is not None:
            sources_total_gas = user_input.get(CONF_SOURCES_TOTAL_GAS, [])
            if not sources_total_gas:
                errors["base"] = "invalid_sources_total_gas"
            else:
                self.updated_config[CONF_SOURCES_TOTAL_GAS] = sources_total_gas

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=self.updated_config
                )

                return self.async_create_entry(title="", data=None)

        # Show the power consumers form.
        return self.async_show_form(
            step_id="gas_consumers", 
            data_schema=SOURCES_TOTAL_GAS_SCHEMA, 
            errors=errors,
            last_step=True
        )