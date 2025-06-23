# --- instruction.py ---

class Instruction:
    def __init__(self, raw):
        self.raw = raw.strip()
        self.opcode = None
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.imm = None
        self.type = None
        self.result = None  # Computed result
        self.addr = None    # For memory address
        self.value = None   # For store value
        self.parse()

    def parse(self):
        tokens = self.raw.replace(',', '').split()
        if not tokens:
            return

        self.opcode = tokens[0]

        if self.opcode == 'nop':
            self.type = 'NOP'
            return

        elif self.opcode in ('add', 'sub', 'and', 'or', 'xor', 'slt', 'sltu'):
            self.rd, self.rs1, self.rs2 = tokens[1:4]
            self.type = 'R'

        elif self.opcode == 'addi':
            self.rd, self.rs1, self.imm = tokens[1:4]
            self.type = 'I'

        elif self.opcode == 'lw':
            self.rd = tokens[1]
            offset_base = tokens[2]
            if '(' in offset_base and ')' in offset_base:
                self.imm, self.rs1 = offset_base.replace(')', '').split('(')
                self.type = 'I'
            else:
                raise ValueError(f"Invalid lw format: {self.raw}")

        elif self.opcode == 'sw':
            self.rs2 = tokens[1]
            offset_base = tokens[2]
            if '(' in offset_base and ')' in offset_base:
                self.imm, self.rs1 = offset_base.replace(')', '').split('(')
                self.type = 'S'
            else:
                raise ValueError(f"Invalid sw format: {self.raw}")

        elif self.opcode in ('beq', 'bne'):
            self.rs1, self.rs2, self.imm = tokens[1:4]
            self.type = 'B'

        elif self.opcode == 'jal':
            self.rd, self.imm = tokens[1:3]
            self.type = 'J'

        else:
            raise ValueError(f"Unknown instruction: {self.raw}")

        # Optional: debug print
        # print(f"[PARSE] {self.opcode}: rd={self.rd}, rs1={self.rs1}, rs2={self.rs2}, imm={self.imm}")
