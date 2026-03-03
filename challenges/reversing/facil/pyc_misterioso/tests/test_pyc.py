import os
import sys
import pytest
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

PYC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "misterioso.pyc")
SOLUTION_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "solution.py")
FLAG = "CTF{el_bytecode_tambien_habla}"


@pytest.mark.skipif(not os.path.exists(PYC_PATH), reason="misterioso.pyc no generado. Ejecuta gen.py")
def test_pyc_exists():
    assert os.path.exists(PYC_PATH)
    assert os.path.getsize(PYC_PATH) > 100


@pytest.mark.skipif(not os.path.exists(PYC_PATH), reason="misterioso.pyc no generado. Ejecuta gen.py")
def test_flag_present_in_pyc_blob():
    data = open(PYC_PATH, "rb").read()
    assert b"CTF{" in data
    assert FLAG.encode() in data


@pytest.mark.skipif(not os.path.exists(PYC_PATH), reason="misterioso.pyc no generado. Ejecuta gen.py")
def test_solution_extracts_flag():
    spec = importlib.util.spec_from_file_location("pyc_solution", SOLUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    assert module.solve(PYC_PATH) == FLAG
