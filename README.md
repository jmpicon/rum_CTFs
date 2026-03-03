# Plataforma CTF Docente

Repositorio para desplegar una plataforma CTF basada en CTFd + Docker Swarm, con retos de:
- Crypto
- Forense
- Web
- Reversing

## Estructura del repositorio

- `platform/`: stack principal (CTFd, MariaDB, Redis, Traefik)
- `challenges/`: retos organizados por categoria y dificultad
- `install.sh`: instalador y despliegue automatico en Swarm
- `.github/workflows/challenge-ci.yaml`: CI de validacion, generacion y testing de retos
- `requirements-dev.txt`: dependencias para pruebas locales y CI

## Convencion de un reto

Cada reto sigue, en general, esta estructura:

```
challenges/<categoria>/<dificultad>/<nombre_reto>/
  challenge.yml
  solution.py          # solo docente
  gen.py               # opcional: generar artefactos
  tests/
    test_*.py
  <artefactos>         # ejemplo: .pcap, .pyc, .txt, .hex
```

## Retos actuales

### Crypto
- `challenges/crypto/facil/xor_perezoso`
- `challenges/crypto/medio/b64_no_es_cifrado`
- `challenges/crypto/medio/rsa_pequeno`
- `challenges/crypto/dificil/vigenere_roto`

### Forense
- `challenges/forense/facil/metadatos_reveladores`
- `challenges/forense/medio/trafico_sospechoso`

### Web
- `challenges/web/facil/robots_secretos`
- `challenges/web/medio/cookie_falsa`
- `challenges/web/medio/sqli_login`
- `challenges/web/avanzado/admin_roto`

### Reversing
- `challenges/reversing/facil/pyc_misterioso`

## Uso rapido local (tests)

1. Instalar dependencias:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

2. Generar artefactos de retos que lo requieran:

```bash
python3 challenges/forense/facil/metadatos_reveladores/gen.py
python3 challenges/forense/medio/trafico_sospechoso/gen.py
python3 challenges/reversing/facil/pyc_misterioso/gen.py
```

3. Ejecutar pruebas:

```bash
pytest -q challenges/crypto challenges/forense challenges/reversing --tb=short -v
pytest -q challenges/web --tb=short -v
```

## Despliegue de plataforma

Para instalar y desplegar todo en un host Linux:

```bash
sudo ./install.sh
```

Variables utiles:
- `CTF_DOMAIN` (por defecto `ctf.tu-instituto.edu`)
- `ACME_EMAIL` (por defecto `profesor@tu-instituto.edu`)

### Acceso al portal

- URL principal (Traefik): `https://ctf.tu-instituto.edu`
- Fallback directo a CTFd (sin proxy): `http://<IP_DEL_HOST>:8000`

Nota importante sobre DNS/TLS:
- Si el dominio no existe en DNS publico, LetsEncrypt no podra emitir certificado valido.
- En entorno local/lab, agrega una entrada en `/etc/hosts`:
  - `<IP_DEL_HOST> ctf.tu-instituto.edu`
- Con esa entrada, Traefik enruta correctamente por `Host` y puedes trabajar aunque el certificado no sea de confianza publica.

### Detalle tecnico de Traefik

- Para evitar incompatibilidades de API Docker en algunos entornos, Traefik se configura con **file provider**.
- Configuracion dinamica en: `platform/traefik/dynamic/ctfd.yml`
- Backend objetivo: `http://tasks.ctfd:8000` (resolucion por DNS interna de Swarm a tareas reales del servicio).

## Notas de seguridad

- Cambiar secretos y passwords por defecto antes de produccion.
- Los scripts `solution.py` y `gen.py` son para entorno docente.
- No exponer informacion de solucion a participantes.
