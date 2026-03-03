#!/usr/bin/env python3
"""
solution.py — B64 no es Cifrado  [SOLO DOCENTE]
================================================
Proceso inverso: B64 → B64 → ROT13 (en orden inverso al cifrado)

Cifrado aplicó: ROT13 → B64 → B64
Descifrado:     B64^-1 → B64^-1 → ROT13^-1
"""
import base64, codecs


def solve(encoded: str) -> str:
    # Capa 3 inversa: decodificar Base64 exterior
    step1 = base64.b64decode(encoded.strip()).decode()
    print(f"[*] Tras primer b64decode : {step1}")

    # Capa 2 inversa: decodificar Base64 interior
    step2 = base64.b64decode(step1.strip()).decode()
    print(f"[*] Tras segundo b64decode: {step2}")

    # Capa 1 inversa: deshacer ROT13 (ROT13 es su propio inverso)
    flag = codecs.decode(step2, "rot_13")
    print(f"[+] FLAG: {flag}")
    return flag


if __name__ == "__main__":
    encoded = open("encoded.txt").read().strip()
    solve(encoded)
