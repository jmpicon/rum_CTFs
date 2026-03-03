#!/usr/bin/env python3
"""
solution.py  —  XOR Perezoso  [SOLO DOCENTE]
=============================================
Técnica: Known-Plaintext Attack (KPA)
Sabemos que el flag empieza con "CTF{" → podemos recuperar los
primeros 4 bytes de la clave. Como la clave tiene 8 bytes y se repite,
y la longitud del ciphertext nos da más bytes de la clave conocidos.
"""

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def recover_key_kpa(ct: bytes, known_plain: bytes) -> bytes:
    """Recupera bytes de clave usando texto en claro conocido."""
    return bytes([ct[i] ^ known_plain[i] for i in range(len(known_plain))])


def solve(ciphertext_hex: str) -> str:
    ct = bytes.fromhex(ciphertext_hex)

    # Paso 1: Known-Plaintext Attack con el prefijo "CTF{"
    known = b"CTF{"
    partial_key = recover_key_kpa(ct, known)
    # partial_key = primeros 4 bytes de la clave: b"clas"
    print(f"[*] Primeros 4 bytes de clave recuperados: {partial_key}")

    # Paso 2: La clave tiene 8 bytes → obtenemos más bytes del texto
    # si descifro parcialmente con esos 4 bytes obtengo más contexto
    # Sabiendo que la palabra inglesa "clas" → "classkey"
    # (un alumno puede probar extensiones o analizar más bytes)
    KEY = b"classkey"
    flag = xor_bytes(ct, KEY).decode("utf-8")
    print(f"[*] Clave completa: {KEY}")
    print(f"[+] FLAG: {flag}")
    return flag


if __name__ == "__main__":
    ct_hex = open("ciphertext.hex").read().strip()
    solve(ct_hex)
