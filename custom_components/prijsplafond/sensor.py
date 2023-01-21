#!/usr/bin/env python3
from __future__ import annotations
"""
Sensor component for Prijsplafond
Author: Richard Brink
"""

from datetime import datetime
from _sha1 import sha1

from .const.const import (
    _LOGGER,
    CONF_SOURCES_TOTAL_GAS,
    CONF_SOURCES_TOTAL_POWER,
    DOMAIN,
    ATTR_FRIENDLY_NAME,
    ATTR_THIS_MONTH_CAP,
    ATTR_THIS_MONTH_COSTS,
    ATTR_UNIT_OF_MEASUREMENT,
    GAS_PRICE,
    NAME,
    POWER_PRICE,
    PRICE_CAP_GAS_MONTH,
    PRICE_CAP_POWER_MONTH,
    UNIT_OF_MEASUREMENT_GAS,
    UNIT_OF_MEASUREMENT_POWER,
    UPDATE_MIN_TIME,
    ATTR_PREVIOUS_TOTAL_USAGE
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

        

class PrijsplafondSensor(SensorEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        type,
        total_power_entities,
        total_gas_entities
    ):
        self.entity_id = f"sensor.{DOMAIN}_{type}"
        self.friendly_name = f"{type.capitalize()}gebruik deze maand"
        self._state = 0
        self._previous_total_usage = 0

        self._current_month = datetime.now().month

        if type == 'gas':
            self.this_month_cap = PRICE_CAP_GAS_MONTH[self._current_month]
            self.this_month_costs = 0
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_GAS

            self._price = GAS_PRICE
            self._sources = total_gas_entities
        else:
            self.this_month_cap = PRICE_CAP_POWER_MONTH[self._current_month]
            self.this_month_costs = 0
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_POWER

            self._price = POWER_PRICE
            self._sources = total_power_entities

    @property
    def unique_id(self):
        return str(
            sha1(
                ";".join(
                    [str(type),",".join(self._sources)]
                ).encode("utf-8")
            ).hexdigest()
        )

    @property
    def name(self):
        return self.friendly_name

    @property
    def native_value(self):
        return None

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def native_unit_of_measurement(self):
        return None

    @property
    def icon(self):
        return None

    @property
    def state(self):
        return round(self._state, 2)

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def device_class(self):
        return None

    @property
    def extra_state_attributes(self):
        return {
            ATTR_FRIENDLY_NAME: self.friendly_name,
            ATTR_THIS_MONTH_CAP: self.this_month_cap,
            ATTR_THIS_MONTH_COSTS: round(self.this_month_costs, 2),
            ATTR_UNIT_OF_MEASUREMENT: self._unit_of_measurement,
            ATTR_PREVIOUS_TOTAL_USAGE: self._previous_total_usage
        }

    @Throttle(UPDATE_MIN_TIME)
    async def async_update(self):
        total_usage = 0
        for entity_id in self._sources:
            if self._previous_total_usage is 0:
                state = await self._get_first_recorded_state(entity_id)
            else:
                state = self.hass.states.get(entity_id)

            if state is None:
                _LOGGER.error('Unable to find entity "%s"', entity_id)
                continue

            # As we need a sum of the sources to calculate the usage.
            total_usage += float(state.state)

        if self._previous_total_usage > 0:
            old_state = self.hass.states.get(self.entity_id)
            if old_state is None:
                self._state = 0
            else:
                previous = old_state.attributes.get(ATTR_PREVIOUS_TOTAL_USAGE, 0) 
                if previous > 0:
                    self._state += (total_usage - previous)

        self._previous_total_usage = total_usage
        self.this_month_costs = self._state * self._price

    async def _get_first_recorded_state(self, entity_id: str):    
        history_list = await get_instance(self.hass).async_add_executor_job(
            history.state_changes_during_period,
            self.hass,
            datetime.now().today().replace(day=1, hour=0, minute=0, second=0),
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
