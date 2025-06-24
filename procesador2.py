import tkinter as tk
import time
# Import the updated processor with hazard unit logic
from processorHU import Processor

def crear_procesador2(parent_frame, modo):
    program = [
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

    # Use the imported Processor
    cpu = Processor(program)
    start_time = time.time()
    cycle = [0]
    running = [False]

    main_frame = tk.Frame(parent_frame)
    main_frame.pack()

    # --- GUI Setup (Register, Memory, Log text boxes) ---
    info_frame = tk.Frame(main_frame)
    info_frame.grid(row=0, column=1, rowspan=4, sticky="ns", padx=5, pady=5)
    
    reg_text = tk.Text(info_frame, height=10, width=45, bg="#e0f7fa", relief="solid", borderwidth=1)
    reg_text.pack(pady=2)
    mem_text = tk.Text(info_frame, height=10, width=45, bg="#e0f7fa", relief="solid", borderwidth=1)
    mem_text.pack(pady=2)
    log_text = tk.Text(info_frame, height=10, width=45, bg="#e0f7fa", relief="solid", borderwidth=1)
    log_text.pack(pady=2)
    
    # --- Canvas for Processor Diagram ---
    canvas_w, canvas_h = 1500, 500
    canvas = tk.Canvas(main_frame, width=canvas_w, height=canvas_h, bg="#f0f8ff")
    canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

    # --- Status Labels ---
    status_frame = tk.Frame(main_frame)
    status_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="ew")
    cycle_label = tk.Label(status_frame, text="Cycle: 0", fg="#00796b", font=("Arial", 10))
    cycle_label.pack(side=tk.LEFT, padx=10)
    pc_label = tk.Label(status_frame, text="PC: 0", fg="#00796b", font=("Arial", 10))
    pc_label.pack(side=tk.LEFT, padx=10)
    time_label = tk.Label(status_frame, text="Time: 0.00s", fg="#00796b", font=("Arial", 10))
    time_label.pack(side=tk.LEFT, padx=10)

    # Coordinates for all graphical components
    coords = {
        "PC": (150, 210, 220, 240),
        "Instr. memory": (270, 160, 420, 240),
        "Compressed decode": (270, 270, 420, 300),
        "IF/ID": (440, 108, 470, 420),
        "Decode": (530, 210, 590, 300),
        "Registers": (660, 160, 800, 260),
        "Imm": (687, 270, 720, 330),
        "ID/EX": (820, 108, 850, 420),
        "ALU": (935, 160, 1035, 260),
        "Branch": (915, 315, 1000, 340),
        "EX/MEM": (1060, 108, 1090, 420),
        "Data memory": (1130, 190, 1240, 260),
        "MEM/WB": (1280, 108, 1310, 420)
    }

    # --- Draw all components on the canvas ---
    block_ids = {}

    # Helper function for drawing a MUX
    def draw_mux(x, y, w=28, h=22):
        points = [x, y, x + w, y + h // 4, x + w, y + 3 * h // 4, x, y + h]
        return canvas.create_polygon(points, fill="#b2ebf2", outline="#0097a7", width=2)

    # Helper function for drawing the ALU
    def draw_alu(x, y, w=100, h=70):
        points = [x, y + h*0.2, x + w*0.3, y, x + w, y + h*0.3, x + w, y + h*0.7, x + w*0.3, y + h, x, y + h*0.8]
        return canvas.create_polygon(points, fill="#b2ebf2", outline="#0097a7", width=2)
    
    # Draw standard rectangular blocks
    for name, (x1, y1, x2, y2) in coords.items():
        if name != "ALU":
             fill_color = "#FFFFFF" if "/" in name else "#b2ebf2"
             block_ids[name] = canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="#0097a7", width=2)
             text = name.replace("/", "/\n") if "/" in name else name
             canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, font=("Arial", 9, "bold"), fill="#00796b")

    # Draw special shapes and add them to block_ids
    block_ids["ALU"] = draw_alu(coords["ALU"][0], coords["ALU"][1], coords["ALU"][2]-coords["ALU"][0], coords["ALU"][3]-coords["ALU"][1])
    canvas.create_text(coords["ALU"][0]+50, coords["ALU"][1]+35, text="ALU", font=("Arial", 11, "bold"), fill="#00796b")
    
    block_ids["SUMADOR"] = draw_mux(235, 110, w=20, h=30)
    canvas.create_text(245, 100, text="ADD", font=("Arial", 7, "bold"))

    block_ids["mux0_id"] = draw_mux(171, 104, w=20, h=30)
    block_ids["mux1_id"] = draw_mux(115, 210, w=20, h=30)
    block_ids["mux_extra_id"] = draw_mux(880, 163, w=20, h=30) # ALU operand 1 MUX
    block_ids["mux2_id"] = draw_mux(880, 230, w=20, h=30)      # ALU operand 2 MUX
    block_ids["mux_final_id"] = draw_mux(1380, 160, w=20, h=50) # WB MUX

    # Draw connecting lines (datapath) - purely visual
    # (Lines are omitted for brevity, but would be drawn here)

    # --- Control Buttons ---
    control_frame = tk.Frame(info_frame)
    control_frame.pack(pady=20)
    step_btn = tk.Button(control_frame, text="Next Cycle", command=lambda: update())
    step_btn.pack(fill=tk.X)
    start_btn = tk.Button(control_frame, text="Auto-Run", command=lambda: start_auto())
    start_btn.pack(fill=tk.X)
    stop_btn = tk.Button(control_frame, text="Stop", command=lambda: stop_auto())
    stop_btn.pack(fill=tk.X)
    run_all_btn = tk.Button(control_frame, text="Run All", command=lambda: run_all())
    run_all_btn.pack(fill=tk.X)
    reset_btn = tk.Button(control_frame, text="Reset", command=lambda: reset())
    reset_btn.pack(fill=tk.X)
        
    def refresh_gui():
        # Update labels
        cycle_label.config(text=f"Cycle: {cycle[0]}")
        pc_label.config(text=f"PC: {cpu.pc}")
        time_label.config(text=f"Time: {time.time() - start_time:.2f}s")

        # Update Register display
        reg_text.delete(1.0, tk.END)
        reg_text.insert(tk.END, "--- Registers ---\n")
        for i in range(0, 32, 4):
            line = f"x{i:02}:{cpu.regs.registers[i]:<5} x{i+1:02}:{cpu.regs.registers[i+1]:<5} x{i+2:02}:{cpu.regs.registers[i+2]:<5} x{i+3:02}:{cpu.regs.registers[i+3]:<5}\n"
            reg_text.insert(tk.END, line)

        # Update Memory and Log displays
        mem_text.delete(1.0, tk.END)
        mem_text.insert(tk.END, "--- Data Memory ---\n")
        # Only show first 16 memory locations for brevity
        for i in range(0, 16*4, 4):
             mem_text.insert(tk.END, f"[{i:03}]: {cpu.mem.read_word(i)}\n")
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "--- Memory Access Log ---\n")
        for action, addr, val in cpu.mem.get_access_log(n=10):
            log_text.insert(tk.END, f"{action} @ {addr} = {val}\n")

        # --- UPDATE COMPONENT COLORS ---
        # First, reset all component colors to default
        for name, block_id in block_ids.items():
            fill_color = "#FFFFFF" if "/" in name else "#b2ebf2"
            canvas.itemconfig(block_id, fill=fill_color)
        
        # Then, highlight active components based on the cpu.modules dictionary
        if hasattr(cpu, "modules"):
            for name, is_active in cpu.modules.items():
                gui_name = name # Default name
                # Map logic names to GUI names if they differ
                if name == "Memoria": gui_name = "Data memory"
                if name == "Instr_Memoria": gui_name = "Instr. memory"

                if is_active and gui_name in block_ids:
                    canvas.itemconfig(block_ids[gui_name], fill="#FFD700") # Gold for active

        # --- Display instruction in each stage ---
        # FIX: Moved the cleanup logic here, inside the function.
        if hasattr(refresh_gui, "stage_text_ids"):
            for tid in refresh_gui.stage_text_ids:
                canvas.delete(tid)
        refresh_gui.stage_text_ids = []

        stage_coords = [(345, 150), (640, 150), (950, 150), (1185, 180), (1350, 150)]
        stage_names = ["IF", "ID", "EX", "MEM", "WB"]
        for i, instr in enumerate(cpu.pipeline):
            text = f"[{stage_names[i]}] {instr.raw if instr else '---'}"
            if i == 2 and cpu.stalled: text = "[STALL]"
            
            x, y = stage_coords[i]
            tid = canvas.create_text(x, y - 80, text=text, font=("Arial", 9, "italic"), fill="#c62828", anchor="n")
            refresh_gui.stage_text_ids.append(tid)

    # --- Control Functions ---
    def update():
        cpu.step()
        cycle[0] += 1
        refresh_gui()

    def auto_run():
        if running[0]:
            update()
            main_frame.after(500, auto_run) # 500ms delay for visibility

    def start_auto():
        if not running[0]:
            running[0] = True
            auto_run()

    def stop_auto():
        running[0] = False

    def run_all():
        stop_auto()
        while cpu.pc // 4 < len(cpu.instructions) or any(cpu.pipeline):
            update()

    def reset():
        nonlocal cpu, start_time
        stop_auto()
        cpu = Processor(program)
        cycle[0] = 0
        start_time = time.time()
        refresh_gui()

    refresh_gui() # Initial Draw
