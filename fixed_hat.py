from sense_hat import SenseHat
import numpy as np

class FixedHat(SenseHat):


    RPI_CPU_THERMAL_ZONE = '/sys/class/thermal/thermal_zone0/temp' 		


    def __init__(self, temp_cpu_factor=1.5):
        self._temp_cpu_factor = temp_cpu_factor
        super(FixedHat, self).__init__()


    def get_temperature_from_humidity(self):
        """
        Returns the temperature in Celsius accounting for the influence 
        from the CPU temperature
        """

        temp_humidity = super(FixedHat, self).get_temperature_from_humidity()
        temp_cpu = int(open(self.RPI_CPU_THERMAL_ZONE).read()) / 1e3

        temp_increase_cpu = (temp_cpu - temp_humidity) / self._temp_cpu_factor

        return temp_humidity - temp_increase_cpu


    def _get_sat_vapor_density(self, T):
	"""
        Returns saturation vapor density in g/m^3 for the given temperature T
        """
	
	M = 18 # Water molar mass [g/mol]
        R = 0.0623665 # Ideal gas constant [mmHg * m^3 * K^-1 *mol^-1]
        T_in_Kelvin =  self._to_kelvin(T)

        # Saturation vapor pressure [mmHg] according to August-Roche-Magnus 
        # formula, T in Celsius
        ps = (0.61078 * 7.501) * np.exp((17.2694*T)/(238.3+T))

        return (M / (R * T_in_Kelvin)) * ps


    def _to_kelvin(self, T):
        """
        Returns temperature in Kelvin
        """

	return T + 273.15

    def get_absolute_humidity(self):
    	"""
    	Returns absolute humidity using relative humidity and temperature 
        measured by senseHat
    	"""
	
        relative_humidity = super(FixedHat, self).get_humidity()
    	T_senseHat = super(FixedHat, self).get_temperature_from_humidity()	
    	sat_vapor_density = self._get_sat_vapor_density(T_senseHat)
	
    	return relative_humidity  * 0.01 * sat_vapor_density
	

    def get_humidity(self):
        """
        Returns the percentage of relative humidity for the calculated
        temperature accounting for the influence from the CPU temperature
        """

        absolute_humidity = self.get_absolute_humidity()
        T = self.get_temperature_from_humidity()
        sat_vapor_density = self._get_sat_vapor_density(T)
	
	return (absolute_humidity / sat_vapor_density) * 100


    def get_pressure(self):
        """
        Returns the pressure in Millibars for the adjusted temperature 
        (in Kelvin)
        """

        T_senseHat = super(FixedHat, self).get_temperature_from_pressure()
        P_senseHat = super(FixedHat, self).get_pressure()
        T_real = self.get_temperature_from_humidity()
        
        return (self._to_kelvin(T_real) * P_senseHat) \
            / self._to_kelvin(T_senseHat) 
