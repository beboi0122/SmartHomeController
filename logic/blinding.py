from hardware.actuators.servo import Servo
from observer_pattern.observer import Observer
from hardware.sensors.raw_analog import RawAnalog
from logic.function import Function
import globals


class Blinding(Observer, Function):

    def __init__(self, room_name, function_name, servo: Servo, lower_state: int, higher_state: int,
                 trigger: int = None, sensor_in: RawAnalog = None, sensor_out: RawAnalog = None):
        if sensor_in is not None and sensor_out is None:
            raise Exception("Both or none of sensor_in and sensor_out must be None")
        if sensor_in is None and sensor_out is not None:
            raise Exception("Both or none of sensor_in and sensor_out must be None")
        self.room_name = room_name
        self.function_name = function_name
        self.servo: Servo = servo
        self.trigger: int = trigger
        self.sensor_in = sensor_in
        self.sensor_out = sensor_out
        self.lower_state = lower_state
        self.higher_state = higher_state
        servo.set_state(self.lower_state)
        self.triggered = False

    def update(self, *args):
        if self.trigger is not None and self.sensor_in is None:
            if args[0][1] == 1:
                self.__update_via_trigger()
        elif self.trigger is None and self.sensor_in is not None:
            self.__update_via_sensor()
        elif self.trigger is not None and self.sensor_in is not None:
            if isinstance(args[0], RawAnalog) and not self.triggered:
                self.__update_via_sensor()
            elif not isinstance(args[0], RawAnalog):
                if args[0][1] == 1:
                    if self.triggered:
                        self.triggered = False
                        self.__update_via_sensor()
                    else:
                        self.triggered = True
                        self.__update_via_trigger()

    def __update_via_sensor(self):
        if self.sensor_in.sensor_value is None or self.sensor_out.sensor_value is None:
            return
        # this means that if the blinds are up and the it's brighter inside than outside, the blinds will go down
        if (self.servo.state == self.higher_state) and (self.sensor_in.sensor_value > self.sensor_out.sensor_value):
            self.servo.set_state(self.lower_state)
            self.set_state()
        # this means that if the blinds are down and the it's darker inside than outside, the blinds will go up
        elif self.servo.state == self.lower_state and self.sensor_in.sensor_value < self.sensor_out.sensor_value:
            self.servo.set_state(self.higher_state)
            self.set_state()

    def __update_via_trigger(self):
        if self.servo.state == self.lower_state:
            self.servo.set_state(self.higher_state)
            self.set_state()
        else:
            self.servo.set_state(self.lower_state)
            self.set_state()

    def status_changed(self, status):
        if status == "RESET":
            self.triggered = False
        else:
            self.triggered = True
            self.servo.set_state(self.higher_state) if status else self.servo.set_state(self.lower_state)

    def set_state(self):
        globals.state["state"]["rooms"][self.room_name]["functions"][self.function_name]["state"] = False if self.servo.state == self.lower_state else True
        globals.fireBase.send_state()

    def load_state(self):
        self.servo.set_state(self.servo.state)