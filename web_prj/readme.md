# Documentation

This directory contains a demonstration python code for the Solar Pi_Platter board.
This is a web interface to interact with the <a href="http://danjuliodesigns.com/products/solar_pi_platter/solar_pi_platter.html">Solar Pi Platter</a> offered by <a href="http://danjuliodesigns.com/">Dan Julio Designs</a> which can be purchased on <a href="https://www.tindie.com/products/globoy/solar-pi-platter/">Tindie</a>.

## Python main file

Demonstration code for using Solar Pi_Platter board with a Raspberry Pi zero W. This project will allow a user to connect to their Solar Pi_Platter using a web browser in order to view and change system settings.

This program demonstrates:
1. Report battery voltage
2. Shutdown when battery is low
3. Restart once battery voltage has recovered
4. Switch USB ports for further power management
5. Setting Pi Platter Real Time Clock
6. Manage I/O like PWM outputs and analog inputs

## Manual install of talkpp utility

talkpp is a utility program to simplify communicating with the Solar Pi_Platter board. It provides a simple command-line interface to allow the user to directly (or via scripts) send commands to the board and to easily manage the Real Time Clock.  

It can communicate with the board via either the pseudo-tty /dev/pi-platter if the ppd daemon is running or the actual hardware serial device associated with the board if ppd is not running.  It uses udev to automatically find the correct serial device for the board, independent of other USB serial devices.

Instructions for this process can be found <a href="https://github.com/danjulio/rocketblue-automation/tree/master/pi_platter/unix_applets/talkpp">here</a>.

Go to utility and follow the instructions.

## Manual install of solar pi_platter_UX
To run this program on the Raspberry Pi zero W at startup, the method which has been chosen is to use systemd.

instructions will be elaborated from <a href="http://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/">here</a>.

    sudo apt-get install python-bottle
    sudo apt-get install python-requests
    
Before making an executable file, test file by command python:
    
    python web_pi_platter.py
    
Final step is to set-up the web server to run as a service and starts up automatically with boot.

    sudo chmod 775 ~/solar_pi0_ws/web_prj/web_pi_platter.py
    sudo nano /lib/systemd/system/web_pi_platter.service
    add in the following text:
        [Unit]
        Description=My Script Service
        After=multi-user.target
    
        [Service]
        Type=idle
        ExecStart=/usr/bin/python /home/pi/solar_pi0_ws/web_prj/web_pi_platter.py
    
        [Install]
        WantedBy=multi-user.target
    exit nano editor
    ExecStart=/usr/bin/python /home/pi/solar_pi0_ws/web_prj/web_pi_platter.py > /home/pi/solar_pi0_ws/web_prj/web_pi_platter.log 2>&1
    sudo chmod 644 /lib/systemd/system/web_pi_platter.service
    sudo systemctl daemon-reload
    sudo systemctl enable web_pi_platter.service
    sudo reboot
    sudo systemctl status web_pi_platter.service
