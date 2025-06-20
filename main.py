import tkinter as tk
from procesador1 import crear_procesador1
from procesador2 import crear_procesador2

root = tk.Tk()
root.title("Simulador RISCV - Pipeline ")


# Frame Procesador 1
frame1 = tk.Frame(root, bg="#6c47c7")
frame1.pack(fill="x", padx=10, pady=(10, 0))
label1 = tk.Label(frame1, text="Procesador 1", bg="#6c47c7", fg="white", font=("Arial", 14, "bold"))
label1.pack(anchor="center", pady=(2, 0))
main_frame1 = tk.Frame(root)
main_frame1.pack()
crear_procesador1(main_frame1)

# Frame Procesador 2
frame2 = tk.Frame(root, bg="#1ea7c6")
frame2.pack(fill="x", padx=10, pady=(5, 0))  
label2 = tk.Label(frame2, text="Procesador 2", bg="#1ea7c6", fg="white", font=("Arial", 14, "bold"))
label2.pack(anchor="center", pady=(2, 0))
main_frame2 = tk.Frame(root)
main_frame2.pack()
crear_procesador2(main_frame2)

root.mainloop()