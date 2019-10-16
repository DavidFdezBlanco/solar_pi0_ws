import time
import busio
import digitalio
import board
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# RFM9x breakout pinouts
cs = digitalio.DigitalInOut(board.D8)
irq = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# TTN device address, 4 Bytes, MSB
devaddr = bytearray([0x00, 0x00, 0x00, 0x00])

# TTN network Key, 16 Bytes, MSB
nwkey = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

# TTN application key, 16 Bytess, MSB
app = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

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
