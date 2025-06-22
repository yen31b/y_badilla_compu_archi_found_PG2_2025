# --- components.py ---
from instruction import Instruction


class MUX:
    def select(self, sel, a, b):
        return a if sel == 0 else b

class Sumador:
    def sumar(self, a, b):
        return (a + b) & 0xFFFFFFFF  # resultado de 32 bits
    
class Decoder:
    def decode(self, instr_text):
        return Instruction(instr_text)  # ya implementado

class ImmediateGenerator:
    def generate(self, instr):
        if instr.imm is None:
            return 0
        return int(instr.imm)