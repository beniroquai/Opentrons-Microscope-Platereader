# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:41:15 2021

@author: diederichbenedict
"""

import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
from scipy import interpolate
import openflexure_microscope_client as ofm_client

# global lists for the autofocus value
myvallist = []
myvallist_avg = []
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


def getfocusval(ser, N_datapoints = 120, n_avg = 5, is_display=False):
    # Read the focus value
    focus_val = -1
    focus_val_avg = -1
    while(True):    
        try:
            ser_bytes = ser.readline()
            decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            values = (decoded_bytes.split(","))
            values = np.uint16(np.array(values[0:len(values)-1]))
            #plt.plot(values), plt.show()
            ser.flushInput()
            
            # fit function
            y_data = values
            x_data = np.linspace(0,1,y_data.shape[0])
            x_data_new = np.linspace(0,1,1000)
            if (values.shape[0] == N_datapoints):
                if(False):
                    y_data = values / np.max(values)
                    y_data = gaussian_filter(y_data, sigma=5)
                    
                    # p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
                    if "p0" in locals:
                        p0 = coeff
                    else:
                        p0 = [1., np.mean(y_data), 1.]
                    
                    coeff, var_matrix = curve_fit(gauss, x_data, y_data, p0=p0)
                    
                    # Get the fitted curve
                    y_fit = gauss(x_data, *coeff)
                    focus_val = p0[1]*y_data.shape[0]
                else:
                    y_fit = gaussian_filter(y_data, sigma=5)
                    f = interpolate.interp1d(x_data, y_fit)
                    focus_val = np.argmax(f(x_data_new))/x_data_new.shape[0]

                if focus_val != -1: 
                    myvallist.append(focus_val)
                    if len(myvallist)>=n_avg:
                        myvallist_avg.append(focus_val_avg)
                        focus_val_avg = np.mean(np.array(myvallist)[-n_avg:])
                    else:
                        myvallist_avg.append(focus_val)
                        focus_val_avg = focus_val
                    
                    return focus_val, focus_val_avg
                
                if is_display:
                    plt.subplot(121)
                    plt.plot(x_data, y_data, label='Test data')
                    plt.plot(x_data, y_fit, label='Fitted data')
                    plt.subplot(122)
                    N_Display=20
                    if len(myvallist)>n_avg:
                        plt.plot(myvallist_avg[-N_Display:])
                    plt.plot(np.array(myvallist)[-N_Display:])
                    plt.show()
                
                    

    # except KeyboardInterrupt as e:
    #     focus_val = -1 #ser.close()
    #     return
        except Exception as e:
            print("missed something:" + str(e))
            #print(decoded_bytes)
            ser.flushInput()
       

# Initiliaze Focussensor
myserialport = "COM23" #"/dev/ttyUSB1"
ser = serial.Serial(myserialport, 115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
time.sleep(2)
ser.flushInput()
N_datapoints = 120
is_display = False
n_avg = 5
avglis = []



## setup microscope
microscope = ofm_client.MicroscopeClient("21.3.2.3", port=5000)

#%%
microscope.set_zero()
pos = microscope.position
starting_pos = pos.copy()

#%
# let the sensor warm up 
for _ in range(n_avg): getfocusval(ser, N_datapoints)
_,focus_val_avg=getfocusval(ser, N_datapoints)
# assign current best focus position
focus_val_fix = focus_val_avg
print("My best focus value: "+str(focus_val_fix))

# move to different location
print('Moving to some coordinate')
pos = setpos(0,1000,0)
microscope.move(pos)

# let the sensor rearrange:
for _ in range(n_avg): getfocusval(ser, N_datapoints)
_,focus_val_new=getfocusval(ser, N_datapoints)
print("My new focus value: "+str(focus_val_new))

# do autofocus
focus_val_diff = 1

# measure difference
_,focus_val_avg=getfocusval(ser, N_datapoints)
focus_val_diff = focus_val_avg - focus_val_fix
steps_to_move = -focus_val_diff*50000
print("FocusVal: "+str(focus_val_avg)+", focus_val_diff: "+str(focus_val_diff) + " Steps to move: "+ str(steps_to_move))

#%%
# move focus
microscope.move_rel(setpos(0,0,steps_to_move))

# measure difference again
_,focus_val_avg=getfocusval(ser, N_datapoints)
focus_val_diff = focus_val_avg - focus_val_fix
steps_to_move = -focus_val_diff*50000
print("FocusVal: "+str(focus_val_avg)+", focus_val_diff: "+str(focus_val_diff) + " Steps to move: "+ str(steps_to_move))

       
#%%    

#ser.close()