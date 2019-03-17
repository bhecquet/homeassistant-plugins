"""
Support for the OpenWeatherMap (OWM) service.
This weather component uses OWM component but uses cache in case internet access is lost

in configuration.yml:
weather:
  - platform: owm
    api_key: <openweathermap key>
"""
import logging

import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED, PLATFORM_SCHEMA)
from homeassistant.components.weather.openweathermap import (WeatherData, OpenWeatherMapWeather, CONDITION_CLASSES)
from homeassistant.const import (
    CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_MODE, CONF_NAME)
import homeassistant.helpers.config_validation as cv
from .cache import Cache

REQUIREMENTS = ['pyowm==2.10.0']

_LOGGER = logging.getLogger(__name__)

FORECAST_MODE = ['hourly', 'daily', 'freedaily']

DEFAULT_NAME = 'CustomOpenWeatherMap'

 
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_MODE, default='hourly'): vol.In(FORECAST_MODE),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the OpenWeatherMap weather platform."""

    longitude = config.get(CONF_LONGITUDE, round(hass.config.longitude, 5))
    latitude = config.get(CONF_LATITUDE, round(hass.config.latitude, 5))
    name = config.get(CONF_NAME)
    mode = config.get(CONF_MODE)

    Cache.set_cache_path(hass.config.path(""))
    owm = OwmClientWrapper(config.get(CONF_API_KEY))

    data = WeatherData(owm, latitude, longitude, mode)

    add_entities([CustomOpenWeatherMapWeather(
        name, data, hass.config.units.temperature_unit, mode)], True)


class CustomOpenWeatherMapWeather(OpenWeatherMapWeather):
    """Implementation of an OpenWeatherMap sensor."""


    @property
    def forecast(self):
        """Return the forecast array."""
        data = []

        def calc_precipitation(rain, snow):
            """Calculate the precipitation."""
            rain_value = 0 if rain is None else rain
            snow_value = 0 if snow is None else snow
            if round(rain_value + snow_value, 1) == 0:
                return None
            return round(rain_value + snow_value, 1)

        if self._mode == 'freedaily':
            weather = self.forecast_data.get_weathers()[::8]
        else:
            weather = self.forecast_data.get_weathers()

        for entry in weather:
            if self._mode == 'daily':
                data.append({
                    ATTR_FORECAST_TIME:
                        entry.get_reference_time('unix') * 1000,
                    ATTR_FORECAST_TEMP:
                        entry.get_temperature('celsius').get('day'),
                    ATTR_FORECAST_TEMP_LOW:
                        entry.get_temperature('celsius').get('night'),
                    ATTR_FORECAST_PRECIPITATION:
                        calc_precipitation(
                            entry.get_rain().get('all'),
                            entry.get_snow().get('all')),
                    ATTR_FORECAST_WIND_SPEED:
                        entry.get_wind().get('speed'),
                    ATTR_FORECAST_WIND_BEARING:
                        entry.get_wind().get('deg'),
                    ATTR_FORECAST_CONDITION:
                        [k for k, v in CONDITION_CLASSES.items()
                         if entry.get_weather_code() in v][0]
                })
            else:
                entry_hour = entry.get_reference_time('date').hour
                
                # do not keep night
                if 0 <= entry_hour < 6:
                    continue
                data.append({
                    ATTR_FORECAST_TIME:
                        entry.get_reference_time('unix') * 1000,
                    ATTR_FORECAST_TEMP:
                        entry.get_temperature('celsius').get('temp'),
                    ATTR_FORECAST_TEMP_LOW:
                        entry.get_temperature('celsius').get('night'),
                    ATTR_FORECAST_WIND_SPEED:
                        entry.get_wind().get('speed'),
                    ATTR_FORECAST_WIND_BEARING:
                        entry.get_wind().get('deg'),
                    ATTR_FORECAST_PRECIPITATION:
                        (round(entry.get_rain().get('3h'), 1)
                         if entry.get_rain().get('3h') is not None
                         and (round(entry.get_rain().get('3h'), 1) > 0)
                         else None),
                    ATTR_FORECAST_CONDITION:
                        [k for k, v in CONDITION_CLASSES.items()
                         if entry.get_weather_code() in v][0]
                })
        return data


class OwmClientWrapper:
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.owm = None
        
        self.weather_at_coords_cache = Cache(DEFAULT_NAME + "_weather_at_coords")
        self.daily_forecast_at_coords_cache = Cache(DEFAULT_NAME + "_daily_forecast_at_coords")
        self.three_hours_forecast_at_coords_cache = Cache(DEFAULT_NAME + "_three_hours_forecast_at_coords")
        
    def get_owm_client(self):
        import pyowm
        
        if self.owm:
            return self.owm
        else:
            try:
                return pyowm.OWM(self.api_key)
            except Exception as e:
                return None
                
    def weather_at_coords(self, latitude, longitude):
        owm = self.get_owm_client()

        try:
            return self.weather_at_coords_cache.update(owm.weather_at_coords(latitude, longitude))
        except:
            if self.weather_at_coords_cache.exists():
                print("111")
                return self.weather_at_coords_cache.get()
            else:
                return None
        
    def daily_forecast_at_coords(self, latitude, longitude, limit=None):
        owm = self.get_owm_client()
        
        try:
            return self.daily_forecast_at_coords_cache.update(owm.daily_forecast_at_coords(latitude, longitude, limit=None))
        except:
            if self.daily_forecast_at_coords_cache.exists():
                return self.daily_forecast_at_coords_cache.get()
            else:
                return None
        
    def three_hours_forecast_at_coords(self, latitude, longitude):
        
        owm = self.get_owm_client()
        
        try:
            return self.three_hours_forecast_at_coords_cache.update(owm.three_hours_forecast_at_coords(latitude, longitude))
        except:
            if self.three_hours_forecast_at_coords_cache.exists():
                return self.three_hours_forecast_at_coords_cache.get()
            else:
                return None

