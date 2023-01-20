'''
THIS SCRIPT RUNS LOG IV FOR 2602A KEITHLEY ON CHANNEL A - JUST CLICK RUN 

WORKS FOR ANY 2602A KEITHLEY : JUST MAKE SURE GPIB ADDRESS IS RIGHT 

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN
'''


'''Adding packages'''
import pyvisa
import time
from datetime import date
from datetime import datetime
import os 
import csv
import numpy as np
import matplotlib.pyplot as plt

'''Input parameters here'''
#Choose starting and end current in A (e.g 1nA = 1e-9)
start_current = 1e-9
end_current = 250e-3 

points = 200 #how many points you want to take

#Path for file to be saved 
file_name = 'test_IV'

path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work'


'''Setting up test'''
start_current = np.log10(start_current)
end_current = np.log10(end_current)
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
I = np.logspace(start_current, end_current, num=points, base=10)
V = []
index = 0 #index with for loops

#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Make sure it is the right address for Keithley 
keithley = rm.open_resource('GPIB0::28::INSTR')

#Checking on console that it is correct address
print(keithley.query("*IDN?"))

#Going to display screen
keithley.write('display.screen = 0')

keithley.write("errorqueue.clear()")
#keithley.write("smub.source.autorangev = smua.AUTORANGE_ON")
#keithley.write("smub.source.limitv = " + str(limit))

'''Beginning test'''
keithley.write("smua.source.func = smua.OUTPUT_DCAMPS")

#Changing to 0 just before turning it on 
keithley.write("smua.source.leveli = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")


for i in I:
    keithley.write("smua.source.leveli = " + str(i))
    time.sleep(0.05)
    keithley.write('print(smua.measure.v())') #careful with the quotation mark placement.
    v = keithley.read()
    v = float(v)
    V.append(v) #saving value to list
    print(f"I: {i}mA  V: {v}V")
  
    
keithley.write("smub.source.output = smua.OUTPUT_OFF ")     
'''Saving data to a csv file'''
os.chdir(r_path)   #chaning path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (mA)', 'Voltage (V)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        v = V[index]
        thewriter.writerow({'Current (mA)':i, 'Voltage (V)':v}) #adding lists to rows
        index = index + 1


#plot IV 
plt.plot(V, I, linewidth = 0.4)
plt.yscale("log")
plt.yscale("log")
plt.xlabel("Current (A)")
plt.ylabel("Voltage (V)")
plt.show()
    
    
    

