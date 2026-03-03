#!/usr/bin/env python3
"""
solution.py — PYC Misterioso  [SOLO DOCENTE]
============================================
Recupera la flag de un fichero .pyc recorriendo constantes del code object.
"""
from __future__ import annotations

import marshal
import re
import types

FLAG_PATTERN = re.compile(r"CTF\{[^}]+\}")


def _walk_consts(code_obj: types.CodeType):
    for c in code_obj.co_consts:
        yield c
        if isinstance(c, types.CodeType):
            yield from _walk_consts(c)


def solve(path: str = "misterioso.pyc") -> str:
    with open(path, "rb") as f:
        data = f.read()

    # Header de .pyc (16 bytes en versiones modernas de Python)
    code_obj = marshal.loads(data[16:])

    for const in _walk_consts(code_obj):
        if isinstance(const, str):
            m = FLAG_PATTERN.search(const)
            if m:
                flag = m.group(0)
                print(f"[+] FLAG encontrada: {flag}")
                return flag

    raise ValueError("No se encontró ninguna flag en el bytecode")


if __name__ == "__main__":
    result = solve("misterioso.pyc")
    assert result.startswith("CTF{") and result.endswith("}")
