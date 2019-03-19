"""
Support for BME280 temperature, humidity and pressure sensor.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.bme280/
"""
from datetime import timedelta
from functools import partial
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    TEMP_FAHRENHEIT, CONF_NAME, CONF_MONITORED_CONDITIONS)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.util.temperature import celsius_to_fahrenheit

REQUIREMENTS = ['adafruit-circuitpython-bme280==2.3.0']

_LOGGER = logging.getLogger(__name__)

CONF_CS_GPIO = 'cs_gpio'
CONF_DELTA_TEMP = 'delta_temperature'

DEFAULT_NAME = 'BME280 SPI Sensor'
DEFAULT_CS_GPIO = 5
DEFAULT_I2C_BUS = 1
DEFAULT_T_STANDBY = 5  # Tstandby 5ms
DEFAULT_DELTA_TEMP = 0.

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=3)

SENSOR_TEMP = 'temperature'
SENSOR_HUMID = 'humidity'
SENSOR_PRESS = 'pressure'
SENSOR_TYPES = {
    SENSOR_TEMP: ['Temperature', None],
    SENSOR_HUMID: ['Humidity', '%'],
    SENSOR_PRESS: ['Pressure', 'mb']
}
DEFAULT_MONITORED = [SENSOR_TEMP, SENSOR_HUMID, SENSOR_PRESS]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_CS_GPIO, default=DEFAULT_CS_GPIO): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=DEFAULT_MONITORED):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_DELTA_TEMP,
                 default=DEFAULT_DELTA_TEMP): vol.Coerce(float),
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the BME280 sensor."""
    import board
    import digitalio
    import busio
    from adafruit_bme280 import Adafruit_BME280_SPI


    SENSOR_TYPES[SENSOR_TEMP][1] = hass.config.units.temperature_unit
    name = config.get(CONF_NAME)
    cs_gpio = config.get(CONF_CS_GPIO)
    
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    bme_cs = digitalio.DigitalInOut(getattr(board, "D" + cs_gpio))

    sensor = await hass.async_add_job(
        partial(Adafruit_BME280_SPI, spi, bme_cs)
    )
    if not sensor.temperature:
        _LOGGER.error("BME280 sensor not detected at %s", cs_gpio)
        return False

    sensor_handler = await hass.async_add_job(BME280Handler, sensor)

    dev = []
    try:
        for variable in config[CONF_MONITORED_CONDITIONS]:
            dev.append(BME280Sensor(
                sensor_handler, variable, SENSOR_TYPES[variable][1], name))
    except KeyError:
        pass

    async_add_entities(dev, True)


class BME280Handler:
    """BME280 sensor working in i2C bus."""

    def __init__(self, sensor):
        """Initialize the sensor handler."""
        self.sensor = sensor
        self.sample_ok = False
        self.update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Read sensor data."""
        self.temperature = self.sensor.temperature
        self.humidity = self.sensor.humidity
        self.pressure = self.sensor.pressure
        self.sample_ok = True


class BME280Sensor(Entity):
    """Implementation of the BME280 sensor."""

    def __init__(self, bme280_client, sensor_type, temp_unit, name):
        """Initialize the sensor."""
        self.client_name = name
        self._name = SENSOR_TYPES[sensor_type][0]
        self.bme280_client = bme280_client
        self.temp_unit = temp_unit
        self.type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.client_name, self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return self._unit_of_measurement

    async def async_update(self):
        """Get the latest data from the BME280 and update the states."""
        await self.hass.async_add_job(self.bme280_client.update)
        if self.bme280_client.sample_ok:
            if self.type == SENSOR_TEMP:
                temperature = round(self.bme280_client.temperature, 1)
                if self.temp_unit == TEMP_FAHRENHEIT:
                    temperature = round(celsius_to_fahrenheit(temperature), 1)
                self._state = temperature
            elif self.type == SENSOR_HUMID:
                self._state = round(self.bme280_client.humidity, 1)
            elif self.type == SENSOR_PRESS:
                self._state = round(self.bme280_client.pressure, 1)
        else:
            _LOGGER.warning("Bad update of sensor.%s", self.name)
 
