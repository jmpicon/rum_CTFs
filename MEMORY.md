# MEMORY — CTF Docente

Documento de continuidad técnica del proyecto.

## Estado actual (v2)

- **Plataforma**: Flask + SQLite custom (reemplazó CTFd por completo)
- **Arranque**: `docker compose up -d` en `platform/`, luego acceso en `http://localhost:5000`
- **Tests**: `pytest -q` → 30 passed, 17 skipped (web skip sin Docker activo)
- **CI**: `.github/workflows/challenge-ci.yaml` valida challenge.yml + tests estáticos

## Arquitectura de la plataforma

- `platform/app.py` — Flask con rutas de auth, retos, scoreboard, API y admin
- `platform/models.py` — SQLAlchemy: User, Challenge, Hint, Solve, HintUnlock, Submission, Setting
- `platform/templates/` — Bootstrap 5.3 dark theme, AJAX submission, auto-refresh scoreboard
- Score: `Σ max(0, challenge.value − hints_cost)` por cada solve

## Retos implementados

| Ruta                                        | Flag                                        | Pts |
|---------------------------------------------|---------------------------------------------|-----|
| crypto/facil/xor_perezoso                   | CTF{xor_es_lineal_pero_ensena_algo}         | 100 |
| crypto/medio/b64_no_es_cifrado              | CTF{encoding_no_es_cifrado_amigo}           | 200 |
| crypto/medio/rsa_pequeno                    | CTF{rsa_primer_contacto}                    | 250 |
| crypto/dificil/vigenere_roto                | CTF{vigenere_cae_ante_la_estadistica}       | 400 |
| forense/facil/metadatos_reveladores         | CTF{exif_revela_mas_de_lo_que_crees}        | 100 |
| forense/medio/trafico_sospechoso            | CTF{sniffing_texto_plano_es_peligroso}      | 200 |
| web/facil/robots_secretos                   | CTF{robots_txt_no_es_seguridad}             | 100 |
| web/medio/cookie_falsa                      | CTF{nunca_confies_en_el_cliente}            | 200 |
| web/medio/sqli_login                        | CTF{sqli_las_comillas_mandan}              | 200 |
| web/avanzado/admin_roto                     | CTF{idor_nunca_confies_en_el_id}            | 300 |
| reversing/facil/pyc_misterioso              | CTF{el_bytecode_tambien_habla}              | 150 |

## Convenciones de reto

- Estructura mínima: `challenge.yml`, `solution.py`, `tests/test_*.py`
- Artefactos binarios: generar con `gen.py`, gitignore los .pyc/.pcap/.jpg grandes
- Tests con artefacto: usar `pytest.mark.skipif(not path.exists(), ...)`
- Tests con servicio web: usar `_service_up()` + `skip_if_down` mark (no RuntimeError)

## Patrón de carga de tests (evita colisiones de módulo)

```python
import importlib.util, pathlib
_sol = importlib.util.spec_from_file_location(
    "nombre_unico_solution",
    pathlib.Path(__file__).parent.parent / "solution.py"
)
_mod = importlib.util.module_from_spec(_sol)
_sol.loader.exec_module(_mod)
solve = _mod.solve
```

Esto evita colisiones en `sys.modules` cuando pytest carga varios `solution.py`.
Ver también: `pytest.ini` con `--import-mode=importlib`.

## Flujo para añadir un reto nuevo

1. Crear `challenges/<cat>/<dificultad>/<nombre>/`
2. Escribir `challenge.yml` (nombre, author, category, difficulty, value, flag, hints, description)
3. Crear `solution.py` y `tests/test_*.py` usando el patrón importlib de arriba
4. Si necesita artefacto: `gen.py` + ejecutar una vez + ignorar en .gitignore si es grande
5. `pytest -q challenges/<cat>/<dificultad>/<nombre>/` — debe pasar
6. Push → CI valida automáticamente

## Dependencias de desarrollo

Archivo: `requirements-dev.txt`
```
pytest>=7.4
requests>=2.31
scapy>=2.5
Pillow>=10.0
piexif>=1.1
```
