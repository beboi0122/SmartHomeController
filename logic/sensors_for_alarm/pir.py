from logic.sensors_for_alarm.alarm_sensor import AlarmSensor


class Pir(AlarmSensor):
    def __init__(self, pin, name: str):
        super().__init__(pin, name)

    def update(self, *args):
        if args[0][1] == 1 and not self.turn_on_alarm:
            self.turn_on_alarm = True
            self.notify()

