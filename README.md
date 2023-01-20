## Home Assistant sensor component/integration for the Dutch nutservice pricecap in the Netherlands

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

- - -

If you like my work, please buy me a coffee. This will keep me awake :)

<a href="https://www.buymeacoffee.com/devsnow" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

- - -

### Manual installation:
- Copy the files in the /custom_components/prijsplafond/ folder to: [homeassistant]/config/custom_components/prijsplafond/

### Known limitations
- On startup this integration uses the first recorded state of the configured sources. In case the recording is later than the first day of current month somewhat around 00:00. The calculation might be off.. If anyone knows a workaround for this, please let me know :).