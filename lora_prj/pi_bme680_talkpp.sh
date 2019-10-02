#!/bin/bash
#
# Shell script designed to take 3 measures within 1'30
# using a BME680 sensor.
#
# The Solar Pi Platter wakes the Pi up every 15 minutes during the day and allows
# the RFM95W LoRa module the, taking 3 meauses, storing the result in a file
# and sending to LoRa gateway server.
#
# The script is designed to be run by /etc/rc.local when the Pi boots.  It looks at
# the power-up reason and does not execute if the Pi was powered on because the user
# powered up using the Solar Pi Platter button.
#

# Get the date from the RTC
MYDATE=$(talkpp -t)
MYHHMM=${MYDATE:4:4}

# Set our date from the RTC
date $MYDATE

# Get the power-up reason from the board (along with other status)
STATUS=$(talkpp -c S)

# Bail out of the script if we powered on because the user manually turned us on
if [ $STATUS -ge 16 ]; then
	# STATUS includes a power-up reason of "Button"
	exit
fi

# Set our next wakeup time
if [ $MYHHMM -gt 2000 ]; then
	# Getting dark: Set an alarm for tomorrow morning
	talkpp -a $(date --date=tomorrow +%m%d)08002019.00
	ENDOFDAY=1
else
	# Set an alarm for 15 minutes from now
	talkpp -d 900
	ENDOFDAY=0
fi

# Enable the alarm
talkpp -c C0=1

# read battery voltage
battery=$(talkpp -c B)
if (battery -lt 3.67)
    talkpp -c E3=272    # start back up at 4.00 volts
    talkpp -c C7=1  # set to restart
    talkpp -c O=30  # Turn off Pi Platter in 30 seconds
else
    # Run measurement program
    sudo python pi_bme680_read.py

# At the end of the day, we remain powered for a bit in case someone wants to log in
# and download some images. 
if [ $ENDOFDAY -eq 1 ]; then
	sleep 1800
fi

# And finally shutdown and then power off
talkpp -c O=30
shutdown now

