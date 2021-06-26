# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 16:43:24 2021

@author: diederichbenedict
"""
import serial
import time


class pyGraver():
    def __init__(self, port="/dev/ttyUSB0"):
        self.is_debug = False
        self.port = port
        self.baudrate = 57600
        self.location = [0,0]
        self.init_connexion()
        
    def init_connexion(self):
        self.homing()

    def homing(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate )
        except:
            print("Reopening the connection")
            self.serial.close()
            time.sleep(3)
            self.serial = serial.Serial(self.port, self.baudrate )
            
        self.location = [0,0]
            
        # HOMING
        # #FF#09#5A#A5
        self.send_CMD(9, 90, 165)
        # #FF#AA#08#01#01#5A#A5#55
        self.send_CMD_array([170, 8, 1, 1, 90, 165, 85])
        time.sleep(4)

    def close(self):
        self.serial.close()

    def send_CMD(self, D1, D2, D3):
        buffer = bytes([255, D1, D2, D3])
        if self.is_debug: print("send", buffer)
        self.serial.write(buffer)
        self.serial.flush()

    def send_CMD_array(self, arr):
        if self.is_debug: print("send", arr)
        buffer = bytes([255]+arr)
        if self.is_debug: print("send", buffer)
        self.serial.write(buffer)
        self.serial.flush()


    def moveXY(self, x, y):
        diff_x, diff_y = x-self.location[0],y-self.location[1]
        self.location = [x,y]
        self.send_CMD_array([
            170, 16, 5, 1, 80, 1,
            int(x // 256), int(x % 256),
            int(y // 256), int(y % 256),
            0, 0, 0, 0, 85])
        if self.is_debug:  print("I need to wait: "+str((abs(diff_x)+abs(diff_y))/500) + "s")
        #time.sleep((abs(diff_x)+abs(diff_y))/500)
        

    def move(self):
        x = self.location[0]
        y = self.location[1]
        self.moveXY(x, y)

 
# TODO command line usage
g = pyGraver("COM7")

#%%


j =10
ix=0
i= 10
for i in range(255):
    print(i)
    ix += 3
    g.send_CMD(i, j, 0)
    if ix == 10:
        time.sleep(1)
    g.send_CMD(9, j, 0)
    g.moveXY(ix,100)
    time.sleep(.1)
#%%
g.moveXY(10,100)
g.moveXY(1200,1000)
g.moveXY(100,100)

dfsg
g.homing()


g.close()