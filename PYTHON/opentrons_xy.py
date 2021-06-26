# -*- coding: utf-8 -*-

# GNU nano 2.9.3                                        main.py

'''
IMPORTANT: Execute as sudo
copyright@Bene
License GPLv3
'''
import serial
import time
import time, datetime, os
#import picamera


'''
Define the XYZ Stepper class
'''
class xyzStepper:
    mycurrentposition = 0
    max_steps = 100
    mystepper = 'x'
    backlash = 0
    highspeed = 2500
    lowspeed = 2500 
    '''
    X -> backwards
    x -> forwards
    '''

    def __init__(self, serial_xyz = "/dev/ttyUSB0",
                 mycurrentposition=0, backlash=0):

        self.mycurrentposition = mycurrentposition
        self.backlash = backlash
        
        print('Initializing XYZ-stepper')
        self.serial_xyz = serial.Serial(serial_xyz,115200) # Open grbl serial port
        self.serial_xyz.write("\r\n\r\n".encode())# Wake up grbl
        time.sleep(1)   # Wait for grbl to initialize 
        self.serial_xyz.flushInput()  # Flush startup text in serial input
        

    def go_to(self, pos_x, pos_y):
        #
        # Stream g-code to grbl
        g_dim = "G20"
        g_dist = "G90" # G91 is for incremental, G90 is for absolute distance
        g_x = "X"+str(pos_x)
        g_y = "Y"+str(pos_y)
        g_speed = "F25"
        line = g_dim + " " + g_dist + " "  + g_x + " " + g_y + " " + g_speed
        l = line.strip() # Strip all EOL characters for consistency        print( 'Sending: ' + l)
        self.serial_xyz.write((l + '\n').encode()) # Send g-code block to grbl
        grbl_out = self.serial_xyz.readline() # Wait for grbl response with carriage return
        print( ' : ' + (grbl_out.strip()).decode())

        self.mycurrentposition = (pos_x, pos_y)

#        time.sleep(abs(self.mystepstogo)*.01+.5)

  

#%%


### ATTENTION: replace 'usb' with something which looks like an Arduino

import serial.tools.list_ports as ports
com_ports = list(ports.comports()) # create a list of com ['COM1','COM2'] 
for i in com_ports:            
    if str(i).find('usb'):
        serialport = i.device
        print(serialport)
        
        
#%%
'''
initiliaze camera
'''
# GLOBAL PARAMETERS
mydatafolder = './RESULTS/'

# cam = picamera.PiCamera()
# cam.resolution = (3280, 2464)
# cam.resolution = (1640, 922)
# cam.start_preview()
# # Camera warm-up time
# time.sleep(2)

# parameters for the x/y stage 
stepsize = 3 

'''
File IO
'''
# create folder for measurements
try: 
	os.mkdir(mydatafolder)	
except: 
	print('Folder already exists')
todaystr = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

myfolder = mydatafolder + 'scan_'+todaystr
os.mkdir(myfolder)


'''
Initialize position of the XY-stages
'''
Stepper_XY = xyzStepper(serial_xyz=serialport)
stepx = 10
stepy = 10
Stepper_XY.go_to(stepx, stepy)


