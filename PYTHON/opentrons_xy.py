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
import xystepper as xy
import picamera

# GLOBAL PARAMETERS
mydatafolder = './RESULTS/'

# Connect GLBR to Raspi: https://github.com/grbl/grbl/issues/1316

# Initialize the USB-Serial connection
serial = serial.Serial("/dev/ttyUSB0",115200)
time.sleep(1) # connect to ARduino

# Wake up grbl
serial.write("\r\n\r\n".encode())

# initiliaze camera
cam = picamera.PiCamera()
cam.resolution = (3280, 2464)
cam.resolution = (1640, 922)
cam.start_preview()
# Camera warm-up time
time.sleep(2)

# parameters for the x/y stage 
stepsize_x = 0.03 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
stepsize_y = 0.023 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
myoffsetx = 0  # offset steps for the x dirrection
myoffsety = 0 # offset steps for the y dirrection
mybacklashx = 7
mybacklashy = 45 # this is required to offset the stage from the non-moving rim
Nx = 15
Ny = 15
stepsizeZ = 500
z_min = 8500
z_max = 9000


# create folder for measurements
try: 
	os.mkdir(mydatafolder)	
except: 
	print('Folder already exists')
todaystr = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
myfolder = mydatafolder + 'scan_'+todaystr
os.mkdir(myfolder)


# Initialize position of the XY-stages
Stepper_XY = xy.xyStepper(myserial=serial, mycurrentposition=(0,0), mystepper='xy', backlash=mybacklashx)

print('Start programm')

# Flush anything which is on the pipe..
serial.flushInput()

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
            time.sleep(1.5)
    	    # grab a frame and wait until the camera settles
    	    #print('Grabbing frame')
            for iz in range(z_min,z_max,stepsizeZ):
                Stepper_XY.go_to_z(iz)
                time.sleep(.25)
                filename = myfolder+'/scan_xyz_'+str(iscan) + '_' + str(stepx)+'_'+str(stepy)+'_'+str(iz)+'.jpg'
                cam.capture(filename)
                iscan +=1
                print(filename)
            Stepper_XY.go_to_z(0)	    
    # Reset position of X/Y stepper
except Exception as e: 
    print(e)
    Stepper_XY.go_to_z(0)
    Stepper_XY.go_to(myoffsetx, myoffsety)

# return to the home coordinates 
Stepper_XY.go_to_z(0)
Stepper_XY.go_to(myoffsetx, myoffsety)