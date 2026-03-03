#!/usr/bin/env python3
"""
challenge.py  —  XOR Perezoso
==============================
Este script muestra CÓMO se cifró el mensaje.
Tu misión es encontrar la KEY y descifrar ciphertext.hex

La KEY tiene exactamente 8 bytes.
XOR(XOR(mensaje, KEY), KEY) == mensaje  ← ¡usa esto a tu favor!
"""

def xor_bytes(data: bytes, key: bytes) -> bytes:
    """Aplica XOR byte a byte repitiendo la clave."""
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


if __name__ == "__main__":
    # Así se generó ciphertext.hex (la KEY está oculta):
    #
    #   FLAG = b"CTF{...}"
    #   KEY  = b"????????"   ← 8 bytes, encuéntrala
    #   ct   = xor_bytes(FLAG, KEY)
    #   open("ciphertext.hex", "w").write(ct.hex())
    #
    # Pista: el texto en claro empieza con b"CTF{"

    ciphertext_hex = open("ciphertext.hex").read().strip()
    ct = bytes.fromhex(ciphertext_hex)
    print(f"Longitud del ciphertext: {len(ct)} bytes")
    print(f"Primeros 8 bytes (hex): {ct[:8].hex()}")
    print()
    print("¿Cuál es la clave? Impleméntalo aquí:")

    # TODO: descubre KEY y descomenta la siguiente línea
    # KEY = b"????????"
    # print("FLAG:", xor_bytes(ct, KEY).decode())
