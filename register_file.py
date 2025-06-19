class RegisterFile:
    def __init__(self):
        self.registers = [0] * 32

    def read(self, reg):
        idx = int(reg[1:])
        return self.registers[idx]

    def write(self, reg, value):
        idx = int(reg[1:])
        if idx != 0:
            self.registers[idx] = value