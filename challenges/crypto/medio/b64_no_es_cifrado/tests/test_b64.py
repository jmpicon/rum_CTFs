import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from solution import solve
import base64, codecs

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
