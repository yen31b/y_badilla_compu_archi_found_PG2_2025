import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from procesador1 import crear_procesador1
from procesador2 import crear_procesador2

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

MODOS = [
    "Sin unidad de riesgo",
    "Con unidad de riesgos",
    "Con predicción de saltos",
    "Con unidad de riesgos y predicción de saltos"
]


def lanzar_ventana_principal(modo1, modo2):
    root = tk.Toplevel()
    root.title("Simulador RISCV - Pipeline ")
    root.geometry("2000x1000")

    # Frame Procesador 1
    frame1 = tk.Frame(root, bg="#6c47c7")
    frame1.pack(fill="x", padx=10, pady=(10, 0))
    label1 = tk.Label(frame1, text="Procesador 1", bg="#6c47c7", fg="white", font=("Arial", 14, "bold"))
    label1.pack(anchor="center", pady=(2, 0))
    main_frame1 = tk.Frame(root)
    main_frame1.pack()
    crear_procesador1(main_frame1, modo1)

    # Frame Procesador 2
    frame2 = tk.Frame(root, bg="#1ea7c6")
    frame2.pack(fill="x", padx=10, pady=(5, 0))
    label2 = tk.Label(frame2, text="Procesador 2", bg="#1ea7c6", fg="white", font=("Arial", 14, "bold"))
    label2.pack(anchor="center", pady=(2, 0))
    main_frame2 = tk.Frame(root)
    main_frame2.pack()
    crear_procesador2(main_frame2, modo2)

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


# --- Ventana de inicio ---
start_win = tk.Tk()
start_win.title("Simulador RISC-V")
start_win.geometry("1500x1000")
start_win.configure(bg="#ffffff")  # Fondo blanco

# Configura el grid para centrar los cuadros
start_win.grid_columnconfigure(0, weight=1)
start_win.grid_columnconfigure(1, weight=1)
start_win.grid_columnconfigure(2, weight=1)
start_win.grid_rowconfigure(0, weight=1)
start_win.grid_rowconfigure(1, weight=1)
start_win.grid_rowconfigure(2, weight=1)

titulo = tk.Label(start_win, text="Simulador RISC-V", font=("Arial", 48, "bold"), bg="#ffffff", fg="#1565c0")
titulo.grid(row=0, column=0, columnspan=3, pady=(60, 20), sticky="nsew")

# Opciones para Procesador 1
frame1 = tk.Frame(start_win, bg="#f5f5f5", bd=3, relief="ridge")
frame1.grid(row=1, column=1, padx=60, pady=40, sticky="nsew")
modo1_label = tk.Label(frame1, text="Modo Procesador 1:", font=("Arial", 20, "bold"), bg="#f5f5f5", fg="#1976d2")
modo1_label.pack(pady=(20, 10))
modo1_var = tk.StringVar(value=MODOS[0])
modo1_combo = ttk.Combobox(frame1, textvariable=modo1_var, values=MODOS, font=("Arial", 16), state="readonly", width=32)
modo1_combo.pack(padx=30, pady=(0, 20))
modo1_combo.current(0)

# Opciones para Procesador 2
frame2 = tk.Frame(start_win, bg="#f5f5f5", bd=3, relief="ridge")
frame2.grid(row=1, column=2, padx=60, pady=40, sticky="nsew")
modo2_label = tk.Label(frame2, text="Modo Procesador 2:", font=("Arial", 20, "bold"), bg="#f5f5f5", fg="#1976d2")
modo2_label.pack(pady=(20, 10))
modo2_var = tk.StringVar(value=MODOS[0])
modo2_combo = ttk.Combobox(frame2, textvariable=modo2_var, values=MODOS, font=("Arial", 16), state="readonly", width=32)
modo2_combo.pack(padx=30, pady=(0, 20))
modo2_combo.current(0)

# Botón continuar
def continuar():
    modo1 = modo1_var.get()
    modo2 = modo2_var.get()
    if not modo1 or not modo2:
        messagebox.showwarning("Falta selección", "Selecciona un modo para ambos procesadores.")
        return
    start_win.withdraw()
    lanzar_ventana_principal(modo1, modo2)

btn = tk.Button(start_win, text="Continuar", font=("Arial", 24, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white", command=continuar, bd=3, relief="raised")
btn.grid(row=2, column=1, columnspan=2, pady=60)

start_win.mainloop()
