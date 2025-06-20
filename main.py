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
    'sw x3, 0(x0)',
    'lw x8, 0(x0)',
    'xor x10, x1, x2',
    'and x11, x1, x2',
    'or x12, x1, x2',
    'slt x13, x2, x3',
    'sltu x14, x2, x3',
    'sub x15, x3, x1'
]

cpu = Processor(program)  

root = tk.Tk() 
root.title("Simulador RISCV - Pipeline")

start_time = time.time()  
cycle = 0                # Contador de ciclos
running = False          # Bandera para ejecución automática

# --- Layout principal ---
main_frame = tk.Frame(root)  # Frame principal para organizar widgets
main_frame.pack()

# --- Paneles de texto a la derecha ---
reg_text = tk.Text(main_frame, height=8, width=37)  # Muestra los registros
reg_text.grid(row=0, column=1, padx=5, pady=2)
mem_text = tk.Text(main_frame, height=8, width=37)  # Muestra la memoria
mem_text.grid(row=1, column=1, padx=5, pady=2)
log_text = tk.Text(main_frame, height=8, width=37)  # Muestra el log de accesos a memoria
log_text.grid(row=2, column=1, padx=5, pady=2)

# --- Labels de estado ---
status_frame = tk.Frame(root)  
status_frame.pack()
cycle_label = tk.Label(status_frame, text="Ciclo: 0")  # Muestra el ciclo actual
cycle_label.pack(side=tk.LEFT, padx=8)
pc_label = tk.Label(status_frame, text="PC: 0")        # Muestra el valor del PC
pc_label.pack(side=tk.LEFT, padx=8)
time_label = tk.Label(status_frame, text="Tiempo transcurrido: 0.00s")  # Muestra el tiempo
time_label.pack(side=tk.LEFT, padx=8)

# --- Botones de control ---
btn_frame = tk.Frame(root)  #
btn_frame.pack(pady=10)
step_btn = tk.Button(btn_frame, text="Siguiente ciclo", width=16)     
start_btn = tk.Button(btn_frame, text="Inicio automático", width=16)   
stop_btn = tk.Button(btn_frame, text="Detener automático", width=16)   
run_all_btn = tk.Button(btn_frame, text="Ejecutar completo", width=16)
reset_btn = tk.Button(btn_frame, text="Reiniciar", width=16)         

step_btn.pack(side=tk.LEFT, padx=5)
start_btn.pack(side=tk.LEFT, padx=5)
stop_btn.pack(side=tk.LEFT, padx=5)
run_all_btn.pack(side=tk.LEFT, padx=5)
reset_btn.pack(side=tk.LEFT, padx=5)

# --- Canvas---

coords = {
    "PC": (50, 100, 130, 160),                    
    "Instr. memory": (170, 80, 320, 150),         
    "Compressed decode": (170, 160, 320, 190),    
    "IF/ID": (340, 60, 370, 190),                 
    "Decode": (420, 90, 500, 150),               
    "Registers": (560, 80, 720, 150),          
    "Imm": (560, 160, 650, 200),                  
    "ID/EX": (740, 60, 770, 190),                 
    "ALU": (815, 80, 940, 150),                  
    "Branch": (815, 160, 940, 200),               
    "EX/MEM": (960, 60, 990, 190),              
    "Data memory": (1050, 80, 1170, 150),        
    "MEM/WB": (1180, 60, 1210, 190)              
}

stage_dividers = [340, 740, 960, 1180]  # Coordenadas de las líneas divisorias de etapas

# --- Canvas principal ---
canvas_w, canvas_h = 1350, 350  # Tamaño del canvas
canvas = tk.Canvas(main_frame, width=canvas_w, height=canvas_h, bg="white")  
canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

canvas.config(width=canvas_w, height=canvas_h)


