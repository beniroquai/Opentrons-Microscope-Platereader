# -*- coding: utf-8 -*-
"""
Created on Wed May 27 13:46:54 2020

@author: diederichbenedict
"""
from scipy.ndimage import  gaussian_filter
import tifffile as tif
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib
from scipy.optimize import curve_fit
import serial
import time
import time, datetime, os
import xystepper as xy
import picamera
import numpy
import cv2

# GLOBAL PARAMETERS
myfolder = './RESULTS/'

# Connect GLBR to Raspi: https://github.com/grbl/grbl/issues/1316

# Initialize the USB-Serial connection
serial = serial.Serial("/dev/ttyUSB0",115200)
time.sleep(1) # connect to ARduino

# Wake up grbl
serial.write("\r\n\r\n".encode())

# initiliaze camera
cam = picamera.PiCamera()

Npix_x, Npix_y = 640, 320 # (3280, 2464)
cam.resolution = (Npix_x, Npix_y)
cam.awb_mode = 'off'
cam.iso = 800
cam.start_preview()
#cam.exposure_compensation = 8
# Camera warm-up time
time.sleep(3)
print(cam.exposure_speed)

print(cam.framerate)
#cam.exposure_mode = 'off'
from fractions import Fraction
cam.framerate = Fraction(5,1)
cam.shutter_speed = 100000

# parameters for the x/y stage
stepsize_x = 0.03 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
stepsize_y = 0.023 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
myoffsetx = 0  # offset steps for the x dirrection
myoffsety = 0 # offset steps for the y dirrection
mybacklashx = 7
mybacklashy = 45 # this is required to offset the stage from the non-moving rim
Nx = 2
Ny = 2
stepsizeZ = 15 # 10
z_min = 500
z_max = 700



# Initialize position of the XY-stages
Stepper_XY = xy.xyStepper(myserial=serial, mycurrentposition=(0,0), mystepper='xy', backlash=mybacklashx)

iscan = 0
try:
    # move stepper forward/backward in X
    for ix in range(Nx):
        for iy in range(Ny):
            #print('going to position X/Y :' + str(ix)+'/'+str(iy))
            # go to xy-step
            stepx = stepsize_x*ix+myoffsetx
            stepy = stepsize_y*iy+myoffsety

            Stepper_XY.go_to(stepx, stepy)
            time.sleep(.5)
            # grab a frame and wait until the camera settles
            # print('Grabbing frame')
            mystdall = []
            myzstepsall = []
            #background = np.empty((Npix_y, Npix_x, 3), dtype=np.uint8)
            #cam.capture(background, 'bgr')

            for iz in range(z_min,z_max,stepsizeZ):
                Stepper_XY.go_to_z(iz)
                time.sleep(0.)
                image = np.empty((Npix_y, Npix_x, 3), dtype=np.uint8)
                cam.capture(image, 'bgr')
                #image = np.mean(image,-1)
                #image = image/(background+1)
                image = image[:,:,1]
                image = gaussian_filter(image, 1.5)
                #image = image-np.min(image)
                #image = image/np.max(image)*255
                mystd = np.std(image)
                #cv2.imwrite(filename, image)
                mystdall.append(mystd)
                myzstepsall.append(iz)

                print(str(iscan)+ " STDV: " + str(mystd))
            #Stepper_XY.go_to_z(0)
    # Reset position of X/Y stepper
            # fitting
            mystd = np.squeeze(np.array(mystdall))
            myallz = np.squeeze(np.array(myzstepsall))

            mystd -= np.min(mystd)
            mystd /= np.max(mystd)
            mystd = gaussian_filter(mystd,2)

            def gauss(x, a0, mu, sigma):
                return a0*np.exp(-(x-mu)**2/(2.*sigma**2))

            xdatafit = np.linspace(0,1,100) #mystd.shape[0])
            xdata = np.linspace(0,1,mystd.shape[0])
            p0 = [1., np.mean(mystd), 2.]
            coeff, var_matrix = curve_fit(gauss, xdata, mystd, p0=p0)

            # Get the fitted curve
            gauss_fit = gauss(xdatafit, coeff[0], coeff[1], coeff[2])
            gaussmax = coeff[1] # np.argmax(gauss_fit)
            print(gaussmax)
            zstepmax = np.int32(np.squeeze(gaussmax*(z_max-z_min)+z_min))
            #zstepmax = np.squeeze(myallz[gauss_fit==np.max(gauss_fit)])
            #zstepmax = np.squeeze(myallz[mystd==np.max(mystd)])
            print("Going to: "+str(zstepmax))
            # go to position with max stdv
            Stepper_XY.go_to_z(zstepmax + stepsizeZ)
            time.sleep(1)

            filename = myfolder+'/scan_xyz_'+str(iscan) + '_' + str(stepx)+'_'+str(stepy)+'_'+str(iz)+'.jpg'
            cam.capture(filename)
            iscan +=1



except Exception as e:
    print(e)
    cam.stop_preview()
    Stepper_XY.go_to_z(0)
    Stepper_XY.go_to(myoffsetx, myoffsety)


cam.stop_preview()
plt.plot(xdata, mystd, label='raw data')
plt.plot(xdatafit, gauss_fit, label='Fitted ydata')
plt.show()

Stepper_XY.go_to_z(0)
