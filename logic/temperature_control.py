from observer_pattern.observer import Observer
from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from globals import serial_out_buffer
import globals
from logic.function import Function


class TemperatureControl(Observer, Function):
    def __init__(self, room_name, cooling_pin, heating_pin, target_temperature, hister: float = 0.5):
        self.room_name = room_name
        self.cooling_pin = cooling_pin
        self.heating_pin = heating_pin
        self.target_temperature = target_temperature
        self.hister: float = hister

        self.temperature = -1
        self.humidity = -1

        self.last_sent = None

        self.heating: bool = False
        self.cooling: bool = False

    def update(self, subject: TemperatureAndHumidity):
        ud = False
        if self.humidity != subject.humidity or self.temperature != subject.temperature:
            ud = True
            self.temperature = subject.temperature
            self.humidity = subject.humidity
            if self.last_sent is None or False:
                globals.state["state"]["rooms"][self.room_name]["temperature"] = self.temperature
                globals.state["state"]["rooms"][self.room_name]["humidity"] = self.humidity
        if globals.global_heating:
            if self.cooling:
                self.cooling = False
                self.__set_pin(self.cooling_pin, False)
            if subject.temperature < self.target_temperature and not self.heating:
                self.heating = True
                self.__set_pin(self.heating_pin, self.heating)
                self.__set_pin(self.cooling_pin, False)
            elif subject.temperature > self.target_temperature+self.hister and self.heating:
                self.heating = False
                self.__set_pin(self.heating_pin, self.heating)
                self.__set_pin(self.cooling_pin, False)
        elif globals.global_cooling:
            if self.heating:
                self.heating = False
                self.__set_pin(self.heating_pin, False)
            if subject.temperature > self.target_temperature and not self.cooling:
                self.cooling = True
                self.__set_pin(self.cooling_pin, self.cooling)
                self.__set_pin(self.heating_pin, False)
            elif subject.temperature < self.target_temperature-self.hister and self.cooling:
                self.cooling = False
                self.__set_pin(self.cooling_pin, self.cooling)
                self.__set_pin(self.heating_pin, False)
        elif not globals.global_cooling and self.cooling:
            self.cooling = False
            self.__set_pin(self.cooling_pin, False)
        elif not globals.global_heating and self.heating:
            self.heating = False
            self.__set_pin(self.heating_pin, False)
        if ud:
            globals.fireBase.send_state()

    def __set_pin(self, pin, state: bool):
        if "shift_out_" in pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(state))
                                     + "}}")

    def status_changed(self, status):
        self.update(globals.smartHome.rooms[self.room_name].temperature_and_humidity_sensor)

    def load_state(self):
        self.status_changed(None)