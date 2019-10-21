import time
import busio
import digitalio
import board
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa

# Board LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# RFM9x Breakout Pinouts
cs = digitalio.DigitalInOut(board.D8)
irq = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D25)

# Feather M0 RFM9x Pinouts
# cs = digitalio.DigitalInOut(board.RFM9X_CS)
# irq = digitalio.DigitalInOut(board.RFM9X_D0)
# rst = digitalio.DigitalInOut(board.RFM9x_RST)

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

while True:
    data = bytearray(b"\x43\x57\x54\x46")
    print('Sending packet...')
    lora.send_data(data, len(data), lora.frame_counter)
    print('Packet sent!')
    led.value = True
    lora.frame_counter += 1
    time.sleep(1)
    led.value = False
