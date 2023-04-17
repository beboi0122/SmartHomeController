from observer_pattern.observer import Observer
from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from globals import serial_out_buffer


class TemperatureControl(Observer):
    global_heating: bool = False
    global_cooling: bool = True

    def __init__(self, cooling_pin, heating_pin, target_temperature, hister: float = 0.5):
        self.cooling_pin = cooling_pin
        self.heating_pin = heating_pin
        self.target_temperature = target_temperature
        self.hister: float = hister

        self.heating: bool = False
        self.cooling: bool = False

    def update(self, subject: TemperatureAndHumidity):
        if TemperatureControl.global_heating:
            if subject.temperature < self.target_temperature and not self.heating:
                self.heating = True
                self.__set_pin(self.heating_pin, self.heating)
                self.__set_pin(self.cooling_pin, False)
            elif subject.temperature > self.target_temperature+self.hister and self.heating:
                self.heating = False
                self.__set_pin(self.heating_pin, self.heating)
                self.__set_pin(self.cooling_pin, False)
        elif TemperatureControl.global_cooling:
            if subject.temperature > self.target_temperature and not self.cooling:
                self.cooling = True
                self.__set_pin(self.cooling_pin, self.cooling)
                self.__set_pin(self.heating_pin, False)
            elif subject.temperature < self.target_temperature-self.hister and self.cooling:
                self.cooling = False
                self.__set_pin(self.cooling_pin, self.cooling)
                self.__set_pin(self.heating_pin, False)


    def __set_pin(self, pin, state: bool):
        if "shift_out_" in pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(state))
                                     + "}}")
