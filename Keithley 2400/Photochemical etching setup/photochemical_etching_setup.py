# -*- coding: utf-8 -*-
"""
SCRIPT TO MEASURE CURRENT VS TIME IN PHOTOCHEMICAL ETCHING SETUP

JUST INPUT VALUES IN BELOW SECTION AND RUN

ANY PROBELMS ASK ME - OWEN MOYNIHAN
owen.moynihan@tyndall.ie
"""

''' INPUT VALUES HERE '''

V = 1 # in volts

T = 5  #in minutes

file_name = 'my file name'

#Enter path to save file
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work'










'''PROGRAM SETUP - DONT CHANGE ANYTHING BELOW '''
#adding packages 
import pyvisa
import time
from datetime import date
from datetime import datetime
import os 
import csv
import matplotlib.pyplot as plt
from pylab import *

#setting up connection
rm = pyvisa.ResourceManager()
rm.list_resources()
Keithley = rm.open_resource('GPIB0::29::INSTR') #GPIB ADDRESS FOR KEITHLEY

#assigning variables
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
I = []
T_l = []

T_s = T*60 + 1
T_s = int(T_s)
T_l = list(range(T_s))

#compliance = 20e-3 # in amps

os.chdir(r_path)  #changing path 

index = 0 #index with for loops

#Applying voltage to keithley and measuring current 
Keithley.write("*RST")
Keithley.timeout = 25000

Keithley.write(":SENS:FUNC:CONC OFF")
Keithley.write(":SOUR:FUNC VOLT")
Keithley.write(":SENS:FUNC 'CURR'")
#Keithley.write("SENS:CURR:PROT 10E-3")
Keithley.write(":OUTP ON")

Keithley.write(":SOUR:VOLT:LEV {V}".format(V=V))

Keithley.write(":OUTP ON")
print(f"Time (s): \t Current (A):")
for t in T_l:
    Keithley.query(":READ?")
    i = Keithley.query_ascii_values(":FETC?")
    i = i[1] #reading current from keithley 
    i = float(i) #turning value into float
    I.append(i) #saving value to list
    print(f"{t} \t \t \t {i}") #printing values
    time.sleep(1) #waiting 1 second


Keithley.write(":OUTP OFF")


#Saving data to a csv file
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Time (s)', 'Current (A)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        t = T_l[index]
        thewriter.writerow({'Time (s)':t, 'Current (A)':i}) #adding lists to rows
        index = index + 1

rc('axes', linewidth=2)
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"   

#plotting graph
plt.figure()
plt.plot(T_l, I,color="#0000a8ff", linewidth = 1, marker = 'D',
         markerfacecolor = 'red', markersize = 4)
plt.title(file_name)
matplotlib.pyplot.figtext(0.15,0.8, "V = {V}V".format(V=V), fontsize = "large")
plt.grid(True, alpha=0.5)
plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.savefig(f"{file_name}.png", dpi=500 , bbox_inches='tight')

plt.show()



print("\nSee plot in plot window")
print(f"Saved in {r_path}")