'''
THIS SCRIPT RUNS LIV FOR 2602A KEITHLEY ON CHANNEL A - JUST CLICK RUN 

WORKS FOR ANY 2602A KEITHLEY AND THE THORLABS POWER METER

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN
'''

'''Input parameters here'''
#Set voltage in volts
start_voltage = 0
end_voltage = 2
step = 0.05 # in volts


#Current limit A
limit = 0.3

#Path for file to be saved 
file_name = 'LIVtest'


#COPY AND PASTE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work'

keithley_address = 'GPIB1::26::INSTR'

PM_101A = 'USB0::0x1313::0x8076::M00767635::INSTR'
PM_100D = 'USB0::0x1313::0x8078::P0031267::INSTR'

PM_address = PM_100D

'''Setting up test : Dont change anything from here'''

#adding packages 
import pyvisa
import time
from datetime import date
from datetime import datetime
import os 
import csv
import matplotlib.pyplot as plt
import win32gui
import win32com.client
import traceback
import subprocess
import usb
from IPython import get_ipython
import matplotlib.pyplot as plt 
from collections import deque 
get_ipython().run_line_magic('matplotlib', 'qt')

s_c_x = start_voltage/step #changing steps for loop
e_c_x = end_voltage/step #changing steps for loop
s_c_x = int(s_c_x)
e_c_x = int(e_c_x)

v = abs(e_c_x - s_c_x)
V_K = list(range(s_c_x,e_c_x + 1)) 
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
os.chdir(r_path)   #changing path 
I = []
V = []
P = []

index = 0 #index with for loops


#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Make sure it is the right address for Keithley 
keithley = rm.open_resource(keithley_address)

subprocess.call(["taskkill","/F","/IM","Thorlabs Optical Power Monitor.exe"])
inst = rm.open_resource('USB0::0x1313::0x8078::P0031267::INSTR') 
power_meter = rm.open_resource(PM_address)

#power_meter = ThorlabsPM100(inst=inst) #setting thorlabs to be talked to 

#Checking on console that it is correct address
print(keithley.query("*IDN?"))

keithley.write("smua.reset()")  
keithley.write("errorqueue.clear()")
keithley.write("smua.source.autorangei = smua.AUTORANGE_ON")
keithley.write("smua.source.limiti = " + str(limit))

#Going to display screen
#keithley.write('display.screen = 0')

power_meter.write('power:dc:unit W')

'''Beginning test'''
keithley.write("smua.source.func = smua.OUTPUT_DCVOLTS")

#Changing to 0 just before turning it on 
keithley.write("smua.source.levelv = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")


#reads untrue high value at the beginning (as it switches range)
for i in range(10):
    power_meter.query('measure:power?')
    time.sleep(0.1)

for v in V_K:
    v = v*step
    v = "{:.6f}".format(v) #going to 6 decimal places
    keithley.write("smua.source.levelv = " + str(v))
    time.sleep(0.05)
    keithley.write('print(smua.measure.i())') #careful with the quotation mark placement.
    i = keithley.read()
    i = i[:-1] # taking off some string line
    i = float(i)
    I.append(i) #saving value to list
    v = float(v)
    V.append(v)
    power = power_meter.query('measure:power?')
    p = float(power)
    P.append(p)
    print(f"V = {v}  I = {i} P = {p}")
    

    plt.pause(0.05) 
    
keithley.write("smua.source.output = smua.OUTPUT_OFF ")   


'''Saving data to a csv file'''
#should really change this to the numpy way...
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (A)', 'Voltage (V)', 'Power (W)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        v = V[index]
        p = P[index]
        thewriter.writerow({'Current (A)':i, 'Voltage (V)':v, 'Power (W)': p}) #adding lists to rows
        index = index + 1

get_ipython().run_line_magic('matplotlib', 'inline')         

from pylab import *      
rc('axes', linewidth=2)
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"     

#PLOTTING VI
plt.plot(V, I, linewidth = 0.4)
plt.xlabel("Voltage (V)")
plt.ylabel("Current (A)")
plt.show()

plt.plot(I, P, linewidth = 0.4)
plt.xlabel("Current (A)")
plt.ylabel("Power (W)")
plt.show()


fig = plt.figure()
a1 = fig.add_axes([0,0,1,1])
a1.plot(I,V)
a1.set_ylabel('Voltage (V)')
a2 = a1.twinx()
a2.plot(I, P,'r')
a2.set_ylabel('Power (W)')
a1.set_xlabel('Current (A)')
fig.legend(labels = ('I','L'), bbox_to_anchor=(1.18,1 ))
plt.grid(True, alpha=0.5)
plt.savefig(f"{file_name}.png", dpi=500, bbox_inches='tight')
plt.show()

print("\nSee plot in plot window")
print(f"Saved in {r_path}")

    
    
    


