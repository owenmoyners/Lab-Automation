'''
SAVES SPECTRUM FROM ANDO OSA IN C.107 

MAKE SURE IT IS CONNECTED AND THE GPIB ADRESS IS CORRECT

SAVES AS CSV FILE AT PATH SPECIFIED 

ANY PROBLEMS ASK ME - OWEN MOYNIHAN
'''

'''Adding Packages'''
import pyvisa
import matplotlib.pyplot as plt
import os 
import csv
import time
from datetime import date
from datetime import datetime




'''Input parameters here'''
#Name  your file 
file_name = 'A3803 2mm laser 2V'

#Set path for file to be saved to 
path ="\\FS1\Docs2\owen.moynihan\My Documents\Project work\Testing Results\A3803 laser"



''' program starts here'''
index = 0

rm = pyvisa.ResourceManager()
print(rm.list_resources())

OSA = rm.open_resource('GPIB0::1::INSTR')

OSA.timeout = None #High resolution files can take longer than timeout time 

print(OSA.query("*IDN?")) # Check to make sure it is OSA

#GETTING POWER OF SPECTRUM
OSA.write("LDATA") #Trace A level data
#data_B = OSA.write("LDATB") #Trace B level data
#data_C = OSA.write("LDATC") #Trace C level data

print(OSA.read_bytes)

spectrum = OSA.read()  # reading output from OSA

spectrum_float = [float(s) for s in spectrum.split(',')] # splitting list elements into floats 
spectrum_float.pop(0) # taking out first term - not a data point

#GETTING WAVELENGTHS SPAN
OSA.write("WDATA") # writting command to get wavelength data
wl = OSA.read() # reading output from OSA
print(spectrum_float)

wl_float = [float(s) for s in wl.split(',')] # splitting list elements into floats 
wl_float.pop(0) # taking out first term - not a data point
print(wl_float)

#PLOTTING SPECTRUM
plt.plot(wl_float, spectrum_float, linewidth = 0.4)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Power (dBm)")
plt.ylim(-80)
plt.show()


#MAKING CSV FILE OF DATA
r_path=  repr(path)[1:-1]
os.chdir(r_path)  

with open(file_name + ".csv", 'w', newline='') as csvfile:
    
    fieldnames =['Wavelength (nm)', 'Power (dBm)'] #setting the row titles
    
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames) 
    
    thewriter.writeheader()
    
    for wl in wl_float:
        
        power = spectrum_float[index]
        wavelength = wl_float[index]
        thewriter.writerow({'Wavelength (nm)':wavelength, 'Power (dBm)':power}) #adding lists to rows
        index = index + 1 


''' Things that also work 
OSA.write("CTRWL 1550") #specify center wl
OSA.write("SPAN 50") #span of measurement
OSA.write("SMPL 1000") #samplying number
OSA.write("RESLN 1") #resolution in nm
OSA.write("RPT") #repeat scans
OSA.write("SGL") #single scan

'''