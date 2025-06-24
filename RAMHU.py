class RAM:
    def __init__(self, size_in_bytes):
        self.size = size_in_bytes  # Tamaño total de la RAM en bytes
        self.data = bytearray(size_in_bytes)  # Arreglo de bytes que representa la memoria
        self.access_log = []  # Lista para registrar el historial de accesos a la RAM

    def check_address(self, address, size):
        # Verifica que la dirección esté dentro del rango y alineada según el tamaño de acceso
        if address < 0 or address + size > self.size:
            raise IndexError("Dirección fuera de rango")
        if size == 4 and address % 4 != 0:
            raise ValueError("Acceso de palabra no alineado")
        if size == 2 and address % 2 != 0:
            raise ValueError("Acceso de half-word no alineado")

    def read_word(self, address):
        self.check_address(address, 4)  # Verifica dirección y alineación para palabra 4 bytes
        value = int.from_bytes(self.data[address:address+4], byteorder='little', signed=True)  # Lee 4 bytes y los convierte a entero
        self.access_log.append(("read_word", address, value))  # Registra el acceso
        return value  # Devuelve el valor leído

    def write_word(self, address, value):
        self.check_address(address, 4)  # Verifica dirección y alineación
        self.data[address:address+4] = value.to_bytes(4, byteorder='little', signed=True)  # Escribe 4 bytes en la memoria
        self.access_log.append(("write_word", address, value))  # Registra el acceso

    def read_half(self, address):
        self.check_address(address, 2)  # Verifica dirección y alineación para half-word 2 bytes
        value = int.from_bytes(self.data[address:address+2], byteorder='little', signed=True)  # Lee 2 bytes y los convierte a entero
        self.access_log.append(("read_half", address, value))  # Registra el acceso
        return value

    def write_half(self, address, value):
        self.check_address(address, 2)
        self.data[address:address+2] = value.to_bytes(2, byteorder='little', signed=True)
        self.access_log.append(("write_half", address, value))

    def read_byte(self, address):
        self.check_address(address, 1)  # Verifica dirección para un byte
        value = int.from_bytes(self.data[address:address+1], byteorder='little', signed=True)  # Lee 1 byte
        self.access_log.append(("read_byte", address, value))
        return value

    def write_byte(self, address, value):
        self.check_address(address, 1)
        self.data[address:address+1] = value.to_bytes(1, byteorder='little', signed=True)
        self.access_log.append(("write_byte", address, value))

    def dump(self):
        # Devuelve una lista de palabras 4 bytes que representan toda la memoria 
        return [int.from_bytes(self.data[i:i+4], 'little', signed=True)
                for i in range(0, self.size, 4)]

    def dump_range(self, inicio, fin):
        # Devuelve una lista de palabras en el rango de direcciones dado
        inicio_alineado = inicio - (inicio % 4)
        fin_alineado = fin + (4 - (fin % 4)) if (fin % 4) != 0 else fin
        return [int.from_bytes(self.data[i:i+4], 'little', signed=True)
                for i in range(inicio_alineado, fin_alineado, 4)]

    def reset(self):
        self.data = bytearray(self.size)  # Borra toda la memoria 
        self.access_log.clear()  # Limpia el historial de accesos

    def load_from_list(self, valores, base_address=0):
        # Inicializa la RAM con una lista de enteros, escribiéndolos como palabras desde base_address
        for i, v in enumerate(valores):
            addr = base_address + 4 * i
            if addr + 4 <= self.size:
                self.write_word(addr, v)

    def get_access_log(self, n=20):
        # Devuelve los últimos n accesos realizados a la RAM
        return self.access_log[-n:]