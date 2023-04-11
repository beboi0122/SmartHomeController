import json
import threading

import serial
import time


ser = serial.Serial(port='/dev/tty.usbserial-0001', baudrate=9600)
time.sleep(3)

ser = ser

ser.flushInput()
f = open("config.json", "r")
config = json.load(f)
config_str = str(config)
b = bytes(config_str + "\n", 'ascii')
ser.write(b)
print(b)

def read_from_serial():
    leds = [False, False, False, False, False, False, False, False]
    while 1:
        if ser.inWaiting() > 0:
            try:
                incoming_tag = ser.readline().decode().replace("\n", "")
            except:
                continue

            if incoming_tag == 'SENSOR_DATA_FROM_ESP32':
                data_length = int(ser.readline().decode())
                data = json.loads(ser.read(data_length).decode().replace("\n", ""))
                # data = ser.read(data_length).decode().replace("\n", "")
                print(data)
            elif incoming_tag == "INERRUPT_FROM_ESP32":
                data_length = int(ser.readline().decode())
                data = json.loads(ser.read(data_length).decode().replace("\n", ""))
                bitstring = "{0:b}".format(data['shift_register_in']["values"][0])[::-1]
                for idx, val in enumerate(bitstring):
                    if val == "1":
                        leds[idx] = not leds[idx]
                        a = '{"SHIFT_OUT_PIN_VAL": {"pin": ' + str(idx) + ', "val": ' + str(int(leds[idx])) + '}}'
                        ser.write(bytes(a + "\n", 'ascii'))

                print(data)

t = threading.Thread(target=read_from_serial, daemon=True)
t.start()





