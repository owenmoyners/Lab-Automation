"""
SCRIPT TO MEASURE CURRENT VS TIME IN PHOTOCHEMICAL ETCHING SETUP

JUST INPUT VALUES IN BELOW SECTION AND RUN

ANY PROBELMS ASK ME - OWEN MOYNIHAN
owen.moynihan@tyndall.ie
"""

''' INPUT VALUES HERE '''

V = 1 # in volts

T = 0.5  #in minutes

file_name = 'Etch' # do not specify file type (saves as csv)

LED_power = "10mW" #record LED power

etchant = "FeCl3 0.1M" #record etchant and molarity

#Enter path to save file
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work'










'''PROGRAM SETUP - DONT CHANGE ANYTHING BELOW '''
'''
v1.0 - base test
v1.1 - added warning for overwriting file 

'''
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
Keithley = rm.open_resource('GPIB0::24::INSTR') #GPIB ADDRESS FOR KEITHLEY

#assigning variables
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error

os.chdir(r_path)  #changing path 
file_csv = file_name + ".csv"
File = os.path.isfile(file_csv)
#print(File)

if File == True:
    print("WARNING - READ BELOW:")
    time.sleep(1)
    print(f"You will overwrite pervious {file_name} file")
    print("Right click this window and press 'Quit' to cancel, or left click and press anything to continue")
    input("Press Enter to continue: ")
    print("Continuing...")
    
I = []
T_l = []

T_s = T*60 + 1
T_s = int(T_s)
T_l = list(range(T_s))

#compliance = 20e-3 # in amps



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
    i = Keithley.query_ascii_values(":FETC?")[1]
    I.append(i) #saving value to list
    print(f"{t} \t \t \t {i}") #printing values
    time.sleep(0.9) #waiting 1 second


Keithley.write(":OUTP OFF")


#Saving data to a csv file
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Time (s)', 'Current (A)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writerow({'Time (s)': f"Voltage = {V}V, LED power = {LED_power}, Etchant = {etchant}" })     
    
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
matplotlib.pyplot.figtext(0.15,0.85, "V = 2V ".format(V=V), fontsize = "large")
matplotlib.pyplot.figtext(0.15,0.8, f"LED Power = {LED_power} ", fontsize = "large")
matplotlib.pyplot.figtext(0.15,0.75, f"Etchant = {etchant} ", fontsize = "large")
plt.grid(True, alpha=0.5)
plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.savefig(f"{file_name}.png", dpi=500 , bbox_inches='tight')

plt.show()



print("\nSee plot in plot window")
print(f"Saved in {r_path}")