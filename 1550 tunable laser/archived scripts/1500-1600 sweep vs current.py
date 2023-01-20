'''
THIS SCRIPT RUNS A SWEEP WITH THE 1550NM TUNABLE LASER AND  READS CURRENT

MAKE SURE EVERYTHING IS CONNECTED TO THE PC (keithley and laser)

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN
'''

'''Adding Packages'''
from tkinter import *
import tkinter as tk
import win32gui
import win32com.client
import traceback
import pyvisa 
import time
from datetime import date
from datetime import datetime
import csv
import getpass
import matplotlib.pyplot as plt
import os 
import subprocess
import math
from decimal import Decimal


'''Input parameters here'''

'''SET START/END/INTERVAL WAVELENGTHS HERE IN NM'''
start_wl = 1500
end_wl = 1640
interval = 0.5

'''SET POWER AND UNITS HERE''' 
Pow = 0

Pow_unit = 'DBM' # Can Set W, DBM


'''VOLTAGE OF LASER and current limit'''
V = 0
limit = 0.01

''' SET PATH OF FILE'''
path = "\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\A3802 laser - EAM epi"


'''AUTOMATION STARTS HERE: PLEASE DO NOT CHANGE WITHOUT APPROVAL'''

#SETTING UP FILE NAME WINDOW
def closewindow():
    root.destroy()

def SaveFileName():
    FileName = str(FileNameEntry.get())
    FileNameLabel.destroy()
    FileNameEntry.destroy()
    FileNameButton.destroy()
  
root = Tk() #opening main window 

root.wm_attributes("-topmost", 1)
root.title("1500-1600 Sweep") # naming window
root.geometry("700x250") # window size

#Setting label,entry path and save button for file name
FileName = tk.StringVar()
FileNameEntry = Entry(root, width = 50, border = 5 , textvariable = FileName)
FileNameLabel = Label(root, text = "File Name: ")
FileNameButton = Button(root, text = "Save" , command = SaveFileName)
CloseButton = Button(root, text = "Close" , fg = "red" , command = closewindow)



FileNameLabel.grid(row=0,column=0)
FileNameEntry.grid(row=0,column=1)
FileNameButton.grid(row=0,column=2)
CloseButton.grid(row=5,column=0)

root.mainloop()

file_name = FileName.get()
print(f"File Name = {file_name}")

#Creating empty list to take values
WL = []
I = []

#Index used in for loop
index = 0

#Changing wavelengths from floats to integers so they can be used in for loop
start_wl_x = start_wl*100
end_wl_x = end_wl*100
interval_x = interval*100

interval_x = int(interval_x) 
end_wl_x = int(end_wl_x)
start_wl_x = int(start_wl_x)



rm = pyvisa.ResourceManager()
print(rm.list_resources())


#Opening tuneable laser source from GPIB
tune_laser = rm.open_resource('GPIB0::20::INSTR')

#Opening power supply
keithley = rm.open_resource('GPIB0::28::INSTR')
keithley.write("smub.reset()")  
keithley.write("errorqueue.clear()")
keithley.write("smub.source.autorangei = smub.AUTORANGE_ON")
keithley.write("smub.source.limiti = " + str(limit))





#Creating instrument info for info file 
tune_laser_info = 'TUNABLE LASER = ' + tune_laser.query("*IDN?")
#power_supply_info = 'POWER SUPPLY = ' + power_supply.query("*IDN?")
keithley_info ='Keithley = ' + keithley.query("*IDN?")

today = date.today()
now = datetime.now()
Time = now.strftime("%H:%M:%S")
print("Time =", Time)
info = ["Name of tester: " + getpass.getuser(), " \nDate: " + str(today) , "\nTime: " + str(Time) ,"\n" + tune_laser_info , str(keithley_info) ]
print(info)


keithley.write("smub.source.func = smub.OUTPUT_DCVOLTS")

#Changing to 0 just before turning it on 
keithley.write("smub.source.levelv = 0")
    
#Turns on output 
keithley.write("smub.source.output = smub.OUTPUT_ON ")


#set initial wavelength
tune_laser.write(":WAVE 1500nm")
#Sets unit for power
tune_laser.write(":POW:UNIT " + Pow_unit)
#Sets power for laser
tune_laser.write(":POW " + str(Pow))
#Turns laser on
tune_laser.write(":OUTP ON")


keithley.write("smub.source.levelv = " + str(V))

#Starting sweep for wavelength and recording current everytime
for wl in range(start_wl_x, end_wl_x + 1, interval_x):
    wl = wl/100
    tune_laser.write(":WAVE " + str(wl) + "nm") #changing wavelength on laser 
    WL.append(wl) #adding wavelength to file
    time.sleep(0.5) # wait for laser to change wl
    keithley.write('print(smub.measure.i())') #read current
    i = keithley.read() #read current
    i = i[:-1] # taking off some string line
    i = float(i)
    i = abs(i)
    I.append(i) #saving value to list
    print(wl , ' ', i ) #shows result
        

 
   

plt.plot(WL, I)
plt.title("Plot of " + str(file_name))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Current')
plt.show()


#Turning the laser off    
tune_laser.write(":OUTP OFF")
   

r_path=  repr(path)[1:-1]
os.chdir(r_path)    

#Saving the data to a csv file
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Wavelength (nm)', 'Current (A)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()
    
    for wavelength in WL:
        
        i = I[index]
        thewriter.writerow({'Wavelength (nm)':wavelength, 'Current (A)':i }) #adding lists to rows
        index = index + 1


#Saving info to info file
# info_file = open(file_name + "_info" + ".txt","w")
# info_file.writelines(info) 
# info_file.close()       

tune_laser.write(":WAVE 1550nm")
tune_laser.write(":OUTP ON")

#Closing out all instruments
tune_laser.close()
keithley.close()


