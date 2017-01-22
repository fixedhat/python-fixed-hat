from sense_hat import SenseHat

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


    def get_humidity(self):
        """
        Returns the percentage of relative humidity for the calculated
        temperature accounting for the influence from the CPU temperature
        """

        pass # TODO


    def get_pressure(self):
        """
        Returns the pressure in Millibars for the adjusted temperature
        """

        pass # TODO
