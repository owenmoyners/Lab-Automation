# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 15:53:16 2021

@author: owen.moynihan
"""
import win32gui
import win32com.client
import traceback
import time

#Opens Device list
OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)


#Opens USB using serial number
power_meter = OphirCOM.OpenUSBDevice('991112')
channel = 0

print(power_meter)

print('\n----------Data for S/N {0} ---------------'.format('991112'))

pw_reading_info = OphirCOM.GetDeviceInfo(power_meter) # reading power from power meter

print(pw_reading_info)


print(OphirCOM.GetWavelengths(power_meter, channel, 0))

OphirCOM.SetWavelength(power_meter, channel, 0)

ranges = OphirCOM.GetRanges(1000, 0)

print(ranges)

OphirCOM.SetRange(power_meter, channel, 0)

print(OphirCOM.GetMeasurementMode(1000, 0))

OphirCOM.GetMeasurementMode(1000, 0)

OphirCOM.SetMeasurementMode(1000, 0, 0)


OphirCOM.StartStream(1000, 0)
time.sleep(0.5)
power_arrays = OphirCOM.GetData(1000, 0)
print(power_arrays)

power_array =power_arrays[0]

power_reading = power_array[0]

print(power_reading)



OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()
