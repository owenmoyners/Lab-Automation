'''
THIS SCRIPT RUNS A SWEEP WITH THE 1550NM TUNABLE LASER AND  THORLABS POWER METER

MAKE SURE EVERYTHING IS CONNECTED TO THE PC 

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN (owen.moynihan@tyndall.ie)
'''

#INPUT PARAMETERS HERE 
#######################################################################################################################

'''SET START/END/INTERVAL WAVELENGTHS HERE IN NM'''
start_wl = 1440
end_wl = 1640
interval = 1

'''SET POWER AND UNITS HERE''' 
Pow = 0

Pow_unit = 'DBM' # Can Set W, DBM

''' SET PATH OF FILE'''

path="\\FS1\Docs2\owen.moynihan\My Documents\Project work\Fab Room\Processes\SOI\Process tests SOI"
#addresses for instruments - pick which one in the PM_address section
PM_101A = 'USB0::0x1313::0x8076::M00767635::INSTR'
PM_100D = 'USB0::0x1313::0x8078::P0031267::INSTR'

TLS_address = 'GPIB1::20::INSTR' ### use GPIB0 when connected to other PC
PM_address = PM_100D

#######################################################################################################################

'''AUTOMATION STARTS HERE: PLEASE DO NOT CHANGE WITHOUT APPROVAL'''
#v1.0 release with thorlabs powermeter

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
import pandas as pd
from ThorlabsPM100 import ThorlabsPM100
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'qt')
import matplotlib.pyplot as plt 
from collections import deque 


#Closes thorlabs if it is open, otherwise there will be an error
subprocess.call(["taskkill","/F","/IM","Thorlabs Optical Power Monitor.exe"])

#changing directory 
r_path=  repr(path)[1:-1]
os.chdir(r_path) 

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
wavelengths = []
powers = []
powers_dbm = []
save_file = pd.DataFrame({'Wavelength (nm)': wavelengths, 'Power (W)': powers, 'Power (dBm)': powers_dbm})

#Index used in for loop
index = 0

#Changing wavelengths from floats to integers so they can be used in for loop
start_wl_x = start_wl*10000
end_wl_x = end_wl*10000
interval_x = interval*10000

interval_x = int(interval_x) 
end_wl_x = int(end_wl_x)
start_wl_x = int(start_wl_x)

rm = pyvisa.ResourceManager()
#print(rm.list_resources()) # dont use if other people are testing, it will disrupt their communication

#Opening tuneable laser source from GPIB
tune_laser = rm.open_resource(TLS_address)

tune_laser.timeout = None

#change address depending on
inst = rm.open_resource(PM_address)

power_meter = rm.open_resource(PM_address)

#Zero TLS before

tune_laser.write(":OUTP OFF")
time.sleep(2)
power_meter.write('correction:collect:zero:initiate')
time.sleep(3)

#Querying TLS and PM to make sure they are connected 
tune_laser_info = 'TUNABLE LASER = ' + tune_laser.query("*IDN?")
#power_supply_info = 'POWER SUPPLY = ' + power_supply.query("*IDN?")
power_meter_info ='POWER METER = ' + power_meter.query("*IDN?")

#getting info of test
today = date.today()
now = datetime.now()
Time = now.strftime("%H:%M:%S")
print("Time =", Time)
info = ["Name of tester: " + getpass.getuser(), " \nDate: " + str(today) , "\nTime: " + str(Time) ,"\n" + tune_laser_info , str(power_meter_info) ]
print(info)

#setting TLS settings
tune_laser.write(":WAVE " + str(start_wl) + "nm")
tune_laser.write(":POW:UNIT " + Pow_unit)
tune_laser.write(":POW " + str(Pow))
tune_laser.write(":OUTP ON")

#setting power meter settings
power_meter.write('power:dc:unit W')

# Create a fixed-length deque of size 50 to store the data points 
data_points = deque(maxlen=1000000) 
fig, ax = plt.subplots() 
line, = ax.plot([]) 

#reads untrue high value at the beginning (as it switches range)
for i in range(10):
    power_meter.query('measure:power?')
    time.sleep(0.1)
    
        
time.sleep(1)

#Starting sweep for wavelength and recording power everytime
for wl in range(start_wl_x, end_wl_x + 1, interval_x):
    wl = wl/10000
    iwl = int(wl)
    power_meter.write(f"sense:corr:wav {iwl}")
    tune_laser.write(":WAVE " + str(wl) + "nm") #changing wavelength on laser 
    time.sleep(0.3)
    wavelengths.append(wl) #adding wavelength to file
    
    power = power_meter.query('measure:power?')
    power = float(power)
    powers.append(power)
    
    power = abs(power)
    power_dbm = 10*math.log(1000*abs(power) , 10)
    power_dbm = round(power_dbm , 4)
    powers_dbm.append(power_dbm)
    
    print(wl , ' ', power, ' ', power_dbm )
    
    data_points.append((wl, power_dbm)) 
    
    wl_values = [x for x, y in data_points] 
    powerdbm_values = [y for x, y in data_points] 
    
    line.set_data(wl_values, powerdbm_values) 
    ax.set_xlim(min(wl_values),max(wl_values)) 
    ax.set_ylim(min(powerdbm_values),max(powerdbm_values)) 
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Power (dBm)")
    plt.pause(0.05) 
    
    save_file = pd.DataFrame({'Wavelength (nm)': wavelengths, 'Power (W)': powers, 'Power (dBm)': powers_dbm})
    save_file.loc[wl] = [wavelengths[-1], powers[-1],powers_dbm[-1]]
    save_file.to_csv(f'{file_name}.csv', index=False)

plt.show() 

        
get_ipython().run_line_magic('matplotlib', 'inline')        
   
plt.figure()
plt.plot(wavelengths, powers)
plt.title("Plot of " + str(file_name))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Power (W)')
plt.show()

plt.figure()
plt.plot(wavelengths, powers_dbm)
plt.title("Plot of " + str(file_name))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Power (dBm)')
plt.show()


power_meter.write(f"sense:corr:wav 1550")

#Turning the laser off    
tune_laser.write(":OUTP OFF")
   

   

#Saving info to info file
# info_file = open(file_name + "_info" + ".txt","w")
# info_file.writelines(info) 
# info_file.close()  

#Thorlabs = subprocess.Popen([r'C:\Program Files (x86)\Thorlabs\PowerMeters\Optical Power Monitor\Thorlabs Optical Power Monitor.exe'])     

tune_laser.write(":WAVE 1550nm")
tune_laser.write(":OUTP ON")

#Closing out all instruments
tune_laser.close()

