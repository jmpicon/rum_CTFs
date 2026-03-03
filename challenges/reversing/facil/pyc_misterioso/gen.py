#!/usr/bin/env python3
"""
gen.py — Generador de bytecode Python para reto de reversing  [SOLO DOCENTE]
===========================================================================
Genera `misterioso.pyc` desde un script temporal y elimina el fuente.
"""
from __future__ import annotations

import os
import pathlib
import py_compile
import shutil
import tempfile

FLAG = "CTF{el_bytecode_tambien_habla}"

SOURCE_TEMPLATE = f"""#!/usr/bin/env python3
def banner():
    return "Sistema de verificacion interna"

def validar(entrada: str) -> bool:
    # La flag real vive en bytecode (co_consts)
    objetivo = "{FLAG}"
    return entrada == objetivo

if __name__ == "__main__":
    dato = input("Introduce token: ").strip()
    if validar(dato):
        print("Acceso concedido")
    else:
        print("Acceso denegado")
"""


def generate(output_path: str = "misterioso.pyc") -> str:
    output = pathlib.Path(output_path).resolve()

    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "misterioso.py"
        src.write_text(SOURCE_TEMPLATE, encoding="utf-8")

        compiled = py_compile.compile(str(src), doraise=True)
        shutil.copy2(compiled, output)

    print(f"[+] Generado: {output}")
    print(f"[+] Flag embebida en bytecode: {FLAG}")
    return str(output)


if __name__ == "__main__":
    generate("misterioso.pyc")
