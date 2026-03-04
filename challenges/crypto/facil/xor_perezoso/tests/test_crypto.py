import importlib.util, pathlib

CT_HEX = "203827080b041726061f3e1f1a0500180f33111601043a1c0d1f041d1234041504031c"
FLAG    = "CTF{xor_es_lineal_pero_ensena_algo}"
KEY     = b"classkey"

# Cargar solution.py por ruta absoluta (evita colisiones entre retos)
_sol = importlib.util.spec_from_file_location(
    "xor_solution",
    pathlib.Path(__file__).parent.parent / "solution.py"
)
_mod = importlib.util.module_from_spec(_sol)
_sol.loader.exec_module(_mod)
solve = _mod.solve
xor_bytes = _mod.xor_bytes
recover_key_kpa = _mod.recover_key_kpa


def test_xor_roundtrip():
    """XOR aplicado dos veces devuelve el original."""
    data = b"Hello CTF!"
    assert xor_bytes(xor_bytes(data, KEY), KEY) == data


def test_known_plaintext_recovers_key_prefix():
    """Known-Plaintext Attack recupera los primeros bytes de la clave."""
    ct = bytes.fromhex(CT_HEX)
    recovered = recover_key_kpa(ct, b"CTF{")
    assert recovered == KEY[:4], f"Se esperaba {KEY[:4]!r}, se obtuvo {recovered!r}"


def test_full_decryption():
    """La solución completa recupera la flag exacta."""
    flag = solve(CT_HEX)
    assert flag == FLAG, f"Flag incorrecta: {flag}"


def test_flag_format():
    flag = solve(CT_HEX)
    assert flag.startswith("CTF{") and flag.endswith("}")
