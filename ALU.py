class ALU:
    def __init__(self):
        pass
    

    #Metodo operacion_alu: 
    # Ejecuta una operacion de la ALU utilizando dos entradas y una operacion dada.
    # Parametros:
    # op: codigo que representa la operacion que se va a realizar (ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, SLT, SLTU, EQ, NE).
    # a: Primer operando
    # b: Segundo operando
    def operacion_alu(self, op, a, b):
        if op == 'ADD':
            return (a + b) & 0xFFFFFFFF  # Suma de 32 bits
        elif op == 'SUB':
            return (a - b) & 0xFFFFFFFF  # Resta de 32 bits
        elif op == 'AND': 
            return a & b   
        elif op == 'OR': #OR
            return a | b 
        elif op == 'XOR': #XOR
            return a ^ b 
        elif op == 'SLL':
            return (a << (b & 0x1F)) & 0xFFFFFFFF  # Shift left logico
        elif op == 'SRL':
            return (a >> (b & 0x1F)) & 0xFFFFFFFF  # Shift right logico
        elif op == 'SRA':           
            return ((a & 0xFFFFFFFF) >> (b & 0x1F)) | (-(a < 0) << (32 - (b & 0x1F))) # Shift right aritmetico
        elif op == 'SLT':
            return int((a & 0xFFFFFFFF) < (b & 0xFFFFFFFF)) # Comparacion menor que < signed
        elif op == 'SLTU':
            return int((a % (1 << 32)) < (b % (1 << 32))) # Comparacion menor que < unsigned
        elif op == 'EQ':
            return int(a == b) # Comparacion igualdad ==
        elif op == 'NE':
            return int(a != b) # Comparacion desigualdad !=
        else:
            raise ValueError(f"ALU no soporta esa operacion: {op}")

# Operaciones de prueba:
if __name__ == "__main__":
    alu = ALU()
    print("ADD 10 + 5 =", alu.operacion_alu('ADD', 10, 5))
    print("SUB 10 - 5 =", alu.operacion_alu('SUB', 10, 5))
    print("AND 10 & 5 =", alu.operacion_alu('AND', 10, 5))
    print("SLL 1 << 3 =", alu.operacion_alu('SLL', 1, 3))
    print("SRL 8 >> 2 =", alu.operacion_alu('SRL', 8, 2))
    print("SRA -8 >> 2 =", alu.operacion_alu('SRA', -8, 2))
    print("SLT 3 < 5 =", alu.operacion_alu('SLT', 3, 5))
    print("SLTU 3 < 5 =", alu.operacion_alu('SLTU', 3, 5))
    print("EQ 5 == 5 =", alu.operacion_alu('EQ', 5, 5))
    print("NE 5 != 3 =", alu.operacion_alu('NE', 5, 3))
    print("XOR 10 ^ 5 =", alu.operacion_alu('XOR', 10, 5))
    print("OR 10 | 5 =", alu.operacion_alu('OR', 10, 5))