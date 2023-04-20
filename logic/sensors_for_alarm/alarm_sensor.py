from hardware.sensors.sensor import Sensor


class AlarmSensor(Sensor):
    def __init__(self, pin, name: str):
        super().__init__(pin, name)

        self.turn_on_alarm = False

    def reset(self):
        self.turn_on_alarm = False