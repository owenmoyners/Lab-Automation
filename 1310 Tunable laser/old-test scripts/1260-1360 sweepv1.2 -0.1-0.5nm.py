"""
Created on Fri Dec 17 16:02:57 2021 @author: owen.moynihan
"""
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
from datetime import date
from datetime import datetime
import os

'''SET START/END/INTERVAL WAVELENGTHS HERE'''
start_wl = 1260
end_wl = 1360
interval = 0.5

'''SET POWER AND UNITS HERE''' #not working at the moment for some reason
Pow = 3

Pow_unit = 'DBM' # Can set W, MW, UW, NW, PW, DBM, DBMW ...

''' SET PATH OF FILE'''
path = r"\\10.204.28.1\docs2\owen.moynihan\My Documents\Project work\Test programs\Python Files\Tuneable laser test\Results"

''' SET NAME OF CSV FILE'''
file_name = '1260-1360 Sweep_intel_sample ' + str(datetime.now())  #AUTOMATICALLY SETS AS CSV FILE

'''AUTOMATION STARTS HERE: PLEASE DO NOT CHANGE WITHOUT APPROVAL'''

#creating empty list to take values
wavelengths = []
powers = []

#index used in for loop
index = 0

#changing wavelengths from floats to integers so they can be used in for loop
start_wl_x = start_wl*10
end_wl_x = end_wl*10
interval_x = interval*10

interval_x = int(interval_x) 
end_wl_x = int(end_wl_x)
start_wl_x = int(start_wl_x)

#Checking all connected devices
OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)

rm = pyvisa.ResourceManager()
print(rm.list_resources())


#Opening tuneable laser source from GPIB
tune_laser = rm.open_resource('GPIB0::22::INSTR')

#Opening power supply
#power_supply = rm.open_resource('GPIB1::26::INSTR')

#Opening Power Meter using Serial number and using channel (0-3)
power_meter = OphirCOM.OpenUSBDevice('991112')
channel = 0

#Setting range to auto and measurement mode to Power (Check Ophir optoelectronics manual for indexing)
OphirCOM.SetRange(power_meter, channel, 0)
OphirCOM.SetMeasurementMode(power_meter, channel, 0)

#Creating instrument info for info file 
tune_laser_info = 'TUNEABLE LASER = ' + tune_laser.query("*IDN?")
#power_supply_info = 'POWER SUPPLY = ' + power_supply.query("*IDN?")
power_meter_info ='Power Meter = ' + str(OphirCOM.GetDeviceInfo(power_meter))

today = date.today()
now = datetime.now()
Time = now.strftime("%H:%M:%S")
print("Time =", Time)
info = ["Name of tester: " + getpass.getuser(), "Date: " + str(today) , "Time: " + str(Time) , tune_laser_info , str(power_meter_info) ]
print(info)

#Sets unit for power
tune_laser.write(":POW:UNIT " + Pow_unit)
#Sets power for laser
#tune_laser.write(":POW " + str(Pow))
#Turns laser on
tune_laser.write(":OUTP ON")

OphirCOM.StartStream(power_meter, channel)

#Starting sweep for wavelength and recording power everytime
for wl in range(start_wl_x, end_wl_x + 1, interval_x):
    tune_laser.write(":WAVE " + str(wl/10) + "nm")#changing wavelength on laser 
    wavelengths.append(wl/10) #adding wavelength to file
    
    #try if statement that if nothing try again
    time.sleep(0.5)
    power_arrays = OphirCOM.GetData(power_meter, 0) # (Check Ophir optoelectronics manual for indexing)
    time.sleep(0.5)
    power_array = power_arrays[0]
    #if tuple is empty, wait until its not empty
    while power_array == ():
        print("no value found - trying again")
        time.sleep(0.2)
        power_arrays = OphirCOM.GetData(power_meter, 0)
        power_array = power_arrays[0]
    power_reading = power_array[0]
    print(power_reading)
       
    powers.append(power_reading)
    
    
plt.plot(wavelengths, powers)
plt.title("Plot of " + str(file_name))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Power (W)')


print(wavelengths)
print(powers)    
print(len(wavelengths))
print(len(powers))

#Turning the laser off    
tune_laser.write(":OUTP OFF")
    
#Saving the data to a csv file
with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Wavelength (nm)', 'Power (mW)'] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    thewriter.writeheader()
    
    for wavelength in wavelengths:
        
        power = powers[index]
        thewriter.writerow({'Wavelength (nm)':wavelength, 'Power (mW)':power}) #adding lists to rows
        index = index + 1

#Saving info to info file
info_file = open(file_name + "_info" + ".txt","w")
info_file.writelines(info) 
info_file.close()       


#Closing out all instruments
tune_laser.close()
#power_supply.close()
#power_meter.close()
OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()
