'''
SCRIPT TO RUN laser power vs photocurrent FOR 2602A KEITHLEY - CHANNEL A (HAVE FOUND SCRIPT NOT TO WORK FOR OTHER KINDS)

CHANGE PARAMETERS IN PARAMETER SECTION AND RUN 

MAKE SURE EVERYTHING IS CONNECTED TO THE PC 

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
import matplotlib.pyplot as plt
import math

'''INPUT PARAMETERS HERE'''
#Keithley Votlage
v = 0 # in V

#Set laser wavelength and power
wl = 1550 # set wl in nm
Pow_unit = 'DBM' # Can Set W, DBM
start_power = -10 
end_power = 3 
step = 0.1 

#Current limit A
limit = 0.2

#Path for file to be saved 
file_name = '1.5um wg D5 1600nm BvT'

#COPY AND PASTE FILE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\TP EAM\TP EAM Run 2\Target 2\Transmission vs bias'

keithley_address = 'GPIB1::26::INSTR'

laser_address = 'GPIB0::20::INSTR'

'''Setting up test : Dont change anything from here'''
s_c_x = start_power/step #changing steps for loop
e_c_x = end_power/step #changing steps for loop
s_c_x = int(s_c_x)
e_c_x = int(e_c_x)

p = abs(e_c_x - s_c_x)
P_k = list(range(s_c_x,e_c_x + 1)) 
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
I = []
P = []

index = 0 #index with for loops

#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
#print(rm.list_resources())

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
keithley.write(f"smua.source.levelv = {v}")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")

tune_laser = rm.open_resource(laser_address)

#set initial wavelength
tune_laser.write(":WAVE " + str(wl) + "nm")
#Sets unit for power
tune_laser.write(":POW:UNIT " + Pow_unit)
#Sets power for laser
tune_laser.write(":POW " + str(start_power))
#Turns laser on
tune_laser.write(":OUTP ON")

for p in P_k:

    p = p*step
    tune_laser.write(":POW " + str(p))
    p = "{:.5f}".format(v) #going to 6 decimal places
    time.sleep(0.2)
    keithley.write('print(smua.measure.i())') #careful with the quotation mark placement.
    i = keithley.read()
    i = i[:-1] # taking off some string line
    i = float(i)
    I.append(i) #saving value to list
    p = float(p)
    P.append(p)

    print(f"P: {p}{Pow_unit}  I: {i}A")
    
    
keithley.write("smua.source.output = smua.OUTPUT_OFF ")   


'''Saving data to a csv file'''
os.chdir(r_path)   #changing path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (A)', 'Voltage (V)', 'Power (W)', 'Power (dBm)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()
 
    for i in I:
        
        p = P[index]

        thewriter.writerow({'Current (A)':i, 'Power {Pow_unit}':p} ) #adding lists to rows
        index = index + 1
        
#PLOTTING VI
plt.plot(P, I, linewidth = 0.4)
#plt.yscale("log")
plt.xlabel(f"Power {Pow_unit} ")
plt.ylabel("Current (A)")
plt.show()

print("\nSee plot in plot window")
print(f"Saved in {r_path}")