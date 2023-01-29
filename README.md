## Home Assistant sensor component/integration for the Dutch nutservice pricecap (prijsplafond) in the Netherlands

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

- - -

If you like my work, please buy me a coffee. This will keep me awake :)

<a href="https://www.buymeacoffee.com/devsnow" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

- - -

## How does it work?

On the configuration phase of this integration you are asked to fill in 3 types of entities. At first the energy consumers. Then the energy producers, also known as solar panels or small windmills. As last the gas consumers.

### Calculation/update phase
For simplicity I only describe the power (yes.. energy) entity as the gas entity is the same. 

Every 5 minutes the integration call it's update method in where I retrieve the historic value of the given energy consumers.
If you have provided only 1 consumer I will get the historic value for that one, but as a lot of Dutchies have multiple meters (dal and normal) I get both (as long as you have selected them). So lets say at the first of this month the value at 00:00:00 for either meters is 1000 and 1000. So total usage is 2000 at the start of this month. Then I get the same values but instead of the start of this month, the sensor fetches it for the current date and time. Resulting in a higher number. So now it's easy to calculate the usage as it would have been value now - value at the first of this month. 

If you have provided energy producer entities. I substract that of the consumed value. 

### No total consumption counter (e.g. when using the zonneplan-one integration)

As one user mentioned to me, some don't have a total counter of what they have been consuming. Only they have sensors like 'Electricity consumed today' and 'Gas consumption today'. Using those sensors with this integration will result in giving back faulty values as these values get reset to 0 every day.. Obviously they are only todays values. In order to overcome that Home Assistant offers a helper to keep counting the grid consumption. 

This helper is called: [Utility meter](https://www.home-assistant.io/integrations/utility_meter/)

To enable through yaml:
```yaml
utility_meter:
  zonneplan_p1_total_energy:
    name: Zonneplan P1 total energy
    source: YOUR ELECTRICITY CONSUMED TODAY ENTITY
```

If you want to do it via the graphical interface. Please go to Configuration > [Helpers](https://my.home-assistant.io/redirect/helpers/) > Plus (+) > **Utility meter (or in Dutch: Nutsmeter)** and only fill in the name and the input sensor.

*NOTE: If added via the UI. It may be possible that the entities are not yet visible thoughout the entire system. You can overcome this by manually typing in the entity id in the config flow.*

Then after you've added the total consumer entity use that in the configuration of Prijsplafond.

## Installation

### HACS

~~[HACS](https://hacs.xyz/) > Integrations > Plus (+) > **Prijsplafond**~~
(HACS way is still work in progress, the PR has been made.. #waiting)

To download the component [the repository URL must be added as custom repository to HACS](https://hacs.xyz/docs/faq/custom_repositories/).

### Manual

Copy `prijsplafond` folder from [latest release](https://github.com/rbrink/Home-Assistant-Prijsplafond/releases/latest) to `custom_components` folder in your config folder.

## Configuration

Configuration > [Integrations](https://my.home-assistant.io/redirect/integrations/) > Add Integration > [Prijsplafond](https://my.home-assistant.io/redirect/config_flow_start/?domain=prijsplafond)

*If the integration is not in the list or is missing labels during configuration, you need to clear the browser cache.*

## Troubleshooting
- In case you are experiencing random drops in the historic graph of either one of the entities. This integration has debug lines in the sensor. You can make them visible by adding the following to your logger configurations:
```yaml
logger:
  logs:
    custom_components.prijsplafond: debug
```
and enable debug logging by navigating to Configuration > [Integrations](https://my.home-assistant.io/redirect/integrations/) > Prijsplafond > 3 vertical dots > enable debug logging.

## Known design flaws
- As some might have noticed, one of the entities provided by this integration ends with power instead of energy. The answer yes.. I know.. Didn't really think that through. Can I change it? Yes I can but then the persons using the integration already will lose their history. So Sorry folks, I will keep it that way. Can you change it for yourself? Yes you can! As the entitites generated by this integration are given an unique id you can override the entity_id to anything you like. Feel free to change it to energy.
Problem solved!

## Useful template examples:
```yaml
template:
  - sensor:
    # Template sensor to display the current monthly cap.
    - name: Prijsplafond monthly gas cap
      unit_of_measurement: "m³"
      state: "{{ state_attr('sensor.prijsplafond_gas', 'this_month_cap') }}"
      
    # Template sensor to display what this month total costs are.
    - name: Prijsplafond this month costs
      unit_of_measurement: "EUR"
      state: "{{ (state_attr('sensor.prijsplafond_gas', 'this_month_costs') | float) +
                 (state_attr('sensor.prijsplafond_power', 'this_month_costs') | float) }}"
      icon: mdi:currency-eur

    # With thanks to @pluim003 a sensor to show the remaining gas to be used for this month.
    - name: 'Prijsplafond remaining gas'
      unit_of_measurement: "m³"
      state: "{{ (state_attr('sensor.prijsplafond_gas', 'this_month_cap') | float | round(2) ) -
                 (states('sensor.prijsplafond_gas') | float | round(2)) }}"
      icon: mdi:gas-cylinder

    # With thanks to @pluim003 a sensor to show the remaining energy to be used for this month.
    - name: 'Prijsplafond remaining energy'
      unit_of_measurement: "kWh"
      state: "{{ (state_attr('sensor.prijsplafond_power', 'this_month_cap') | float | round(2)) -
                 (states('sensor.prijsplafond_power') | float | round(2)) }}"
      icon: mdi:flash
```
