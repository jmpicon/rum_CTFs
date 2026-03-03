import os
import sys
import pytest
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

PCAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "captura.pcap")
SOLUTION_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "solution.py")
FLAG = "CTF{sniffing_texto_plano_es_peligroso}"


@pytest.mark.skipif(not os.path.exists(PCAP_PATH), reason="captura.pcap no generada. Ejecuta gen.py")
def test_pcap_exists():
    assert os.path.exists(PCAP_PATH)
    assert os.path.getsize(PCAP_PATH) > 100


@pytest.mark.skipif(not os.path.exists(PCAP_PATH), reason="captura.pcap no generada. Ejecuta gen.py")
def test_flag_in_raw_bytes():
    data = open(PCAP_PATH, "rb").read()
    assert FLAG.encode() in data


@pytest.mark.skipif(not os.path.exists(PCAP_PATH), reason="captura.pcap no generada. Ejecuta gen.py")
def test_solver_extracts_flag():
    spec = importlib.util.spec_from_file_location("trafico_solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    flag = module.solve(PCAP_PATH)
    assert flag == FLAG
