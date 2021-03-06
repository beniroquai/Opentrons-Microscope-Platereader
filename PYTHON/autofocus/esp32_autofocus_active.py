# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:41:15 2021

@author: diederichbenedict
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:59:11 2020

@author: bene
"""
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
#import openflexure_microscope_client as ofm_client

# Define model function to be used to fit to the data above:
def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

def setpos(x,y=None,z=None):
    if type(x)==tuple or type(x)==np.ndarray:
        x,y,z=x[0],x[1],x[2]
    
    return {'x': x, 'y': y, 'z': z}

def getpos(pos):
    return np.array(((pos['x']),(pos['y']),(pos['z'])))


def getfocusval(ser, N_datapoints = 120, is_display =False):
    # Read the focus value
    focus_val = -1
    try:
        while(True):
            ser_bytes = ser.readline()
            decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            values = (decoded_bytes.split(","))
            values = np.uint16(np.array(values[0:len(values)-1]))
            #plt.plot(values), plt.show()
            ser.flushInput()
            
            
            # fit function
            y_data = values / np.max(values)
            x_data = np.linspace(0,1,y_data.shape[0])
            
            if (values.shape[0] == N_datapoints):
                if(False):
                    # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
                    p0 = [1., np.mean(y_data), 1.]
                    
                    coeff, var_matrix = curve_fit(gauss, x_data, y_data, p0=p0)
                    
                    # Get the fitted curve
                    y_fit = gauss(x_data, *coeff)
                    focus_val = p0[1]*y_data.shape[0]
                else:
                    y_fit = gaussian_filter(y_data, sigma=5)
                    focus_val = np.argmax(y_fit)/y_data.shape[0]
                if(is_display):
                    plt.plot(x_data, y_data, label='Test data')
                    plt.plot(x_data, y_fit, label='Fitted data')
                    plt.show()
            if focus_val != -1: 
                print("The max focus is: "+str(focus_val))
                return focus_val
            
        # else:
        #     print("Too short")

    except KeyboardInterrupt as e:
        ser.close()
    except:
        print("missed something:")
        #print(decoded_bytes)
        ser.flushInput()
    return focus_val

# Initiliaze Focussensor
myserialport =  "/dev/cu.SLAB_USBtoUART" # "COM23" #"/dev/ttyUSB1"
ser = serial.Serial(myserialport, 115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
time.sleep(2)
ser.flushInput()

focus_val_fix = 0.65 # getfocusval(ser=ser) # returns relative focus pos - if .65 is in focus you should somehow fix this value by moving focus up and down


## setup microscope
microscope = ofm_client.MicroscopeClient("21.3.2.3", port=5000)
microscope.set_zero()
pos = microscope.position
starting_pos = pos.copy()


print('Moving to some coordinate')
pos = setpos(0,1000,0)
microscope.move(pos)
focus_val = getfocusval(ser=ser) # returns relative focus pos - if .65 is in focus you should somehow fix this value by moving focus up and down

wh
focus_val_diff = focus_val - focus_val_fix
microscope.move_rel(setpos(0,0,focus_val_diff*100))

print('Moving to X')
pos = setpos(stepsx,0,0)
microscope.move(pos)
myX2 = input("What is the distance I moved in X?")
microscope.move(setpos(0,0,0))

print('Moving to Y')
pos = setpos(0,stepsy,0)
microscope.move(pos)
myY2 = input("What is the distance I moved in Y?")


# calculate mm per step
stepunitx = abs(float(myX1)-float(myX2))/stepsx # in mm
stepunity = abs(float(myY1)-float(myY2))/stepsy # in mm

np.save('calibxy.npy', (stepunitx,stepunity))
print("One step means: "+(str(stepunitx*1e3))+" mum in X, and "+(str(stepunity*1e3))+" um in Y")
# One step means: 1.5910000000000004 mum in X, and 1.6179999999999999 um in Y


        
        

ser.close()