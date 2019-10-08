# /usr/bin/env python

from rf95_cst import *

import time
from threading import RLock

import spidev
import RPi.GPIO as GPIO

class RF95:
    def __init__(self, cs=0, int_pin=25, reset_pin=None):
        # init class
        self.spi = spidev.SpiDev()
        self.spi_lock = RLock()
        self.cs = cs
        self.int_pin = int_pin
        self.reset_pin = reset_pin
        self.mode = RADIO_MODE_INITIALISING
        self.buf = []         # RX Buffer for interrupts
        self.buflen = 0       # RX Buffer length
        self.last_rssi = -99  # last packet RSSI
        self.last_snr = -99   # last packet SNR
        self.rx_bad = 0       # rx error count
        self.tx_good = 0      # tx packets sent
        self.rx_good = 0      # rx packets recv
        self.rx_buf_valid = False
        self._using_hf_port = None

    def init(self):
        # open SPI and initialize RF95
        self.spi.open(0, self.cs)
        self.spi.max_speed_hz = 488000
        self.spi.close()

        # set interrupt pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.int_pin, GPIO.IN)
        GPIO.add_event_detect(self.int_pin, GPIO.RISING, callback=self.handle_interrupt)

        # set reset pin
        if self.reset_pin is not None:
            GPIO.setup(self.reset_pin, GPIO.OUT)
            GPIO.output(self.reset_pin, GPIO.HIGH)

        # wait for reset
        time.sleep(0.05)

        # set sleep mode and LoRa mode
        self.spi_write(REG_01_OP_MODE, MODE_SLEEP | LONG_RANGE_MODE)

        time.sleep(0.01)
        # check if we are set
        if self.spi_read(REG_01_OP_MODE) != (MODE_SLEEP | LONG_RANGE_MODE):
            return False

        # set up FIFO
        self.spi_write(REG_0E_FIFO_TX_BASE_ADDR, 0)
        self.spi_write(REG_0F_FIFO_RX_BASE_ADDR, 0)

        # default mode
        self.set_mode_idle()

        self.set_modem_config(Bw125Cr45Sf128)
        self.set_preamble_length(8)

        return True

    def handle_interrupt(self, channel):
        # Read the interrupt register
        irq_flags = self.spi_read(REG_12_IRQ_FLAGS)

        if self.mode == RADIO_MODE_RX and irq_flags & (RX_TIMEOUT | PAYLOAD_CRC_ERROR):
            self.rx_bad = self.rx_bad + 1
        elif self.mode == RADIO_MODE_RX and irq_flags & RX_DONE:
            # packet received
            length = self.spi_read(REG_13_RX_NB_BYTES)
            # Reset the fifo read ptr to the beginning of the packet
            self.spi_write(REG_0D_FIFO_ADDR_PTR, self.spi_read(REG_10_FIFO_RX_CURRENT_ADDR))
            self.buf = self.spi_read_data(REG_00_FIFO, length)
            self.buflen = length
            # clear IRQ flags
            self.spi_write(REG_12_IRQ_FLAGS, 0xff)

            # save SNR
            self.last_snr = self.spi_read(REG_19_PKT_SNR_VALUE) / 4

            # save RSSI
            self.last_rssi = self.spi_read(REG_1A_PKT_RSSI_VALUE)

            # Adjust the RSSI, datasheet page 87
            if self.last_snr < 0:
                self.last_rssi += self.last_snr
            else:
                self.last_rssi = (self.last_rssi * 16) / 15

            if self._using_hf_port:
                self.last_rssi -= 157
            else:
                self.last_rssi -= 164

            # We have received a message
            self.rx_good = self.rx_good + 1
            self.rx_buf_valid = True
            self.set_mode_idle()
        elif self.mode == RADIO_MODE_TX and irq_flags & TX_DONE:
            self.tx_good = self.tx_good + 1
            self.set_mode_idle()
        elif self.mode == RADIO_MODE_CAD and irq_flags & CAD_DONE:
            self.cad = bool(irq_flags & CAD_DETECTED)
            self.set_mode_idle()

        # Clear all IRQ flags
        self.spi_write(REG_12_IRQ_FLAGS, 0xff)

    def spi_write(self, reg, data):
        self.spi_lock.acquire()
        self.spi.open(0, self.cs)
        # spi speed is reset on opening, change it
        self.spi.max_speed_hz = 488000
        # transfer one byte
        self.spi.xfer2([reg | SPI_WRITE_MASK, data])
        self.spi.close()
        self.spi_lock.release()

    def spi_read(self, reg):
        self.spi_lock.acquire()
        self.spi.open(0, self.cs)
        self.spi.max_speed_hz = 488000
        data = self.spi.xfer2([reg & ~SPI_WRITE_MASK, 0])
        self.spi.close()
        self.spi_lock.release()
        return data[1]

    def spi_write_data(self, reg, data):
        self.spi_lock.acquire()
        self.spi.open(0, self.cs)
        self.spi.max_speed_hz = 488000
        # transfer byte list
        self.spi.xfer2([reg | SPI_WRITE_MASK] + data)
        self.spi.close()
        self.spi_lock.release()

    def spi_read_data(self, reg, length):
        self.spi_lock.acquire()
        data = []
        self.spi.open(0, self.cs)
        self.spi.max_speed_hz = 488000
        # start address + amount of bytes to read
        data = self.spi.xfer2([reg & ~SPI_WRITE_MASK] + [0] * length)
        self.spi.close()
        self.spi_lock.release()
        # all but first byte
        return data[1:]

    def set_frequency(self, freq):
        freq_value = int((freq * 1000000.0) / FSTEP)
        self._using_hf_port = freq >= 779

        self.spi_write(REG_06_FRF_MSB, (freq_value >> 16) & 0xff)
        self.spi_write(REG_07_FRF_MID, (freq_value >> 8) & 0xff)
        self.spi_write(REG_08_FRF_LSB, freq_value & 0xff)

    def set_mode_idle(self):
        if self.mode != RADIO_MODE_IDLE:
            self.spi_write(REG_01_OP_MODE, MODE_STDBY)
            self.mode = RADIO_MODE_IDLE

    def sleep(self):
        if self.mode != RADIO_MODE_SLEEP:
            self.spi_write(REG_01_OP_MODE, MODE_SLEEP)
            self.mode = RADIO_MODE_SLEEP

        return True

    def set_mode_rx(self):
        if self.mode != RADIO_MODE_RX:
            self.spi_write(REG_01_OP_MODE, MODE_RXCONTINUOUS)
            self.spi_write(REG_40_DIO_MAPPING1, 0x00)
            self.mode = RADIO_MODE_RX

    def set_mode_tx(self):
        if self.mode != RADIO_MODE_TX:
            self.spi_write(REG_01_OP_MODE, MODE_TX)
            self.spi_write(REG_40_DIO_MAPPING1, 0x40)
            self.mode = RADIO_MODE_TX

        return True

    def set_mode_cad(self):
        if self.mode != RADIO_MODE_CAD:
            self.spi_write(REG_01_OP_MODE, MODE_CAD)
            self.spi_write(REG_40_DIO_MAPPING1, 0x80)
            self.mode = RADIO_MODE_CAD

    def set_tx_power(self, power):
        if power > 23:
            power = 23

        if power < 5:
            power = 5

        # A_DAC_ENABLE actually adds about 3dBm to all
        # power levels. We will us it for 21, 22 and 23dBm
        if power > 20:
            self.spi_write(REG_4D_PA_DAC, PA_DAC_ENABLE)
            power = power - 3
        else:
            self.spi_write(REG_4D_PA_DAC, PA_DAC_DISABLE)

        self.spi_write(REG_09_PA_CONFIG, PA_SELECT | (power - 5))

    # set a default mode
    def set_modem_config(self, config):
        self.spi_write(REG_1D_MODEM_CONFIG1, config[0])
        self.spi_write(REG_1E_MODEM_CONFIG2, config[1])
        self.spi_write(REG_26_MODEM_CONFIG3, config[2])

    # set custom mode
    def set_modem_config_custom(self,
        bandwidth = BW_125KHZ,
        coding_rate = CODING_RATE_4_5,
        implicit_header = IMPLICIT_HEADER_MODE_OFF,
        spreading_factor = SPREADING_FACTOR_128CPS,
        crc = RX_PAYLOAD_CRC_ON,
        continuous_tx = TX_CONTINUOUS_MODE_OFF,
        timeout = SYM_TIMEOUT_MSB,
        agc_auto = AGC_AUTO_OFF):

        self.spi_write(REG_1D_MODEM_CONFIG1,
            bandwidth | coding_rate | implicit_header)
        self.spi_write(REG_1E_MODEM_CONFIG2,
            spreading_factor | continuous_tx | crc | timeout)
        self.spi_write(REG_26_MODEM_CONFIG3, agc_auto)

    def set_preamble_length(self, length):
        self.spi_write(REG_20_PREAMBLE_MSB, length >> 8)
        self.spi_write(REG_21_PREAMBLE_LSB, length & 0xff)

    # send data list
    def send(self, data):
        if len(data) > MAX_MESSAGE_LEN:
            return False

        self.wait_packet_sent()
        self.set_mode_idle()
        # beggining of FIFO
        # self.spi_write(REG_0E_FIFO_TX_BASE_ADDR, 0)
        self.spi_write(REG_0D_FIFO_ADDR_PTR, 0)

        # write data
        self.spi_write_data(REG_00_FIFO, data)
        self.spi_write(REG_22_PAYLOAD_LENGTH, len(data))

        # put radio in TX mode
        self.set_mode_tx()
        return True

    def wait_packet_sent(self):
        while self.mode == RADIO_MODE_TX:
            pass
        return True

    def available(self):
        if self.mode == RADIO_MODE_TX:
            return False
        self.set_mode_rx()
        return self.rx_buf_valid

    def channel_active(self):
        if self.mode != RADIO_MODE_CAD:
            self.set_mode_cad()

        while self.mode == RADIO_MODE_CAD:
            pass

        return self.cad

    def clear_rx_buf(self):
        self.rx_buf_valid = False
        self.buflen = 0

    # receive data list
    def recv(self):
        if not self.available():
            return False
        data = self.buf
        self.clear_rx_buf()
        return data

    # cleans all GPIOs, etc
    def cleanup(self):
        if self.reset_pin:
            GPIO.output(self.reset_pin, GPIO.LOW)
            GPIO.cleanup(self.reset_pin)
        if self.int_pin:
            GPIO.cleanup(self.int_pin)

    # helper method to send bytes
    @staticmethod
    def bytes_to_data(bytelist):
        return list(bytelist)

    # helper method to send strings
    @staticmethod
    def str_to_data(string):
        return [ord(c) for c in string]
