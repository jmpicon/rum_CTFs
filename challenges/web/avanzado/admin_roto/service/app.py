from flask import Flask, request, jsonify
import os

app = Flask(__name__)
# Permitimos que la plataforma dinámica inyecte la flag aleatoria
FLAG = os.environ.get("FLAG", "CTF{broken_access_control_demo}")

@app.get("/health")
def health():
    return jsonify(ok=True)

@app.get("/admin")
def admin():
    # Vulnerabilidad DOCENTE: control de acceso basado en parámetro manipulable
    if request.args.get("role") == "admin":
        return jsonify(flag=FLAG)
    return jsonify(error="forbidden"), 403
