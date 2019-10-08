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

echo beginning of script
# Times to start and stop each date are military format: HHMM
STARTOFDAY=0800
ENDOFDAY=2000

# Time (in seconds) between two measures
TIMELAPSE=900

# Get the date from the RTC
MYDATE=$(talkpp -t)
MYHHMM=${MYDATE:4:4}

echo setup date from RTC
# Set our date from the RTC
date $MYDATE

echo setup wakeup and alarm
# Set our next wakeup time
if [ $MYHHMM -gt $ENDOFDAY ]; then
	# Getting dark: Set an alarm for tomorrow morning
	talkpp -a $(date --date=tomorrow +%m%d$STARTOFDAY%Y.00)
else
	# Set an alarm for 15 minutes from now
	talkpp -d $TIMELAPSE
fi

echo alarm ON
# Enable the alarm
talkpp -c C0=1

echo battery test
# read battery voltage
BATT=$(talkpp -c B)

if ($BATT -lt 3.67); then
    talkpp -c E3=272    # start back up at 4.00 volts
    talkpp -c C7=1  # set to restart
    talkpp -c O=30  # Turn off Pi Platter in 30 seconds
else
    echo run python bme680 script
    # Run measurement program
    sudo python pi_bme680_read.py
fi

echo end of script

echo shutdown Pi Platter board
# And finally shutdown and then power off
talkpp -c O=15
shutdown now