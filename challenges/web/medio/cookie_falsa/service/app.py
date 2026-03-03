"""
TokenBank — Demo Cookie/Token tampering
========================================
VULNERABILIDAD DOCENTE: el token de sesión es simplemente un JSON
codificado en Base64, sin firma ni MAC. Cualquier cliente puede
decodificarlo, modificar el campo "rol" a "admin" y re-enviarlo.

Esto ilustra por qué los tokens de sesión DEBEN estar firmados
(HMAC, JWT con secreto, etc.) y nunca confiar en datos del cliente
sin verificación criptográfica.
"""
from flask import Flask, request, jsonify, make_response
import base64, json, os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{nunca_confies_en_el_cliente}")

USERS = {
    "alumno": "alumno123",
    "profesor": "clase2024",
}


def make_token(username: str, rol: str) -> str:
    """Crea un 'token' inseguro: JSON en Base64 sin firma."""
    payload = {"usuario": username, "rol": rol}
    return base64.b64encode(json.dumps(payload).encode()).decode()


def decode_token(token: str) -> dict | None:
    """Decodifica el token. Sin verificación de integridad."""
    try:
        data = json.loads(base64.b64decode(token).decode())
        return data
    except Exception:
        return None


# ── Páginas ────────────────────────────────────────────────

@app.get("/")
def index():
    token = request.cookies.get("session_token")
    user_info = ""
    if token:
        data = decode_token(token)
        if data:
            user_info = f"<p>Sesión activa: <strong>{data.get('usuario')}</strong> (rol: {data.get('rol')})</p>"

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>TokenBank</title>
<style>
  body{{font-family:sans-serif;max-width:600px;margin:60px auto;padding:20px}}
  input,button{{padding:10px;margin:5px;width:100%;box-sizing:border-box}}
  button{{background:#7c3aed;color:#fff;border:none;cursor:pointer;border-radius:6px}}
  .info{{background:#ede9fe;border-left:4px solid #7c3aed;padding:10px;margin:10px 0}}
</style></head>
<body>
<h1>🏦 TokenBank</h1>
<div class="info">Sistema de sesiones seguro™️ con tokens propietarios.</div>
{user_info}
<h2>Iniciar sesión</h2>
<input id="u" placeholder="Usuario">
<input id="p" type="password" placeholder="Contraseña">
<button onclick="login()">Entrar</button>
<button onclick="goAdmin()" style="background:#dc2626;margin-top:20px">
  Intentar acceso /admin
</button>
<pre id="out" style="background:#f3f4f6;padding:10px;border-radius:4px;margin-top:20px"></pre>
<script>
async function login() {{
  const r = await fetch('/api/login', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{
      usuario: document.getElementById('u').value,
      password: document.getElementById('p').value
    }})
  }});
  const d = await r.json();
  document.getElementById('out').textContent = JSON.stringify(d, null, 2);
  if (d.token) location.reload();
}}
async function goAdmin() {{
  const r = await fetch('/admin');
  const d = await r.json();
  document.getElementById('out').textContent = JSON.stringify(d, null, 2);
}}
</script>
</body></html>"""


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("usuario", "")
    password = data.get("password", "")

    if USERS.get(username) == password:
        token = make_token(username, "user")
        resp = make_response(jsonify(
            mensaje="Login correcto",
            token=token,
            pista="Tu token de sesión se guardará como cookie 'session_token'. "
                  "Decodifícalo con Base64 para ver su contenido.",
        ))
        resp.set_cookie("session_token", token, httponly=False)  # httponly=False: visible en JS
        return resp

    return jsonify(error="Credenciales incorrectas"), 401


@app.get("/admin")
def admin():
    """Solo accesible si el token dice rol=admin."""
    token = request.cookies.get("session_token")
    if not token:
        return jsonify(error="Sin sesión. Inicia sesión primero."), 401

    data = decode_token(token)
    if not data:
        return jsonify(error="Token malformado."), 400

    # VULNERABILIDAD: confiamos ciegamente en el campo 'rol' del token
    if data.get("rol") != "admin":
        return jsonify(
            error="Acceso denegado.",
            tu_rol=data.get("rol"),
            necesitas="admin"
        ), 403

    return jsonify(
        mensaje="¡Acceso admin conseguido!",
        usuario=data.get("usuario"),
        flag=FLAG,
        leccion="Nunca confíes en datos del cliente sin firma criptográfica (HMAC/JWT)."
    )
