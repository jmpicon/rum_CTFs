import requests, time

BASE = "http://localhost:8081"


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        try:
            if requests.get(f"{BASE}/health", timeout=1).status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Servicio no disponible")


def test_robots_txt_exists():
    wait_up()
    r = requests.get(f"{BASE}/robots.txt")
    assert r.status_code == 200
    assert "Disallow" in r.text


def test_robots_txt_reveals_path():
    r = requests.get(f"{BASE}/robots.txt")
    assert "panel_4dm1n_s3cr3t0" in r.text


def test_decoy_routes_blocked():
    assert requests.get(f"{BASE}/backup_2024").status_code in (403, 410)
    assert requests.get(f"{BASE}/config.bak").status_code in (403, 410)


def test_flag_at_hidden_path():
    r = requests.get(f"{BASE}/panel_4dm1n_s3cr3t0")
    assert r.status_code == 200
    assert "CTF{" in r.text
    assert "robots_txt_no_es_seguridad" in r.text
