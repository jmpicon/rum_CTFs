import requests
import time

BASE = "http://localhost:8080"

def wait_up():
    for _ in range(30):
        try:
            r = requests.get(f"{BASE}/health", timeout=1)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("service not up")

def test_flag_reachable_in_demo_way():
    wait_up()
    r = requests.get(f"{BASE}/admin?role=admin", timeout=2)
    assert r.status_code == 200
    data = r.json()
    assert data["flag"].startswith("CTF{")
