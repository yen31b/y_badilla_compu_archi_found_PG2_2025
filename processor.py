# --- processor.py ---
from instruction import Instruction
from register_file import RegisterFile
from RAM import RAM
from ALU import ALU  # nueva ALU orientada a objetos
from components import MUX, Sumador

class Processor:
    def __init__(self, instructions):
        self.pc = 0
        self.instructions = [Instruction(line) for line in instructions]
        self.regs = RegisterFile()
        self.mem = RAM(1024)
        self.alu = ALU()  # instancia de la ALU
        self.pipeline = [None] * 5  # IF, ID, EX, MEM, WB
        self.modules = {"ALU": False, "Memoria": False, "Registros": False, "MUX": False,"SUMADOR": False}
        self.jump_taken = False
        self.mux = MUX()
        self.sumador = Sumador()

    def step(self):
        self.modules = {"ALU": False, "Memoria": False, "Registros": False}
        self.jump_taken = False

        if self.pc // 4 < len(self.instructions):
            fetched_instr = self.instructions[self.pc // 4]
        else:
            fetched_instr = None

        self.pipeline[4] = self.pipeline[3]
        self.pipeline[3] = self.pipeline[2]
        self.pipeline[2] = self.pipeline[1]
        self.pipeline[1] = self.pipeline[0]

        # WB
        instr = self.pipeline[4]
        if instr and instr.opcode in ('add', 'addi', 'lw', 'sub', 'and', 'or', 'xor', 'slt', 'sltu'):
            self.regs.write(instr.rd, instr.result)
            self.modules["Registros"] = True

        # MEM
        instr = self.pipeline[3]
        if instr:
            if instr.opcode == 'lw':
                addr = instr.addr
                instr.result = self.mem.read_word(addr)
                self.modules["Memoria"] = True
            elif instr.opcode == 'sw':
                self.mem.write_word(instr.addr, instr.value)
                self.modules["Memoria"] = True

        # EX
        instr = self.pipeline[2]
        if instr:
            if instr.opcode == 'add':
                a = self.regs.read(instr.rs1)
                b = self.regs.read(instr.rs2)
                instr.result = self.alu.operacion_alu('ADD', a, b)
                self.modules["ALU"] = True
            elif instr.opcode == 'addi':
                a = self.regs.read(instr.rs1)
                b = self.mux.select(1, self.regs.read('x0'), int(instr.imm))  # mux ficticio: ignora 'x0', devuelve imm
                instr.result = self.alu.operacion_alu('ADD', a, b)
                self.modules["ALU"] = True
                self.modules["MUX"] = True

            elif instr.opcode in ('sub', 'and', 'or', 'xor', 'slt', 'sltu'):
                a = self.regs.read(instr.rs1)
                b = self.regs.read(instr.rs2)
                instr.result = self.alu.operacion_alu(instr.opcode.upper(), a, b)
                self.modules["ALU"] = True
            elif instr.opcode in ('lw', 'sw'):
                instr.addr = self.regs.read(instr.rs1) + int(instr.imm)
                if instr.opcode == 'sw':
                    instr.value = self.regs.read(instr.rs2)
                self.modules["ALU"] = True
            elif instr.opcode in ('beq', 'bne'):
                val1 = self.regs.read(instr.rs1)
                val2 = self.regs.read(instr.rs2)
                offset = int(instr.imm)
                condition = (val1 == val2) if instr.opcode == 'beq' else (val1 != val2)
                if condition:
                    self.pc += offset - 4
                    self.jump_taken = True
            elif instr.opcode == 'jal':
                self.regs.write(instr.rd, self.pc)
                self.pc += int(instr.imm) - 4
                self.jump_taken = True

        instr = self.pipeline[1]
        # No hazard handling

        if not self.jump_taken:
            self.pc = self.sumador.sumar(self.pc, 4)
            self.modules["SUMADOR"] = True


        self.pipeline[0] = fetched_instr
