"""
Tests del reto Metadatos Reveladores.
Requiere que gen.py haya sido ejecutado para generar foto_gato.jpg.
"""
import importlib.util, pathlib, pytest

_sol = importlib.util.spec_from_file_location(
    "meta_solution",
    pathlib.Path(__file__).parent.parent / "solution.py"
)
_mod = importlib.util.module_from_spec(_sol)
_sol.loader.exec_module(_mod)
solve_raw_exif = _mod.solve_raw_exif
solve_with_pillow = _mod.solve_with_pillow

IMG_PATH = pathlib.Path(__file__).parent.parent / "foto_gato.jpg"
FLAG = "CTF{exif_revela_mas_de_lo_que_crees}"

skip_if_no_image = pytest.mark.skipif(
    not IMG_PATH.exists(), reason="foto_gato.jpg no generada. Ejecuta gen.py"
)


@skip_if_no_image
def test_image_exists():
    assert IMG_PATH.exists()
    assert IMG_PATH.stat().st_size > 100


@skip_if_no_image
def test_flag_in_raw_bytes():
    """La flag debe estar presente en los bytes del fichero."""
    data = IMG_PATH.read_bytes()
    assert FLAG.encode() in data, "La flag no está en los metadatos del JPEG"


@skip_if_no_image
def test_solve_extracts_flag():
    flag = solve_raw_exif(str(IMG_PATH))
    assert flag == FLAG


@skip_if_no_image
def test_pillow_extract():
    try:
        import piexif  # noqa: F401
        from PIL import Image  # noqa: F401
        flag = solve_with_pillow(str(IMG_PATH))
        assert flag == FLAG
    except ImportError:
        pytest.skip("Pillow/piexif no instalados")