canvas.create_text(canvas_w//2, 10, text="5-Stage RISC-V Processor ", font=("Arial", 12, "bold"))  # Título

# --- Divisiones de etapas ---
for x in stage_dividers:
    canvas.create_line(x, 40, x, 220, width=7, fill="#999")  

# --- Etiquetas de etapa ---
canvas.create_text(200, 40, text="IF", font=("Arial", 11, "bold"))      
canvas.create_text(450, 40, text="ID", font=("Arial", 11, "bold"))      
canvas.create_text(800, 40, text="EX", font=("Arial", 11, "bold"))      
canvas.create_text(1080, 40, text="MEM", font=("Arial", 11, "bold"))    
canvas.create_text(1200, 40, text="WB", font=("Arial", 11, "bold"))     

# --- Bloques ---
block_ids = {}
for name, (x1, y1, x2, y2) in coords.items():
    fill = "#FFF" if "/" in name else "#E6E6FA"
    block_ids[name] = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, width=2)
    if name in ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]:
        text = name.replace("/", "/\n")  
        canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text, font=("Arial", 8, "bold"))
    else:
        canvas.create_text((x1+x2)//2, (y1+y2)//2, text=name, font=("Arial", 11, "bold"))

# --- Sumador ---

canvas.create_rectangle(135, 70, 165, 90, fill="#D3D3D3", outline="black")
canvas.create_text(150, 80, text="+", font=("Arial", 10))

# --- Multiplexores--
def draw_mux(canvas, x, y, width=28, height=22):
    points = [
        x, y,  # esquina superior izquierda
        x + width, y + height // 4,  # esquina superior derecha
        x + width, y + 3 * height // 4,  # esquina inferior derecha
        x, y + height  # esquina inferior izquierda
    ]
    return canvas.create_polygon(points, fill="white", outline="black", width=2)

# --- MUX antes del PC---
mux0_id = draw_mux(canvas, 20, 65, width=20, height=30)
canvas.create_text(30, 55, text="MUX", font=("Arial", 6))
canvas.create_text(18, 70, text="2", font=("Arial", 6))
canvas.create_text(18, 90, text="4", font=("Arial", 6))

# --- MUX despues del PC ---
mux1_id = draw_mux(canvas, 135, 110)  
canvas.create_text(135 + 14, 110 - 8, text="MUX", font=("Arial", 6))

# --- MUX antes de la ALU ---
mux2_id = draw_mux(canvas, 778, 110)
canvas.create_text(778 + 14, 110 - 8, text="MUX", font=("Arial", 6))


pc_x2 = coords["PC"][2]
pc_yc = (coords["PC"][1] + coords["PC"][3]) // 2
alu_x1 = coords["ALU"][0]
alu_yc = (coords["ALU"][1] + coords["ALU"][3]) // 2

# --- Refresh GUI ---
def refresh_gui():
    cycle_label.config(text=f"Ciclo: {cycle}")
    pc_label.config(text=f"PC: {cpu.pc}")
    time_label.config(text=f"Tiempo transcurrido: {time.time() - start_time:.2f}s")
    reg_text.delete(1.0, tk.END)
    reg_text.insert(tk.END, "Registros:\n")
    for i in range(0, 32, 4):
        reg_text.insert(tk.END, f"x{i:2}: {cpu.regs.registers[i]:<4}  x{i+1:2}: {cpu.regs.registers[i+1]:<4}  x{i+2:2}: {cpu.regs.registers[i+2]:<4}  x{i+3:2}: {cpu.regs.registers[i+3]:<4}\n")
    mem_text.delete(1.0, tk.END)
    mem_text.insert(tk.END, "Memoria (celdas con valor ≠ 0):\n")
    for i, val in enumerate(cpu.mem.dump()):
        if val != 0:
            mem_text.insert(tk.END, f"[{i*4}] = {val}\n")
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Últimos accesos a memoria:\n")
    for action, addr, val in cpu.mem.get_access_log(n=10):
        log_text.insert(tk.END, f"{action} @ {addr} = {val}\n")

    # --- Restaurar color original de todos los bloques ---
    for name, block_id in block_ids.items():
        fill = "#FFF" if "/" in name else "#E6E6FA"
        canvas.itemconfig(block_id, fill=fill)

    # --- Resaltar TODOS los bloques funcionales donde hay instrucciones en el pipeline ---
    stage_to_block = [
        "Instr. memory",   # IF/ID
        "Registers",       # ID/EX
        "ALU",             # EX/MEM
        "Data memory"      # MEM/WB
    ]
    stage_names = ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]
    if hasattr(cpu, "pipeline"):
        for idx in range(4):
            if cpu.pipeline[idx] is not None:
                # Resalta el bloque funcional
                block_name = stage_to_block[idx]
                if block_name in block_ids:
                    canvas.itemconfig(block_ids[block_name], fill="#FFD700")
                # Resalta el registro de pipeline correspondiente
                stage = stage_names[idx]
                if stage in block_ids:
                    canvas.itemconfig(block_ids[stage], fill="#FFD700")

# --- Controladores ---
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
    global cpu, cycle, start_time, running
    cpu = Processor(program)
    cycle = 0
    start_time = time.time()
    running = False
    refresh_gui()

step_btn.config(command=update)
start_btn.config(command=start_auto)
stop_btn.config(command=stop_auto)
run_all_btn.config(command=run_all)
reset_btn.config(command=reset)

refresh_gui()
root.mainloop()
