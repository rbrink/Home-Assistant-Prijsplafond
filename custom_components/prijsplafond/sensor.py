from __future__ import annotations
"""
Sensor component for Prijsplafond
Author: Richard Brink
"""

from datetime import datetime
import logging
from typing import Any
from _sha1 import sha1
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    STATE_CLASS_MEASUREMENT
)
from homeassistant.config_entries import ConfigEntry
from .const.const import (
    _LOGGER,
    ATTR_FRIENDLY_NAME,
    ATTR_THIS_MONTH_CAP,
    ATTR_THIS_MONTH_COSTS,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_SOURCES_TOTAL_GAS,
    CONF_SOURCES_TOTAL_POWER,
    CONF_SOURCES_TOTAL_SOLAR,
    DOMAIN,
    GAS_PRICE,
    ICON,
    POWER_PRICE,
    PRECISION,
    PRICE_CAP_GAS_MONTH,
    PRICE_CAP_POWER_MONTH,
    UNIT_OF_MEASUREMENT_GAS,
    UNIT_OF_MEASUREMENT_POWER
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(
        [
            PrijsplafondSensor(
                hass,
                "power",
                config_entry.data.get(CONF_SOURCES_TOTAL_POWER),
                config_entry.data.get(CONF_SOURCES_TOTAL_SOLAR)
            ),

            PrijsplafondSensor(
                hass,
                "gas",
                config_entry.data.get(CONF_SOURCES_TOTAL_GAS)
            )
        ]
    )

async def async_setup_platform(
    hass: HomeAssistant, 
    config: ConfigType, 
    async_add_entities: AddEntitiesCallback, 
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    if discovery_info is None:
        _LOGGER.error(
            "This platform is not available to configure "
            "from 'sensor:' in configuration.yaml"
        )
        return

class PrijsplafondSensor(RestoreSensor):
    def __init__(
        self, 
        hass: HomeAssistant,
        type,
        positive_entities,
        negative_entities = []
    ):
        # Common.
        self.entity_id = f"sensor.{DOMAIN}_{type}"
        self.friendly_name = f"{type.capitalize()} usage this month"
        
        # Sensor specific.
        self.this_month_costs = 0
        self._pos_sources = positive_entities
        self._neg_sources = negative_entities

        if type == 'gas':
            self.this_month_cap = PRICE_CAP_GAS_MONTH[self._current_month]
            self._price = GAS_PRICE

            # Entity specific.
            self.device_class = SensorDeviceClass.GAS
            self.unit_of_measurement = UNIT_OF_MEASUREMENT_GAS
        else:
            self.this_month_cap = PRICE_CAP_POWER_MONTH[self._current_month]
            self._price = POWER_PRICE

            # Entity specific.
            self.device_class = SensorDeviceClass.ENERGY
            self.unit_of_measurement = UNIT_OF_MEASUREMENT_POWER

        self._state = 100

    @property
    def unique_id(self):
        return str(
            sha1(
                ";".join(
                    [str(type), ",".join(self._pos_sources), ",".join(self._neg_sources)]
                ).encode("utf-8")
            ).hexdigest()
        )

    @property
    def name(self):
        return self.friendly_name

    @property
    def icon(self):
        return ICON

    @property
    def state(self):
        return round(self._state, PRECISION)

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def extra_state_attributes(self):
        return {
            ATTR_FRIENDLY_NAME: self.friendly_name,
            ATTR_THIS_MONTH_CAP: self.this_month_cap,
            ATTR_THIS_MONTH_COSTS: round(self.this_month_costs, PRECISION),
            ATTR_UNIT_OF_MEASUREMENT: self.unit_of_measurement
        }