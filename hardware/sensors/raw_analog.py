from hardware.sensors.sensor import Sensor



class RawAnalog(Sensor):
    def __init__(self, pin: int, name: str):
        super().__init__(pin, name)
        self.sensor_value = None

    def update(self, new_value):
        if new_value is not self.sensor_value:
            self.sensor_value = new_value
            self.notify()