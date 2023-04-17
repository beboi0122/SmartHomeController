import json
import threading
import time
import serial
from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from hardware.sensors.raw_analog import RawAnalog
from hardware.sensors.sensor import Sensor
from hardware.shiftregisters.shift_register_in import ShiftRegisterIn
from hardware.shiftregisters.shift_register_out import ShiftRegisterOut
from hardware.actuators.servo import Servo
from logic.blinding import Blinding
from logic.lighting import Lighting
from logic.room import Room
from globals import serial_out_buffer
from logic.temperature_control import TemperatureControl
from logic.ventilation import Ventilation


class SmartHome:
    def __init__(self, config_file_path: str):
        self._config_file_path = config_file_path
        # self._serial_port = None
        self._serial_port = serial.Serial(port='/dev/tty.usbserial-0001', baudrate=9600)
        self._hardware_config = None
        self._smart_home_config = None
        self._sensors = dict()
        self._servos = dict()
        self._rooms = dict()
        self._shift_register_in: ShiftRegisterIn = None
        self._shift_register_out = None
        self._write_to_serial_thread = threading.Thread(target=self._write_to_serial)
        self._read_from_serial_thread = threading.Thread(target=self._read_from_serial)

        with open(self._config_file_path, "r") as f:
            config = json.load(f)
            self._hardware_config = config["hardware_config"]
            self._smart_home_config = config["smart_home_config"]

        self._load_hardware_config()
        self._load_smart_home_config()

        time.sleep(3)
        self._send_config_to_esp()
        self._serial_port.flushInput()
        time.sleep(1)


        self._write_to_serial_thread.start()
        self._read_from_serial_thread.start()



    def _send_config_to_esp(self):
        self._serial_port.write(bytes(str(self._hardware_config) + "\n", 'ascii'))

    def _load_hardware_config(self):
        if "sensors" in self._hardware_config:
            for sensor in self._hardware_config["sensors"]:
                if self._hardware_config["sensors"][sensor]["type"] == "dht11":
                    self._sensors[sensor] = TemperatureAndHumidity(
                        pin=self._hardware_config["sensors"][sensor]["pin"],
                        name=sensor
                    )
                elif self._hardware_config["sensors"][sensor]["type"] == "raw_analog":
                    self._sensors[sensor] = RawAnalog(
                        pin=self._hardware_config["sensors"][sensor]["pin"],
                        name=sensor
                    )
                else:
                    raise Exception("unknown sensor type")

        if "shift_register_in" in self._hardware_config:
            self._shift_register_in = ShiftRegisterIn(
                latch=self._hardware_config["shift_register_in"]["latch"],
                data=self._hardware_config["shift_register_in"]["data"],
                clock=self._hardware_config["shift_register_in"]["clock"],
                shift_reg_num=self._hardware_config["shift_register_in"]["shift_reg_num"]
            )

        if "shift_register_out" in self._hardware_config:
            self._shift_register_out = ShiftRegisterOut()
            # TODO

        if "servo" in self._hardware_config:
            for servo in self._hardware_config["servo"]:
                self._servos[servo] = Servo(
                    name=servo,
                    pin=self._hardware_config["servo"][servo]["pin"]
                )

    def _load_smart_home_config(self):
        for room in self._smart_home_config["rooms"]:
            self._rooms[room] = self.__set_up_room(self._smart_home_config["rooms"][room])
            for function in self._smart_home_config["rooms"][room]["functions"]:
                if self._smart_home_config["rooms"][room]["functions"][function]["type"] == "lighting":
                    pin = self._smart_home_config["rooms"][room]["functions"][function]["pin"]
                    trigger = self._smart_home_config["rooms"][room]["functions"][function]["trigger"]
                    light = Lighting(pin, trigger)
                    self._rooms[room].add_functions(function_name=function, function=light)
                    if "shift_in_" in trigger:
                        trigger = int(trigger.replace("shift_in_", ""))
                        self._shift_register_in.add(light, trigger)
                    else:
                        pass
                        # TODO
                elif self._smart_home_config["rooms"][room]["functions"][function]["type"] == "blinding":
                    params = self._smart_home_config["rooms"][room]["functions"][function]
                    self.__setup_blinding(room, function, params)
                else:
                    print("NO")

    def _write_to_serial(self):
        while 1:
            if len(serial_out_buffer) > 0:
                for _ in range(len(serial_out_buffer)):
                    # print(serial_out_buffer.pop(0))
                    self._serial_port.write(bytes(serial_out_buffer.pop(0) + "\n", 'ascii'))

    def _read_from_serial(self):
        while 1:
            if self._serial_port.inWaiting() > 0:
                try:
                    incoming: json = json.loads(self._serial_port.readline().decode().replace("\n", ""))
                except:
                    continue

                if 'SENSOR_DATA_FROM_ESP32' in incoming:
                    sensor_name = list(incoming['SENSOR_DATA_FROM_ESP32'].keys())[0]
                    print(incoming['SENSOR_DATA_FROM_ESP32'])
                    self._sensors[sensor_name].update(incoming['SENSOR_DATA_FROM_ESP32'])
                elif "INERRUPT_FROM_ESP32" in incoming:
                    self._shift_register_in.update(incoming["INERRUPT_FROM_ESP32"])
                    print(incoming["INERRUPT_FROM_ESP32"])
                elif "CONFIG_FILE_NEEDED" in incoming:
                    self._send_config_to_esp()
                    self._serial_port.flushInput()
                    time.sleep(1)
                    print(incoming)
                    # print(data)

    def __setup_blinding(self, room, function, params):
        if "trigger" in params and "sensor" not in params:
            trigger = params["trigger"]
            blinding = Blinding(
                servo=self._servos[params["servo"]],
                trigger=params["trigger"],
                lower_state=params["lower_state"],
                higher_state=params["higher_state"]
            )
            self._rooms[room].add_functions(function_name=function, function=blinding)
            if "shift_in_" in trigger:
                trigger = int(trigger.replace("shift_in_", ""))
                self._shift_register_in.add(blinding, trigger)
        elif "trigger" not in params and "sensor" in params:
            sensor: RawAnalog = self._sensors[params["sensor"]]
            blinding = Blinding(
                servo=self._servos[params["servo"]],
                lower_state=params["lower_state"],
                higher_state=params["higher_state"],
                sensor=sensor,
                hister_val=params["hister_val"],
                trigger_val=params["trigger_val"]
            )
            self._rooms[room].add_functions(function_name=function, function=blinding)
            sensor.add(blinding)
        elif "trigger" in params and "sensor" in params:
            trigger = params["trigger"]
            sensor: RawAnalog = self._sensors[params["sensor"]]
            blinding = Blinding(
                trigger=trigger,
                servo=self._servos[params["servo"]],
                lower_state=params["lower_state"],
                higher_state=params["higher_state"],
                sensor=sensor,
                hister_val=params["hister_val"],
                trigger_val=params["trigger_val"]
            )
            self._rooms[room].add_functions(function_name=function, function=blinding)

            if "shift_in_" in trigger:
                trigger = int(trigger.replace("shift_in_", ""))
                self._shift_register_in.add(blinding, trigger)

    def __set_up_room(self, room: json)->Room:
        sensor: TemperatureAndHumidity = None
        ventilation: Ventilation = None
        temperature_control: TemperatureControl = None
        if "temperature_and_humidity" in room:
            sensor = self._sensors[room["temperature_and_humidity"]]
            if "temperature_control" in room:
                temperature_control = TemperatureControl(
                    cooling_pin=room["temperature_control"]["cooling_pin"],
                    heating_pin=room["temperature_control"]["heating_pin"],
                    target_temperature=room["temperature_control"]["target_temperature"],
                    hister=room["temperature_control"]["hister"]
                )
                sensor.add(temperature_control)
            if "ventilation" in room:
                ventilation = Ventilation(
                    pin=room["ventilation"]["pin"],
                    target_humidity=room["ventilation"]["target_humidity"],
                    hister=room["ventilation"]["hister"]
                )
                sensor.add(ventilation)
        return Room(
            temperature_and_humidity_sensor=sensor,
            temp_control=temperature_control,
            ventilation=ventilation
        )

