import json
import threading
import time
import serial

import globals
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
from logic.sensors_for_alarm.pir import Pir
from logic.sensors_for_alarm.reed_relay import ReadRelay
from logic.alarm_system import AlarmSystem
from logic.sensors_for_alarm.alarm_sensor import AlarmSensor


class SmartHome:
    def __init__(self):
        with open("serial.json", "r") as f:
            self._serial_port_name = json.load(f)["port"]

        self._serial_port = serial.Serial(port=self._serial_port_name, baudrate=9600)
        self._hardware_config = None
        self._smart_home_config = None
        self._sensors = dict()
        self._servos = dict()
        self.rooms = dict()
        self._shift_register_in: ShiftRegisterIn = None
        self._shift_register_out = None
        self._write_to_serial_thread = threading.Thread(target=self._write_to_serial)
        self._read_from_serial_thread = threading.Thread(target=self._read_from_serial)

        self.alarm_system = None

        self._hardware_config = globals.config["hardware_config"]
        self._smart_home_config = globals.config["smart_home_config"]

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
        if "shift_register_in" in self._hardware_config:
            self._shift_register_in = ShiftRegisterIn(
                latch=self._hardware_config["shift_register_in"]["latch"],
                data=self._hardware_config["shift_register_in"]["data"],
                clock=self._hardware_config["shift_register_in"]["clock"],
                shift_reg_num=self._hardware_config["shift_register_in"]["shift_reg_num"]
            )

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
                elif self._hardware_config["sensors"][sensor]["type"] == "digital":
                    if self._hardware_config["sensors"][sensor]["logical_type"] == "pir":
                        pin = self._hardware_config["sensors"][sensor]["pin"]
                        self._sensors[sensor] = Pir(
                            pin=pin,
                            name=sensor
                        )
                        if "shift_in_" in pin:
                            p = int(pin.replace("shift_in_", ""))
                            self._shift_register_in.add(self._sensors[sensor], p)
                    elif self._hardware_config["sensors"][sensor]["logical_type"] == "reed":
                        pin = self._hardware_config["sensors"][sensor]["pin"]
                        self._sensors[sensor] = ReadRelay(
                            pin=pin,
                            name=sensor
                        )
                        if "shift_in_" in pin:
                            p = int(pin.replace("shift_in_", ""))
                            self._shift_register_in.add(self._sensors[sensor], p)
                else:
                    raise Exception("unknown sensor type")



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
            self.rooms[room] = self.__set_up_room(self._smart_home_config["rooms"][room], room)
            for function in self._smart_home_config["rooms"][room]["functions"]:
                if self._smart_home_config["rooms"][room]["functions"][function]["type"] == "lighting":
                    params = self._smart_home_config["rooms"][room]["functions"][function]
                    self.__setup_lighting(room, function, params)
                elif self._smart_home_config["rooms"][room]["functions"][function]["type"] == "blinding":
                    params = self._smart_home_config["rooms"][room]["functions"][function]
                    self.__setup_blinding(room, function, params)
                else:
                    print("NO")
        if "alarm_system" in self._smart_home_config:
            self.__set_up_alarm_system(self._smart_home_config["alarm_system"])
    def _write_to_serial(self):
        while 1:
            if len(serial_out_buffer) > 0:
                for _ in range(len(serial_out_buffer)):
                    out = serial_out_buffer.pop(0)
                    self._serial_port.write(bytes(out + "\n", 'ascii'))

    def _read_from_serial(self):
        while 1:
            if self._serial_port.inWaiting() > 0:
                try:
                    incoming: json = json.loads(self._serial_port.readline().decode().replace("\n", ""))
                except:
                    continue
                if 'SENSOR_DATA_FROM_ESP32' in incoming:
                    sensor_name = list(incoming['SENSOR_DATA_FROM_ESP32'].keys())[0]
                    # print(incoming['SENSOR_DATA_FROM_ESP32'])
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

    def __setup_lighting(self, room, function, params):
        pin = params["pin"]
        trigger = params["trigger"]
        light = Lighting(
            room_name=room,
            function_name=function,
            light_pin=pin,
            trigger_pin=trigger
        )
        self.rooms[room].add_functions(function_name=function, function=light)
        if "shift_in_" in trigger:
            trigger = int(trigger.replace("shift_in_", ""))
            self._shift_register_in.add(light, trigger)

    def __setup_blinding(self, room, function, params):
        if "trigger" in params and "sensor" not in params:
            trigger = params["trigger"]
            blinding = Blinding(
                room_name=room,
                function_name=function,
                servo=self._servos[params["servo"]],
                trigger=params["trigger"],
                lower_state=params["lower_state"],
                higher_state=params["higher_state"]
            )
            self.rooms[room].add_functions(function_name=function, function=blinding)
            if "shift_in_" in trigger:
                trigger = int(trigger.replace("shift_in_", ""))
                self._shift_register_in.add(blinding, trigger)
        elif "trigger" not in params and "sensor" in params:
            sensor: RawAnalog = self._sensors[params["sensor"]]
            blinding = Blinding(
                room_name=room,
                function_name=function,
                servo=self._servos[params["servo"]],
                lower_state=params["lower_state"],
                higher_state=params["higher_state"],
                sensor=sensor,
                hister_val=params["hister_val"],
                trigger_val=params["trigger_val"]
            )
            self.rooms[room].add_functions(function_name=function, function=blinding)
            sensor.add(blinding)
        elif "trigger" in params and "sensor" in params:
            trigger = params["trigger"]
            sensor: RawAnalog = self._sensors[params["sensor"]]
            blinding = Blinding(
                room_name=room,
                function_name=function,
                trigger=trigger,
                servo=self._servos[params["servo"]],
                lower_state=params["lower_state"],
                higher_state=params["higher_state"],
                sensor=sensor,
                hister_val=params["hister_val"],
                trigger_val=params["trigger_val"]
            )
            self.rooms[room].add_functions(function_name=function, function=blinding)

            if "shift_in_" in trigger:
                trigger = int(trigger.replace("shift_in_", ""))
                self._shift_register_in.add(blinding, trigger)
            sensor.add(blinding)

    def __set_up_room(self, room: json, room_name)->Room:
        sensor: TemperatureAndHumidity = None
        ventilation: Ventilation = None
        temperature_control: TemperatureControl = None
        if "temperature_and_humidity" in room:
            sensor = self._sensors[room["temperature_and_humidity"]]
            if "temperature_control" in room:
                temperature_control = TemperatureControl(
                    room_name=room_name,
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

    def __set_up_alarm_system(self, alarm: json):
        shell_sensors = list()
        full_sensors = list()
        siren_pin = alarm["siren"],
        reset_pin = alarm["reset"],
        off_mode_pin = alarm["off_mode"],
        shell_mode_pin = alarm["shell_mode"],
        full_mode_pin = alarm["full_mode"],
        for sen_name in alarm["shell_sensors"]:
            shell_sensors.append(self._sensors[sen_name])

        for sen_name in alarm["full_sensors"]:
            full_sensors.append(self._sensors[sen_name])

        self.alarm_system = AlarmSystem(
            siren_pin=siren_pin,
            reset_pin=reset_pin[0],
            off_mode_pin=off_mode_pin[0],
            shell_mode_pin=shell_mode_pin[0],
            full_mode_pin=full_mode_pin[0],
            shell_sensors=shell_sensors,
            full_sensors=full_sensors
        )
        self._shift_register_in.add(self.alarm_system, int(reset_pin[0].replace("shift_in_", "")))
        self._shift_register_in.add(self.alarm_system, int(off_mode_pin[0].replace("shift_in_", "")))
        self._shift_register_in.add(self.alarm_system, int(shell_mode_pin[0].replace("shift_in_", "")))
        self._shift_register_in.add(self.alarm_system, int(full_mode_pin[0].replace("shift_in_", "")))
        for sen in shell_sensors:
            sen.add(self.alarm_system)

        for sen in full_sensors:
            sen.add(self.alarm_system)