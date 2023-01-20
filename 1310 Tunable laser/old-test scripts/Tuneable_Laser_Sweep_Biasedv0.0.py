# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 15:53:16 2021

@author: owen.moynihan
"""
import win32gui
import win32com.client
import traceback

OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)

power_meter = OphirCOM.OpenUSBDevice('991112')

print(power_meter)

print('\n----------Data for S/N {0} ---------------'.format('991112'))

pw_reading_info = OphirCOM.GetDeviceInfo(power_meter) # reading power from power meter

print(pw_reading_info)


ranges = OphirCOM.GetRanges(1000, 0)

print(ranges)

OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()
