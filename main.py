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

    # --- Barras de desplazamiento ---
    canvas = tk.Canvas(root, borderwidth=0, background="#f0f0f0")
    scroll_y = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas, background="#f0f0f0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")

    # --- Procesador 1 ---
    frame1 = tk.Frame(scrollable_frame, bg="#6c47c7")
    frame1.pack(fill="x", padx=10, pady=(10, 0))
    label1 = tk.Label(frame1, text="Procesador 1", bg="#6c47c7", fg="white", font=("Arial", 14, "bold"))
    label1.pack(anchor="center", pady=(2, 0))
    main_frame1 = tk.Frame(scrollable_frame)
    main_frame1.pack()
    crear_procesador1(main_frame1, modo1)

    # --- Procesador 2 ---
    frame2 = tk.Frame(scrollable_frame, bg="#1ea7c6")
    frame2.pack(fill="x", padx=10, pady=(5, 0))
    label2 = tk.Label(frame2, text="Procesador 2", bg="#1ea7c6", fg="white", font=("Arial", 14, "bold"))
    label2.pack(anchor="center", pady=(2, 0))
    main_frame2 = tk.Frame(scrollable_frame)
    main_frame2.pack()
    crear_procesador2(main_frame2, modo2)

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
