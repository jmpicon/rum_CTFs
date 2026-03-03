#!/usr/bin/env python3
"""
solution.py — Tráfico Sospechoso  [SOLO DOCENTE]
================================================
Extrae la flag desde un PCAP buscando el comando FTP:
    PASS CTF{...}
"""
import re


FLAG_RE = re.compile(rb"PASS\s+(CTF\{[^}\r\n]+\})", re.IGNORECASE)


def solve(path: str = "captura.pcap") -> str:
    """
    Método robusto y sin dependencias: buscar directamente en bytes.
    Funciona incluso si no hay scapy/tshark instalados.
    """
    data = open(path, "rb").read()
    match = FLAG_RE.search(data)
    if not match:
        raise ValueError("No se encontró la flag en el PCAP")
    flag = match.group(1).decode("ascii", errors="ignore")
    print(f"[+] FLAG encontrada: {flag}")
    return flag


if __name__ == "__main__":
    flag = solve("captura.pcap")
    assert flag.startswith("CTF{") and flag.endswith("}")
