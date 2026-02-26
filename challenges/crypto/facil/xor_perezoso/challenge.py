# Generador de reto (ejemplo educativo)
FLAG = b"CTF{xor_es_lineal_pero_ensena_algo}"
KEY = b"classkey"

def xor_bytes(data: bytes, key: bytes) -> bytes:
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)])
    return bytes(out)

if __name__ == "__main__":
    ct = xor_bytes(FLAG, KEY)
    print(ct.hex())
