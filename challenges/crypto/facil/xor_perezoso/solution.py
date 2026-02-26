def xor_bytes(data: bytes, key: bytes) -> bytes:
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)])
    return bytes(out)

def solve(cipher_hex: str, key: bytes) -> str:
    ct = bytes.fromhex(cipher_hex)
    return xor_bytes(ct, key).decode("utf-8", errors="strict")
