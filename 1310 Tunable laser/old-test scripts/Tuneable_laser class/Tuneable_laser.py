"""
Created on Wed Dec 22 13:46:02 2021

@author: owen.moynihan
"""


''' THIS IS A CLASS FOR THE TUNEABLE LASER AFTER IT HAS BEEN CONNECTED VIA PYVISA'''

#tuneable_laser_assigment = assigment given to laser from rm.open_resource(GPIBXX)

class Tuneable_Laser:
    
    def __innit__(self, tuneable_laser_assigment, Power, Power_unit, wavel, start_wl, end_wl, interval):
        
        self.tuneable_laser_assigment = tuneable_laser_assigment
        self.Power = Power 
        self.Power_unit = Power_unit
        self.wavel = wavel
        self.start_wl = start_wl
        self.end_wl = end_wl
        self.interval = interval
    
    def test():
        print("test ")
        
    def query(self,tuneable_laser_assignment):
        tune_laser = tuneable_laser_assignment
        tune_laser_info = 'TUNEABLE LASER = ' + tune_laser.query("*IDN?")
        print(tune_laser_info)
    
    def set_power(self, tuneable_laser_assignment, Power, Power_unit):
        tune_laser = tuneable_laser_assignment
        Pow = Power
        Pow_unit = Power_unit
        tune_laser.write(":POW:UNIT " + Pow_unit)
        tune_laser.write(":POW " + str(Pow))
        
          
    def turn_on_laser(self, tuneable_laser_assignment):
        tune_laser = tuneable_laser_assignment
        tune_laser.write(":OUTP ON")
        
    def turn_off_laser(self, tuneable_laser_assignment):
        tune_laser = tuneable_laser_assignment
        tune_laser.write(":OUTP OFF")
        
    def set_wavelength(self, tuneable_laser_assignment, wavel):
        tune_laser = tuneable_laser_assignment
        tune_laser.write(":WAVE " + str(wavel) + "nm")
        
    def set_wavelength_sweep(self, tuneable_laser_assignment, start_wl, end_wl, interval):
        tune_laser = tuneable_laser_assignment
        start_wl_x = start_wl*1E9
        end_wl_x = end_wl*1E9
        interval_x = interval*1E9

        interval_x = int(interval_x) 
        end_wl_x = int(end_wl_x)
        start_wl_x = int(start_wl_x)
        
        for wl in range(start_wl_x, end_wl_x + 1, interval_x):
            tune_laser.write(":WAVE " + str(wl) + "nm")
        
    
            
    
