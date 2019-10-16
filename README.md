# Documentation
description of the project --> TODO

## RFM95W HopeRF breakout pinout
RFM95W      GPIO        Pin_Connector
Vin                     17        
GND                     25        
EN          NC          NC
GO          22          15
SCK         11          23
MISO        09          21
MOSI        10          19
CS          08          24
RST         25          22

## BME680 sensor breakout pinout
BME680      GPIO        Pin_Connector
3V                      1
GND                     09
SCK         03          05        
SDO         NC          NC
SDI         02          03
CS          NC          NC

# Manual install
This project has been tested on Raspbian Jessie and Raspbian Stretch.
At first, in order to comunicate between Pi-Platter board and Raspberry Pi Zero W, we have to install two utility programs.
To install these programs, we have to open utility folder and follow the instructions written in readme.cmd file.

## Dependencies install for sensor and HopeRF
In order to use BME680 sensor and LoRaWAN HopeRF RFM95M with Raspebbry Pi Zero W, we have to install SPI and I2C port drivers at first and, then, install BME680 and RFM95W  libraries in dist-package of our raspbian distribution.

    sudo apt-get update
    sudo apt-get install i2c-tools python3-smbus python3-spidev python3-pip

Let's go to Adafruit_CircuitPython_BME680-master folder and launch
    sudo python3 setup.py install

Let's go to Adafruit_CircuitPython_TinyLoRa-master folder and launch
    sudo python3 setup.py install

We can test these two devices by going in examples folder. Different scripts are proposed by Adafruit CircuitPython libraries.

In lora_prj folder, we  can see two scripts:
    pi_bme680 --> test if data are sent to TTN
    pi_talkpp.sh --> script of this project with communication with Pi_Platter board

The pi_talkpp.sh script is designed to be run by /etc/rc.local when the Pi Zero boots.  It looks at the power-up reason and does not execute if the Pi was powered on because the user powered up using the Solar Pi Platter button.



    