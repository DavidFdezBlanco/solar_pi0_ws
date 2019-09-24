#!/usr/bin/env python
# NOTE: device address is set in /usr/local/lib/python2.7/dist-packages/bme680/__init__.py

import bme680
import time
from rf95 import RF95, Bw31_25Cr48Sf512

# set frequency and power
rf95.set_frequency(868.5)
rf95.set_tx_power(5)
# Custom predefined mode
rf95.set_modem_config(Bw31_25Cr48Sf512)

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

try:
    inc = 0
    backup_cpt = 0
    delay = 30  # delay between two measure in seconds
    n_meas = 3  # number of measures before program terminated
    while inc < n_meas && backup_cpt < n_meas + 5 :
            if sensor.get_sensor_data():
                output = '{0:.2f} C,{1:.2f} hPa,{2:.3f} %RH'.format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity)
                print(output)
                print("sending...")
                rf95.send(rf95.str_to_data(output))
                rf95.wait_packet_sent()
                print("sent!")
                rf95.set_mode_idle()
                rf95.cleanup()
                time.sleep(30)    # time.sleep(secs)
                inc++
        backup_cpt++

except KeyboardInterrupt:
    pass
