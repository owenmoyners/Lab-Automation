'''
SCRIPT TO RUN AN VI FOR 2602A KEITHLEY - CHANNEL B (HAVE FOUND SCRIPT NOT TO WORK FOR OTHER KINDS)

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

'''INPUT PARAMETERS HERE'''
#Set current in mA
start_voltage = 0
end_voltage = 4
step = 0.05 #V



#Current limit A
limit = 0.03

#Path for file to be saved 
file_name = 'ThinlaserVI_test'

#COPY AND PASTE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work\Test programs\Python Files\Keithly 2602A\IV\TestIV_folder'

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
index = 0 #index with for loops

#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Make sure it is the right address for Keithley 
keithley = rm.open_resource(keithley_address)

#Checking on console that it is correct address
print(keithley.query("*IDN?"))

keithley.write("smub.reset()")  
keithley.write("errorqueue.clear()")
keithley.write("smub.source.autorangei = smua.AUTORANGE_ON")
keithley.write("smub.source.limiti = " + str(limit))

#Going to display screen
#keithley.write('display.screen = 0')

'''Beginning test'''
keithley.write("smub.source.func = smua.OUTPUT_DCVOLTS")

#Changing to 0 just before turning it on 
keithley.write("smub.source.levelv = 0")
    
#Turns on output 
keithley.write("smub.source.output = smua.OUTPUT_ON ")


for v in V_K:
    v = v*step
    v = "{:.6f}".format(v) #going to 6 decimal places
    keithley.write("smub.source.levelv = " + str(v))
    time.sleep(0.2)
    keithley.write('print(smub.measure.i())') #careful with the quotation mark placement.
    i = keithley.read()
    i = i[:-1] # taking off some string line
    i = float(i)
    I.append(i) #saving value to list
    v = float(v)
    V.append(v)
    print(f"V: {v}V  I: {i}A")
    
keithley.write("smub.source.output = smub.OUTPUT_OFF ")   

'''Saving data to a csv file'''



os.chdir(r_path)   #changing path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (A)', 'Voltage (V)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        v = V[index]
        thewriter.writerow({'Current (A)':i, 'Voltage (V)':v}) #adding lists to rows
        index = index + 1
        

#PLOTTING VI
plt.plot(V, I, linewidth = 0.4)
plt.yscale("log")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (A)")
plt.show()

print("\nSee plot in plot window")
print(f"Saved in {r_path}")

    
    
    



