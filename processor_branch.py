from instruction import Instruction
from register_file import RegisterFile
from RAM import RAM
from ALU import ALU
from components import MUX, Sumador

class BranchPredictionProcessor:
    def __init__(self, instructions):
        self.pc = 0
        self.instructions = [Instruction(line) for line in instructions]
        self.regs = RegisterFile()
        self.mem = RAM(1024)
        self.alu = ALU()
        self.pipeline = [None] * 5
        self.jump_taken = False
        self.flush_next = False
        self.mux = MUX()
        self.sumador = Sumador()
        self.branch_history = []
        self.branch_predictor = {}  # predicción 1-bit por dirección

        self.modules = {
            "ALU": False, "Memoria": False, "Registros": False, "MUX": False,
            "SUMADOR": False, "DECODE": False, "IMM": False, "PC": False,
            "COMPRESSED_DECODE": False, "BRANCH": False,
            "mux0_id": False, "mux1_id": False, "mux_extra_id": False,
            "mux2_id": False, "mux_final_id": False
        }

    def step(self):
        self.modules = {k: False for k in self.modules}
        self.jump_taken = False

        # Flush por mala predicción
        if self.flush_next:
            self.pipeline[0] = None  # IF
            self.pipeline[1] = None  # ID
            self.flush_next = False

        current_pc = self.pc
        instr = None
        if current_pc // 4 < len(self.instructions):
            instr = self.instructions[current_pc // 4]
            self.modules["PC"] = True
            self.modules["COMPRESSED_DECODE"] = True

        # --- Predicción dinámica 1-bit ---
        predicted_jump = False
        target_pc = current_pc + 4  # default
        if instr and instr.opcode in ('beq', 'bne', 'jal'):
            pred = self.branch_predictor.get(current_pc, False)  # default: no se toma
            predicted_jump = pred
            if pred:
                if instr.opcode == 'jal':
                    target_pc = current_pc + int(instr.imm)
                else:
                    target_pc = current_pc + int(instr.imm)

        # Guardar predicción
        predicted_pc = target_pc if predicted_jump else self.sumador.sumar(current_pc, 4)
        self.modules["SUMADOR"] = True
        self.modules["mux0_id"] = True

        # Avanza pipeline
        self.pipeline[4] = self.pipeline[3]
        self.pipeline[3] = self.pipeline[2]
        self.pipeline[2] = self.pipeline[1]
        self.pipeline[1] = self.pipeline[0]
        self.pipeline[0] = instr

        # WB
        wb = self.pipeline[4]
        if wb and wb.opcode in ('add', 'addi', 'lw', 'sub', 'and', 'or', 'xor', 'slt', 'sltu'):
            self.regs.write(wb.rd, wb.result)
            self.modules["Registros"] = True
            self.modules["mux_final_id"] = True

        # MEM
        mem = self.pipeline[3]
        if mem:
            if mem.opcode == 'lw':
                mem.result = self.mem.read_word(mem.addr)
                self.modules["Memoria"] = True
            elif mem.opcode == 'sw':
                self.mem.write_word(mem.addr, mem.value)
                self.modules["Memoria"] = True

        # EX
        ex = self.pipeline[2]
        if ex:
            self.modules["ALU"] = True
            if ex.opcode in ('add', 'sub', 'and', 'or', 'xor', 'slt', 'sltu'):
                a = self.regs.read(ex.rs1)
                b = self.regs.read(ex.rs2)
                ex.result = self.alu.operacion_alu(ex.opcode.upper(), a, b)
            elif ex.opcode == 'addi':
                a = self.regs.read(ex.rs1)
                b = int(ex.imm)
                ex.result = self.alu.operacion_alu('ADD', a, b)
                self.modules["mux2_id"] = True
            elif ex.opcode in ('lw', 'sw'):
                ex.addr = self.regs.read(ex.rs1) + int(ex.imm)
                if ex.opcode == 'sw':
                    ex.value = self.regs.read(ex.rs2)
            elif ex.opcode in ('beq', 'bne'):
                val1 = self.regs.read(ex.rs1)
                val2 = self.regs.read(ex.rs2)
                offset = int(ex.imm)
                taken = (val1 == val2) if ex.opcode == 'beq' else (val1 != val2)
                actual_pc = current_pc + offset if taken else current_pc + 4
                pred = self.branch_predictor.get(current_pc, False)

                print(f"[DEBUG] PC={current_pc} | {ex.opcode} | rs1={ex.rs1}({val1}) vs rs2={ex.rs2}({val2}) | imm={offset} | pred={pred} | taken={taken}")

                self.modules["BRANCH"] = True
                self.modules["mux1_id"] = True

                if pred != taken:
                    self.pc = actual_pc
                    self.flush_next = True
                    self.jump_taken = True
                    self.branch_history.append((current_pc, "MAL PREDICHO"))
                else:
                    self.branch_history.append((current_pc, "BIEN PREDICHO"))
                self.branch_predictor[current_pc] = taken

            elif ex.opcode == 'jal':
                self.regs.write(ex.rd, predicted_pc)
                actual_pc = current_pc + int(ex.imm)
                pred = self.branch_predictor.get(current_pc, False)
                self.modules["mux1_id"] = True
                if pred != True:
                    self.pc = actual_pc
                    self.flush_next = True
                    self.jump_taken = True
                    self.branch_history.append((current_pc, "MAL PREDICHO"))
                else:
                    self.branch_history.append((current_pc, "BIEN PREDICHO"))
                self.branch_predictor[current_pc] = True

        # ID
        id_instr = self.pipeline[1]
        if id_instr:
            self.modules["DECODE"] = True
            if id_instr.imm is not None:
                self.modules["IMM"] = True

        if not self.jump_taken:
            self.pc = predicted_pc
