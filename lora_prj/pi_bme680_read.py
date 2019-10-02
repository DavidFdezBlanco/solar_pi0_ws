#!/usr/bin/env python

import bme680
import time
from i2c import I2CAdapter
from rf95 import RF95, Bw31_25Cr48Sf512

# create rf95 object with CS0 and external interrupt on pin 25
# CS=0 (SPI CS0) pin 24, IRQ_pin -> G0 pin 15 (GPIO 22), RST -> pin GPIO 25
lora = rf95.RF95(0, 22, 25)

if not lora.init(): # returns True if found
    print("RF95 not found")
    quit(1)
else:
    print("RF95 LoRa mode ok")

# set frequency and power
lora.set_frequency(868.5)
lora.set_tx_power(5)
# Custom predefined mode
lora.set_modem_config(Bw31_25Cr48Sf512)

i2c_dev = I2CAdapter()
sensor = bme680.BME680(i2c_device=i2c_dev)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

print("taking 3 meausres:")
try:
    inc = 0
    delay = 30  # delay between two measure in seconds
    n_meas = 3  # number of measures before program terminated
    while inc < n_meas:
            if sensor.get_sensor_data():
                output = '{0:.2f} C,{1:.2f} hPa,{2:.3f} %RH'.format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity)
                print(output)
                print("sending...")
                lora.send(lora.str_to_data(output))
                lora.wait_packet_sent()
                print("sent!")
                lora.set_mode_idle()
                lora.cleanup()
                
        time.sleep(15)    # time.sleep(secs)
        inc = inc + 1

except KeyboardInterrupt:
    pass