"""
SeguraCorp Web — Demo Information Disclosure via robots.txt
============================================================
VULNERABILIDAD DOCENTE: robots.txt revela rutas sensibles.
Aunque el estándar pide a los bots que NO visiten esas rutas,
cualquier persona puede leer robots.txt y acceder directamente.
Esto ilustra que "seguridad por oscuridad" no es seguridad real.
"""
from flask import Flask, Response
import os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{robots_txt_no_es_seguridad}")

# ── Página pública ─────────────────────────────────────────
@app.get("/")
def index():
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>SeguraCorp</title>
<style>
  body{font-family:sans-serif;max-width:700px;margin:80px auto;text-align:center}
  h1{color:#1e40af} p{color:#374151}
</style></head>
<body>
<h1>🏢 SeguraCorp</h1>
<p>Bienvenido a nuestro portal corporativo.</p>
<p>Nuestros sistemas son <strong>completamente seguros</strong>.</p>
<p><em>No hay nada interesante aquí. Circulen.</em></p>
</body></html>"""


# ── robots.txt que revela la ruta oculta ──────────────────
@app.get("/robots.txt")
def robots():
    return Response(
        "User-agent: *\n"
        "Disallow: /panel_4dm1n_s3cr3t0\n"
        "Disallow: /backup_2024\n"
        "Disallow: /config.bak\n",
        mimetype="text/plain"
    )


# ── Rutas falsas (señuelos) ────────────────────────────────
@app.get("/backup_2024")
def backup():
    return Response(
        "Error: backup corrompido. Contacta con soporte.",
        status=403
    )


@app.get("/config.bak")
def config_bak():
    return Response("Fichero eliminado.", status=410)


# ── La ruta real con la flag ───────────────────────────────
@app.get("/panel_4dm1n_s3cr3t0")
def admin_panel():
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>Panel Admin</title>
<style>
  body{{font-family:monospace;background:#0f172a;color:#22d3ee;
       max-width:600px;margin:80px auto;text-align:center;padding:20px}}
  .flag{{background:#164e63;border:1px solid #06b6d4;padding:20px;
         border-radius:8px;font-size:1.3em;margin-top:30px}}
</style></head>
<body>
<h1>🔑 Panel de Administración</h1>
<p>¡Acceso conseguido! El administrador pensó que robots.txt era una cerradura...</p>
<div class="flag">
  <strong>FLAG:</strong><br><br>
  <code>{FLAG}</code>
</div>
<p style="margin-top:30px;font-size:0.8em;color:#94a3b8">
  Lección: robots.txt es una <em>solicitud</em> a los buscadores, no una barrera de seguridad.
</p>
</body></html>"""


@app.get("/health")
def health():
    return {"ok": True}
