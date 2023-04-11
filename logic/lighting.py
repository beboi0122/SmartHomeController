from observer_pattern.observer import Observer
from globals import serial_out_buffer


class Lighting(Observer):
    def __init__(self, light_pin, trigger_pin):
        self.trigger = trigger_pin
        self.pin = light_pin
        self.light_on: bool = False

    def update(self, pin_value):
        if pin_value == 1:
            self.light_on = not self.light_on
            if "shift_out_" in self.pin:
                serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                               + str(int(self.pin.replace("shift_out_", "")))
                                               + ", 'val': "
                                               + str(int(self.light_on))
                                               + "}}")
