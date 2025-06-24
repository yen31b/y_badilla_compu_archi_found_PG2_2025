# --- register_file.py ---
class RegisterFile:
    def __init__(self):
        self.registers = [0] * 32

    def read(self, reg):
        idx = self._get_index(reg)
        return self.registers[idx]

    def write(self, reg, value):
        idx = self._get_index(reg)
        if idx != 0:
            self.registers[idx] = value

    def _get_index(self, reg):
        if isinstance(reg, str) and reg.startswith('x'):
            return int(reg[1:])
        elif isinstance(reg, int):
            return reg
        else:
            raise ValueError(f"Invalid register format: {reg}")
