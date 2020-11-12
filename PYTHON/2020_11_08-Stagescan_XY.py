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
cam.resolution = (1024, 768)
cam.start_preview()
# Camera warm-up time
time.sleep(2)

# parameters for the x/y stage 
stepsize = 0.1 # One STEPSIZE in X/Y of the cheap-stage  is 17.27 µm
myoffsetx = 0  # offset steps for the x dirrection
myoffsety = 0 # offset steps for the y dirrection
mybacklashx = 7
mybacklashy = 45 # this is required to offset the stage from the non-moving rim
Nx = 10
Ny = 10 
StepsizeX = 10
StepsizeY = 10

# create folder for measurements
try: 
	os.mkdir(mydatafolder)	
except: 
	print('Folder already exists')
todaystr = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
myfolder = mydatafolder + 'ptycho_'+todaystr
os.mkdir(myfolder)


# Initialize position of the XY-stages
Stepper_XY = xy.xyStepper(myserial=serial, mycurrentposition=(0,0), mystepper='xy', backlash=mybacklashx)

if(0):
    # Make sure we are at the edge of the stage 
    mycmd = Stepper_X.reset_pos()
    mycmd = Stepper_Y.reset_pos()


print('Start programm')

# Flush anything which is on the pipe..
serial.flushInput()

# move stepper forward/backward in X
for ix in range(Nx):
    for iy in range(Ny):
        print('going to position X/Y :' + str(ix)+'/'+str(iy))
        # go to xy-step
        Stepper_XY.go_to(stepsize*ix+myoffsetx, stepsize*iy+myoffsety)
        time.sleep(3)
            # grab a frame and wait until the camera settles
            #print('Grabbing frame')
        cam.capture(mydatafolder+'scan_xy_'+str(ix)+'_'+str(iy)+'.jpg')
        
        for iz in range(15):
            Stepper_XY.go_to_z(1000*iz)
            time.sleep(.5)
            
# Reset position of X/Y stepper
Stepper_XY.go_to(myoffsetx, myoffsety)



