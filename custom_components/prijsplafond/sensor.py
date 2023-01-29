from __future__ import annotations
"""
Sensor component for Prijsplafond
Author: Richard Brink
"""

import asyncio
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
from homeassistant.util import Throttle
from homeassistant.components.recorder import get_instance, history
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
    UNIT_OF_MEASUREMENT_POWER,
    UPDATE_MIN_TIME
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.debug("Async setup Prijsplafond")
    
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
        self._type = type

        _LOGGER.debug(f"[{self.entity_id}] Positive entities: {positive_entities}")
        _LOGGER.debug(f"[{self.entity_id}] Negative entities: {negative_entities}")

        self._current_month = datetime.now().month

        if self._type == 'gas':
            self.this_month_cap = PRICE_CAP_GAS_MONTH[self._current_month]
            self._price = GAS_PRICE

            # Entity specific.
            self._attr_device_class = SensorDeviceClass.GAS
            self._attr_unit_of_measurement = UNIT_OF_MEASUREMENT_GAS
        else:
            self.this_month_cap = PRICE_CAP_POWER_MONTH[self._current_month]
            self._price = POWER_PRICE

            # Entity specific.
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_unit_of_measurement = UNIT_OF_MEASUREMENT_POWER

        # Setting state to none as we are waiting for the update.
        self._state = None

    @property
    def unique_id(self):
        return str(
            sha1(
                self._type.encode("utf-8")
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
        if self._state is not None:
            return round(self._state, PRECISION)
        return self._state

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def extra_state_attributes(self):
        return {
            ATTR_FRIENDLY_NAME: self.friendly_name,
            ATTR_THIS_MONTH_CAP: self.this_month_cap,
            ATTR_THIS_MONTH_COSTS: round(self.this_month_costs, PRECISION),
            ATTR_UNIT_OF_MEASUREMENT: self._attr_unit_of_measurement
        }

    @Throttle(UPDATE_MIN_TIME)
    async def async_update(self):
        # Checking if we have entered a new month.
        now_month = datetime.now().month
        if self._current_month is not now_month:
            # If so.. change the cap to new values.
            self._current_month = now_month
            if self._type == 'gas':
                self.this_month_cap = PRICE_CAP_GAS_MONTH[self._current_month]
            else:
                self.this_month_cap = PRICE_CAP_POWER_MONTH[self._current_month]

        # Positive entities are consumers.
        pos_usage = 0        
        for entity_id in self._pos_sources:
            pos_usage += await self._get_value(entity_id)
        _LOGGER.debug(f"[{self.entity_id}] In update pos_usage is {pos_usage}")

        # Negative entities are producers like solar panels.
        neg_usage = 0
        for entity_id in self._neg_sources:
            neg_usage += await self._get_value(entity_id)
        _LOGGER.debug(f"[{self.entity_id}] In update neg_usage is {neg_usage}")

        total_usage = pos_usage - neg_usage
        _LOGGER.debug(f"[{self.entity_id}] In update total_usage is {total_usage}")
        if total_usage < 0:
            total_usage = 0           

        self._state = total_usage
        self.this_month_costs = self._state * self._price
        # To make sure we don't get negative costs..
        if self.this_month_costs < 0: self.this_month_costs = 0

    async def _get_value(self, entity_id):
        state_old = await self._get_first_recorded_state_in_month(entity_id)
        if state_old is None:
            _LOGGER.error('Unable to find historic value for entity "%s". Skipping..', entity_id)
            return None
        try:
            usage = float(state_old.state)
            _LOGGER.debug(f"Getting first recorded state of this month for: {entity_id} resulted in: {usage}")
        except ValueError:
            _LOGGER.warning(f"Unable to convert the first recorded state of this month for: {entity_id} to float..Value is: {state_old.state}. Setting usage to 0.")
            usage = 0

        # Fetching what the entity has for state now.
        state_now = self.hass.states.get(entity_id)
        if state_now is None:
            _LOGGER.error('Unable to find entity "%s". Skipping..', entity_id)
            return None
        usage_now = float(state_now.state)
        _LOGGER.debug(f"Getting current state for {entity_id} resulted in: {usage_now}")

        return usage_now - usage 

    async def _get_first_recorded_state_in_month(self, entity_id: str):    
        history_list = await get_instance(self.hass).async_add_executor_job(
            history.state_changes_during_period,
            self.hass,
            datetime.now().today().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            datetime.now(),
            str(entity_id),
            False,
            False,
            1
        )
        if (
            entity_id not in history_list.keys()
            or history_list[entity_id] is None
            or len(history_list[entity_id]) == 0
        ):
            _LOGGER.warning(
                'Historical data not found for entity "%s". Total usage may be off.', entity_id
            )
            return None
        else:
            return history_list[entity_id][0]