from globals import serial_out_buffer
from observer_pattern.observer import Observer
from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from logic.function import Function
import globals


class Ventilation(Observer, Function):
    def __init__(self, pin, room_name, target_humidity: float, hister: float = 10.0):
        self.pin = pin
        self.room_name = room_name
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
        # print(f"VENT: {self.ventilation}")

    def __set_pin(self):
        if "shift_out_" in self.pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(self.pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(self.ventilation))
                                     + "}}")

    def status_changed(self, status):
        self.update(globals.smartHome.rooms[self.room_name].temperature_and_humidity_sensor)

    def load_state(self):
        self.status_changed(None)
