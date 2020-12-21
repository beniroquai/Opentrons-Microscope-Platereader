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



#%% Initialize position of the XY-stages
Stepper_XYZ = xyz.xyzStepper(serial_xyz = "/dev/ttyUSB0", serial_focus = "/dev/ttyUSB1", mycurrentposition=(0,0),backlash=mybacklashx)

#%% find focus manually:
iz = 0
ix = 0
myfixfocus,iz=Stepper_XYZ.find_focus(iz_min=iz, iz_max=1024)

#%% save for later use
myallx = []
myally = []
myallz = []

# define scan positions
myscanpos = np.hstack((np.arange(0,Ny),np.arange(Ny,0,-1)))
iscan = 0


#%%
# drive n steps fwd and bwd, mesureocus with sensor and compare both RESULTS
for iy in myscanpos:
    if(1):
        
        #Stepper_XYZ.go_to_z(0)        

        #print('going to position X/Y :' + str(ix)+'/'+str(iy))
        # go to xy-step
        stepx = stepsize_x*ix+myoffsetx
        stepy = stepsize_y*iy+myoffsety

        Stepper_XYZ.go_to(stepx, stepy)
        time.sleep(1)

        # Read the focus value
        focuspos, focusval = Stepper_XYZ.measure_focus()
        
        print("stepy: "+str(stepy)+", focuspos: "+str(focuspos))
        myally.append(stepy)
        myallz.append(focuspos)
        
        filename = myfolder+'/scan_xyz_'+str(iscan) + '.jpg'
        cam.capture(filename)
        iscan +=1
        
        # correct focus:
        iz = Stepper_XYZ.hold_focus(aimedfocus=myfixfocus, currentz=iz, zstep=3)
        
                
        
        
Stepper_XYZ.go_to_z(0)        

myally = np.array(myally)
myallz = np.array(myallz)
print("Saving the table")

np.save("myscanpos_z.npy", myallz)
np.save("myscanpos_y.npy", myally)

import matplotlib.pyplot as plt
plt.plot(myallz, 'x-'), plt.show()