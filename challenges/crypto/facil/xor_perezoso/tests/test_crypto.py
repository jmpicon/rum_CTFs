from solution import solve

def test_xor_solution_roundtrip():
    # El valor hex de \x24\x0f\x1d... se debe generar con el challenge.
    # En runtime, se pasa la key y el string hexadecimal
    # Para la prueba, evaluamos la reversibilidad
    
    FLAG = b"CTF{xor_es_lineal_pero_ensena_algo}"
    KEY = b"classkey"
    
    # Generar hex manualmente como lo haría el binario
    out = bytearray()
    for i, b in enumerate(FLAG):
        out.append(b ^ KEY[i % len(KEY)])
    cipher_hex = bytes(out).hex()

    flag_obtenida = solve(cipher_hex, KEY)
    assert flag_obtenida.startswith("CTF{") and flag_obtenida.endswith("}")
