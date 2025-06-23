from processorHU import Processor

instructions = [
    # Initial Setup: Load some initial values into registers and memory.
    "addi x5, x0, 100",     # x5 = 100
    "addi x6, x0, 200",     # x6 = 200
    "sw   x6, 12(x0)",      # mem[12] = 200

    # --- Test Scenarios ---

    # 1. Baseline (No Hazard)
    "addi x10, x0, 10",     # x10 = 10

    # 2. EX/MEM Forward
    # The 'add' needs x10 from the 'addi' immediately before it.
    # Expected: Forward from EX/MEM. add x11, x10, x5 -> x11 = 10 + 100 = 110
    "add  x11, x10, x5",

    # 3. MEM/WB Forward
    # The 'or' needs x10 from two instructions ago.
    # Expected: Forward from MEM/WB. or x12, x10, x0 -> x12 = 10 | 0 = 10
    "or   x12, x10, x0",

    # 4. Double Hazard (EX/MEM takes priority - assuming forwarding_unit fix)
    # 'add' produces x11 = 100. 'sub' produces x11 = 100.
    # The 'xor' needs x11. It should use the result from 'sub' (100) from EX/MEM, not 'add' (100) from MEM/WB.
    "add  x11, x5, x0",     # x11 = 100 + 0 = 100 (This will be in MEM stage when xor is in ID)
    "sub  x11, x6, x5",     # x11 = 200 - 100 = 100 (This will be in EX stage when xor is in ID, should be used)
    "xor  x13, x11, x5",    # Expected: Forward from EX/MEM. xor x13, x11, x5 -> x13 = 100 ^ 100 = 0

    # 5. Load-Use Hazard (Stall and Forward)
    # 'lw' loads a value into x14. The very next instruction 'slt' uses x14.
    # Expected: The pipeline must stall for one cycle.
    # Then, the value from memory (200) is forwarded from the MEM/WB path.
    "lw   x14, 12(x0)",     # Load value from mem[12] into x14. x14 = 200 (set by initial sw)
    "slt  x15, x0, x14",    # Expected: x15 = (0 < 200) = 1

    # 6. Forward to `sw` data source (rs2)
    # The 'sw' needs the result of 'add' (x16) to store into memory.
    # Expected: Forward from EX/MEM.
    "add  x16, x5, x10",    # x16 = 100 + 10 = 110
    "sw   x16, 16(x0)",     # Store x16 (110) into mem[16].

    # 7. Forward to `beq` sources and Branch Hazard
    # The 'beq' needs the results from the 'add' (x17) and 'sub' (x18).
    # Expected: Forward x17 from MEM/WB, forward x18 from EX/MEM. Branch should be taken.
    "add  x17, x0, x5",     # x17 = 100
    "sub  x18, x6, x5",     # x18 = 200 - 100 = 100
    "beq  x17, x18, 12",    # Branch if 100 == 100. Should jump over the next 3 instructions (4*3 = 12 bytes).
                            # The branch target is the instruction at PC + 12 (i.e., 'addi x20, x0, 777').
    "addi x19, x0, 999",    # This instruction should be flushed and never executed.
    "addi x19, x0, 999",    # Placeholder instruction to be skipped
    "addi x20, x0, 777",    # This is the branch target.
]

processor = Processor(instructions)
# Initialize memory as some of the tests read from it
# mem[12] will be written by the 'sw x6, 12(x0)' at the start of instructions.
# You can pre-load it for robustness, but the test case itself populates it.
# processor.mem.load_from_list([0] * (16 // 4) + [200], base_address=0) # ensure mem[12] exists and can be written

print("\n--- PIPELINE SIMULATION ---\n")
# Run for enough cycles to allow all instructions to complete,
# plus extra cycles for pipeline drain and potential stalls.
# A safe number would be len(instructions) + number_of_pipeline_stages + max_stalls.
# Max stalls for load-use is 1. Max pipeline stages is 4 after fetch.
# A general rule of thumb is len(instructions) + 5 stages.
for cycle in range(len(instructions) + 10): # Added more cycles for complex hazards and branch
    print(f"Cycle {cycle}")
    for i, stage in enumerate(["IF", "ID", "EX", "MEM", "WB"]):
        instr = processor.pipeline[i]
        name = instr.opcode if instr else "NOP"
        print(f"Stage {i} ({stage}): {name}")
    print()
    processor.step()

print("\n--- REGISTER STATE ---")
# Print relevant registers that are modified in the tests
regs_to_check = [0, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
for i in sorted(list(set(regs_to_check))): # Use set to avoid duplicates and sort for order
    print(f"x{i}: {processor.regs.read(f'x{i}')}")

print("\n--- MEMORY STATE ---")
# Print relevant memory locations that are modified in the tests
print(f"mem[12]: {processor.mem.read_word(12)}")
print(f"mem[16]: {processor.mem.read_word(16)}")