'''
THIS SCRIPT RUNS LIV FOR 2602A KEITHLEY ON CHANNEL A - JUST CLICK RUN 

WORKS FOR ANY 2602A KEITHLEY AND THE NEWPORT POWER METER 

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN
'''

'''Adding Packages'''
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
from pylab import *

'''Input parameters here'''
#Set current in mA
start_voltage = -0.5
end_voltage = 1.8
step = 0.01 # in volts


#Current limit A
limit = 0.5

#Path for file to be saved 
file_name = 'A3803 2mm laser device'

#COPY AND PASTE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\A3803 laser'

keithley_address = 'GPIB0::28::INSTR'


'''Setting up test : Dont change anything from here'''
s_c_x = start_voltage/step #changing steps for loop
e_c_x = end_voltage/step #changing steps for loop
s_c_x = int(s_c_x)
e_c_x = int(e_c_x)

v = abs(e_c_x - s_c_x)
V_K = list(range(s_c_x,e_c_x + 1)) 
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
I = []
V = []
P = []

index = 0 #index with for loops

#Closes PMManager if it is open, otherwise there will be an error
subprocess.call(["taskkill","/F","/IM","PMManager 3.62.exe"])
time.sleep(0.1)

OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)

#Opening Power Meter using Serial number and using channel (0-3)
power_meter = OphirCOM.OpenUSBDevice('991112')
channel = 0

#Setting range to auto and measurement mode to Power (Check Ophir optoelectronics manual for indexing)
OphirCOM.SetRange(power_meter, channel, 0)
OphirCOM.SetMeasurementMode(power_meter, channel, 0)

#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Make sure it is the right address for Keithley 
keithley = rm.open_resource(keithley_address)

#Checking on console that it is correct address
print(keithley.query("*IDN?"))

keithley.write("smua.reset()")  
keithley.write("errorqueue.clear()")
keithley.write("smua.source.autorangei = smua.AUTORANGE_ON")
keithley.write("smua.source.limiti = " + str(limit))

#Going to display screen
#keithley.write('display.screen = 0')

'''Beginning test'''
keithley.write("smua.source.func = smua.OUTPUT_DCVOLTS")

#Changing to 0 just before turning it on 
keithley.write("smua.source.levelv = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")

#turning on power meter 
OphirCOM.StartStream(power_meter, channel)
time.sleep(1)

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
    p_arrays = OphirCOM.GetData(power_meter, 0) # (Check Ophir optoelectronics manual for indexing)
    time.sleep(0.05)
    p_array = p_arrays[0]
    while p_array == ():
        print("Changing range of power meter")
        time.sleep(0.2)
        p_arrays = OphirCOM.GetData(power_meter, 0)
        p_array = p_arrays[0]
    p = p_array[0]
    p = abs(p)
    P.append(p)
    print(f"V: {v}V  I: {i}A P: {p}W")
    
keithley.write("smua.source.output = smua.OUTPUT_OFF ")   

OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()

'''Saving data to a csv file'''
os.chdir(r_path)   #changing path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (A)', 'Voltage (V)', 'Power (W)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        v = V[index]
        p = P[index]
        thewriter.writerow({'Current (A)':i, 'Voltage (V)':v, 'Power (W)': p}) #adding lists to rows
        index = index + 1
     
        
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
a1.plot(V,V)
a1.set_ylabel('Current (A)')
a2 = a1.twinx()
a2.plot(I, P,'r')
a2.set_ylabel('Power (W)')
a1.set_xlabel('Voltage (V)')
fig.legend(labels = ('I','L'), bbox_to_anchor=(1.18,1 ))
plt.grid(True, alpha=0.5)
plt.savefig(f"{file_name}.png", dpi=500, bbox_inches='tight')
plt.show()

print("\nSee plot in plot window")
print(f"Saved in {r_path}")

    
    
    


