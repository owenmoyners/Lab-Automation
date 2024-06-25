# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 14:26:50 2021

@author: owen.moynihan
"""
import pyvisa 
import time

rm = pyvisa.ResourceManager()

print(rm.list_resources())

#Opening tuneable laser source
tune_laser = rm.open_resource('GPIB1::22::INSTR')


start_wl = 1280E-9
end_wl = 1350E-9
interval = 1E-9

start_wl_x = start_wl*1E9
end_wl_x = end_wl*1E9
interval_x = interval*1E9

print(start_wl_x)
print(end_wl_x)
print(interval_x)

interval_x = int(interval_x) 
end_wl_x = int(end_wl_x)
start_wl_x = int(start_wl_x)


for x in range(start_wl_x, end_wl_x, interval_x):
    time.sleep(1)
    tune_laser.write(":WAVE " + str(x) + "nm")
    
    
tune_laser.close()    