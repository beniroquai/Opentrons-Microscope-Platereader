#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:59:11 2020

@author: bene
"""
import serial
import time
import xyz_stepper as xyz
import picamera
import numpy as np
import time, datetime, os

# Initiliaze Focussensor
serial_focus = "/dev/ttyUSB1"
serial_xyz = "/dev/ttyUSB0"


# GLOBAL PARAMETERS
mydatafolder = './RESULTS/'

# Initialize the USB-Serial connection
time.sleep(1) # connect to ARduino

# Wake up grbl
serial.write("\r\n\r\n".encode())

# initiliaze camera
cam = picamera.PiCamera()

Npix_x, Npix_y = 640, 320 # (3280, 2464)
cam.resolution = (Npix_x, Npix_y)
#cam.awb_mode = 'off'
#cam.iso = 800
cam.start_preview(fullscreen=False,window=(200,000,Npix_y,Npix_x))


# parameters for the x/y stage
stepsize_x = 0.03 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
stepsize_y = 0.023 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
myoffsetx = 0  # offset steps for the x dirrection
myoffsety = 0 # offset steps for the y dirrection
mybacklashx = 7
mybacklashy = 45 # this is required to offset the stage from the non-moving rim
Nx = 20
Ny = 20
stepsizeZ = 5 # 10
z_min = 500
z_max = 700

# create folder for measurements
try: 
	os.mkdir(mydatafolder)	
except: 
	print('Folder already exists')
todaystr = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
myfolder = mydatafolder + 'scan_'+todaystr
os.mkdir(myfolder)



# Initialize position of the XY-stages
Stepper_XY = xyz.xyStepper(myserial=serial, mycurrentposition=(0,0), mystepper='xy', backlash=mybacklashx)

ierror = 0

# save for later use
myallx = []
myally = []
myallz = []

# define scan positions
myscanpos = np.hstack((np.arange(0,Ny),np.arange(Ny,0,-1)))
focuspos =0 
ix=0



def find_focus(self, iz_min, iz_max=1024):
    '''
    find_focus will go through z-steps andasks you to find the perceptually 
    best matching focus plane; Hit CTRL+c to stop the focus search
    
    
    Parameters
    ----------
    iz_min : INT
        Minimum search value.
    iz_max : INT, optional
        Maximum serach value. The default is 1024.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    
    # match focal planes
    iz = iz_min     # this should be outside the loop, I think
    while True:    # infinite loop
        try:
            
            # measure
            ser.flushInput()  # make sure latest line is read
            ser_bytes = ser.readline()
            decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            focuspos = int(decoded_bytes.split("pos: ")[-1])
            focusval = int(decoded_bytes.split("Val: ")[-1].split(" at")[0])
    
            print("iz: "+str(iz)+", "+str(focusval))
            
            # move 
            iz +=10
            Stepper_XY.go_to_z(iz)
            time.sleep(.2)
            
            if iz>iz_max:
                break
        except:
            print("Save the current slice as focus position")
            break
    
    # save them for later
    myfixfocus = focuspos
    myfixz = int(iz)
    
    return myfixfocus, myfixz

iscan = 0
# drive n steps fwd and bwd, mesureocus with sensor and compare both RESULTS
for iy in myscanpos:
    if(1):
        
        #Stepper_XY.go_to_z(0)        

        #print('going to position X/Y :' + str(ix)+'/'+str(iy))
        # go to xy-step
        stepx = stepsize_x*ix+myoffsetx
        stepy = stepsize_y*iy+myoffsety

        Stepper_XY.go_to(stepx, stepy)
        time.sleep(1)

        # Read the focus value
        ser.flushInput()  # make sure latest line is read
        ser_bytes = ser.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        focuspos = int(decoded_bytes.split("pos: ")[-1])
        
        print("stepy: "+str(stepy)+", focuspos: "+str(focuspos))
        myally.append(stepy)
        myallz.append(focuspos)
        
        filename = myfolder+'/scan_xyz_'+str(iscan) + '.jpg'
        cam.capture(filename)
        iscan +=1

        
        # correct focus:
        while np.abs(myfixfocus-focuspos)>0:
            # if the distance is positive, the curent sample is too high, hence we 
            # we must move the focus down, which corresponds to an increased iz value
            if (focuspos-myfixfocus)>0:
                iz += 3
            else:
                iz -= 3
            Stepper_XY.go_to_z(iz)
            time.sleep(.2)
            
            # Read the focus value
            ser.flushInput()  # make sure latest line is read
            ser_bytes = ser.readline()
            decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            focuspos = int(decoded_bytes.split("pos: ")[-1])
            print("Focus pos (should): "+str(myfixfocus)+", Focus pos (is):"+str(focuspos))

                
                
        
        
Stepper_XY.go_to_z(0)        

myally = np.array(myally)
myallz = np.array(myallz)
print("Saving the table")

np.save("myscanpos_z.npy", myallz)
np.save("myscanpos_y.npy", myally)

import matplotlib.pyplot as plt
plt.plot(myallz, 'x-'), plt.show()