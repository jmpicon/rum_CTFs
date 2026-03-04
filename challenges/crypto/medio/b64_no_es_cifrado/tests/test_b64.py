import importlib.util, pathlib, base64, codecs

_sol = importlib.util.spec_from_file_location(
    "b64_solution",
    pathlib.Path(__file__).parent.parent / "solution.py"
)
_mod = importlib.util.module_from_spec(_sol)
_sol.loader.exec_module(_mod)
solve = _mod.solve

ENCODED = "VUVkVGUzSmhjR0p4ZG1GMFgyRmlYM0ptWDNCMmMyVnVjV0pmYm5wMmRHSjk="
FLAG    = "CTF{encoding_no_es_cifrado_amigo}"


def test_solve_returns_flag():
    assert solve(ENCODED) == FLAG


def test_flag_format():
    flag = solve(ENCODED)
    assert flag.startswith("CTF{") and flag.endswith("}")


def test_encoding_chain_invertible():
    """Verifica que el proceso de codificación/decodificación es coherente."""
    original = FLAG
    # Cifrar
    s1 = codecs.encode(original, "rot_13")
    s2 = base64.b64encode(s1.encode()).decode()
    s3 = base64.b64encode(s2.encode()).decode()
    # Descifrar
    assert solve(s3) == original
