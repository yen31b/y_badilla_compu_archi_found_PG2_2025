# --- hazard_unit.py ---

class HazardUnit:
    def __init__(self):
        pass

    def detect_load_use_hazard(self, id_instr, ex_instr):
        if not id_instr or not ex_instr:
            return False
        if ex_instr.opcode == 'lw' and ex_instr.rd:
            return (
                ex_instr.rd == id_instr.rs1 or
                ex_instr.rd == id_instr.rs2
            )
        return False
