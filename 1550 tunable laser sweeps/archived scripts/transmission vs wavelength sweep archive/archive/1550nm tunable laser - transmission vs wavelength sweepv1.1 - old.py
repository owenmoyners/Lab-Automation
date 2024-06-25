'''
THIS SCRIPT RUNS A SWEEP WITH THE 1550NM TUNABLE LASER AND  MKS POWER METER

MAKE SURE EVERYTHING IS CONNECTED TO THE PC 

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN (owen.moynihan@tyndall.ie)
'''

#INPUT PARAMETERS HERE
#######################################################################################################################


'''SET START/END/INTERVAL WAVELENGTHS HERE IN NM'''
start_wl = 1540
end_wl = 1545
interval = 1

'''SET POWER AND UNITS HERE''' 
Pow = 0

Pow_unit = 'DBM' # Can Set W, DBM


''' SET PATH OF FILE'''
path = "\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\A3802 laser - EAM epi\transmission"

#######################################################################################################################
'''AUTOMATION STARTS HERE: PLEASE DO NOT CHANGE WITHOUT APPROVAL'''
#v1.0 - wavelength vs transmission sweep
#v1.1 - saves file after every datapoint + math error bug fix? (hopefully)

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

#Closes PMManager if it is open, otherwise there will be an error
subprocess.call(["taskkill","/F","/IM","PMManager 3.62.exe"])

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

#Checking all connected devices
OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)

rm = pyvisa.ResourceManager()
print(rm.list_resources())


#Opening tuneable laser source from GPIB
tune_laser = rm.open_resource('GPIB0::20::INSTR')

#Opening power supply
#power_supply = rm.open_resource('GPIB1::26::INSTR')

#Opening Power Meter using Serial number and using channel (0-3)
power_meter = OphirCOM.OpenUSBDevice('991112')
channel = 0

#Setting range to auto and measurement mode to Power (Check Ophir optoelectronics manual for indexing)
OphirCOM.SetRange(power_meter, channel, 2)
OphirCOM.SetWavelength(power_meter, channel, 3)
wl_r = OphirCOM.GetWavelengths(power_meter, channel)
wl_extra = OphirCOM.GetWavelengthsExtra(power_meter, channel)
print(wl_r)
print(wl_extra)
OphirCOM.SetMeasurementMode(power_meter, channel, 0)
OphirCOM.SaveSettings(power_meter, channel)
#Creating instrument info for info file 
tune_laser_info = 'TUNABLE LASER = ' + tune_laser.query("*IDN?")
#power_supply_info = 'POWER SUPPLY = ' + power_supply.query("*IDN?")
power_meter_info ='POWER METER = ' + str(OphirCOM.GetDeviceInfo(power_meter))

today = date.today()
now = datetime.now()
Time = now.strftime("%H:%M:%S")
print("Time =", Time)
info = ["Name of tester: " + getpass.getuser(), " \nDate: " + str(today) , "\nTime: " + str(Time) ,"\n" + tune_laser_info , str(power_meter_info) ]
print(info)

#set initial wavelength
tune_laser.write(":WAVE " + str(start_wl) + "nm")
#Sets unit for power
tune_laser.write(":POW:UNIT " + Pow_unit)
#Sets power for laser
tune_laser.write(":POW " + str(Pow))
#Turns laser on
tune_laser.write(":OUTP ON")



OphirCOM.StartStream(power_meter, channel)
time.sleep(1)

#reads untrue high value at the beginning (as it switches range)
for i in range(10):
    power_arrays = OphirCOM.GetData(power_meter, 0)
    power_array = power_arrays[0]
    time.sleep(0.1)
    while power_array == ():
        time.sleep(0.1)
        power_arrays = OphirCOM.GetData(power_meter, 0)
        power_array = power_arrays[0]
    discard_reading = power_array[0]
        
time.sleep(1)

#Starting sweep for wavelength and recording power everytime
for wl in range(start_wl_x, end_wl_x + 1, interval_x):
    wl = wl/10000
    tune_laser.write(":WAVE " + str(wl) + "nm") #changing wavelength on laser 
    wavelengths.append(wl) #adding wavelength to file
    
    time.sleep(0.3)
    #if tuple is empty, wait until its not empty
    try:
        
        power_arrays = OphirCOM.GetData(power_meter, 0) # (Check Ophir optoelectronics manual for indexing)
        time.sleep(0.4)
        power_array = power_arrays[0]
        #if power meter has no value 
        while power_array == ():
            print("Changing range of power meter")
            time.sleep(0.5)
            power_arrays = OphirCOM.GetData(power_meter, 0)
            power_array = power_arrays[0]
        #if power meter gives not real value 
        power_reading = power_array[0]
        power_reading = abs(power_reading)
        while power_reading <= 0:
            print("Null value")
            time.sleep(0.5)
            power_arrays = OphirCOM.GetData(power_meter, 0)
            power_array = power_arrays[0]
            power_reading = power_array[0]
        
        power_reading = abs(power_reading)
        power_dbm = 10*math.log(1000*abs(power_reading) , 10)
        power_dbm = round(power_dbm , 4)
        powers.append(power_reading)
        powers_dbm.append(power_dbm)
        print(wl , ' ', power_reading, ' ', power_dbm )
        
        
    except ValueError:
        print("Value Error! - retrying")
        power_arrays = OphirCOM.GetData(power_meter, 0) # (Check Ophir optoelectronics manual for indexing)
        time.sleep(0.2)
        power_array = power_arrays[0]
        while power_array == ():
            print("no value found - trying again")
            time.sleep(0.5)
            power_arrays = OphirCOM.GetData(power_meter, 0)
            power_array = power_arrays[0]
        power_reading = power_array[0]
        power_reading = abs(power_reading)
        power_reading_dec = Decimal(power_reading)
        power_dbm = 10*math.log(1000*abs(power_reading_dec) , 10)
        power_dbm = round(power_dbm , 4)
        powers.append(power_reading)
        powers_dbm.append(power_dbm)
        print(wl , ' ', power_reading, ' ' ,power_dbm )
    

    save_file = pd.DataFrame({'Wavelength (nm)': wavelengths, 'Power (W)': powers, 'Power (dBm)': powers_dbm})
    save_file.loc[wl] = [wavelengths[-1], powers[-1],powers_dbm[-1]]
    save_file.to_csv('f{file_name}.csv', index=False)
        
        
   
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


#Turning the laser off    
tune_laser.write(":OUTP OFF")
   

   




#Saving info to info file
# info_file = open(file_name + "_info" + ".txt","w")
# info_file.writelines(info) 
# info_file.close()       

tune_laser.write(":WAVE 1550nm")
tune_laser.write(":OUTP ON")

#Closing out all instruments
tune_laser.close()
#power_supply.close()
OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()


#Reopens PMManager for realignment
PMManager = subprocess.Popen([r'C:\Program Files\Newport\PMManager 3.62\PMManager 3.62.exe'])

