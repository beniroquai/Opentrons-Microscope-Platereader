#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 07:16:31 2020

@author: bene
"""
import csv
import numpy as np
import matplotlib.pyplot as plt

# read data
data_raw = np.genfromtxt('RAW.csv', delimiter=';')
data_processed = np.genfromtxt('PROC.csv', delimiter=';')

plt.subplot(211), plt.title('RAW IR laser on ESP camera'),  plt.imshow(data_raw)
plt.subplot(212), plt.title('Gaussian filtered on ESP camera'),  plt.imshow(data_processed)
