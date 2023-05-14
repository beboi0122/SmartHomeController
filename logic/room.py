from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from logic.ventilation import Ventilation
from logic.temperature_control import TemperatureControl

class Room:
    def __init__(self, temperature_and_humidity_sensor: TemperatureAndHumidity = None,
                 temp_control: TemperatureControl = None, ventilation: Ventilation = None):
        self.temperature_and_humidity_sensor: TemperatureAndHumidity = temperature_and_humidity_sensor
        if self.temperature_and_humidity_sensor is None:
            self.temp_control: TemperatureControl = None
            self.ventilation: Ventilation = None
        else:
            self.temp_control: TemperatureControl = temp_control
            self.ventilation: Ventilation = ventilation
        
        self.functions = dict()

    def add_functions(self, function_name, function):
        self.functions[function_name] = function

    def status_changed(self):
        for function in self.functions:
            function.status_changed()
