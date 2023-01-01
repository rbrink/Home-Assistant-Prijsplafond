## Home Assistant sensor component/integration for the Dutch nutservice pricecap in the Netherlands

- - -

If you like my work, please buy me a coffee or donate some crypto currencies. This will keep me awake :)

<a href="https://www.buymeacoffee.com/devsnow" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

- - -

### Install:
- Copy the files in the /custom_components/prijsplafond/ folder to: [homeassistant]/config/custom_components/prijsplafond/

Example config:
(Or use the lazy and easier route and just copy paste the values from this [configuration.yaml](https://github.com/rbrink/Home-Assistant-Prijsplafond/blob/main/example/configuration.yaml))
```Configuration.yaml:
sensor:
  - platform: prijsplafond
    sources_total_power:
    - sensor.p1_meter_5c2faf0544ee_total_power_import_t1
    - sensor.p1_meter_5c2faf0544ee_total_power_import_t2
    source_total_gas: sensor.p1_meter_5c2faf0544ee_total_gas
```

### Known limitations
- On startup this integration uses the first recorded state of the configured sourcees. In case the recording is later than the first day of current month somewhat around 00:00. The calculation might be off.. If anyone knows a workaround for this, please let me know :).