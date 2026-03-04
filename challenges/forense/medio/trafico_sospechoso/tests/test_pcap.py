"""
Tests del reto Tráfico Sospechoso.
Requiere que gen.py haya sido ejecutado para generar captura.pcap.
"""
import importlib.util, pathlib, pytest

_sol = importlib.util.spec_from_file_location(
    "pcap_solution",
    pathlib.Path(__file__).parent.parent / "solution.py"
)
_mod = importlib.util.module_from_spec(_sol)
_sol.loader.exec_module(_mod)
solve = _mod.solve

PCAP_PATH = pathlib.Path(__file__).parent.parent / "captura.pcap"
FLAG = "CTF{sniffing_texto_plano_es_peligroso}"

skip_if_no_pcap = pytest.mark.skipif(
    not PCAP_PATH.exists(), reason="captura.pcap no generada. Ejecuta gen.py"
)


@skip_if_no_pcap
def test_pcap_exists():
    assert PCAP_PATH.exists()
    assert PCAP_PATH.stat().st_size > 50


@skip_if_no_pcap
def test_flag_in_raw_bytes():
    """La flag debe estar en los bytes del PCAP (en el PASS FTP)."""
    data = PCAP_PATH.read_bytes()
    assert FLAG.encode() in data, "La flag no está en los bytes del PCAP"


@skip_if_no_pcap
def test_ftp_pass_command_present():
    """El patrón FTP PASS debe estar presente."""
    data = PCAP_PATH.read_bytes()
    assert b"PASS " in data, "No hay comando PASS en el PCAP"
    assert b"USER " in data, "No hay comando USER en el PCAP"


@skip_if_no_pcap
def test_solve_extracts_flag():
    flag = solve(str(PCAP_PATH))
    assert flag == FLAG


@skip_if_no_pcap
def test_flag_format():
    flag = solve(str(PCAP_PATH))
    assert flag.startswith("CTF{") and flag.endswith("}")
