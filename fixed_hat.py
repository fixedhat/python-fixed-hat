from math import exp
from sense_hat import SenseHat

class FixedHat(SenseHat):


    RPI_CPU_THERMAL_ZONE = '/sys/class/thermal/thermal_zone0/temp'
    WATER_MOLAR_MASS = 18 # [g/mol]
    GAS_CONSTANT = 8.3144598e-3 # [hPa * m^3 * K^-1 * mol^-1]


    def __init__(self, temp_cpu_factor=1.5):
        self._temp_cpu_factor = temp_cpu_factor
        super(FixedHat, self).__init__()

    def _sat_vapor_density(self, temp):
	"""
        Returns saturation vapor density in g/m^3 for the given temperature
        """
	
        temp_kelvin = self._to_kelvin(temp)

        # Alduchov, O. and R. Eskridge, 1996:
        # Improved Magnus Form Approximation of Saturation Vapor Pressure
        psat = 6.1094 * exp(17.625 * temp / (243.04 + temp)) # [hPa]
        return self.WATER_MOLAR_MASS / (self.GAS_CONSTANT * temp_kelvin) * psat

    def _to_kelvin(self, T):
        """
        Returns temperature in Kelvin
        """

	return T + 273.15

    def get_temperature_from_cpu(self):
        return int(open(self.RPI_CPU_THERMAL_ZONE).read()) / 1e3

    def get_temperature_from_humidity(self):
        """
        Returns the temperature in Celsius accounting for the influence 
        from the CPU temperature
        """

        temp_humidity = super(FixedHat, self).get_temperature_from_humidity()
        temp_cpu = self.get_temperature_from_cpu()
        temp_increase_cpu = (temp_cpu - temp_humidity) / self._temp_cpu_factor
        return temp_humidity - temp_increase_cpu

    def get_absolute_humidity(self):
    	"""
    	Returns absolute humidity using relative humidity and temperature 
        measured by senseHat
    	"""
	
        relative_humidity = super(FixedHat, self).get_humidity()
    	temp_humidity = super(FixedHat, self).get_temperature_from_humidity()
    	sat_vapor_density = self._sat_vapor_density(temp_humidity)
    	return relative_humidity * 0.01 * sat_vapor_density

    def get_humidity(self):
        """
        Returns the percentage of relative humidity for the calculated
        temperature accounting for the influence from the CPU temperature
        """

        absolute_humidity = self.get_absolute_humidity()
        temp_humidity = self.get_temperature_from_humidity()
        sat_vapor_density = self._sat_vapor_density(temp_humidity)
	return (absolute_humidity / sat_vapor_density) * 100


    def get_pressure(self):
        """
        Returns the pressure in Millibars for the adjusted temperature 
        (in Kelvin)
        """

        temp_pressure = super(FixedHat, self).get_temperature_from_pressure()
        pressure = super(FixedHat, self).get_pressure()
        temp_adjusted = self.get_temperature_from_humidity()
        
        return (self._to_kelvin(temp_adjusted) * pressure) \
            / self._to_kelvin(temp_pressure)
