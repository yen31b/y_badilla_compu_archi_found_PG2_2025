from processorHU_BP import Processor  # Importa el procesador con branch prediction

instructions = [
    # Initial Setup: Load some initial values into registers and memory.
    "addi x5, x0, 100",     # x5 = 100
    "addi x6, x0, 200",     # x6 = 200
    "sw   x6, 12(x0)",      # mem[12] = 200

    # --- Test Scenarios ---

    # 1. Baseline (No Hazard)
    "addi x10, x0, 10",     # x10 = 10

    # 2. EX/MEM Forward
    "add  x11, x10, x5",    # x11 = 10 + 100 = 110

    # 3. MEM/WB Forward
    "or   x12, x10, x0",    # x12 = 10 | 0 = 10

    # 4. Double Hazard
    "add  x11, x5, x0",     # x11 = 100 + 0 = 100
    "sub  x11, x6, x5",     # x11 = 200 - 100 = 100
    "xor  x13, x11, x5",    # x13 = 100 ^ 100 = 0

    # 5. Load-Use Hazard
    "lw   x14, 12(x0)",     # x14 = 200
    "slt  x15, x0, x14",    # x15 = (0 < 200) = 1

    # 6. Forward to `sw` data source
    "add  x16, x5, x10",    # x16 = 100 + 10 = 110
    "sw   x16, 16(x0)",     # mem[16] = 110

    # 7. Branch Prediction Test
    "add  x17, x0, x5",     # x17 = 100
    "sub  x18, x6, x5",     # x18 = 200 - 100 = 100
    "beq  x17, x18, 12",    # Branch if 100 == 100. Should jump to "addi x20, x0, 777".
    "addi x19, x0, 999",    # Should be flushed due to branch.
    "addi x19, x0, 999",    # Placeholder instruction to be skipped.
    "addi x20, x0, 777",    # Branch target.
]

processor = Processor(instructions)

print("\n--- PIPELINE SIMULATION WITH BRANCH PREDICTION ---\n")
# Run for enough cycles to allow all instructions to complete,
# plus extra cycles for pipeline drain and potential stalls.
for cycle in range(len(instructions) + 10):  # Extra cycles for branch mispredictions
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
for i in sorted(list(set(regs_to_check))):  # Use set to avoid duplicates and sort for order
    print(f"x{i}: {processor.regs.read(f'x{i}')}")

print("\n--- MEMORY STATE ---")
# Print relevant memory locations that are modified in the tests
print(f"mem[12]: {processor.mem.read_word(12)}")
print(f"mem[16]: {processor.mem.read_word(16)}")