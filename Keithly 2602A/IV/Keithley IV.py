'''
SCRIPT TO RUN AN IV FOR 2602A KEITHLEY - CHANNEL A (HAVE FOUND SCRIPT NOT TO WORK FOR OTHER KINDS)

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
start_current = -5
end_current = 5
step = 0.2 #mA



#In volts
limit = 5

#Path for file to be saved 
file_name = 'A3650_thinlaser_070722'

#COPY AND PASTE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work'

keithley_address = 'GPIB0::28::INSTR'


'''Setting up test : Dont change anything from here'''
s_c_x = start_current/step #changing steps for loop
e_c_x = end_current/step #changing steps for loop
s_c_x = int(s_c_x)
e_c_x = int(e_c_x)

i = abs(e_c_x - s_c_x)
I_K = list(range(s_c_x,e_c_x + 1)) 
r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
V = []
I =[]
index = 0 #index with for loops

#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Make sure it is the right address for Keithley 
keithley = rm.open_resource(keithley_address)

#Checking on console that it is correct address
print(keithley.query("*IDN?"))

keithley.write("errorqueue.clear()")
keithley.write("smua.source.autorangev = smua.AUTORANGE_ON")
#keithley.write("smua.source.autorangei = smua.AUTORANGE_ON")
keithley.write("smua.source.limitv = " + str(limit))

#Going to display screen
#keithley.write('display.screen = 0')

'''Beginning test'''
keithley.write("smua.source.func = smua.OUTPUT_DCAMPS")

#Changing to 0 just before turning it on 
keithley.write("smua.source.leveli = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")


for i in I_K:
    i = i*step/1000
    i = "{:.6f}".format(i) #going to 6 decimal places
    keithley.write("smua.source.leveli = " + str(i))
    time.sleep(0.2)
    keithley.write('print(smua.measure.v())') #careful with the quotation mark placement.
    v = keithley.read()
    v = v[:-1] # taking off some string line
    v = float(v)
    V.append(v) #saving value to list
    i = float(i)
    I.append((i))
    print(f"I: {i}A  V: {v}V")
    
keithley.write("smua.source.output = smua.OUTPUT_OFF ")   

'''Saving data to a csv file'''



os.chdir(r_path)   #changing path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Current (A)', 'Voltage (V)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        v = V[index]
        thewriter.writerow({'Current (A)':int(i), 'Voltage (V)':v}) #adding lists to rows
        index = index + 1


#plot IV 
plt.plot(I, V, linewidth = 0.4)
plt.xlabel("Current (A)")
plt.ylabel("Voltage (V)")
plt.show()

print("\nSee plot in plot window")
print(f"Saved in {r_path}")

    
    
    

