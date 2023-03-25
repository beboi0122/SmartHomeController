import serial
import json

def main():
    ser = serial.Serial(port='/dev/tty.usbserial-0001', baudrate=9600)
    ser.flushInput()
    ser.flushOutput()
    while 1:
        if ser.inWaiting()>0:
            try:
                incoming_tag = ser.readline().decode().replace("\n", "")
            except:
                continue

            if incoming_tag == 'SENSOR_DATA_FROM_ESP32':
                data_length = int(ser.readline().decode())
                #data = json.loads(ser.read(data_length).decode().replace("\n", ""))
                data = ser.read(data_length).decode().replace("\n", "")
                print(data)
            elif incoming_tag == "INERRUPT_FROM_ESP32":
                data_length = int(ser.readline().decode())
                data = ser.read(data_length).decode().replace("\n", "")
                print(data)


if __name__ == '__main__':
    main()