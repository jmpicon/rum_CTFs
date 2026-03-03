"""
Tests del reto Metadatos Reveladores.
Requiere que gen.py haya sido ejecutado para generar foto_gato.jpg.
"""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "foto_gato.jpg")
FLAG = "CTF{exif_revela_mas_de_lo_que_crees}"


@pytest.mark.skipif(not os.path.exists(IMG_PATH), reason="foto_gato.jpg no generada. Ejecuta gen.py")
def test_image_exists():
    assert os.path.exists(IMG_PATH)
    assert os.path.getsize(IMG_PATH) > 100


@pytest.mark.skipif(not os.path.exists(IMG_PATH), reason="foto_gato.jpg no generada. Ejecuta gen.py")
def test_flag_in_raw_bytes():
    """La flag debe estar presente en los bytes del fichero."""
    data = open(IMG_PATH, "rb").read()
    assert FLAG.encode() in data, "La flag no está en los metadatos del JPEG"


@pytest.mark.skipif(not os.path.exists(IMG_PATH), reason="foto_gato.jpg no generada. Ejecuta gen.py")
def test_solve_extracts_flag():
    from solution import solve_raw_exif
    flag = solve_raw_exif(IMG_PATH)
    assert flag == FLAG


@pytest.mark.skipif(not os.path.exists(IMG_PATH), reason="foto_gato.jpg no generada. Ejecuta gen.py")
def test_pillow_extract():
    try:
        import piexif
        from PIL import Image
        from solution import solve_with_pillow
        flag = solve_with_pillow(IMG_PATH)
        assert flag == FLAG
    except ImportError:
        pytest.skip("Pillow/piexif no instalados")
