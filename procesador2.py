from processor import Processor
import tkinter as tk
import time

def crear_procesador2(parent_frame, modo):
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
    start_time = time.time()
    cycle = [0]
    running = [False]

    main_frame = tk.Frame(parent_frame)
    main_frame.pack()

    reg_text = tk.Text(main_frame, height=8, width=37, bg="#e0f7fa")
    reg_text.grid(row=0, column=1, padx=5, pady=2)
    mem_text = tk.Text(main_frame, height=8, width=37, bg="#e0f7fa")
    mem_text.grid(row=1, column=1, padx=5, pady=2)
    log_text = tk.Text(main_frame, height=8, width=37, bg="#e0f7fa")
    log_text.grid(row=2, column=1, padx=5, pady=2)

    canvas_w, canvas_h = 1500, 500 
    canvas = tk.Canvas(main_frame, width=canvas_w, height=canvas_h, bg="#e0f7fa")
    canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
    canvas.config(width=canvas_w, height=canvas_h)
    canvas.create_text(canvas_w//2, 10, text="5-Stage RISC-V Processor ", font=("Arial", 12, "bold"), fill="#00796b")

    # --- Status frame debajo del cuadro de "Últimos accesos a memoria" ---
    status_frame = tk.Frame(main_frame)
    status_frame.grid(row=3, column=1, pady=(10, 0), sticky="w")
    cycle_label = tk.Label(status_frame, text="Ciclo: 0", fg="#00796b")
    cycle_label.pack(side=tk.LEFT, padx=8)
    pc_label = tk.Label(status_frame, text="PC: 0", fg="#00796b")
    pc_label.pack(side=tk.LEFT, padx=8)
    time_label = tk.Label(status_frame, text="Tiempo transcurrido: 0.00s", fg="#00796b")
    time_label.pack(side=tk.LEFT, padx=8)

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

    stage_dividers = [440, 820, 1060, 1280]

    canvas.create_text(canvas_w//2, 10, text="5-Stage RISC-V Processor ", font=("Arial", 12, "bold"), fill="#00796b")

    # Botones 
    btn_y = 290  
    btn_x = 30   
    btn_sep = 28 

    btn_font = ("Arial", 8) 

    step_btn = tk.Button(canvas, text="Siguiente ciclo", width=12, font=btn_font, bg="#b2ebf2")
    start_btn = tk.Button(canvas, text="Inicio automático", width=12, font=btn_font, bg="#b2ebf2")
    stop_btn = tk.Button(canvas, text="Detener automático", width=12, font=btn_font, bg="#b2ebf2")
    run_all_btn = tk.Button(canvas, text="Ejecutar completo", width=12, font=btn_font, bg="#b2ebf2")
    reset_btn = tk.Button(canvas, text="Reiniciar", width=12, font=btn_font, bg="#b2ebf2")

    canvas.create_window(btn_x, btn_y, window=step_btn, anchor="nw")
    canvas.create_window(btn_x, btn_y + btn_sep, window=start_btn, anchor="nw")
    canvas.create_window(btn_x, btn_y + 2*btn_sep, window=stop_btn, anchor="nw")
    canvas.create_window(btn_x, btn_y + 3*btn_sep, window=run_all_btn, anchor="nw")
    canvas.create_window(btn_x, btn_y + 4*btn_sep, window=reset_btn, anchor="nw")

    for x in stage_dividers:
        canvas.create_line(x, 90, x, 430, width=7, fill="#0097a7")  # Divisores azul 

    block_ids = {}
    for name, (x1, y1, x2, y2) in coords.items():
        if name == "ALU":
            continue
        fill = "#FFF" if "/" in name else "#b2ebf2"  # Bloques celestes
        block_ids[name] = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, width=2)
        if name in ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]:
            text = name.replace("/", "/\n")
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text, font=("Arial", 8, "bold"), fill="#00796b")
        else:
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=name, font=("Arial", 11, "bold"), fill="#00796b")

    def draw_mux(canvas, x, y, width=28, height=22):
        points = [
            x, y,
            x + width, y + height // 4,
            x + width, y + 3 * height // 4,
            x, y + height
        ]
        return canvas.create_polygon(points, fill="#b2ebf2", outline="#0097a7", width=2)

    def draw_alu(canvas, x, y, width=100, height=70):
        notch_depth = width * 0.13
        notch_height = height * 0.28
        points = [
            (x + notch_depth -10, y ),
            (x + width - 1, y +10),
            (x + width - 1, y - 10 + height),
            (x + notch_depth -10, y + height),
            (x, y + height - notch_height),
            (x + notch_depth, y + height // 2),
            (x, y + notch_height)
        ]
        flat_points = [coord for pt in points for coord in pt]
        alu_id = canvas.create_polygon(flat_points, fill="#b2ebf2", outline="#0097a7", width=2)
        return alu_id

    # --- Sumador ---
    muxS_id = draw_mux(canvas, 235, 110, width=20, height=30)  
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
    canvas.create_line(1045, 30, 1045, 210) #M1 y ALU
    canvas.create_line(50, 30, 1045, 30) #M1 y ALU
    canvas.create_line(50, 30, 50, 235) #M1 y ALU
    canvas.create_line(50, 235, 115, 235) #M1 y ALU

    # --- MUX arriba antes de la ALU ---
    mux_extra_id = draw_mux(canvas, 905, 163, width=15, height=30)
    canvas.create_line(920, 177, 1000, 177) #M a ALU

    # --- MUX abajo antes de la ALU ---
    mux2_id = draw_mux(canvas, 905, 230, width=15, height=30)
    canvas.create_line(920, 243, 1000, 243) #M a ALU

      # --- MUX arriba primero de la ALU ---
    mux_extra_id = draw_mux(canvas, 865, 163, width=18, height=28)
    canvas.create_line(849, 180, 865, 180) #M a ALU

    # --- MUX abajo primero de la ALU ---
    mux2_id = draw_mux(canvas, 865, 220, width=18, height=28)
    canvas.create_line(849, 232, 865, 232) #M a ALU

    # --- MUX después de MEM/WB ---
    mux_final_id = draw_mux(canvas, 1380, 160, width=20, height=50)

    #--- Líneas ---
    canvas.create_line(255, 123, 440, 123)  #sumador a 1 bloque separador
    canvas.create_line(469, 123, 821, 123)  #Bloque 1 a bloque 2
    canvas.create_line(851, 123, 1060,123)  #Bloque 2 a bloque 3
    canvas.create_line(1090,123, 1278,123)  #Bloque 3 a bloque 4
    canvas.create_line(1309, 123,1338,123)  #Bloque 5 a mux final
    canvas.create_line(1338, 123, 1338, 165)  
    canvas.create_line(1338, 165, 1380, 165) 
    canvas.create_line(220, 224, 270, 224)#PC y IM
    canvas.create_line(240, 140, 240, 224)#PC y MS
    canvas.create_line(240, 150, 440, 150) # PC + Y bloque 1
    canvas.create_line(470, 150, 821, 150) # Bloque 1 a bloque 2
    canvas.create_line(851, 150, 890, 150) # iD/EX y LINEA mux arriba alu
    canvas.create_line(890, 150, 890, 170)
    canvas.create_line(890, 170, 905, 170)
    canvas.create_line(883, 180, 905, 180) #union multiplexores alu arriba
    canvas.create_line(894, 180, 894, 320) #union multiplexores alu arriba y branch
    canvas.create_line(894, 320, 915, 320) 
    canvas.create_line(855, 170, 865, 170) #primer mux alu hacia arriba
    canvas.create_line(857, 187, 865, 187) #primer mux alu hacia abajo
    canvas.create_line(857, 187, 857, 425)
    canvas.create_line(857, 425, 1111, 425)
    canvas.create_line(1110, 210, 1110, 425)
    canvas.create_line(855, 225, 865, 225) #segundo mux alu hacia arriba
    canvas.create_line(855, 70, 855, 225)
    canvas.create_line(857, 236, 865, 236) #segundo mux alu hacia abajo
    canvas.create_line(888, 300, 1060, 300) #Nodo MuxAb branch a EX/men
    canvas.create_line(801, 182, 821, 182) #Register y ID/EX
    canvas.create_line(801, 232, 821, 232) 
    canvas.create_line(345, 240, 345, 270)#Instr M y CompressedD
    canvas.create_line(720, 280, 820, 280) #IMM Y ID/EX
    canvas.create_line(850, 280, 900, 280)
    canvas.create_line(899, 250, 899, 280)
    canvas.create_line(899, 250, 904, 250)
    canvas.create_line(883, 235, 905, 235) #union multiplexores alu abajo
    canvas.create_line(888, 236, 888, 335) #union multiplexores alu abajo y branch
    canvas.create_line(888, 335, 916, 335)
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

    canvas.create_line(1020, 210, 1060, 210) #ALU y EX/MEM
    canvas.create_line(590, 215, 660, 215) #Decode y registers  R
    canvas.create_line(590, 230, 660, 230) 
    canvas.create_line(1090, 210, 1130, 210)#EX/MEM data memory arriba
    canvas.create_line(1090, 300, 1105, 300) #EX/MEM data memory abajo
    canvas.create_line(1105, 245, 1105, 300)
    canvas.create_line(1105, 245, 1130, 245)
    canvas.create_line(1240, 210, 1280, 210)#data memory arriba y MEM/WB
    canvas.create_line(1110, 165, 1280, 165)
    canvas.create_line(1110, 165, 1110, 210)
    canvas.create_line(1310, 210, 1330, 210)# Mem/WB MUX
    canvas.create_line(1329, 200, 1329, 210)# Mem/WB MUX
    canvas.create_line(1329, 200, 1381, 200)# Mem/WB MUX
    canvas.create_line(1310, 165, 1320, 165) #linea centro mux final
    canvas.create_line(1320, 165, 1320, 181)
    canvas.create_line(1320, 181, 1381, 181)


    alu_x1, alu_y1, alu_x2, alu_y2 = coords["ALU"]
    alu_width = alu_x2 - alu_x1
    alu_height = alu_y2 - alu_y1
    alu_id = draw_alu(canvas, alu_x1, alu_y1, width=alu_width, height=alu_height)
    block_ids["ALU"] = alu_id
    canvas.create_text((alu_x1 + alu_x2)//2, (alu_y1 + alu_y2)//2, text="ALU", font=("Arial", 11, "bold"), fill="#00796b")
    canvas.create_text(alu_x1 + 18, alu_y1 + 12, text="Op 1", font=("Arial", 7), fill="#00796b")
    canvas.create_text(alu_x1 + 18, alu_y2 - 12, text="Op 2", font=("Arial", 7), fill="#00796b")
    canvas.create_text(alu_x2 - 15, (alu_y1 + alu_y2)//2, text="Res", font=("Arial", 7), fill="#00796b")

    def refresh_gui():
        cycle_label.config(text=f"Ciclo: {cycle[0]}")
        pc_label.config(text=f"PC: {cpu.pc}")
        time_label.config(text=f"Tiempo transcurrido: {time.time() - start_time:.2f}s")
        reg_text.delete(1.0, tk.END)
        reg_text.insert(tk.END, "Registros:\n")
        for i in range(0, 32, 4):
            reg_text.insert(tk.END, f"x{i:2}: {cpu.regs.registers[i]:<4}  x{i+1:2}: {cpu.regs.registers[i+1]:<4}  x{i+2:2}: {cpu.regs.registers[i+2]:<4}  x{i+3:2}: {cpu.regs.registers[i+3]:<4}\n")
        mem_text.delete(1.0, tk.END)
        mem_text.insert(tk.END, "Memoria (todas las celdas):\n")
        for i, val in enumerate(cpu.mem.dump()):
            mem_text.insert(tk.END, f"[{i*4:04}] = {val}\n")
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "Últimos accesos a memoria:\n")
        for action, addr, val in cpu.mem.get_access_log(n=10):
            log_text.insert(tk.END, f"{action} @ {addr} = {val}\n")

        for name, block_id in block_ids.items():
            fill = "#FFF" if "/" in name else "#b2ebf2"
            canvas.itemconfig(block_id, fill=fill)

        stage_to_block = [
            "Instr. memory",
            "Registers",
            "ALU",
            "Data memory"
        ]
        stage_names = ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]
        if hasattr(cpu, "pipeline"):
            for idx in range(4):
                if cpu.pipeline[idx] is not None:
                    block_name = stage_to_block[idx]
                    if block_name in block_ids:
                        canvas.itemconfig(block_ids[block_name], fill="#FFD700")
                    stage = stage_names[idx]
                    if stage in block_ids:
                        canvas.itemconfig(block_ids[stage], fill="#FFD700")

        if hasattr(refresh_gui, "stage_text_ids"):
            for tid in refresh_gui.stage_text_ids:
                canvas.delete(tid)
        refresh_gui.stage_text_ids = []

        for idx in range(4):
            instr = cpu.pipeline[idx]
            if instr is not None:
                block_name = stage_to_block[idx]
                if block_name in coords:
                    x1, y1, x2, y2 = coords[block_name]
                    text_id = canvas.create_text(
                        (x1 + x2) // 2, y1 - 15,
                        text=instr,
                        font=("Arial", 8, "italic"),
                        fill="#00796b"
                    )
                    refresh_gui.stage_text_ids.append(text_id)

    def update():
        cpu.step()
        cycle[0] += 1
        refresh_gui()

    def auto_run():
        if running[0]:
            update()
            main_frame.after(1000, auto_run)

    def start_auto():
        running[0] = True
        auto_run()

    def stop_auto():
        running[0] = False

    def run_all():
        while cpu.pc // 4 < len(cpu.instructions) or any(cpu.pipeline):
            update()

    def reset():
        nonlocal cpu, start_time
        cpu = Processor(program)
        cycle[0] = 0
        start_time = time.time()
        running[0] = False
        refresh_gui()

    step_btn.config(command=update)
    start_btn.config(command=start_auto)
    stop_btn.config(command=stop_auto)
    run_all_btn.config(command=run_all)
    reset_btn.config(command=reset)

    refresh_gui()