from globals import serial_out_buffer

class Servo:
    def __init__(self, name: str, pin):
        self.pin = pin
        self.name = name
        self.state = 0

    def set_state(self, state: int):
        self.state = state
        serial_out_buffer.append("{'SET_SERVO': {'name': '" + self.name + "', 'pos': " + str(self.state) + "}}")


