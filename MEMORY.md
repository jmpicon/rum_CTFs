# MEMORY

Documento de memoria tecnica para mantener continuidad del proyecto.

## Estado general

- Plataforma base: CTFd en Docker Swarm con Traefik y plugin Whale.
- CI: validacion de `challenge.yml`, generacion de artefactos y tests por categoria.
- Retos ya implementados en: Crypto, Forense, Web y Reversing.

## Convenciones operativas

- Reto minimo:
  - `challenge.yml` valido
  - `solution.py` (uso docente)
  - `tests/test_*.py`
- Si el reto depende de binarios/artefactos:
  - agregar `gen.py`
  - evitar depender de herramientas externas cuando sea posible
  - dejar fallback sin dependencias criticas
- Flags con formato `CTF{...}`.
- Tests tolerantes cuando un artefacto no fue generado aun (`pytest.mark.skipif`).

## Retos forense/reversing completados en esta iteracion

### Forense
- `challenges/forense/medio/trafico_sospechoso`
  - `solution.py`: extrae flag desde `captura.pcap` por busqueda de `PASS CTF{...}`.
  - `tests/test_trafico.py`: valida existencia de artefacto y extraccion correcta.
  - `gen.py` existente: genera `captura.pcap` con trafico FTP en texto plano.

### Reversing
- `challenges/reversing/facil/pyc_misterioso`
  - `challenge.yml` creado.
  - `gen.py`: genera `misterioso.pyc` desde codigo temporal compilado.
  - `solution.py`: carga bytecode con `marshal` y recupera la flag desde `co_consts`.
  - `tests/test_pyc.py`: valida artefacto y solucion.

## Dependencias de desarrollo

- Archivo: `requirements-dev.txt`
- Incluye: `pytest`, `requests`, `scapy`, `Pillow`, `uncompyle6`.

## Flujo recomendado para nuevos retos

1. Crear carpeta en `challenges/<categoria>/<dificultad>/<nombre>/`.
2. Definir `challenge.yml` con narrativa, flag, hints y metadata.
3. Crear `solution.py` y tests reproducibles.
4. Si aplica, crear `gen.py` para artefactos y ejecutar una vez.
5. Correr `pytest` de la categoria.
6. Verificar que CI pasa en push/PR.
