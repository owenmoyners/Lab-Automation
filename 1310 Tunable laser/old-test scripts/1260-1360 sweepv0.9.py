"""
Created on Fri Dec 17 16:02:57 2021 @author: owen.moynihan
"""
import win32gui
import win32com.client
import traceback
import pyvisa 
import time
import csv


'''SET START/END/INTERVAL WAVELENGTHS HERE'''
start_wl = 1260E-9
end_wl = 1360E-9
interval = 1E-9

'''SET POWER AND UNITS HERE'''
Pow = 10

Pow_unit = 'DBM' # Can set W, MW, UW, NW, PW, DBM, DBMW ...

''' SET NAME OF CSV FILE'''
file_name = '1260-1360 Sweep_Example' #AUTOMATICALLY SETS AS CSV FILE


'''AUTOMATION STARTS HERE: PLEASE DO NOT CHANGE WITHOUT APPROVAL'''

wavelengths = []

powers = []

index = 0

start_wl_x = start_wl*1E9
end_wl_x = end_wl*1E9
interval_x = interval*1E9

interval_x = int(interval_x) 
end_wl_x = int(end_wl_x)
start_wl_x = int(start_wl_x)

#Connecting all needed devices
OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)

rm = pyvisa.ResourceManager()
print(rm.list_resources())


#Opening tuneable laser source
tune_laser = rm.open_resource('GPIB1::22::INSTR')
tune_laser = rm.open_resource('GPIB1::22::INSTR')

#Opening power supply
#power_supply = rm.open_resource('GPIB1::26::INSTR')

#Opening Power Meter 
power_meter = OphirCOM.OpenUSBDevice('991112')
channel = 0

OphirCOM.SetRange(power_meter, channel, 0)
OphirCOM.SetMeasurementMode(power_meter, channel, 0)

#Creating instrument info for info file 
tune_laser_info = 'TUNEABLE LASER = ' + tune_laser.query("*IDN?")
#power_supply_info = 'POWER SUPPLY = ' + power_supply.query("*IDN?")
power_meter_info ='Power Meter = ' + str(OphirCOM.GetDeviceInfo(power_meter))

#Getting date/time for info file 
Date = "Date of test = " + tune_laser.query(":SYST:DAT?")
Time = "Time of test = " + tune_laser.query(":SYST:TIM?")

info = [ Date , Time , tune_laser_info , str(power_meter_info) +" \n"]
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
    tune_laser.write(":WAVE " + str(wl) + "nm") #changing wavelength on laser 
    wavelengths.append(wl) #adding wavelength to file
    
    time.sleep(1)
    power_arrays = OphirCOM.GetData(1000, 0)
    power_array = power_arrays[0]
    power_reading = power_array[0]
    print(power_reading)
    powers.append(power_reading)
    

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
