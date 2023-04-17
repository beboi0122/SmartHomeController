import json
from logic.lighting import Lighting
from hardware.shiftregisters.shift_register_in import ShiftRegisterIn
from smartHome import SmartHome

# with open("smarthome.json", "r") as f:
#     config = json.load(f)
#
# breakpoint()

s = SmartHome("smarthome.json")
breakpoint()



# with open("smarthome.json", "r") as f:
#     config = json.load(f)
#     hardware_config = config["hardware_config"]
#     smart_home_config = config["smart_home_config"]
#
# breakpoint()
# # import json
# # import time
# #
# # import serial_port
# #
# # ser = serial_port.ser
# #
# # ser.flushInput()
# # f = open("config.json", "r")
# # config = json.load(f)
# # config_str = str(config)
# # # # a = "{'SHIFT_OUT_PIN_VAL': {'pin': 1, 'val': 1}}"
# # # # a = "{'SET_SERVO': {'name': "servo1", 'pos': 180}}"
# # b = bytes(config_str + "\n", 'ascii')
# # ser.write(b)
# # print(b)
# #
# # # time.sleep(3)
# # # ser.write(bytes(a, 'ascii'))
# #
# # while 1:
# #     pass
# #     # print("__________________")
# #     # time.sleep(1)
# #     a = input()
# #     ser.write(bytes(a + "\n", 'ascii'))
# #
# #
# # # def main():
# # #     ser = serial.Serial(port='/dev/tty.usbserial-0001', baudrate=9600)
# # #     ser.flushInput()
# # #     ser.flushOutput()
# # #     while 1:
# # #         if ser.inWaiting()>0:
# # #             try:
# # #                 incoming_tag = ser.readline().decode().replace("\n", "")
# # #             except:
# # #                 continue
# # #
# # #             if incoming_tag == 'SENSOR_DATA_FROM_ESP32':
# # #                 data_length = int(ser.readline().decode())
# # #                 #data = json.loads(ser.read(data_length).decode().replace("\n", ""))
# # #                 data = ser.read(data_length).decode().replace("\n", "")
# # #                 print(data)
# # #             elif incoming_tag == "INERRUPT_FROM_ESP32":
# # #                 data_length = int(ser.readline().decode())
# # #                 data = ser.read(data_length).decode().replace("\n", "")
# # #                 print(data)
# # #
# # #
# # # if __name__ == '__main__':
# # #     main()