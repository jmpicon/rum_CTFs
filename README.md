# Plataforma CTF Docente

Plataforma CTF **completamente custom** construida con Flask + SQLite.
Sin dependencias externas de CTFd ni Docker Swarm — un solo `docker compose up` es suficiente.

## Arranque rápido

```bash
sudo ./install.sh
```

La plataforma queda disponible en **http://localhost:7000**.

Credenciales de administrador por defecto:
- Usuario: `admin`
- Contraseña: `ctf_admin_2024` (cambiala en producción via variable `ADMIN_PASSWORD`)

## Estructura del repositorio

```
.
├── platform/                   # Plataforma CTF (Flask)
│   ├── app.py                  # Aplicación principal
│   ├── models.py               # Modelos SQLAlchemy (User, Challenge, Solve…)
│   ├── templates/              # Jinja2 + Bootstrap 5 dark theme
│   ├── requirements.txt        # Dependencias de producción
│   ├── Dockerfile
│   └── docker-compose.yml      # plataforma + 4 servicios web de retos
│
├── challenges/                 # Retos organizados por categoría/dificultad
│   ├── crypto/
│   │   ├── facil/xor_perezoso/
│   │   ├── medio/b64_no_es_cifrado/
│   │   ├── medio/rsa_pequeno/
│   │   └── dificil/vigenere_roto/
│   ├── forense/
│   │   ├── facil/metadatos_reveladores/
│   │   └── medio/trafico_sospechoso/
│   ├── web/
│   │   ├── facil/robots_secretos/
│   │   ├── medio/cookie_falsa/
│   │   ├── medio/sqli_login/
│   │   └── avanzado/admin_roto/
│   └── reversing/
│       └── facil/pyc_misterioso/
│
├── conftest.py                 # Carga aislada de solution.py por reto
├── pytest.ini                  # testpaths=challenges, --import-mode=importlib
├── requirements-dev.txt        # pytest, requests, Pillow, scapy…
└── install.sh                  # Instalador todo-en-uno
```

## Estructura de un reto

```
challenges/<categoria>/<dificultad>/<nombre>/
  challenge.yml     # metadata: nombre, puntos, flag, hints, descripción
  solution.py       # solución docente (no se entrega a alumnos)
  gen.py            # (opcional) genera artefactos binarios
  tests/
    test_*.py
  <artefactos>      # ej: ciphertext.hex, captura.pcap, foto_gato.jpg
```

## Retos incluidos

| Categoría  | Dificultad | Nombre                   | Técnica                              | Puntos |
|------------|------------|--------------------------|--------------------------------------|--------|
| Crypto     | Fácil      | xor_perezoso             | XOR + Known-Plaintext Attack         | 100    |
| Crypto     | Medio      | b64_no_es_cifrado        | ROT13 + Base64 × 2                   | 200    |
| Crypto     | Medio      | rsa_pequeno              | RSA con n pequeño (factorización)    | 250    |
| Crypto     | Difícil    | vigenere_roto            | Vigenère + análisis de frecuencias   | 400    |
| Forense    | Fácil      | metadatos_reveladores    | EXIF Artist con piexif               | 100    |
| Forense    | Medio      | trafico_sospechoso       | PCAP FTP en texto plano              | 200    |
| Web        | Fácil      | robots_secretos          | robots.txt information disclosure    | 100    |
| Web        | Medio      | cookie_falsa             | Cookie Base64 tampering              | 200    |
| Web        | Medio      | sqli_login               | SQL Injection login bypass           | 200    |
| Web        | Avanzado   | admin_roto               | IDOR (OWASP A01:2021)                | 300    |
| Reversing  | Fácil      | pyc_misterioso           | Bytecode Python (.pyc) con marshal   | 150    |

## Tests locales

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Generar artefactos binarios (solo primera vez)
python3 challenges/forense/facil/metadatos_reveladores/gen.py
python3 challenges/forense/medio/trafico_sospechoso/gen.py
python3 challenges/reversing/facil/pyc_misterioso/gen.py

# Ejecutar todos los tests
pytest -q
# Resultado esperado: 30 passed, 17 skipped (web tests se saltan sin Docker)
```

Los tests de retos web necesitan los servicios Docker corriendo.
Con `docker compose up -d` en `platform/`, los 17 tests web también pasan.

## Plataforma web

La plataforma Flask incluye:

- **Registro / Login** de alumnos
- **Panel de retos** con filtros por categoría, modales con descripción Markdown, envío AJAX de flags
- **Pistas** con coste en puntos (descuento del score)
- **Scoreboard** en tiempo real con podio top-3 y auto-refresh
- **Panel admin**: importar retos desde YAML, gestionar usuarios/retos, reset de progreso
- **Score**: `Σ max(0, valor_reto − coste_pistas_usadas)`

### Variables de entorno

| Variable        | Defecto              | Descripción                    |
|-----------------|----------------------|--------------------------------|
| `CTF_NAME`      | `CTF Docente`        | Nombre mostrado en la UI       |
| `SECRET_KEY`    | (generada al inicio) | Clave Flask para sesiones      |
| `ADMIN_PASSWORD`| `ctf_admin_2024`     | Contraseña del admin inicial   |
| `DATABASE_URL`  | `sqlite:////data/ctf.db` | URL de la base de datos   |

## Seguridad

- Cambiar `ADMIN_PASSWORD` y `SECRET_KEY` antes de exponer en red.
- `solution.py` y `gen.py` son solo para uso docente — no incluir en imagen de producción.
- Las flags en `challenge.yml` y en la base de datos están en texto plano (diseño educativo).
