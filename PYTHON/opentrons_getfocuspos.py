#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:59:11 2020

@author: bene
"""
import serial
ser = serial.Serial("/dev/cu.SLAB_USBtoUART", 115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
ser.flushInput()

while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        focuspos = decoded_bytes.split("pos: ")[-1]
        focusval = decoded_bytes.split("Val: ")[-1].split(" at")[0]
        print()
    except:
        pass