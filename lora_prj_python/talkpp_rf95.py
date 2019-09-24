#!/usr/bin/env python

import os
import sys
import subprocess
from   subprocess import Popen, PIPE
import time
from   datetime import datetime
#from rf95 import RF95, Bw31_25Cr48Sf512
import schedule

# set frequency and power
#rf95.set_frequency(868.5)
#rf95.set_tx_power(5)
# Custom predefined mode
#rf95.set_modem_config(Bw31_25Cr48Sf512)

def main(argv):
    if datetime.today().year > 2018: # if the OS time is current then set the RTC
        ticks = time.time()
        settimecmd = "talkpp -c T=" + str(int(ticks))
        print("Setting Pi Platter RTC")
        os.system(settimecmd)  # set the system time
    else:
        cmd = Popen('talkpp -c T', shell=True, stdout=PIPE)  # read date from piplatter
        alloutput = cmd.stdout.read()
        alloutput.splitlines()
        mytime = int(alloutput.splitlines()[0])
        #print mytime
        if mytime > 148000000:  #only set the os time if the RTC was previously set
            print ("Setting OS time")
            datecmd = Popen('sudo date %s' % mytime, shell=True, stdout=PIPE) # set os date
            dateoutput = datecmd.stdout.readlines()
    
    print("solar pi_platter start")

    previous_second = 0
    last_good_battery_voltage = 0
    
    os.system("talkpp -c C0=1") # enable the alarm
    
    while True:  # monitor battery and log voltage once a minute
        now = datetime.today()
        schedule.run_pending()
        
        battery_voltage = subprocess.check_output("talkpp -c B", shell=True)  # read battery voltage
        
        if is_float(battery_voltage) :  # talkpp does not always return a value - put in last known value if not
            last_good_battery_voltage = battery_voltage
        else:
            battery_voltage = last_good_battery_voltage
        battery_volt = float(battery_voltage)
        if (battery_volt < 3.67) and (battery_volt > 1.50):  # shut down if battery voltage is getting to low
            print("powering down now")
            # Threshold=(1.024/(Restart_Voltage-0.15))*1023
            os.system("talkpp -c E3=272") # start back up at 4.00 volts
            os.system("talkpp -c C7=1")  # set to restart
            os.system("talkpp -c E7=1")  # set to restart every time
            os.system("talkpp -c O=30")  # Turn off Pi Platter in 30 seconds
            os.system("sudo halt")       # shut down Pi Zero now
        ouput = '{} {}\n'.format(str(now)[:-7], battery_volt)
        print (output)
#        print("sending...")
#            rf95.send(rf95.str_to_data(output))
#            rf95.wait_packet_sent()
#        print("sent!")
#            rf95.set_mode_idle()
#            rf95.cleanup()
        time.sleep(60)  # check and log about once a minute

def is_float(volts):  # test to see if the returned value looks like a proper floating point number
    try:
        newVolts = float(volts)
        return newVolts
    except ValueError:
        return None

# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))
    
    try:  # exit cleanly on keyboard interrupt.
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
