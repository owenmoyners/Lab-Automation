'''
SCRIPT TO RUN AN CURRENT VS TIME FOR 2602A KEITHLEY - CHANNEL B (HAVE FOUND THEM NOT TO WORK FOR OTHER KINDS)

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

#voltage 
V = 0

#time 
T = 5 # minutes

#current limit
limit = 0.03

#Path for file to be saved 
file_name = 'A3650-timelight0V'

#COPY AND PASTE PATH AS IS, NO NEED TO ADD SECOND SLASHES 
path = '\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\Surface passivation run\Current time'

keithley_address = 'GPIB0::26::INSTR'


'''Setting up test : Dont change anything from here'''

r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error
I = []
T_l = []

T_s = T*60
T_s = int(T_s)
T_l = list(range(T_s))
 
index = 0 #index with for loops

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

keithley.write("smua.source.levelv = " + str(V))
    
for t in T_l:
    keithley.write('print(smua.measure.i())') #careful with the quotation mark placement.
    i = keithley.read() #reading current from keithley 
    i = i[:-1] # taking off some string line
    i = float(i)
    I.append(i) #saving value to list
    time.sleep(1)
    
    
keithley.write("smua.source.output = smua.OUTPUT_OFF ")   


'''Saving data to a csv file'''

os.chdir(r_path)  #changing path 


with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Time (s)', 'Current (A)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()

    
    for i in I:
        
        t = T_l[index]
        thewriter.writerow({'Time (s)':t, 'Current (A)':i}) #adding lists to rows
        index = index + 1
        

#PLOTTING Current time 
plt.plot(T_l, I, linewidth = 0.4)
plt.title(file_name)
plt.gca().invert_yaxis()
plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.savefig(f"{file_name}.png", dpi=500 , bbox_inches='tight')
plt.show()


plt.plot(T_l/60, I, linewidth = 0.4)
plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.show()


print("\nSee plot in plot window")
print(f"Saved in {r_path}")

    
    
    


