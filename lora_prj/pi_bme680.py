#!/usr/bin/env python

import time
import busio
import digitalio
import board
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa
from busio import I2C
import adafruit_bme680

# create library object using bus I2C and SPI port
i2c = I2C(board.SCL, board.SDA)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1013.25

# RFM9x breakout pinouts
cs = digitalio.DigitalInOut(board.D8)
irq = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D25)

# TTN device address, 4 Bytes, MSB
devaddr = bytearray([0x26, 0x01, 0x18, 0xE6])

# TTN network Key, 16 Bytes, MSB
nwkey = bytearray([0x05, 0xC0, 0x6D, 0x82, 0xF2, 0x97, 0x3D, 0x05,
                   0x88, 0x41, 0xDE, 0x26, 0x0C, 0x0A, 0x9B, 0xA3])

# TTN application key, 16 Bytess, MSB
app = bytearray([0xDA, 0x7E, 0x5B, 0x0C, 0xC4, 0x6A, 0xFD, 0x9E,
                 0x3E, 0xC9, 0x94, 0x56, 0xA5, 0x9D, 0xBC, 0xDD])

ttn_config = TTN(devaddr, nwkey, app, country='EU')

# Broadcasting on channel 0 in US Region - 903.9 MHz
lora = TinyLoRa(spi, cs, irq, rst, ttn_config, channel=0)

# Data Packet to send to TTN
data = bytearray(10)

for nb_meas in range (0, 3, 1):
    press_val = bme680.pressure
    temp_val = bme680.temperature
    humid_val = bme680.humidity
    gas_val = bme680.gas
    alt_val = bme680.altitude

    # Encode float as int
    press_val = int(press_val * 100)
    temp_val = int(temp_val * 100)
    humid_val = int(humid_val * 100)
    gas_val = int(gas_val * 100)
    alt_val = int(alt_val * 100)

    # Encode payload as bytes
    data[0] = (press_val >> 8) & 0xff
    data[1] = press_val & 0xff
    data[2] = (temp_val >> 8) & 0xff
    data[3] = temp_val & 0xff
    data[4] = (humid_val >> 8) & 0xff
    data[5] = humid_val & 0xff
    data[6] = (gas_val >> 8) & 0xff
    data[7] = gas_val & 0xff
    data[8] = (alt_val >> 8) & 0xff
    data[9] = alt_val & 0xff

    # Send data packet
    print('Sending packet...')
    lora.send_data(data, len(data), lora.frame_counter)
    print('Packet Sent!')
    lora.frame_counter += 1
    time.sleep(15)

