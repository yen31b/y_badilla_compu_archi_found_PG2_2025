from instructionHU import Instruction
from register_fileHU import RegisterFile
from RAMHU import RAM
from ALU import ALU
from forwarding_unit import ForwardingUnit
from hazard_unit import HazardUnit

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
        
        # This dictionary will hold the state of each component for the GUI
        self.modules = {
            "ALU": False,
            "Memoria": False,          # Corresponds to "Data memory" in the GUI
            "Instr_Memoria": False,    # Corresponds to "Instr. memory" in the GUI
            "Registros": False,
            "SUMADOR": False,
            "DECODE": False,
            "IMM": False,
            "PC": False,
            "COMPRESSED_DECODE": False, # Placeholder, not implemented in logic
            "BRANCH": False,
            "mux0_id": False,
            "mux1_id": False,
            "mux_extra_id": False,
            "mux2_id": False,
            "mux_final_id": False
        }
        self.jump_taken = False
        self.stalled = False

    def step(self):
        # --- Reset all module states at the beginning of the cycle ---
        for module in self.modules:
            self.modules[module] = False

        pc_at_start_of_cycle = self.pc

        # --- WB STAGE ---
        instr_wb = self.pipeline[4]
        if instr_wb and instr_wb.opcode in ('add', 'addi', 'lw', 'sub', 'and', 'or', 'xor', 'slt', 'sltu', 'jal'):
            if instr_wb.rd:
                # Register file is being written to
                self.modules["Registros"] = True
                self.regs.write(instr_wb.rd, instr_wb.result)
                print(f"[WB] {instr_wb.rd} = {instr_wb.result}")

                # The final MUX selects between data from memory (for LW) 
                # and data from the ALU result.
                if instr_wb.opcode == 'lw':
                     self.modules["mux_final_id"] = True

        # --- MEM STAGE ---
        instr_mem = self.pipeline[3]
        if instr_mem:
            if instr_mem.opcode == 'lw':
                # Data memory is being read
                self.modules["Memoria"] = True
                instr_mem.result = self.mem.read_word(instr_mem.addr)
            elif instr_mem.opcode == 'sw':
                # Data memory is being written
                self.modules["Memoria"] = True
                self.mem.write_word(instr_mem.addr, instr_mem.value)
                print(f"[MEM] Writing {instr_mem.value} to memory at {instr_mem.addr}")

        # --- EX STAGE ---
        instr_ex = self.pipeline[2]
        if instr_ex:
            print(f"[EX] {instr_ex.opcode}: rs1={instr_ex.rs1}, rs2={instr_ex.rs2}, rd={instr_ex.rd}, imm={instr_ex.imm}")
            self.modules["ALU"] = True # ALU is always conceptually active in EX stage

            fwdA, fwdB = self.forwarding_unit.detect_forwarding(instr_ex, instr_mem, instr_wb)

            if fwdA > 0: self.modules['mux_extra_id'] = True
            if fwdB > 0: self.modules['mux2_id'] = True

            a = self.regs.read(instr_ex.rs1) if instr_ex.rs1 else 0
            if fwdA == 1: a = instr_mem.result
            elif fwdA == 2: a = instr_wb.result

            b = 0
            if instr_ex.opcode in ('addi', 'lw', 'sw', 'jal'):
                b = int(instr_ex.imm)
            elif instr_ex.rs2:
                b = self.regs.read(instr_ex.rs2)
                if fwdB == 1: b = instr_mem.result
                elif fwdB == 2: b = instr_wb.result

            if instr_ex.opcode in ('add', 'addi'):
                instr_ex.result = self.alu.operacion_alu('ADD', a, b)
            elif instr_ex.opcode in ('sub', 'and', 'or', 'xor', 'slt', 'sltu'):
                instr_ex.result = self.alu.operacion_alu(instr_ex.opcode.upper(), a, b)
            elif instr_ex.opcode in ('lw', 'sw'):
                instr_ex.addr = a + b
                if instr_ex.opcode == 'sw':
                    val2_for_sw = self.regs.read(instr_ex.rs2)
                    if fwdB == 1: val2_for_sw = instr_mem.result
                    elif fwdB == 2: val2_for_sw = instr_wb.result
                    instr_ex.value = val2_for_sw
            elif instr_ex.opcode in ('beq', 'bne'):
                self.modules["BRANCH"] = True
                condition = (a == b) if instr_ex.opcode == 'beq' else (a != b)
                if condition:
                    self.modules['mux1_id'] = True
                    # Original, correct branch calculation
                    self.pc = (pc_at_start_of_cycle - 12) + int(instr_ex.imm) 
                    print(f"[EX] Branch taken, new PC = {self.pc}")
                    self.pipeline[0] = None
                    self.pipeline[1] = None
                    self.jump_taken = True
            elif instr_ex.opcode == 'jal':
                self.modules['mux1_id'] = True
                instr_ex.result = pc_at_start_of_cycle # PC of instruction after JAL
                self.pc = (pc_at_start_of_cycle - 4) + int(instr_ex.imm)
                print(f"[EX] JAL taken, new PC = {self.pc}, RA = {instr_ex.result}")
                self.pipeline[0] = None
                self.pipeline[1] = None
                self.jump_taken = True

        # --- ID STAGE ---
        instr_id = self.pipeline[1]
        if instr_id and instr_id.opcode != 'nop' and not self.stalled:
            self.modules['DECODE'] = True
            self.modules['Registros'] = True # Reading from register file
            if instr_id.imm is not None:
                self.modules['IMM'] = True
        
        # --- HAZARD DETECTION ---
        stall_detected_this_cycle = self.hazard_unit.detect_load_use_hazard(self.pipeline[1], self.pipeline[2])

        # --- PIPELINE ADVANCEMENT AND IF STAGE ---
        if self.jump_taken:
            self.jump_taken = False
            self.stalled = False
            self.pipeline[4] = self.pipeline[3]
            self.pipeline[3] = self.pipeline[2]
            self.pipeline[2] = None
        elif stall_detected_this_cycle:
            print("[STALL] Load-use hazard detected. Stalling pipeline.")
            self.pipeline[4] = self.pipeline[3]
            self.pipeline[3] = self.pipeline[2]
            self.pipeline[2] = None
            self.stalled = True
        else:
            self.stalled = False
            self.pipeline[4] = self.pipeline[3]
            self.pipeline[3] = self.pipeline[2]
            self.pipeline[2] = self.pipeline[1]
            self.pipeline[1] = self.pipeline[0]
            
            if self.pc // 4 < len(self.instructions):
                self.modules['PC'] = True
                self.modules['SUMADOR'] = True
                self.modules['mux0_id'] = True
                self.modules['Instr_Memoria'] = True
                fetched_instr = self.instructions[self.pc // 4]
                self.pipeline[0] = fetched_instr
                print(f"[FETCH] PC={self.pc} => {fetched_instr.raw}")
                self.pc += 4
            else:
                self.pipeline[0] = None
