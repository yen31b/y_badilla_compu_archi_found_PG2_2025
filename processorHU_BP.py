from instructionHU import Instruction
from register_fileHU import RegisterFile
from RAMHU import RAM
from ALU import ALU
from forwarding_unit import ForwardingUnit
from hazard_unit import HazardUnit
from branch_predictor import branch_predictor_2_bit  # Import the branch predictor

class Processor:
    def __init__(self, instructions):
        self.pc = 0
        self.instructions = [Instruction(line) for line in instructions]
        self.regs = RegisterFile()
        self.mem = RAM(1024)
        self.alu = ALU()
        self.forwarding_unit = ForwardingUnit()
        self.hazard_unit = HazardUnit()
        self.pipeline = [None] * 5  # IF, ID, EX, MEM, WB
        self.modules = {  # GUI state
            "ALU": False, "Memoria": False, "Instr_Memoria": False, "Registros": False,
            "SUMADOR": False, "DECODE": False, "IMM": False, "PC": False, "BRANCH": False,
            "mux0_id": False, "mux1_id": False, "mux_extra_id": False, "mux2_id": False,
            "mux_final_id": False
        }
        self.jump_taken = False
        self.stalled = False
        self.branch_predictor = branch_predictor_2_bit()  # Predictor de 2 bits

    def step(self):
        # Reset module states
        for module in self.modules:
            self.modules[module] = False

        pc_at_start_of_cycle = self.pc

        # --- WB STAGE ---
        instr_wb = self.pipeline[4]
        if instr_wb and instr_wb.opcode in ('add', 'addi', 'lw', 'sub', 'and', 'or', 'xor', 'slt', 'sltu', 'jal'):
            if instr_wb.rd:
                self.modules["Registros"] = True
                self.regs.write(instr_wb.rd, instr_wb.result)
                print(f"[WB] {instr_wb.rd} = {instr_wb.result}")

                if instr_wb.opcode == 'lw':
                    self.modules["mux_final_id"] = True

        # --- MEM STAGE ---
        instr_mem = self.pipeline[3]
        if instr_mem:
            if instr_mem.opcode == 'lw':
                self.modules["Memoria"] = True
                instr_mem.result = self.mem.read_word(instr_mem.addr)
                print(f"[MEM] Loaded {instr_mem.result} from mem[{instr_mem.addr}]")
            elif instr_mem.opcode == 'sw':
                self.modules["Memoria"] = True
                self.mem.write_word(instr_mem.addr, instr_mem.value)
                print(f"[MEM] Stored {instr_mem.value} to mem[{instr_mem.addr}]")

        # --- EX STAGE ---
        instr_ex = self.pipeline[2]
        if instr_ex:
            self.modules["ALU"] = True
            fwdA, fwdB = self.forwarding_unit.detect_forwarding(instr_ex, instr_mem, instr_wb)

            a = self.regs.read(instr_ex.rs1) if instr_ex.rs1 else 0
            if fwdA == 1: a = instr_mem.result
            elif fwdA == 2: a = instr_wb.result

            b = int(instr_ex.imm) if instr_ex.opcode in ('addi', 'lw', 'sw', 'jal') else self.regs.read(instr_ex.rs2)
            if fwdB == 1: b = instr_mem.result
            elif fwdB == 2: b = instr_wb.result

            if instr_ex.opcode in ('add', 'addi'):
                instr_ex.result = self.alu.operacion_alu('ADD', a, b)
                print(f"[EX] {instr_ex.opcode} result: {instr_ex.result}")
            elif instr_ex.opcode in ('sub', 'and', 'or', 'xor', 'slt', 'sltu'):
                instr_ex.result = self.alu.operacion_alu(instr_ex.opcode.upper(), a, b)
                print(f"[EX] {instr_ex.opcode} result: {instr_ex.result}")
            elif instr_ex.opcode in ('beq', 'bne'):
                self.modules["BRANCH"] = True
                condition = (a == b) if instr_ex.opcode == 'beq' else (a != b)
                actual_taken = condition
                predicted_taken = self.branch_predictor.predict(pc_at_start_of_cycle)
                self.branch_predictor.update(pc_at_start_of_cycle, actual_taken)
                print(f"[EX] Branch {instr_ex.opcode}: predicted {predicted_taken}, actual {actual_taken}")
                if actual_taken != predicted_taken:
                    # Flush IF and ID stages
                    self.pipeline[0] = None
                    self.pipeline[1] = None
                    # Update PC to branch target or next sequential instruction
                    self.pc = instr_ex.branch_target() if actual_taken else pc_at_start_of_cycle + 4
                    return
            elif instr_ex.opcode == 'jal':
                self.modules['mux1_id'] = True
                instr_ex.result = pc_at_start_of_cycle
                self.pc = (pc_at_start_of_cycle - 4) + int(instr_ex.imm)
                self.pipeline[0] = None
                self.pipeline[1] = None
                self.jump_taken = True

        # --- ID STAGE ---
        instr_id = self.pipeline[1]
        if instr_id and instr_id.opcode != 'nop' and not self.stalled:
            self.modules['DECODE'] = True
            self.modules['Registros'] = True
            if instr_id.imm is not None:
                self.modules['IMM'] = True

        # --- FETCH STAGE ---
        if self.pc // 4 < len(self.instructions):
            fetched_instr = self.instructions[self.pc // 4]
            if fetched_instr.opcode in ('beq', 'bne'):
                prediction = self.branch_predictor.predict(self.pc)
                self.pc = fetched_instr.branch_target() if prediction else self.pc + 4
            self.pipeline[0] = fetched_instr
        else:
            self.pipeline[0] = None

        # Advance pipeline
        self.pipeline[4] = self.pipeline[3]
        self.pipeline[3] = self.pipeline[2]
        self.pipeline[2] = self.pipeline[1]
        self.pipeline[1] = self.pipeline[0]