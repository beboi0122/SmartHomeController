import json
import threading
import time
import serial
from hardware.sensors.temp_and_hum_sen import TemperatureAndHumidity
from hardware.sensors.raw_analog import RawAnalog
from hardware.shiftregisters.shift_register_in import ShiftRegisterIn
from hardware.shiftregisters.shift_register_out import ShiftRegisterOut


class SmartHome:
    serial_out_buffer = []

    def __init__(self, config_file_path: str):
        self._config_file_path = config_file_path
        # self._serial_port = serial.Serial(port='/dev/tty.usbserial-0001', baudrate=9600)
        self._hardware_config = None
        self._smart_home_config = None
        self._sensors = dict()
        self._shift_register_in = None
        self._shift_register_out = None
        self._write_to_serial_thread = threading.Thread(target=self._write_to_serial)

        with open(self._config_file_path, "r") as f:
            config = json.load(f)
            self._hardware_config = config["hardware_config"]
            self._smart_home_config = config["smart_home_config"]

        self._load_hardware_config()

        # time.sleep(3)
        # self._send_config_to_esp()

        self._write_to_serial_thread.start()



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

        if "servo" in self._hardware_config:
            pass

    def _write_to_serial(self):
        while 1:
            if len(SmartHome.serial_out_buffer) > 0:
                for _ in range(len(SmartHome.serial_out_buffer)):
                    print(SmartHome.serial_out_buffer.pop(0))
                    # self._serial_port.write(bytes(SmartHome.serial_out_buffer.pop(0) + "\n", 'ascii'))
