Sensor for retrieving daily weather information: rain, max temperature, min temperature, max wind

in configuration.yaml

```yaml
sensor:
  - platform: meteociel
    code: <code>
```
code can be retrieved in URL when retrieving city data on page: http://www.meteociel.fr/temps-reel/obs_villes.php 
