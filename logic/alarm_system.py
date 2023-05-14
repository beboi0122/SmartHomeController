import globals
from globals import serial_out_buffer
from logic.function import Function
from observer_pattern.observer import Observer
from logic.sensors_for_alarm.alarm_sensor import AlarmSensor


class AlarmSystem(Observer, Function):

    class AlarmSystemMode:
        OFF = 0
        SHELL = 1
        FULL = 2

    def __init__(self, siren_pin, reset_pin, off_mode_pin, shell_mode_pin, full_mode_pin,
                 shell_sensors=None, full_sensors=None):
        self.full_sensors = full_sensors
        self.shell_sensors = shell_sensors
        self.siren_pin = siren_pin[0]
        self.reset_pin = reset_pin
        self.off_mode_pin = off_mode_pin
        self.shell_mode_pin = shell_mode_pin
        self.full_mode_pin = full_mode_pin

        self.mode = self.AlarmSystemMode.OFF

        self.is_alarm_on = False

    def update(self, *args):
        if isinstance(args[0], AlarmSensor):
            if self.mode is not self.AlarmSystemMode.OFF:
                sen: AlarmSensor = args[0]
                if self.mode is self.AlarmSystemMode.SHELL:
                    if sen in self.shell_sensors and sen.turn_on_alarm:
                        self.__turn_alarm_on()
                elif self.mode is self.AlarmSystemMode.FULL:
                    if sen.turn_on_alarm:
                        self.__turn_alarm_on()

        else:
            pin_name = args[0][0]
            pin_val = args[0][1]
            if pin_val == 1:
                if pin_name == self.off_mode_pin:
                    self.mode = self.AlarmSystemMode.OFF
                    globals.state["state"]["alarm_system"]["state"] = "OFF"
                elif pin_name == self.shell_mode_pin:
                    self.mode = self.AlarmSystemMode.SHELL
                    globals.state["state"]["alarm_system"]["state"] = "SHELL"
                elif pin_name == self.full_mode_pin:
                    self.mode = self.AlarmSystemMode.FULL
                    globals.state["state"]["alarm_system"]["state"] = "FULL"

                self.__reset_alarm()

    def __reset_alarm(self):
        self.is_alarm_on = False
        globals.state["state"]["alarm_system"]["alarm"] = False
        globals.fireBase.send_state()
        if "shift_out_" in self.siren_pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(self.siren_pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(self.is_alarm_on))
                                     + "}}")
        for sen in self.full_sensors:
            sen.reset()
        for sen in self.shell_sensors:
            sen.reset()

    def __turn_alarm_on(self):
        print(self.siren_pin)
        globals.state["state"]["alarm_system"]["alarm"] = True
        globals.fireBase.send_state()
        self.is_alarm_on = True
        if "shift_out_" in self.siren_pin:
            serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                     + str(int(self.siren_pin.replace("shift_out_", "")))
                                     + ", 'val': "
                                     + str(int(self.is_alarm_on))
                                     + "}}")

    def status_changed(self, status):
        if status == "OFF":
            self.mode = self.AlarmSystemMode.OFF
            print("OFF")
        elif status == "SHELL":
            self.mode = self.AlarmSystemMode.SHELL
            print("SHELL")
        elif status == "FULL":
            self.mode = self.AlarmSystemMode.FULL
            print("FULL")

        self.__reset_alarm()