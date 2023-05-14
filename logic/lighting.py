import globals
from observer_pattern.observer import Observer
from globals import serial_out_buffer
from logic.function import Function


class Lighting(Observer, Function):

    def __init__(self, room_name, function_name, light_pin, trigger_pin):
        self.function_name = function_name
        self.room_name = room_name
        self.trigger = trigger_pin
        self.pin = light_pin
        self.light_on: bool = False

    def update(self, msg):
        pin_value = msg[1]
        if pin_value == 1:
            self.light_on = not self.light_on
            self.set_pin()
            self.set_state()

    def set_pin(self):
        if "shift_out_" in self.pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(self.pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(self.light_on))
                                     + "}}")

    def status_changed(self, status):
        self.light_on = status
        self.set_pin()

    def set_state(self):
        globals.state["state"]["rooms"][self.room_name]["functions"][self.function_name]["state"] = self.light_on
        globals.fireBase.send_state()
