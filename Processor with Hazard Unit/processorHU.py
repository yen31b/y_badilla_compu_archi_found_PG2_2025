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
        self.modules = {"ALU": False, "Memoria": False, "Registros": False}
        self.jump_taken = False # Flag to indicate if a jump/branch was taken in the EX stage of the previous cycle
        self.stalled = False # Flag to track if we are currently stalled due to load-use hazard

    def step(self):
        self.modules = {"ALU": False, "Memoria": False, "Registros": False}

        # Store the PC before the potential increment for the current cycle's fetch
        # This is useful for correct branch target calculation
        pc_at_start_of_cycle = self.pc

        # WB stage
        instr_wb = self.pipeline[4]
        if instr_wb and instr_wb.opcode in ('add', 'addi', 'lw', 'sub', 'and', 'or', 'xor', 'slt', 'sltu', 'jal'):
            if instr_wb.rd:
                print(f"[WB] {instr_wb.rd} = {instr_wb.result}")
                self.regs.write(instr_wb.rd, instr_wb.result)
                self.modules["Registros"] = True

        # MEM stage
        instr_mem = self.pipeline[3]
        if instr_mem:
            if instr_mem.opcode == 'lw':
                instr_mem.result = self.mem.read_word(instr_mem.addr)
                self.modules["Memoria"] = True
            elif instr_mem.opcode == 'sw':
                self.mem.write_word(instr_mem.addr, instr_mem.value)
                print(f"[MEM] Writing {instr_mem.value} to memory at {instr_mem.addr}")
                self.modules["Memoria"] = True

        # EX stage
        instr_ex = self.pipeline[2]
        if instr_ex:
            print(f"[EX] {instr_ex.opcode}: rs1={instr_ex.rs1}, rs2={instr_ex.rs2}, rd={instr_ex.rd}, imm={instr_ex.imm}")
            
            # Use current MEM/WB for forwarding
            fwdA, fwdB = self.forwarding_unit.detect_forwarding(instr_ex, instr_mem, instr_wb) 

            # Operand A
            a = self.regs.read(instr_ex.rs1) if instr_ex.rs1 else 0
            if fwdA == 1: # Forward from EX/MEM
                a = instr_mem.result
            elif fwdA == 2: # Forward from MEM/WB
                a = instr_wb.result

            # Operand B (second ALU input, or immediate where applicable)
            b = 0 # Default value

            if instr_ex.opcode in ('addi', 'lw', 'sw', 'jal'):
                # For these, the immediate is used as the second operand for ALU or address calculation.
                b = int(instr_ex.imm)
            elif instr_ex.rs2: # For R-type and B-type instructions, rs2 is the second operand
                b = self.regs.read(instr_ex.rs2)
                # Apply forwarding for rs2 (b)
                if fwdB == 1: # Forward from EX/MEM
                    b = instr_mem.result
                elif fwdB == 2: # Forward from MEM/WB
                    b = instr_wb.result

            # ALU operations
            if instr_ex.opcode == 'add':
                instr_ex.result = self.alu.operacion_alu('ADD', a, b)
            elif instr_ex.opcode == 'addi':
                instr_ex.result = self.alu.operacion_alu('ADD', a, b)
            elif instr_ex.opcode in ('sub', 'and', 'or', 'xor', 'slt', 'sltu'):
                instr_ex.result = self.alu.operacion_alu(instr_ex.opcode.upper(), a, b)
            elif instr_ex.opcode in ('lw', 'sw'):
                instr_ex.addr = a + b
                if instr_ex.opcode == 'sw':
                    # Forward rs2 value for store
                    # The `b` variable already holds the forwarded value for rs2 in case of sw, but b is the imm for sw.
                    # We need the value of rs2, which is val2 from the branch logic
                    val2_for_sw = self.regs.read(instr_ex.rs2)
                    if fwdB == 1: # Forward from EX/MEM
                        val2_for_sw = instr_mem.result
                    elif fwdB == 2: # Forward from MEM/WB
                        val2_for_sw = instr_wb.result
                    instr_ex.value = val2_for_sw
                    print(f"[EX] Forwarded {instr_ex.rs2} = {instr_ex.value} to store at addr {instr_ex.addr}")
            elif instr_ex.opcode in ('beq', 'bne'):
                val1 = a # Use forwarded value for rs1
                val2 = b # Use forwarded value for rs2
                offset = int(instr_ex.imm)
                condition = (val1 == val2) if instr_ex.opcode == 'beq' else (val1 != val2)
                if condition:
                    # Correct PC for the branch target: (PC of beq at fetch) + offset
                    # When 'beq' (fetched at PC_beq) is in EX stage, self.pc is currently
                    # (PC_beq + 3 * 4) = (PC_beq + 12) if no stalls occurred for beq itself.
                    # So, PC_beq = pc_at_start_of_cycle - 12.
                    # Thus, new PC = (pc_at_start_of_cycle - 12) + offset.
                    self.pc = (pc_at_start_of_cycle - 12) + offset
                    
                    # Ensure the print statement is always there for a taken branch
                    print(f"[EX] Branch taken, new PC = {self.pc}")
                    
                    # Flush IF, ID, EX stages
                    self.pipeline[0] = None # IF flush
                    self.pipeline[1] = None # ID flush
                    self.pipeline[2] = None # EX flush (current instr_ex becomes NOP effectively)
                    self.jump_taken = True

                # else: self.jump_taken remains False, pipeline continues sequentially
            elif instr_ex.opcode == 'jal':
                # Return address is PC of next instruction, which is current self.pc before jal changes it
                instr_ex.result = pc_at_start_of_cycle # This would be the PC of the instruction *after* JAL
                self.pc = (pc_at_start_of_cycle - 4) + int(instr_ex.imm) # Original PC was PC_at_start_of_cycle - 4
                
                # Flush IF, ID, EX
                self.pipeline[0] = None # IF flush
                self.pipeline[1] = None # ID flush
                self.pipeline[2] = None # EX flush (current instr_ex becomes NOP effectively)
                self.jump_taken = True
                print(f"[EX] JAL taken, new PC = {self.pc}, RA = {instr_ex.result}")
            elif instr_ex.opcode == 'nop':
                pass # Do nothing for NOP in EX

            self.modules["ALU"] = True
        
        # ID stage (nothing to do here in terms of execution, just preparation for EX)
        # instr_id = self.pipeline[1]

        # Hazard detection BEFORE advancing pipeline, considering the current ID and EX instructions
        stall_detected_this_cycle = self.hazard_unit.detect_load_use_hazard(self.pipeline[1], self.pipeline[2])

        # Pipeline Advancement
        if self.jump_taken:
            # If a jump was taken in the EX stage, the pipeline has already been flushed.
            # Reset jump_taken for the next cycle. PC is already updated.
            self.jump_taken = False
            # No further pipeline advancement in this specific "jump taken" branch,
            # as flushing effectively created NOPs that will propagate.
            # Fetch for the new PC will happen in the next cycle in the 'else' block
            # of the stall logic.
            self.pipeline[4] = self.pipeline[3] # Propagate MEM to WB (will be NOP if EX was flushed)
            self.pipeline[3] = None # MEM stage is NOP after flush
            # IF, ID, EX are already NOPs from the flush.
            self.stalled = False # Ensure no lingering stall flag interferes

        elif stall_detected_this_cycle:
            # If a new stall is detected, insert a bubble into EX stage,
            # and hold IF and ID stages.
            print(f"[STALL] Load-use hazard detected. Stalling pipeline.")
            self.pipeline[4] = self.pipeline[3] # MEM -> WB
            self.pipeline[3] = self.pipeline[2] # EX -> MEM
            self.pipeline[2] = None             # Bubble in EX
            # IF, ID, PC remain frozen
            self.stalled = True 
        else:
            # Normal pipeline advance or coming out of a stall
            self.pipeline[4] = self.pipeline[3] # MEM -> WB
            self.pipeline[3] = self.pipeline[2] # EX -> MEM
            self.pipeline[2] = self.pipeline[1] # ID -> EX
            self.pipeline[1] = self.pipeline[0] # IF -> ID
            
            # Fetch new instruction and increment PC
            if self.pc // 4 < len(self.instructions):
                fetched_instr = self.instructions[self.pc // 4]
                self.pipeline[0] = fetched_instr
                print(f"[FETCH] PC={self.pc} => {fetched_instr.raw}")
                self.pc += 4
            else:
                self.pipeline[0] = None # No more instructions to fetch
            
            self.stalled = False # Clear stall flag if not stalling this cycle