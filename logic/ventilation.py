from globals import serial_out_buffer
from observer_pattern.observer import Observer
from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from logic.function import Function


class Ventilation(Observer, Function):
    def __init__(self, pin, target_humidity: float, hister: float = 10.0):
        self.pin = pin
        self.target_humidity: float = target_humidity
        self.hister: float = hister

        self.ventilation:bool = False

    def update(self, subject: TemperatureAndHumidity):
        if not self.ventilation and subject.humidity > self.target_humidity:
            self.ventilation = True
            self.__set_pin()
        if self.ventilation and subject.humidity < self.target_humidity - self.hister:
            self.ventilation = False
            self.__set_pin()

    def __set_pin(self):
        if "shift_out_" in self.pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(self.pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(self.ventilation))
                                     + "}}")

    def status_changed(self, status):
        print("vent")
