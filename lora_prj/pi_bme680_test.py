#!/usr/bin/env python

import bme680
import time

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

print("polling mode for the sensor test:")
try:
    while True:
        if sensor.get_sensor_data():
            # number formatting: {:+.2f} -1.00 -> 2 decimal places with sign
            output = '{0:+.2f} C, {1:.2f} hPa, {2:.0f} %RH, {3:.0f} ohm'.format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity,
                sensor.data.gas_resistance)
            print(output)
            # time.sleep(seconds) -> 5s delay
            time.sleep(10)
            
except KeyboardInterrupt:
    pass
