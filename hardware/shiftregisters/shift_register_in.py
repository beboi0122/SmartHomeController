import json

from observer_pattern.subject import Subject


class ShiftRegisterIn(Subject):
    def __init__(self, latch, data, clock, shift_reg_num):
        super().__init__()
        self.shift_reg_num = shift_reg_num
        self.clock = clock
        self.data = data
        self.latch = latch
        for _ in range(shift_reg_num*8):
            self.observers.append([])

    def add(self, observer, pin):
        self.observers[pin].append(observer)


    def remove(self, observer, pin):
        self.observers[pin].remove(observer)



    def notify(self, pin, val):
        for observer in self.observers[pin]:
            observer.update(["shift_in_"+str(pin), val])

    def update(self, json_in: json):
        # print('call')
        for idx, val in enumerate(json_in['shift_register_in']["values"]):
            bitstring = "{0:08b}".format(val)[::-1]
            for j, val in enumerate(bitstring):
                self.notify((8 * idx) + j, int(val))

