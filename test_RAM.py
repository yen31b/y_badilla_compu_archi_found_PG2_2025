from .RAM import RAM

def test_RAM():
    ram = RAM(64)  # 64 bytes = 16 palabras (32 bits cada una)

    # Prueba de escritura y lectura de palabra
    ram.write_word(0, 123)
    assert ram.read_word(0) == 123

    # Prueba de alineamiento (esto debe funcionar)
    ram.write_word(4, 456)
    assert ram.read_word(4) == 456

    # Prueba de error de alineamiento (esto debe lanzar excepción)
    try:
        ram.write_word(2, 789)
        print("Error: No lanzó excepción por alineamiento incorrecto")
    except ValueError:
        print("OK: Excepción por alineamiento detectada")

    # Prueba de acceso fuera de rango
    try:
        ram.read_word(1000)
        print("Error: No lanzó excepción por fuera de rango")
    except IndexError:
        print("OK: Excepción por fuera de rango detectada")

    # Prueba de lectura y escritura de byte
    ram.write_byte(8, 0x7F)
    assert ram.read_byte(8) == 0x7F

    # Prueba de dump (debe haber 16 palabras)
    dump = ram.dump()
    print("RAM dump:", dump)
    assert len(dump) == 16

    print("¡Todas las pruebas pasaron!")

if __name__ == "__main__":
    test_RAM()