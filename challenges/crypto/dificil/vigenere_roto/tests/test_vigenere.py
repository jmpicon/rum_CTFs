import importlib.util, pathlib, re

_sol = importlib.util.spec_from_file_location(
    "vigenere_solution",
    pathlib.Path(__file__).parent.parent / "solution.py"
)
_mod = importlib.util.module_from_spec(_sol)
_sol.loader.exec_module(_mod)
vigenere_decrypt = _mod.vigenere_decrypt
solve = _mod.solve

CT_PATH = pathlib.Path(__file__).parent.parent / "ciphertext.txt"
FLAG    = "CTF{vigenere_cae_ante_la_estadistica}"
KEY     = "SEGURO"


def test_decrypt_with_known_key():
    ct = CT_PATH.read_text()
    plain = vigenere_decrypt(ct, KEY)
    assert FLAG in plain


def test_solve_returns_flag():
    ct = CT_PATH.read_text()
    flag = solve(ct)
    assert flag == FLAG


def test_vigenere_roundtrip():
    """Cifrar y descifrar devuelve el original."""
    original = "HolaMundo"

    def vigenere_encrypt(text, key):
        key = key.upper()
        result = []
        ki = 0
        for ch in text:
            if ch.isalpha():
                shift = ord(key[ki % len(key)]) - ord("A")
                if ch.isupper():
                    result.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
                else:
                    result.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
                ki += 1
            else:
                result.append(ch)
        return "".join(result)

    encrypted = vigenere_encrypt(original, KEY)
    assert vigenere_decrypt(encrypted, KEY) == original


def test_flag_in_ciphertext_file():
    ct = CT_PATH.read_text()
    plain = vigenere_decrypt(ct, KEY)
    matches = re.findall(r"CTF\{[^}]+\}", plain)
    assert len(matches) == 1
    assert matches[0] == FLAG
