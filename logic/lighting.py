from observer_pattern.observer import Observer


class Lighting(Observer):
    def __init__(self, light_pin, trigger_pin):
        self.trigger = trigger_pin
        self.pin = light_pin
        self.light_on: bool = False

    def update(self, pin_value):
        if pin_value == 1:
            self.light_on = not self.light_on
            print(self.light_on)


