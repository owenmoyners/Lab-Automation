# -*- coding: utf-8 -*-
"""
Program to test tuneable laser source
"""
#IMPORTING PACKAGES
import pyvisa 
import time


#SETTING PARAMETERS
"""
SET WAVELENGTH HERE 
"""
Wavel = 1300E-9

"""
SET POWER HERE 
"""
Pow = 1E-3


#CONNECTING INSTRUMENTS AND SETUP
#Checking for instruments connected
rm = pyvisa.ResourceManager()

print(rm.list_resources())

#Opening tuneable laser source
tune_laser = rm.open_resource('GPIB1::22::INSTR')

#Opening power supply
#power_supply = rm.open_resource('GPIB1::26::INSTR')

#Opening Power Meter 
#power_meter = rm.open_resource('TCPIP0::K-33522B-00434::inst0::INSTR')

#Checking that instruments are assigned correctly
print('\n')
print('TUNEABLE LASER = ' + tune_laser.query("*IDN?"))
#print('POWER SUPPLY = ' + power_supply.query("*IDN?")) 
#print('POWER METER = ' + power_meter.query("*IDN?")) 


#CONDUCTING TEST
#Prints date an time of test for admin 
print("Date of test = " + tune_laser.query(":SYST:DAT?"))
print("Time of test = " + tune_laser.query(":SYST:TIM?")) 

#sets wavelength given  
tune_laser.write(":WAVE " + str(Wavel))

#Setting power units - can also set W, MW, UW, NW, PW, DBMW ...
tune_laser.write(":POW:UNIT MW")

#Turning on laser 
tune_laser.write(":OUTP ON")
print(tune_laser.query(":OUTP?") + "+1 means on/ +0 means off")


tune_laser.write(":POW " + str(Pow))
print(tune_laser.query(":POW?"))






time.sleep(3)
tune_laser.write(":OUTP OFF")

tune_laser.close()
#power_supply.close()
#power_meter.close()