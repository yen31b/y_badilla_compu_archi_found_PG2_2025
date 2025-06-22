# --- main.py ---
from processor import Processor
import tkinter as tk
import time

program = [
    'addi x1, x0, 5',
    'addi x2, x0, 5',
    'beq x1, x2, 4',
    'nop',
    'addi x3, x0, 99',
    'bne x1, x2, 4',
    'addi x4, x0, 123',
    'jal x5, 4',
    'nop',
    'addi x6, x0, 88',
    'addi x7, x0, 77',
    'sw x3, 0(x0)',         # guardar x3 en memoria
    'lw x8, 0(x0)',         # cargar valor guardado en x3 en x8
    'xor x10, x1, x2',     # x10 = x1 ^ x2
    'and x11, x1, x2',     # x11 = x1 & x2
    'or x12, x1, x2',      # x12 = x1 | x2
    'slt x13, x2, x3',     # x13 = 1 si x2 < x3
    'sltu x14, x2, x3',    # x14 = 1 si x2 < x3 (unsigned)
    'sub x15, x3, x1'      # x15 = x3 - x1
]

cpu = Processor(program)

root = tk.Tk()
root.title("Simulador RISCV - Pipeline")

start_time = time.time()
cycle = 0
running = False

cycle_label = tk.Label(root, text="Ciclo: 0")
cycle_label.pack()

pc_label = tk.Label(root, text="PC: 0")
pc_label.pack()

time_label = tk.Label(root, text="Tiempo transcurrido: 0.00s")
time_label.pack()

pipeline_labels = [tk.Label(root, text=f"{stage}: None") for stage in ['IF', 'ID', 'EX', 'MEM', 'WB']]
for label in pipeline_labels:
    label.pack()

reg_text = tk.Text(root, height=6, width=60)
reg_text.pack()

mem_text = tk.Text(root, height=6, width=60)
mem_text.pack()

log_text = tk.Text(root, height=6, width=60)
log_text.pack()

module_labels = {
    "ALU": tk.Label(root, text="ALU", width=25, bg="lightcoral", relief="solid"),
    "Memoria": tk.Label(root, text="Memoria", width=25, bg="lightcoral", relief="solid"),
    "Registros": tk.Label(root, text="Registros", width=25, bg="lightcoral", relief="solid"),
    "MUX": tk.Label(root, text="MUX", width=25, bg="lightcoral", relief="solid"),
    "SUMADOR": tk.Label(root, text="SUMADOR", width=25, bg="lightcoral", relief="solid")
}

for label in module_labels.values():
    label.pack()

canvas = tk.Canvas(root, width=600, height=150)

canvas.pack()

stage_blocks = {}
stage_positions = [(50, 30), (150, 30), (250, 30), (350, 30), (450, 30)]

for i, name in enumerate(['IF', 'ID', 'EX', 'MEM', 'WB']):
    x, y = stage_positions[i]
    rect_id = canvas.create_rectangle(x, y, x+80, y+60, fill="lightcoral")
    text_id = canvas.create_text(x+40, y+30, text=name)
    stage_blocks[name] = {"rect": rect_id, "canvas": canvas}

def refresh_gui():
    cycle_label.config(text=f"Ciclo: {cycle}")
    pc_label.config(text=f"PC: {cpu.pc}")
    time_label.config(text=f"Tiempo transcurrido: {time.time() - start_time:.2f}s")

    for i, instr in enumerate(cpu.pipeline):
        txt = instr.raw if instr else "None"
        pipeline_labels[i].config(text=f"{['IF', 'ID', 'EX', 'MEM', 'WB'][i]}: {txt}")

    reg_text.delete(1.0, tk.END)
    reg_text.insert(tk.END, "Registros:\n")
    for i in range(0, 32, 4):
        reg_text.insert(tk.END, f"x{i}: {cpu.regs.registers[i]:<4}  x{i+1}: {cpu.regs.registers[i+1]:<4}  x{i+2}: {cpu.regs.registers[i+2]:<4}  x{i+3}: {cpu.regs.registers[i+3]:<4}\n")

    mem_text.delete(1.0, tk.END)
    mem_text.insert(tk.END, "Memoria (todas las celdas):\n")
    for i, val in enumerate(cpu.mem.dump()):
        mem_text.insert(tk.END, f"[{i*4:04}] = {val}\n")


    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Últimos accesos a memoria:\n")
    for action, addr, val in cpu.mem.get_access_log(n=10):
        log_text.insert(tk.END, f"{action} @ {addr} = {val}\n")

    for name, label in module_labels.items():
        color = "lightgreen" if cpu.modules[name] else "lightcoral"
        label.config(bg=color)

    for i, name in enumerate(['IF', 'ID', 'EX', 'MEM', 'WB']):
        instr = cpu.pipeline[i]
        if instr:
            color = "lightblue" if getattr(instr, "type", "") == "NOP" else "lightgreen"
        else:
            color = "lightcoral"
        stage_blocks[name]["canvas"].itemconfig(stage_blocks[name]["rect"], fill=color)

def update():
    global cycle
    cpu.step()
    cycle += 1
    refresh_gui()

def auto_run():
    global running
    if running:
        update()
        root.after(1000, auto_run)

def start_auto():
    global running
    running = True
    auto_run()

def stop_auto():
    global running
    running = False

def run_all():
    while cpu.pc // 4 < len(cpu.instructions) or any(cpu.pipeline):
        update()

def reset():
    global cpu, cycle, start_time
    cpu = Processor(program)
    cycle = 0
    start_time = time.time()
    refresh_gui()

step_btn = tk.Button(root, text="Siguiente ciclo", command=update)
step_btn.pack()

start_btn = tk.Button(root, text="Inicio automático", command=start_auto)
start_btn.pack()

stop_btn = tk.Button(root, text="Detener automático", command=stop_auto)
stop_btn.pack()

run_all_btn = tk.Button(root, text="Ejecutar completo", command=run_all)
run_all_btn.pack()

reset_btn = tk.Button(root, text="Reiniciar", command=reset)
reset_btn.pack()

root.mainloop()
