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

    async def async_step_user(self, info):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_power_consumers()
    
    async def async_step_power_consumers(self, user_input=None):
        if user_input is not None:
            _LOGGER.error(user_input)

            # If we got all power consumers defined, we go to the next step.
            return self.async_show_form(
                step_id="power_producers", data_schema=SOURCES_TOTAL_SOLAR_SCHEMA
            )


        # Show the power consumers form.
        return self.async_show_form(
            step_id="power_consumers", data_schema=SOURCES_TOTAL_POWER_SCHEMA
        )

        # # Show the gas consumers form.
        # return self.async_show_form(
        #     step_id="gas_consumers", data_schema=SOURCES_TOTAL_GAS_SCHEMA
        # )

    async def async_step_power_producers(self, user_input=None):
        if user_input is not None:
            _LOGGER.error(user_input)

            # If we got all power producers defined, we go to the next step.
            return self.async_show_form(
                step_id="gas_consumers", data_schema=SOURCES_TOTAL_GAS_SCHEMA
            )

        # Show the power producers form.
        return self.async_show_form(
            step_id="power_producers", data_schema=SOURCES_TOTAL_SOLAR_SCHEMA
        )
        
    async def async_step_gas_consumers(self, user_input=None):
        if user_input is not None:
            _LOGGER.error("FINAL STEP..!")
            _LOGGER.error(user_input)

    def _get_data(self):
        return {
            CONF_SOURCES_TOTAL_POWER: self._sources_total_power,
            CONF_SOURCES_TOTAL_SOLAR: self._sources_total_solar,
            CONF_SOURCES_TOTAL_GAS: self._sources_total_gas
        }