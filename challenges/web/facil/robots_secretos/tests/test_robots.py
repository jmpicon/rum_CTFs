"""
Tests del reto Robots Secretos.
Requiere el servicio Docker corriendo en localhost:8081.
"""
import requests, time, pytest

BASE = "http://localhost:8081"


def _service_up(timeout=3):
    try:
        return requests.get(f"{BASE}/health", timeout=timeout).status_code == 200
    except Exception:
        return False


skip_if_down = pytest.mark.skipif(
    not _service_up(), reason="Servicio robots_secretos no disponible (arranca Docker)"
)


def wait_up(timeout=15):
    for _ in range(timeout * 5):
        if _service_up(1):
            return
        time.sleep(0.2)
    pytest.skip("Servicio no disponible tras esperar")


@skip_if_down
def test_robots_txt_exists():
    wait_up()
    r = requests.get(f"{BASE}/robots.txt")
    assert r.status_code == 200
    assert "Disallow" in r.text


@skip_if_down
def test_robots_txt_reveals_path():
    r = requests.get(f"{BASE}/robots.txt")
    assert "panel_4dm1n_s3cr3t0" in r.text


@skip_if_down
def test_decoy_routes_blocked():
    assert requests.get(f"{BASE}/backup_2024").status_code in (403, 410)
    assert requests.get(f"{BASE}/config.bak").status_code in (403, 410)


@skip_if_down
def test_flag_at_hidden_path():
    r = requests.get(f"{BASE}/panel_4dm1n_s3cr3t0")
    assert r.status_code == 200
    assert "CTF{" in r.text
    assert "robots_txt_no_es_seguridad" in r.text
