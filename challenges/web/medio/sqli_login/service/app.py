"""
AdminPortal — Demo SQL Injection (Login Bypass)
================================================
VULNERABILIDAD DOCENTE: la consulta SQL se construye concatenando
directamente los inputs del usuario sin sanitizar ni usar
consultas parametrizadas.

Esto ilustra OWASP A03:2021 – Injection.

Payloads de ejemplo que funcionan:
  usuario=' OR '1'='1    contraseña=cualquiera
  usuario=admin'--        contraseña=(vacía)
  usuario=' OR 1=1--     contraseña=(vacía)
"""
import sqlite3, os
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(32)
FLAG = os.environ.get("FLAG", "CTF{sqli_las_comillas_mandan}")

# ── Base de datos en memoria ───────────────────────────────
def get_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


# Base de datos global (demo, no usar en producción)
DB = get_db()

def init_db():
    DB.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        usuario TEXT UNIQUE,
        contrasena TEXT,
        rol TEXT,
        secreto TEXT
    )""")
    DB.execute("INSERT OR IGNORE INTO usuarios VALUES (1,'admin','S3cr3tP4ss!Admin','admin',?)",
               (FLAG,))
    DB.execute("INSERT OR IGNORE INTO usuarios VALUES (2,'juan','password123','user','nada_interesante')")
    DB.execute("INSERT OR IGNORE INTO usuarios VALUES (3,'maria','qwerty','user','nada_interesante')")
    DB.commit()


init_db()


# ── Endpoints ─────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify(ok=True)


@app.get("/")
def index():
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>AdminPortal</title>
<style>
  *{box-sizing:border-box} body{font-family:sans-serif;background:#0f172a;
  color:#e2e8f0;display:flex;align-items:center;justify-content:center;
  min-height:100vh;margin:0}
  .card{background:#1e293b;padding:40px;border-radius:12px;width:380px;
        box-shadow:0 4px 24px rgba(0,0,0,.5)}
  h1{text-align:center;color:#38bdf8;margin:0 0 30px}
  input{width:100%;padding:12px;margin:8px 0;background:#0f172a;border:1px solid #334155;
        color:#e2e8f0;border-radius:6px}
  button{width:100%;padding:12px;background:#0ea5e9;color:#fff;border:none;
         border-radius:6px;cursor:pointer;font-size:1em;margin-top:10px}
  button:hover{background:#0284c7}
  #result{margin-top:20px;background:#0f172a;padding:15px;border-radius:6px;
          font-family:monospace;white-space:pre-wrap;font-size:.85em}
  .hint{font-size:.75em;color:#64748b;margin-top:20px;text-align:center}
</style></head>
<body>
<div class="card">
  <h1>🔐 AdminPortal</h1>
  <input id="u" placeholder="Usuario" autocomplete="off">
  <input id="p" type="password" placeholder="Contraseña">
  <button onclick="doLogin()">Iniciar sesión</button>
  <div id="result">—</div>
  <p class="hint">¿No tienes credenciales? Quizá no las necesitas...</p>
</div>
<script>
async function doLogin() {
  const r = await fetch('/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      usuario: document.getElementById('u').value,
      password: document.getElementById('p').value
    })
  });
  const d = await r.json();
  document.getElementById('result').textContent = JSON.stringify(d, null, 2);
}
</script>
</body></html>"""


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario  = data.get("usuario", "")
    password = data.get("password", "")

    # VULNERABILIDAD: concatenación directa de inputs en la query SQL
    query = f"SELECT * FROM usuarios WHERE usuario='{usuario}' AND contrasena='{password}'"

    try:
        row = DB.execute(query).fetchone()
    except sqlite3.OperationalError as e:
        return jsonify(
            error="Error en la consulta SQL",
            detalle=str(e),          # ← también expone info útil para el atacante
            query_ejecutada=query
        ), 500

    if row:
        return jsonify(
            mensaje=f"¡Bienvenido, {row['usuario']}!",
            rol=row['rol'],
            secreto=row['secreto'],   # ← muestra el secreto del usuario autenticado
            query_ejecutada=query
        )

    return jsonify(
        error="Credenciales incorrectas.",
        query_ejecutada=query         # ← NUNCA hagas esto en producción
    ), 401
