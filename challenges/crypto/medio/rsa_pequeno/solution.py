#!/usr/bin/env python3
"""
solution.py — RSA: Primer Contacto  [SOLO DOCENTE]
===================================================
Ataque: factorización de n pequeño + descifrado RSA clásico.
"""


def factorize(n: int) -> tuple[int, int]:
    """Factoriza n buscando el factor primo p por fuerza bruta."""
    if n % 2 == 0:
        return 2, n // 2
    p = next(i for i in range(3, int(n**0.5) + 2, 2) if n % i == 0)
    return p, n // p


def solve(n: int, e: int, ciphertexts: list[int]) -> str:
    # Paso 1: Factorizar n
    p, q = factorize(n)
    print(f"[*] n = {n}")
    print(f"[*] p = {p}, q = {q}  (verificación: p×q = {p*q} == n: {p*q==n})")

    # Paso 2: Calcular φ(n)
    phi = (p - 1) * (q - 1)
    print(f"[*] φ(n) = {phi}")

    # Paso 3: Calcular d = e^-1 mod φ(n)
    d = pow(e, -1, phi)
    print(f"[*] d = {d}")

    # Paso 4 y 5: Descifrar y convertir a texto
    flag = "".join(chr(pow(c, d, n)) for c in ciphertexts)
    print(f"[+] FLAG: {flag}")
    return flag


if __name__ == "__main__":
    n, e = 81072007, 65537
    ct_line = open("ciphertext.txt").read()
    ciphertexts = [int(x) for x in ct_line if x.strip().startswith("#") is False
                   for x in ct_line.split("\n") if not x.startswith("#") and x.strip()][0].split(",")
    # Parse limpio
    ciphertexts = []
    for line in open("ciphertext.txt"):
        if not line.startswith("#") and line.strip():
            ciphertexts = list(map(int, line.strip().split(",")))
            break

    solve(n, e, ciphertexts)
