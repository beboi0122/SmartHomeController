from hardware.sensors.sensor import Sensor


class TemperatureAndHumidity(Sensor):
    def __init__(self, pin: int, name: str):
        super().__init__(pin, name)
        self.temperature = None
        self.humidity = None

    def update(self, temperature: float, humidity: float):
        if self.humidity is not humidity or self.temperature is not temperature:
            self.temperature = temperature
            self.humidity = humidity
            self.notify()


