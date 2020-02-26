Based on: https://github.com/bramkragten/custom-ui/blob/master/weather-card/README.md
This card assumes openweathermap weather data (3h forecast)
Customized to present 2 days forecast if each day has only 6 slots


# Manual:

1. Download the [weather-card.js](https://raw.githubusercontent.com/bramkragten/custom-ui/master/weather-card/weather-card.js) to `/config/www/custom-lovelace/weather-card/`. (or an other folder in `/config/www/`)
2. Save, the [amCharts icons](https://www.amcharts.com/free-animated-svg-weather-icons/) (The contents of the folder "animated") under `/config/www/custom-lovelace/weather-card/icons/` (or an other folder in `/config/www/`)
3. If you use Lovelace in storage mode, and want to use the editor, download the [weather-card-editor.js](https://raw.githubusercontent.com/bramkragten/custom-ui/master/weather-card/weather-card-editor.js) to `/config/www/custom-lovelace/weather-card/`. (or the folder you used above)

Add the following to resources in your lovelace config:

```yaml
resources:
  - url: /local/weather-card/weather-card.js
    type: module
views:
  - title: Home
    cards:
      - entity: weather.customopenweathermap
        name: Prévisions
        type: 'custom:weather-card'
        icons: "/local/weather-card/icons/"
```

Make sure the `sun` component is enabled:

```yaml
# Example configuration.yaml entry
sun:
```
