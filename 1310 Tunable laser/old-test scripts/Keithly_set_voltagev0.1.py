# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 16:00:29 2021

@author: owen.moynihan
"""
import pyvisa
import time

'''Set Voltage Here
'''
Vol = 2


rm = pyvisa.ResourceManager()

#Opens Keithly for Communication
ps = rm.open_resource("GPIB1::26::INSTR")

#Sets Voltage 
ps.write("smua.source.levelv=" + str(Vol) )

#Turns on Keithly 
ps.write("smua.source.output=smua.OUTPUT_ON")

time.sleep(1)

#Meaures something?
ps.write("currenta, voltagea = smua.measure.iv()")

#Turns keithly off
ps.write("smua.source.output=smua.OUTPUT_OFF")

current = ps.query("print(currenta)")

voltage = ps.query("print(voltagea)")

