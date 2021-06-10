class TemperatureSensor:

    def __init__(self, w1_id):
        self.__file_name = f'/sys/bus/w1/devices/{w1_id}/w1_slave'


    @property
    def temperature(self):
        with open(self.__file_name) as sensor_file:
            temp_str = sensor_file.read().rstrip('\n').split(' ')[-1].strip('t=')
            return round(float(temp_str) / 1000, 2)