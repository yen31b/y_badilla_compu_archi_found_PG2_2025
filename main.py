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
    "PC": (150, 210, 220, 240),                    
    "Instr. memory": (270, 160, 420, 240),         
    "Compressed decode": (270, 270, 420, 300),    
    "IF/ID": (440, 108, 470, 450),      
    "Decode": (530, 210, 590, 300),               
    "Registers": (660, 160, 800, 260),          
    "Imm": (687, 270, 720, 330),                  
    "ID/EX": (820, 108, 850, 450),      
    "ALU": (935, 160, 1035, 260),                  
    "Branch": (915, 292, 1000, 310),               
    "EX/MEM": (1060, 108, 1090, 450),    
    "Data memory": (1110, 130, 1230, 200),  
    "MEM/WB": (1280, 108, 1310, 450)   
}

stage_dividers = [440, 820, 1060, 1280]  # Antes: [340, 740, 960, 1180]

# --- Canvas principal ---
canvas_w, canvas_h = 1550, 500  # Nuevo tamaño del canvas
canvas = tk.Canvas(main_frame, width=canvas_w, height=canvas_h, bg="white")  
canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

canvas.config(width=canvas_w, height=canvas_h)

canvas.create_text(canvas_w//2, 10, text="5-Stage RISC-V Processor ", font=("Arial", 12, "bold"))  # Título

# --- Divisiones de etapas ---
for x in stage_dividers:
    canvas.create_line(x, 90, x, 310, width=7, fill="#999")  

# --- Bloques ---
block_ids = {}
for name, (x1, y1, x2, y2) in coords.items():
    if name == "ALU":
        continue  # No dibujes aquí, la dibujamos abajo con forma especial
    fill = "#FFF" if "/" in name else "#E6E6FA"
    block_ids[name] = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, width=2)
    if name in ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]:
        text = name.replace("/", "/\n")  
        canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text, font=("Arial", 8, "bold"))
    else:
        canvas.create_text((x1+x2)//2, (y1+y2)//2, text=name, font=("Arial", 11, "bold"))

# --- Multiplexores--
def draw_mux(canvas, x, y, width=28, height=22):
    points = [
        x, y,  # esquina superior izquierda
        x + width, y + height // 4,  # esquina superior derecha
        x + width, y + 3 * height // 4,  # esquina inferior derecha
        x, y + height  # esquina inferior izquierda
    ]
    return canvas.create_polygon(points, fill="white", outline="black", width=2)

# --- ALU con forma personalizada ---
def draw_alu(canvas, x, y, width=100, height=70):
    """
    Dibuja una ALU con muesca en 'V' en el lado izquierdo
    y etiqueta cada vértice con una letra.
    """
    notch_depth = width * 0.13      # Profundidad horizontal de la muesca
    notch_height = height * 0.28    # Altura desde los bordes hasta la muesca

    points = [
        (x + notch_depth -10, y ),                  
        (x + width - 1, y +10),                      
        (x + width - 1, y - 10 + height),            
        (x + notch_depth -10, y + height),          
        (x, y + height - notch_height),          
        (x + notch_depth, y + height // 2),    
        (x, y + notch_height)                    
    ]

    # Dibuja el polígono
    flat_points = [coord for pt in points for coord in pt]
    alu_id = canvas.create_polygon(flat_points, fill="#E6E6FA", outline="black", width=2)
    return alu_id

# --- Sumador ---
muxS_id = draw_mux(canvas, 235, 110, width=20, height=30)  # +100 en X
canvas.create_text(250, 98, text="Sumador", font=("Arial", 6))

# --- MUX antes arriba del PC---
mux0_id = draw_mux(canvas, 171, 104, width=20, height=30)
canvas.create_text(167, 104, text="4", font=("Arial", 6))
canvas.create_line(158, 107, 168, 107)
canvas.create_text(167, 123, text="2", font=("Arial", 6))
canvas.create_line(158, 127, 168, 127)
canvas.create_line(190, 120, 236, 120)  #M0 y MS

# --- MUX antes del PC ---
mux1_id = draw_mux(canvas, 115, 210, width=20, height=30)  
canvas.create_line(90, 222, 116, 222)  #M1  y S
canvas.create_line(90, 80, 90, 222)  #M1  y S
canvas.create_line(90, 80, 317, 80)  #M1  y S
canvas.create_line(317, 80, 317, 123)  #M1  y S
canvas.create_line(135, 224, 150, 224)#M1 y PC

# --- MUX arriba antes de la ALU ---
mux_extra_id = draw_mux(canvas, 888, 163, width=20, height=30)
canvas.create_line(908, 177, 950, 177) #M a ALU

# --- MUX abajo antes de la ALU ---
mux2_id = draw_mux(canvas, 888, 227, width=20, height=30)
canvas.create_line(908, 243, 950, 243) #M a ALU

# --- MUX después de MEM/WB ---
mux_final_id = draw_mux(canvas, 1380, 160, width=20, height=50)

#--- Líneas ---
canvas.create_line(255, 123, 440, 123)  #sumador a 1 bloque separador
canvas.create_line(469, 123, 821, 123)  #Bloque 1 a bloque 2
canvas.create_line(851, 123, 1060, 123)  #Bloque 2 a bloque 3
canvas.create_line(1090, 123, 1278, 123)  #Bloque 3 a bloque 4
canvas.create_line(1309, 123, 1338, 123)  #Bloque 5 a mux final
canvas.create_line(1338, 123, 1338, 165)  
canvas.create_line(1338, 165, 1380, 165) 
canvas.create_line(220, 224, 270, 224)#PC y IM
canvas.create_line(240, 140, 240, 224)#PC y MS
canvas.create_line(240, 150, 440, 150) # PC + Y bloque 1
canvas.create_line(470, 150, 821, 150) # Bloque 1 a bloque 2
canvas.create_line(871, 150, 880, 150) # BLoque 2 y mux arriba alu
canvas.create_line(880, 150, 880, 167)
canvas.create_line(880, 167, 888, 167) 
canvas.create_line(871, 182, 888, 182)
canvas.create_line(871, 232, 888, 232)
canvas.create_line(821, 182, 841, 182) #Register y ID/EX
canvas.create_line(821, 232, 841, 232) 
canvas.create_line(345, 240, 345, 270)#Instr M y CompressedD
canvas.create_line(720, 280, 820, 280) #IMM Y ID/EX
canvas.create_line(590, 280, 687, 280) #IMM Y Decode 
canvas.create_line(420, 290, 440, 290)#CompressedD y IF
canvas.create_line(469, 290, 508, 290)#IF y decode
canvas.create_line(508, 220, 508, 290)# decode y Imm
canvas.create_line(508, 220, 531, 220)
canvas.create_line(590, 290, 595, 290) #Decode y id/ex
canvas.create_line(595, 290, 595, 355) 
canvas.create_line(595, 355, 820, 355) 
canvas.create_line(508, 320, 688, 320) #IMM nodo decode
canvas.create_line(508, 280, 508, 320)
canvas.create_line(640, 190, 660, 190) #Register con salida del ultimo mux
canvas.create_line(640, 70, 640, 190)
canvas.create_line(640, 70, 1425, 70)
canvas.create_line(1425, 70, 1425, 183)
canvas.create_line(1400, 183, 1425, 183)
canvas.create_line(620, 200, 660, 200) #Register hasta MEM/WB
canvas.create_line(620, 50, 620, 200)
canvas.create_line(620, 50, 1445, 50)
canvas.create_line(1445, 50, 1445, 387)
canvas.create_line(1310, 387, 1445, 387)
canvas.create_line(1090, 387, 1278, 387) #bloque 3 y boque 4 abajo
canvas.create_line(890, 387, 1060, 387) #bloque 2 y boque 3 abajo
canvas.create_line(890, 357, 890, 387) 
canvas.create_line(850, 357, 890, 357) 


canvas.create_line(590, 215, 660, 215) #Decode y registers  R
canvas.create_line(590, 230, 660, 230) 

# --- Dibuja la ALU personalizada y guárdala en block_ids ---
alu_x1, alu_y1, alu_x2, alu_y2 = coords["ALU"]
alu_width = alu_x2 - alu_x1
alu_height = alu_y2 - alu_y1
alu_id = draw_alu(canvas, alu_x1, alu_y1, width=alu_width, height=alu_height)
block_ids["ALU"] = alu_id  # <-- Así la ALU se puede resaltar igual que los demás bloques
canvas.create_text((alu_x1 + alu_x2)//2, (alu_y1 + alu_y2)//2, text="ALU", font=("Arial", 11, "bold"))
canvas.create_text(alu_x1 + 18, alu_y1 + 12, text="Op 1", font=("Arial", 7))
canvas.create_text(alu_x1 + 18, alu_y2 - 12, text="Op 2", font=("Arial", 7))
canvas.create_text(alu_x2 - 15, (alu_y1 + alu_y2)//2, text="Res", font=("Arial", 7))

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

    # --- Mostrar la instrucción sobre cada bloque de etapa ---
    # Limpia textos anteriores (opcional, si agregas textos dinámicos)
    if hasattr(refresh_gui, "stage_text_ids"):
        for tid in refresh_gui.stage_text_ids:
            canvas.delete(tid)
    refresh_gui.stage_text_ids = []

    for idx in range(4):
        instr = cpu.pipeline[idx]
        if instr is not None:
            # Elige el centro del bloque funcional
            block_name = stage_to_block[idx]
            if block_name in coords:
                x1, y1, x2, y2 = coords[block_name]
                # Muestra la instrucción arriba del bloque
                text_id = canvas.create_text(
                    (x1 + x2) // 2, y1 - 15,
                    text=instr,
                    font=("Arial", 8, "italic"),
                    fill="blue"
                )
                refresh_gui.stage_text_ids.append(text_id)

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
