from globals import serial_out_buffer


class ShiftRegisterOut:
    def __init__(self, latch, data, clock, shift_reg_num):
        self.shift_reg_num = shift_reg_num
        self.clock = clock
        self.data = data
        self.latch = latch

    def write_all_zero(self):
        for i in range(self.shift_reg_num):
            for j in range(8):
                serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                         + str((i*8)+j)
                                         + ", 'val': "
                                         + str(0)
                                         + "}}")
    def write_all_one(self):
        for i in range(self.shift_reg_num):
            for j in range(8):
                serial_out_buffer.append("{'SHIFT_OUT_PIN_VAL': {'pin': "
                                         + str((i*8)+j)
                                         + ", 'val': "
                                         + str(1)
                                         + "}}")