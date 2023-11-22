from hardware.actuators.servo import Servo
from observer_pattern.observer import Observer
from logic.function import Function
import globals


class ElectricDoor(Observer, Function):

    def __init__(self, room_name, function_name, servo: Servo, lower_state: int = 0, higher_state: int = 90,
                 trigger: int = None):
        self.room_name = room_name
        self.function_name = function_name
        self.servo: Servo = servo
        self.trigger: int = trigger
        self.lower_state = lower_state
        self.higher_state = higher_state
        servo.set_state(self.lower_state)
        self.triggered = False

    def update(self, msg):
        if msg[1] == 1 and self.servo.state == self.lower_state:
            self.servo.set_state(self.higher_state)
            self.set_state()
        elif msg[1] == 1 and self.servo.state == self.higher_state:
            self.servo.set_state(self.lower_state)
            self.set_state()

    def status_changed(self, status):
        self.servo.set_state(self.higher_state) if status else self.servo.set_state(self.lower_state)

    def set_state(self):
        print("set_state")
        globals.state["state"]["rooms"][self.room_name]["functions"][self.function_name]["state"] = False if self.servo.state == self.lower_state else True
        globals.fireBase.send_state()

    def load_state(self):
        pass