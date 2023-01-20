# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 14:57:50 2022

@author: owen.moynihan
"""

import pyvisa
import matplotlib.pyplot as plt
import os 
import csv
import time
from datetime import date
from datetime import datetime

rm = pyvisa.ResourceManager()
print(rm.list_resources())

TEC = rm.open_resource('GPIB0::15::INSTR') #address for C107 VCSEL setup TEC 

print(TEC.query("*IDN?")) 

TEC.write("LDATA")

TEC.write(":SOUR:TEMP 30") ## change the temperature 

TEC.write(":OUTP ON") #turns on TEC

TEC.write(":OUTP OFF") # turns off TEC


'''
OTHER COMMANDS THAT WORK 
:UNIT:TEMP CEL          Celsius temperature limits
:SOUR:TEMP:PROT 100     Upper temperature limit = 100˚
:SOUR:TEMP:PROT:LOW 10  Lower temperature limit = 10˚
:TEMP:TRAN RTD Select   RTD temperature sensor
:TEMP:RTD:TYPE PT100    Select PT100 RTD sensor
:TEMP:RTD:RANG 100      Set 100Ω range.
:TEMP:CURR:AUTO ON      Use default RTD sensor current
:SYST:RSEN ON           Enable 4-wire sensing
:SOUR:TEMP:LCON 10      Temperature gain constant = 10
:SOUR:TEMP:LCON:INT     0.5 Temperature integral constant = 0.5
:SOUR:TEMP:LCON:DER 0   Temperature derivative constant = 0
'''