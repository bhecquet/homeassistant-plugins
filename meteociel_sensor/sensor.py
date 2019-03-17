"""
in configuration.yaml

sensor:
  - platform: meteociel
    code: <code>
    
code can be retrieved in URL when retrieving city data on page: http://www.meteociel.fr/temps-reel/obs_villes.php

"""

from homeassistant.const import TEMP_CELSIUS, CONF_CODE, ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
import voluptuous as vol
from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

import datetime

REQUIREMENTS = ['beautifulsoup4==4.7.1']

DEFAULT_CITY_CODE = 7235
SCAN_INTERVAL = datetime.timedelta(minutes=10)

ATTRIBUTION = "Data provided by Meteociel"

SENSOR_TYPES = {
    'max_temperature': ['Max Temperature', '°C'],
    'min_temperature': ['Min Temperature', '°C'],
    'wind_speed': ['Wind speed', 'm/s'],
    'rain': ['Rain', 'mm']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CODE, default=DEFAULT_CITY_CODE): cv.positive_int,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the sensor platform."""
    cityCode = config.get(CONF_CODE)
    
    data = WeatherData(cityCode)
    
    dev = []
    for variable in ['rain', 'max_temperature', 'min_temperature', 'wind_speed']:
        dev.append(MeteocielSensor(SENSOR_TYPES[variable][0], data, variable, SENSOR_TYPES[variable][1]))
        
    add_entities(dev, True)

class MeteocielSensor(Entity):
    """Implementation of an OpenWeatherMap sensor."""

    def __init__(self, name, weather_data, sensor_type, unit_of_measurement):
        """Initialize the sensor."""
        self._name = name
        self.meteociel_client = weather_data
        self.type = sensor_type
        self._state = None
        self._unit_of_measurement = unit_of_measurement

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

    def update(self):

        try:
            self.meteociel_client.update()
        except:
            _LOGGER.error("Error when calling API to update data")
            return

        if self.type == 'rain':
            self._state = self.meteociel_client._rain
        elif self.type == 'max_temperature':
            self._state = self.meteociel_client._tmax
        elif self.type == 'min_temperature':
            self._state = self.meteociel_client._tmin
        elif self.type == 'wind_speed':
            self._state = round(self.meteociel_client._wind, 1)


class WeatherData:
    """Get the latest data from OpenWeatherMap."""

    def __init__(self, cityCode):
        """Initialize the data object."""
        
        self._cityCode = cityCode
        self._rain = 0.0
        self._tmax = 19.9
        self._tmin = 9.9
        self._wind = 0.0
        self._sun = 'N/A'

    @Throttle(SCAN_INTERVAL)
    def update(self):
        
        from .meteociel import WeatherData
        data = WeatherData(self._cityCode)
        
        self._tmax = data.tmax if data.tmax else 19.9
        self._tmin = data.tmin if data.tmin else 9.9
        self._wind = data.wind if data.wind else 0.0
        self._sun = data.sun if data.sun else 'N/A'
        self._rain = data.rain if data.rain else 0.0
