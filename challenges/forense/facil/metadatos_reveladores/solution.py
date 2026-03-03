#!/usr/bin/env python3
"""
solution.py — Metadatos Reveladores  [SOLO DOCENTE]
====================================================
Extrae el campo EXIF 'Artist' de foto_gato.jpg usando Pillow + piexif.
También funciona con subprocess + exiftool.
"""
import os, subprocess


def solve_with_pillow(path: str = "foto_gato.jpg") -> str:
    """Extrae la flag del campo EXIF Artist usando Pillow."""
    try:
        import piexif
        from PIL import Image
        img = Image.open(path)
        exif_data = piexif.load(img.info.get("exif", b""))
        artist = exif_data["0th"].get(piexif.ImageIFD.Artist, b"")
        flag = artist.decode("utf-8", errors="ignore")
        print(f"[+] FLAG (campo Artist): {flag}")
        return flag
    except ImportError:
        print("[!] Pillow/piexif no disponibles. Prueba con exiftool.")
        return solve_with_exiftool(path)


def solve_with_exiftool(path: str = "foto_gato.jpg") -> str:
    """Extrae la flag usando exiftool (si está instalado)."""
    try:
        result = subprocess.check_output(
            ["exiftool", "-Artist", path], text=True
        )
        flag = result.split(":")[-1].strip()
        print(f"[+] FLAG (exiftool): {flag}")
        return flag
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] exiftool no encontrado. Instala con: apt install exiftool")
        return ""


def solve_raw_exif(path: str = "foto_gato.jpg") -> str:
    """
    Método bruto: busca la flag directamente en los bytes del JPEG.
    Útil si no tienes ninguna librería instalada.
    """
    data = open(path, "rb").read()
    idx = data.find(b"CTF{")
    if idx >= 0:
        end = data.index(b"}", idx) + 1
        flag = data[idx:end].decode("ascii")
        print(f"[+] FLAG (búsqueda bruta): {flag}")
        return flag
    print("[!] Flag no encontrada en el fichero.")
    return ""


if __name__ == "__main__":
    flag = solve_with_pillow()
    if not flag:
        flag = solve_raw_exif()
    assert flag.startswith("CTF{"), f"Flag inválida: {flag}"
