import serial

class SerialInCommunicationHandler:
    def __int__(self):
        pass


def read_serial_in():
    ser = serial.Serial(port='/dev/tty.usbserial-0001', baudrate=9600)
    time.sleep(3)