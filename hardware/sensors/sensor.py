from observer_pattern.subject import Subject


class Sensor(Subject):
    def __init__(self, pin: int, name: str):
        super().__init__()
        self.pin = pin
        self.name = name

    def update(self, *args):
        raise NotImplementedError("update function should be implemented")