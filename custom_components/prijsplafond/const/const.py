import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

# Integration common info.
NAME = "Prijsplafond"
DOMAIN = "prijsplafond"

# Prices and defaults.
PRICE_CAP_GAS_MONTH = {
    1: 221,
    2: 188,
    3: 156,
    4: 86,
    5: 35,
    6: 19,
    7: 17,
    8: 17,
    9: 24,
    10: 81,
    11: 147,
    12: 206
}
GAS_PRICE = 1.45
UNIT_OF_MEASUREMENT_GAS = "m³"

PRICE_CAP_POWER_MONTH = {
    1: 340,
    2: 280,
    3: 268,
    4: 207,
    5: 181,
    6: 159,
    7: 161,
    8: 176,
    9: 199,
    10: 267,
    11: 306,
    12: 356
}
POWER_PRICE = 0.40
UNIT_OF_MEASUREMENT_POWER = "kWh"

# Configurational variables.
CONF_SOURCES_TOTAL_POWER = "sources_total_power"
CONF_SOURCE_TOTAL_GAS = "source_total_gas"

# Attributes.
ATTR_FRIENDLY_NAME = "friendly_name"
ATTR_THIS_MONTH_CAP = "this_month_cap"
ATTR_THIS_MONTH_COSTS = "this_month_costs"
ATTR_UNIT_OF_MEASUREMENT = "unit_of_measurement"

UPDATE_MIN_TIME = timedelta(minutes=1)