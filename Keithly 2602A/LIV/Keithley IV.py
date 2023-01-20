'''
THIS SCRIPT RUNS IV FOR 2602A KEITHLEY ON CHANNEL A - JUST CLICK RUN 

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

'''Input parameters here'''
#Set current in mA
start_current = -100
end_current = 100

#Path for file to be saved 
file_name = 'test_IV'

path = '//fs1/Docs2/owen.moynihan/My Documents/Project work/Test programs/Python Files/Keithly 2602A/TestIV_folder'



'''Setting up test'''
r_path = repr(path) #changing path to raw string to avoid back slash error
I = list(range(start_current,end_current + 1)) 
V = []
index = 0 #index with for loops

#Setting up address and opening communication with Keithley 
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#Make sure it is the right address for Keithley 
keithley = rm.open_resource('GPIB0::26::INSTR')

#Checking on console that it is correct address
print(keithley.query("*IDN?"))

#Going to display screen
keithley.write('display.screen = 0')



'''Beginning test'''
keithley.write("smua.source.func = smua.OUTPUT_DCAMPS")

#Changing to 0 just before turning it on 
keithley.write("smua.source.leveli = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")


for i in I:
    i = i/100
    keithley.write("smua.source.leveli = " + str(i))
    time.sleep(0.05)
    keithley.write('print(smua.measure.v())') #careful with the quotation mark placement.
    v = keithley.read()
    V.append(v) #saving value to list
    print(f"I: {i}mA  V: {v}V")
  
    
  
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



    
    
    

