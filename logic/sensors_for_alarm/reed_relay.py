from logic.sensors_for_alarm.alarm_sensor import AlarmSensor


class ReadRelay(AlarmSensor):
    def __init__(self, name, pin):
        super().__init__(pin, name)

    def update(self, *args):
        if args[0][1] == 0 and not self.turn_on_alarm:
            self.turn_on_alarm = True
            self.notify()


