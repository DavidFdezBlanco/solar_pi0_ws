#!/usr/bin/env python

import rf95
from rf95 import RF95, Bw31_25Cr48Sf512

# Example, send two strings and (uncomment to) receive and print a reply

# cs0, intr_pin -> gpio 22, rst_pin -> gpio 25
lora = RF95(0, 25, 22)
if not lora.init():
    print("RF95 not found")
    lora.cleanup()
    quit(1)
else:
    print("RF95 LoRa mode ok")

# set frequency and power
lora.set_frequency(868.5)
lora.set_tx_power(5)
# custom predefined mode
lora.set_modem_config(Bw31_25Cr48Sf512)

# send data
print("sending data")
data = [0x00, 0x01, 0x02, 0x03]
lora.send(data)
lora.wait_packet_sent()
print("sent")

# send a string
print("sending a sting")
string = "hello world!"
lora.send(lora.str_to_data(string))
lora.wait_packet_sent()
print("sent")

# wait until data is available
while not lora.available():
    pass
    
# receive data
data = lora.recv()
print (data)
for i in data:
    print(chr(i), end="")
print()

lora.set_mode_idle()
lora.cleanup()
