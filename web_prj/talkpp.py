import requests 
import subprocess 
import os

# Get info from Pi_Platter
def command(arg):
	if arg=='-s' or arg=='-t' or arg=='-f' or arg=='-a' or arg=='-d' or arg=='-w':
		stout = subprocess.check_output(['talkpp', arg]).strip()
	else:
		stout = subprocess.check_output(['talkpp', '-c', arg]).strip()
	return stout

# Write to Pi_Platter
def write2pp(bitname, value):
        os.system("talkpp -c {}={}".format(bitname,value))
        check = command(bitname)
        return check

# Decode the integer status code
def status_info():
	bit_desc=['USB Fault Detected', 
        	  'Reserved', 
	          'powerup_1', 
        	  'powerup_2', 
	          'Battery Charging', 
	          'USB Supplying Power', 
        	  'Battery Critical', 
	          'Battery Low']

	int_code = command('S')	

	status = [{bit_desc[i]:bit} for i, bit in enumerate('{0:08b}'.format(int(int_code)))]
	
	# combine powerup bits and decode
	powerup = status[2]['powerup_1']+status[3]['powerup_2']

	if powerup == '00':
		powerup_txt = 'by alarm'
	elif powerup == '01':
		powerup_txt = 'by button'
	elif powerup == '10':
		powerup_txt = 'battery restart'
	elif powerup == '11':
		powerup_txt = 'watchdog restart'    
    
	# add decoded powerup reason to status list
	status.insert(2,{'Power Up': powerup_txt})

	# remove individual power up bits from status list
	status.pop(4)
	status.pop(3)

	return status

# Decode the analog setting code
def analog_info(arg):

        if arg == '0':
                amode = 'PMIC/RTC VCC'
        elif arg == '1':
                amode = '1.024 V'
        elif arg == '2':
                amode = '2.048 V'
        elif arg == '3':
                amode = '4.096 V'
        else:
        		# return info for debugging
                amode = [arg, type(arg)] 
        return amode

# Decode the PWM setting code
def PWM_info(arg):
	
	if arg == '0':
		pwmmode = 'Fast, 46875 Hz'
	elif arg == '1':
		pwmmode = 'Medium, 2930 Hz'
	elif arg == '2':
		pwmmode = 'Slow, 732 Hz'
	elif arg == '3':
		pwmmode = 'Servo Mode'
	else:
		# return info for debugging
		pwmmode = [arg, type(arg)]
	return pwmmode


def pp_configs(arg):

	if arg == 'general':
		return [
			{'device time':{'setting':command('-f'),'control':{'set':'-s'}}},
			{'version':command('V')},
			{'battery voltage':command('B')},
                      	] + status_info()
	
        elif arg == 'timers':
		return [
			{'current time':command('T')},
			{'power off':command('O')},
			{'wakeup':command('W')},
			{'wakeup pretty':command('-w')},
			{'wakeup repeat':command('R')},
			]

        elif arg == 'io':
		return [
			{'USB-2':{'setting':command('U1'),'control':{'ON':'U1=1','OFF':'U1=0'}}},
			{'USB-3':{'setting':command('U2'),'control':{'ON':'U2=1','OFF':'U2=0'}}},
			{'analog-1':command('A1')},
			{'analog-2':command('A2')},
			{'PWM-1':{'setting':command('P1'),'control':{'+':'P1='+str(int(command('P1'))+3),'-':'P1='+str(int(command('P1'))-3)}}},
			{'PWM-2':{'setting':command('P2'),'control':{'+':'P2='+str(int(command('P2'))+3),'-':'P2='+str(int(command('P2'))-3)}}},
			]

        elif arg == 'control':
		return [
			{'C0: Wakeup Enable':{'setting':command('C0'),'control':{'ON':'C0=1','OFF':'C0=0'}}},
			{'C1: Low Battery Warning Enable':{'setting':command('C1'),'control':{'ON':'C1=1','OFF':'C1=0'}}},
			{'C2: Critical Battery Warning Enable':{'setting':command('C2'),'control':{'ON':'C2=1','OFF':'C2=0'}}},
			{'C3: USB Fault Warning Enable':{'setting':command('C3'),'control':{'ON':'C3=1','OFF':'C3=0'}}},
			{'C4: Analog 1 Reference':{'setting':analog_info(command('C4')),'control':{'PMIC':'C4=0','1.024 V':'C4=1','2.048 V':'C4=2','4.096 V':'C4=3'}}},
			{'C5: Analog 2 Reference':{'setting':analog_info(command('C5')),'control':{'PMIC':'C5=0','1.024 V':'C5=1','2.048 V':'C5=2','4.096 V':'C5=3'}}},
			{'C6: PWM Mode':{'setting':PWM_info(command('C6')),'control':{'Fast':'C6=0','Medium':'C6=1','Slow':'C6=2','Servo':'C6=3'}}},
			{'C7: Restart Enable':{'setting':command('C7'),'control':{'ON':'C7=1','OFF':'C7=0'}}},
			{'C8: Watchdog Control':{'setting':command('C8'),'control':{'ON':'C8=1','OFF':'C8=0'}}},
			]

        elif arg == 'eeprom':
		return [
			{'E0: Battery Low Warn Threshold':{'setting':round(float(command('E0'))*0.00423783877,2),'control':{'up':'E0='+str(int(command('E0'))+2),'down':'E0='+str(int(command('E0'))-2)}}},
			{'E1: Battery Critical Threshold':round(float(command('E1'))*0.00423783877,2)},
                        {'E2: Battery Start Under-voltage Threshold':round(1/(float(command('E2'))/1023)*1.024+0.15,2)},
                        {'E3: Battery Restart Threshold':{'setting':round(1/(float(command('E3'))/1023)*1.024+0.15,2),'control':{'up':'E3='+str(int(command('E3'))-2),'down':'E3='+str(int(command('E3'))+2)}}},
                        {'E4: Battery Critical to Turn-off Timeout':command('E4')},
                        {'E5: Battery Warn Message Enable':{'setting':command('E5'),'control':{'ON':'E5=1','OFF':'E5=0'}}},
                        {'E6: Battery Critical Message Enable':{'setting':command('E6'),'control':{'ON':'E6=1','OFF':'E6=0'}}},
                        {'E7: Battery Restart Enable':{'setting':command('E7'),'control':{'ON':'E7=1','OFF':'E7=0'}}},
                        {'E8: USB Fault Message Enable':{'setting':command('E8'),'control':{'ON':'E8=1','OFF':'E8=0'}}},
                        {'E9: USB Port 2 Default Power Enable':{'setting':command('E9'),'control':{'ON':'E9=1','OFF':'E9=0'}}},
                        {'E10: USB Port 3 Default Power Enable':{'setting':command('E10'),'control':{'ON':'E10=1','OFF':'E10=0'}}},
                        {'E11: Analog 1 Default Reference':{'setting':analog_info(command('E11')),'control':{'PMIC':'E11=0','1.024 V':'E11=1','2.048 V':'E11=2','4.096 V':'E11=3'}}},
                        {'E12: Analog 2 Default Reference':{'setting':analog_info(command('E12')),'control':{'PMIC':'E12=0','1.024 V':'E12=1','2.048 V':'E12=2','4.096 V':'E12=3'}}},
                        {'E13: PWM Mode':{'setting':PWM_info(command('E13')),'control':{'Fast':'E13=0','Medium':'E13=1','Slow':'E13=2','Servo':'E13=3'}}},
                       ]

def main():
	print "library of functions to speak to the pi platter"

if __name__ == "__main__":
	main()
