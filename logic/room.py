
class Room:
    def __init__(self):
        self.sensors = {}

    def add_sensor(self, sensor_name, sensor):
        self.sensors[sensor_name] = sensor
