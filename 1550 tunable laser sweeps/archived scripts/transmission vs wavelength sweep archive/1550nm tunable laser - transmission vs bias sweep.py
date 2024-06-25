'''
SCRIPT TO RUN AN VI FOR 2602A KEITHLEY - CHANNEL A (HAVE FOUND SCRIPT NOT TO WORK FOR OTHER KINDS)

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
#Set current in mA
start_voltage = -8
end_voltage = 1.5
step = 0.02 #V



#Current limit A
limit = 0.2

#Path for file to be saved 
file_name = '1.5um wg D5 1600nm BvT'

#COPY AND PASTE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\TP EAM\TP EAM Run 2\Target 2\Transmission vs bias'

keithley_address = 'GPIB1::26::INSTR'

PM_101A = 'USB0::0x1313::0x8076::M00767635::INSTR'
PM_100D = 'USB0::0x1313::0x8078::P0031267::INSTR'

PM_address = PM_100D


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
powers = []
powers_dbm = []
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
keithley.write("smua.source.levelv = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")

power_meter = rm.open_resource(PM_address)

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
    power = float(power)
    powers.append(power)
    
    power = abs(power)
    power_dbm = 10*math.log(1000*abs(power) , 10)
    power_dbm = round(power_dbm , 4)
    powers_dbm.append(power_dbm)
    
    print(f"V: {v}V  I: {i}A")
    
    
keithley.write("smua.source.output = smua.OUTPUT_OFF ")   

'''Saving data to a csv file'''



os.chdir(r_path)   #changing path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (A)', 'Voltage (V)', 'Power (W)', 'Power (dBm)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        v = V[index]
        power = powers[index]
        power_dbm = powers_dbm[index]
        thewriter.writerow({'Current (A)':i, 'Voltage (V)':v, 'Power (W)': power, 'Power (dBm)': power_dbm} ) #adding lists to rows
        index = index + 1
        

#PLOTTING VI
plt.plot(V, powers_dbm, linewidth = 0.4)
#plt.yscale("log")
plt.xlabel("Voltage (V)")
plt.ylabel("Power (dBm)")
plt.show()

print("\nSee plot in plot window")
print(f"Saved in {r_path}")

    
    
    


