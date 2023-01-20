"""
Created on Thu Feb  3 14:48:26 2022

@author: owen.moynihan
"""


import pyvisa
import matplotlib.pyplot as plt
import os 
import csv
import time
from datetime import date
from datetime import datetime


index = 0


file_name = 'Sample1_DBR_L750_R14_100'


rm = pyvisa.ResourceManager()
print(rm.list_resources())

OSA = rm.open_resource('GPIB0::1::INSTR')

OSA.timeout = None

print(OSA.query("*IDN?")) # Check to make sure it is OSA

#GETTING POWER OF SPECTRUM
OSA.write("LDATA") #Trace A level data
#data_B = OSA.write("LDATB") #Trace B level data
#data_C = OSA.write("LDATC") #Trace C level data

print(OSA.read_bytes)

spectrum = OSA.read()  # reading output from OSA

spectrum_float = [float(s) for s in spectrum.split(',')] # splitting list elements into floats 
spectrum_float.pop(0) # taking out first term - not a data point

#GETTING WAVELENGTHS SPAN
OSA.write("WDATA") # writting command
wl = OSA.read() # reading output from OSA
print(spectrum_float)

wl_float = [float(s) for s in wl.split(',')] # splitting list elements into floats 
wl_float.pop(0) # taking out first term - not a data point
print(wl_float)

#PLOTTING SPECTRUM
plt.plot(wl_float, spectrum_float, linewidth = 0.4)


#MAKING CSV FILE OF DATA
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Wavelength (nm)', 'Power (dBm)'] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames) 
    
    thewriter.writeheader()
    
    for wl in wl_float:
        
        power = spectrum_float[index]
        wavelength = wl_float[index]
        thewriter.writerow({'Wavelength (nm)':wavelength, 'Power (dBm)':power}) #adding lists to rows
        index = index + 1 