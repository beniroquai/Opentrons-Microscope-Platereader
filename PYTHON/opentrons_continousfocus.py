#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:59:11 2020

@author: bene
"""
import serial
import time
import xystepper as xy
import picamera

# Initiliaze Focussensor
ser = serial.Serial("/dev/ttyUSB1", 115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
ser.flushInput()


# Initialize the USB-Serial connection
serial = serial.Serial("/dev/ttyUSB0",115200)
time.sleep(1) # connect to ARduino

# Wake up grbl
serial.write("\r\n\r\n".encode())

# initiliaze camera
cam = picamera.PiCamera()

Npix_x, Npix_y = 640, 320 # (3280, 2464)
cam.resolution = (Npix_x, Npix_y)
#cam.awb_mode = 'off'
#cam.iso = 800
cam.start_preview()

# parameters for the x/y stage 
stepsize_x = 0.03 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
stepsize_y = 0.023 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
myoffsetx = 0  # offset steps for the x dirrection
myoffsety = 0 # offset steps for the y dirrection
mybacklashx = 7
mybacklashy = 45 # this is required to offset the stage from the non-moving rim
Nx = 2
Ny = 2
stepsizeZ = 5 # 10
z_min = 500
z_max = 700


# Initialize position of the XY-stages
Stepper_XY = xy.xyStepper(myserial=serial, mycurrentposition=(0,0), mystepper='xy', backlash=mybacklashx)

ierror = 0

while ierror<3:
    try:
        # Read the focus value
        ser_bytes = ser.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        focuspos = int(decoded_bytes.split("pos: ")[-1])
        focusval = int(decoded_bytes.split("Val: ")[-1].split(" at")[0])
        
        
        # Do some processing to match focuspos to measured value
        focuspos_real = 1024-focuspos*4 # match with dynamic range; also LUT likely necessary
        print(int(focuspos_real))
        # move objective
        Stepper_XY.go_to_z(focuspos_real)
        time.sleep(0.)
        
    except Exception as e: 
        print(e)
        ierror+=1