'''
THIS SCRIPT RUNS A SWEEP WITH THE 1300NM TUNABLE LASER AND  MKS POWER METER

MAKE SURE EVERYTHING IS CONNECTED TO THE PC 

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN
'''
# v1.0 original test script
# v1.1 has the turning on and off of powermeter in loop (has been scrapped)
# v1.2 fixed bug where error appears when trying to take power value + generates plot when finished
# v1.3 sets directory for files
# v1.4 opens window to enter file name and auto opens and closes PMManager, added dBm
# v1.5 fix value math error for dBm measurement, increase resolution and get rid of info file
# v1.6 resolution down to 0.0001nm, added in warning when overwriting file, added in metadata at top of csv (date and laser power)

'''ENTER PARAMAETERS HERE'''

'''SET START/END/INTERVAL WAVELENGTHS HERE IN NM'''
start_wl = 1260
end_wl = 1360
interval = 1

'''SET POWER AND UNITS HERE''' 
Pow = 0

Pow_unit = 'DBM' # Can Set Watt, DBM, DBMW

wavelength = 3 # 780=0, 1290=1, 1800=2, 1310=3, 1550=4

'''VOLTAGE OF LASER and current limit'''
V = 0
limit = 0.015

''' SET PATH OF FILES TO BE SAVED'''
path = "//fs1/Docs2/valentina.rajkumari/My Documents/Meena"


'''AUTOMATION STARTS HERE: PLEASE DO NOT CHANGE WITHOUT APPROVAL'''
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

   
#Closes PMManager if it is open, otherwise there will be an error
#subprocess.call(["taskkill","/F","/IM","PMManager 3.62.exe"])

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
root.title("1260-1360 Sweep") # naming window
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

r_path=  repr(path)[1:-1] #changing path to raw string to avoid back slash error

os.chdir(r_path)  #changing path 
file_csv = file_name + ".csv"
File = os.path.isfile(file_csv)

if File == True:
    print("WARNING - READ BELOW:")
    time.sleep(1)
    print(f"You will overwrite pervious {file_name} file")
    print("Right click this window and press 'Quit' to cancel, or left click and press anything to continue")
    input("Press Enter in commandline here to continue: ")
    print("Continuing...")
    
#creating empty list to take values
wavelengths = []
powers = []
powers_dbm = []
I = []


#index used in for loop
index = 0

#changing wavelengths from floats to integers so they can be used in for loop
start_wl_x = start_wl*1000
end_wl_x = end_wl*1000
interval_x = interval*1000

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
tune_laser = rm.open_resource('GPIB1::2::INSTR')

keithley = rm.open_resource('GPIB1::26::INSTR')
keithley.write("smua.reset()")  
keithley.write("errorqueue.clear()")
keithley.write("smua.source.autorangei = smua.AUTORANGE_ON")
keithley.write("smua.source.limiti = " + str(limit))

keithley.write("smua.source.func = smua.OUTPUT_DCVOLTS")

#Changing to 0 just before turning it on 
keithley.write("smua.source.levelv = 0")
    
#Turns on output 
keithley.write("smua.source.output = smua.OUTPUT_ON ")

#Opening power supply
#power_supply = rm.open_resource('GPIB1::26::INSTR')

#Opening Power Meter using Serial number and using channel (0-3)
power_meter = OphirCOM.OpenUSBDevice('991112')
channel = 0

#Setting range to auto and measurement mode to Power (Check Ophir optoelectronics manual for indexing)
OphirCOM.SetRange(power_meter, channel, 0)
OphirCOM.SetMeasurementMode(power_meter, channel, 0)


OphirCOM.SetWavelength(power_meter, channel, wavelength)
wl_r = OphirCOM.GetWavelengths(power_meter, channel)
print(wl_r)
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
tune_laser.write(":WAV " + str(start_wl))
#Sets unit for power
tune_laser.write(":POW:UNIT " + Pow_unit)
#Sets power for laser
tune_laser.write(":POW " + str(Pow))
#Turns laser on
tune_laser.write(":OUTP ON")

keithley.write("smua.source.levelv = " + str(V))

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
    wl = wl/1000
    tune_laser.write(":WAV " + str(wl)) #changing wavelength on laser 
    wavelengths.append(wl) #adding wavelength to file
    
    keithley.write('print(smua.measure.i())') #read current
    i = keithley.read() #read current
    i = i[:-1] # taking off some string line
    i = float(i)
    i = abs(i)
    I.append(i) #saving value to list
    
    time.sleep(0.2)
    #if tuple is empty, wait until its not empty
    try:
        
        power_arrays = OphirCOM.GetData(power_meter, 0) # (Check Ophir optoelectronics manual for indexing)
        time.sleep(0.1)
        power_array = power_arrays[0]
        while power_array == ():
            print("Changing range of power meter")
            time.sleep(0.1)
            power_arrays = OphirCOM.GetData(power_meter, 0)
            power_array = power_arrays[0]
        power_reading = power_array[0]
        power_reading = abs(power_reading)
        power_reading_dec = Decimal(power_reading)
        power_dbm = 10*math.log(1000*abs(power_reading_dec) , 10)
        power_dbm = round(power_dbm , 3)
        powers.append(power_reading)
        powers_dbm.append(power_dbm)
        print(wl , ' ', power_reading, ' ' ,power_dbm, '  I=',i )
        
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
        power_dbm = round(power_dbm , 3)
        powers.append(power_reading)
        powers_dbm.append(power_dbm)
        print(wl , ' ', power_reading, ' ' ,power_dbm, '  I=',i )
 

from pylab import * 
#makes graphs look nice
rc('axes', linewidth=2)
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"    
    
#plt.plot(wavelengths, powers)
plt.figure()
plt.plot(wavelengths, powers)
plt.title("Plot of " + str(file_name))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Power (W)')
plt.grid(True, alpha=0.5)
plt.show()

plt.figure()
plt.plot(wavelengths, powers_dbm)
plt.title("Plot of " + str(file_name) + " dBm")
plt.xlabel('Wavelength (nm)')
plt.ylabel('Power (dBm)')
plt.grid(True, alpha=0.5)
plt.show()

plt.plot(wavelengths, I)
plt.title("Plot of " + str(file_name))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Current')
plt.show()

#Turning the laser off    
tune_laser.write(":OUTP OFF")
   

#Saving the data to a csv file
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Wavelength (nm)', 'Power (W)'  , 'Power (dBm)', 'Photocurrent (A)' ] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    thewriter.writerow({'Wavelength (nm)': info })  
    thewriter.writerow({'Wavelength (nm)': f"Date of test = {today}, Laser Power = {Pow}{Pow_unit}" })  
    
    thewriter.writeheader()
    
    for wavelength in wavelengths:
        
        power = powers[index]
        power_dbm = powers_dbm[index]
        i = I[index]
        thewriter.writerow({'Wavelength (nm)':wavelength, 'Power (W)':power, 'Power (dBm)':power_dbm, 'Photocurrent (A)': i } ) #adding lists to rows
        index = index + 1


#Saving info to info file
# info_file = open(file_name + "_info" + ".txt","w")
# info_file.writelines(info) 
# info_file.close()       

tune_laser.write(":WAVE 1310nm")
tune_laser.write(":OUTP ON")

#Closing out all instruments
tune_laser.close()
#power_supply.close()
OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()


#Reopens PMManager for realignment
PMManager = subprocess.Popen([r'C:\Program Files\Newport\PMManager 3.62\PMManager 3.62.exe'])
