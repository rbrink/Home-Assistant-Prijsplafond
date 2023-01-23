## Home Assistant sensor component/integration for the Dutch nutservice pricecap (prijsplafond) in the Netherlands

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

- - -

If you like my work, please buy me a coffee. This will keep me awake :)

<a href="https://www.buymeacoffee.com/devsnow" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

- - -

### Installation

[HACS](https://hacs.xyz/) > Integrations > Plus (+) > **Prijsplafond**

Or manually copy `prijsplafond` folder from [latest release](https://github.com/rbrink/Home-Assistant-Prijsplafond/releases/latest) to `custom_components` folder in your config folder.

## Configuration

Configuration > [Integrations](https://my.home-assistant.io/redirect/integrations/) > Add Integration > [Prijsplafond](https://my.home-assistant.io/redirect/config_flow_start/?domain=prijsplafond)

*If the integration is not in the list, you need to clear the browser cache.*

## Configuration UI

Configuration > [Integrations](https://my.home-assistant.io/redirect/integrations/) > **Prijsplafond** > Configure

### Useful template examples:
```yaml
template:
  - sensor:
      # Template sensor to display the current monthly cap.
      - unique_id: sensor_prijsplafond_monthly_gas_cap
        name: Prijsplafond Monthly Gas Cap
        state: "{{ state_attr('sensor.prijsplafond_gas', 'this_month_cap') }}"
        unit_of_measurement:  "m³"
        
      # Template sensor to display what this month total costs are.
      - unique_id: sensor_prijsplafond_this_month_costs
        name: Prijsplafond Thijs Month Costs
        state: "{{ TO DO }}"
        unit_of_measurement: "EUR"
```
