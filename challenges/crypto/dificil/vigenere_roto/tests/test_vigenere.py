import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from solution import vigenere_decrypt, solve

CT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ciphertext.txt")
FLAG    = "CTF{vigenere_cae_ante_la_estadistica}"
KEY     = "SEGURO"


def test_decrypt_with_known_key():
    ct = open(CT_PATH).read()
    plain = vigenere_decrypt(ct, KEY)
    assert FLAG in plain


def test_solve_returns_flag():
    ct = open(CT_PATH).read()
    flag = solve(ct)
    assert flag == FLAG


def test_vigenere_roundtrip():
    """Cifrar y descifrar devuelve el original."""
    from solution import vigenere_decrypt
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
    ct = open(CT_PATH).read()
    plain = vigenere_decrypt(ct, KEY)
    matches = re.findall(r"CTF\{[^}]+\}", plain)
    assert len(matches) == 1
    assert matches[0] == FLAG
