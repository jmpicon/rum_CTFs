#!/usr/bin/env python3
"""
solution.py — Vigenère Roto  [SOLO DOCENTE]
============================================
Técnica: Análisis de frecuencias + longitud de clave conocida.
La clave tiene 6 letras. Asumimos texto en español/inglés.
"""
from collections import Counter


def vigenere_decrypt(text: str, key: str) -> str:
    key = key.upper()
    result = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[ki % len(key)]) - ord("A")
            if ch.isupper():
                result.append(chr((ord(ch) - ord("A") - shift) % 26 + ord("A")))
            else:
                result.append(chr((ord(ch) - ord("a") - shift) % 26 + ord("a")))
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def recover_key_freq(ciphertext: str, key_length: int,
                     assumed_most_common: str = "a") -> str:
    """
    Recupera la clave por análisis de frecuencias.
    Para cada posición i (0..key_length-1), extrae las letras cifradas
    en esa posición y asume que la letra más frecuente corresponde a
    'assumed_most_common' en el texto plano.
    """
    only_letters = [c for c in ciphertext if c.isalpha()]
    key = []
    for i in range(key_length):
        group = [c.upper() for j, c in enumerate(only_letters) if j % key_length == i]
        most_common_cipher = Counter(group).most_common(1)[0][0]
        # shift = ord(cipher_letter) - ord(plain_letter) (mod 26)
        shift = (ord(most_common_cipher) - ord(assumed_most_common.upper())) % 26
        key.append(chr(shift + ord("A")))
    return "".join(key)


def solve(ciphertext: str) -> str:
    KEY_LENGTH = 6

    # Intentar con 'a' como letra más común del texto plano
    key_candidate = recover_key_freq(ciphertext, KEY_LENGTH, "a")
    print(f"[*] Clave candidata (asumiendo 'a'): {key_candidate}")

    decrypted = vigenere_decrypt(ciphertext, key_candidate)
    print(f"[*] Muestra descifrada: {decrypted[:80]}")

    # La clave correcta es "SEGURO"
    KEY = "SEGURO"
    result = vigenere_decrypt(ciphertext, KEY)
    print(f"\n[+] Con clave '{KEY}':")
    print(result)

    # Extraer flag
    import re
    match = re.search(r"CTF\{[^}]+\}", result)
    flag = match.group(0) if match else "FLAG no encontrada"
    print(f"\n[+] FLAG: {flag}")
    return flag


if __name__ == "__main__":
    ct = open("ciphertext.txt").read()
    solve(ct)
