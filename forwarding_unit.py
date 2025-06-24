# --- forwarding_unit.py ---
class ForwardingUnit:
    def detect_forwarding(self, id_ex, ex_mem, mem_wb):
        forwardA = 0
        forwardB = 0

        # Prioritize EX/MEM forwarding (forwardA = 1, forwardB = 1)
        if ex_mem and ex_mem.opcode != 'sw' and ex_mem.rd:
            # Check for rs1
            if ex_mem.rd == id_ex.rs1:
                # Do NOT forward from LW if result not ready (still in EX)
                if ex_mem.opcode != 'lw':
                    forwardA = 1
            # Check for rs2
            if ex_mem.rd == id_ex.rs2:
                # Do NOT forward from LW if result not ready (still in EX)
                if ex_mem.opcode != 'lw':
                    forwardB = 1

        # Check for MEM/WB forwarding (forwardA = 2, forwardB = 2)
        # Only apply if EX/MEM forwarding wasn't already set for that operand
        if mem_wb and mem_wb.opcode != 'sw' and mem_wb.rd:
            # Check for rs1
            if mem_wb.rd == id_ex.rs1:
                if forwardA == 0:  # Only set if not already forwarded from EX/MEM
                    forwardA = 2
            # Check for rs2
            if mem_wb.rd == id_ex.rs2:
                if forwardB == 0:  # Only set if not already forwarded from EX/MEM
                    forwardB = 2

        return forwardA, forwardB

