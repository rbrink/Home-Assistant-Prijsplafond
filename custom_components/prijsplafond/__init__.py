from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Forwarding the config flow to sensor.py.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            entry, Platform.SENSOR
        )
    )
    
    return True