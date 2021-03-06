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
# Define model function to be used to fit to the data above:
def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


# Initiliaze Focussensor
myserialport = "COM23" #"/dev/ttyUSB1"
ser = serial.Serial(myserialport, 115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
time.sleep(2)
ser.flushInput()
N_datapoints = 120//2
is_display = True
myvallist = []
navg = 5
avglis = []
myvallist_avg=[]
#%%
while(1):
    # Read the focus value
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
                
            myvallist.append(focus_val)
            focus_val_avg = np.mean(np.array(myvallist)[-navg:])
            if len(myvallist)>navg:
                myvallist_avg.append(focus_val_avg)
            else:
                myvallist_avg.append(focus_val)
            
            if(is_display):
                plt.subplot(211)
                N_Display=20
                plt.plot(x_data, y_data, label='Test data')
                plt.plot(x_data, y_fit, label='Fitted data')
                plt.subplot(212)
                if len(myvallist)>navg:
                    plt.plot(myvallist_avg[-N_Display:])
                
                plt.plot(np.array(myvallist)[-N_Display:])
                plt.show()
                
            
            print("The max focus is: "+str(focus_val_avg))
        # else:
        #     print("Too short")

    except KeyboardInterrupt as e:
        ser.close()
    except Exception as e: 
        print("missed something:"+str(e))
        #print(decoded_bytes)
        ser.flushInput()
        
        

ser.close()