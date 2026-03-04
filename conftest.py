"""
conftest.py — Raíz del proyecto CTF
=====================================
Proporciona el fixture load_solution que carga solution.py por ruta
absoluta, evitando colisiones entre módulos con el mismo nombre.
"""
import importlib.util
import sys
import pathlib
import pytest


def _load_solution(test_file_path: str):
    """
    Carga el solution.py del reto al que pertenece el test.
    Usa el directorio padre del directorio tests/ como raíz del reto.
    """
    test_dir     = pathlib.Path(test_file_path).parent        # .../tests/
    challenge_dir = test_dir.parent                            # .../challenge_name/
    solution_path = challenge_dir / "solution.py"

    if not solution_path.exists():
        pytest.skip(f"solution.py no encontrado en {challenge_dir}")

    # Nombre único para evitar colisiones en sys.modules
    module_name = f"_solution_{challenge_dir.name}_{id(challenge_dir)}"

    spec   = importlib.util.spec_from_file_location(module_name, solution_path)
    module = importlib.util.module_from_spec(spec)

    # Añadir el directorio del reto al path para que solution.py
    # pueda importar sus propios artefactos (ciphertext.hex, etc.)
    old_dir = str(challenge_dir)
    sys.path.insert(0, old_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        if old_dir in sys.path:
            sys.path.remove(old_dir)

    return module


@pytest.fixture
def solution(request):
    """
    Fixture: devuelve el módulo solution.py del reto actual.

    Uso en tests:
        def test_algo(solution):
            flag = solution.solve(...)
            assert flag == "CTF{...}"
    """
    return _load_solution(request.fspath)
