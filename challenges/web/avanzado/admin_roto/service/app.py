"""
VaultApp – Demo IDOR (Insecure Direct Object Reference)
========================================================
VULNERABILIDAD DOCENTE: el endpoint /api/documentos/<id> no verifica
que el recurso pertenezca al usuario autenticado. Cualquier usuario
autenticado puede acceder a documentos de cualquier otro usuario
simplemente cambiando el ID numérico en la URL.

Esto ilustra OWASP A01:2021 – Broken Access Control.
"""
from flask import Flask, request, jsonify, session
import os, secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAG = os.environ.get("FLAG", "CTF{idor_el_id_no_es_autorizacion}")

# ── Base de usuarios simulada ──────────────────────────────
USERS = {
    "admin":    {"id": 1,    "password": secrets.token_hex(16), "rol": "admin"},
    "invitado": {"id": 1001, "password": "invitado123",          "rol": "user"},
}

# ── Documentos privados por usuario ───────────────────────
DOCUMENTOS = {
    1: [
        {"id": 1,  "titulo": "Contraseñas del sistema",  "contenido": "root:ultrasecret!"},
        {"id": 2,  "titulo": "FLAG CONFIDENCIAL",        "contenido": FLAG},
        {"id": 3,  "titulo": "Notas de admin",           "contenido": "Recordar renovar el certificado SSL."},
    ],
    1001: [
        {"id": 101, "titulo": "Mi lista de tareas",   "contenido": "Hacer la compra, estudiar CTF."},
        {"id": 102, "titulo": "Notas de clase",        "contenido": "Apuntes de criptografía básica."},
    ],
}


def get_current_user():
    uid = session.get("user_id")
    for u in USERS.values():
        if u["id"] == uid:
            return u
    return None


# ── Endpoints ─────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify(ok=True)


@app.get("/")
def index():
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>VaultApp</title>
<style>
  body{font-family:sans-serif;max-width:600px;margin:80px auto;padding:0 20px}
  input,button{padding:8px;margin:4px;width:100%;box-sizing:border-box}
  button{background:#2563eb;color:#fff;border:none;cursor:pointer;border-radius:4px}
  pre{background:#f3f4f6;padding:12px;border-radius:4px;overflow-x:auto}
</style></head>
<body>
<h1>🔒 VaultApp</h1>
<p>Gestión segura de documentos privados.</p>

<h2>Iniciar sesión</h2>
<input id="user" placeholder="Usuario" value="invitado">
<input id="pass" type="password" placeholder="Contraseña" value="invitado123">
<button onclick="login()">Entrar</button>

<h2>Mis documentos</h2>
<button onclick="getMisDocs()">Cargar mis documentos</button>
<pre id="out">—</pre>

<script>
async function login() {
  const r = await fetch('/api/login', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      usuario: document.getElementById('user').value,
      password: document.getElementById('pass').value
    })
  });
  const d = await r.json();
  document.getElementById('out').textContent = JSON.stringify(d, null, 2);
}

async function getMisDocs() {
  const r = await fetch('/api/mis-documentos');
  const d = await r.json();
  document.getElementById('out').textContent = JSON.stringify(d, null, 2);
}
</script>
</body></html>"""


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("usuario", "")
    password = data.get("password", "")

    user = USERS.get(username)
    if user and user["password"] == password:
        session["user_id"] = user["id"]
        return jsonify(
            mensaje="Login correcto",
            usuario=username,
            tu_id_de_usuario=user["id"],
            rol=user["rol"],
            hint="Tus documentos están en /api/mis-documentos"
        )
    return jsonify(error="Credenciales incorrectas"), 401


@app.get("/api/mis-documentos")
def mis_documentos():
    user = get_current_user()
    if not user:
        return jsonify(error="No autenticado. Llama a /api/login primero."), 401

    docs = DOCUMENTOS.get(user["id"], [])
    return jsonify(
        usuario_id=user["id"],
        documentos=[{"id": d["id"], "titulo": d["titulo"]} for d in docs]
    )


@app.get("/api/documentos/<int:doc_id>")
def ver_documento(doc_id):
    """
    VULNERABILIDAD IDOR: No se verifica que el documento pertenezca
    al usuario autenticado. Solo se comprueba que el usuario esté logado.
    """
    user = get_current_user()
    if not user:
        return jsonify(error="No autenticado."), 401

    # Buscar el documento en TODOS los usuarios (¡aquí está el bug!)
    for uid, docs in DOCUMENTOS.items():
        for doc in docs:
            if doc["id"] == doc_id:
                return jsonify(documento=doc)

    return jsonify(error="Documento no encontrado."), 404
