# CTF Docente — Plataforma de Ciberseguridad para el Aula

Plataforma CTF educativa construida con **Flask + SQLite + Docker**.
Sin dependencias externas (sin CTFd, sin Docker Swarm). Un solo comando lo arranca todo.

---

## Índice

1. [¿Qué es esto?](#qué-es-esto)
2. [Requisitos](#requisitos)
3. [Instalación rápida](#instalación-rápida)
4. [Despliegue en servidor de clase](#despliegue-en-servidor-de-clase)
5. [Despliegue desde USB sin internet](#despliegue-desde-usb-sin-internet)
6. [Primeros pasos como administrador](#primeros-pasos-como-administrador)
7. [Cómo se accede (alumnos)](#cómo-se-accede-alumnos)
8. [Retos incluidos](#retos-incluidos)
9. [Estructura del repositorio](#estructura-del-repositorio)
10. [Variables de entorno](#variables-de-entorno)
11. [Comandos útiles](#comandos-útiles)
12. [Tests de desarrollo](#tests-de-desarrollo)
13. [Seguridad](#seguridad)

---

## ¿Qué es esto?

Una plataforma CTF (**Capture The Flag**) pensada para usarse en clase.
Los alumnos se registran, ven los retos, envían flags y compiten en el scoreboard en tiempo real.

Incluye **11 retos** pedagógicos de cinco categorías:

- **Crypto** — XOR, Base64, RSA, Vigenère
- **Forense** — Metadatos EXIF, captura de red PCAP
- **Web** — robots.txt, cookies, SQL Injection, IDOR
- **Reversing** — Bytecode Python (.pyc)

Cada reto tiene descripción, pistas con coste en puntos y solución docente.
Los retos se cargan automáticamente al arrancar — no hay que hacer nada manual.

---

## Requisitos

- **Docker** (versión 20 o superior)
- **Docker Compose v2** (incluido en Docker Desktop y en Docker Engine ≥ 23)
- Sistema operativo: Linux, macOS o Windows con WSL2

Para instalar Docker en Linux:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

---

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/jmpicon/rum_CTFs.git
cd rum_CTFs

# 2. Ejecutar el instalador
sudo ./install.sh
```

El instalador:
- Verifica que Docker esté instalado (lo instala si no está y tienes root)
- Construye todas las imágenes Docker
- Genera los artefactos de los retos (PCAP, EXIF, .pyc)
- Arranca la plataforma y los servicios de retos web
- Muestra la URL y las credenciales al terminar

Al finalizar verás algo así:

```
  ╔══════════════════════════════════════════════════╗
  ║       ¡PLATAFORMA CTF LISTA PARA USAR!           ║
  ╚══════════════════════════════════════════════════╝

  🌐 Portal alumnos: http://192.168.1.50:7000
  👤 Admin:          usuario=admin  contraseña=ctf_admin_2024
  🔧 Panel admin:    http://192.168.1.50:7000/admin

  ✅ Los retos se cargan automáticamente — no hay que hacer nada más.
```

---

## Despliegue en servidor de clase

El escenario habitual es un ordenador conectado a la red local del aula que hace de servidor.

```bash
# En el servidor del aula
git clone https://github.com/jmpicon/rum_CTFs.git
cd rum_CTFs
sudo ./install.sh
```

Los alumnos acceden desde sus navegadores a:

```
http://<IP-del-servidor>:7000
```

Para saber la IP del servidor:

```bash
hostname -I | awk '{print $1}'
```

Si quieres usar un puerto distinto al 7000:

```bash
CTF_PORT=8000 sudo ./install.sh
```

---

## Despliegue desde USB sin internet

Si el servidor de clase **no tiene acceso a internet**, copia el repositorio en un USB y llévalo ya con las imágenes Docker exportadas.

### Paso 1 — Exportar imágenes (en tu máquina con internet)

```bash
cd platform/
docker compose build
docker save \
  platform-ctf \
  platform-web-robots \
  platform-web-cookie \
  platform-web-sqli \
  platform-web-admin \
  -o ../ctf-imagenes.tar
```

Ahora copia **toda la carpeta del proyecto** (incluido `ctf-imagenes.tar`) al USB.

### Paso 2 — Instalar en el servidor sin internet

```bash
# Conectar el USB y copiar la carpeta
cp -r /media/usb/rum_CTFs /opt/ctf
cd /opt/ctf

# Cargar las imágenes Docker desde el tar
docker load -i ctf-imagenes.tar

# Arrancar (ya no necesita descargar nada de internet)
cd platform/
docker compose up -d
```

---

## Primeros pasos como administrador

1. Abre el panel de admin: `http://<IP>:7000/admin`
2. Credenciales por defecto: `admin` / `ctf_admin_2024`
3. Desde el panel puedes:
   - **Cambiar el nombre y descripción** del CTF
   - **Activar o desactivar retos** individualmente
   - **Ver el progreso** de cada alumno
   - **Eliminar usuarios** o resetear todo el progreso
   - **Volver a importar retos** si añades nuevos `challenge.yml`

Los retos se importan solos al arrancar. Si añades nuevos retos después de que la plataforma ya esté corriendo, ve al panel admin y pulsa **"Importar retos"**.

---

## Cómo se accede (alumnos)

1. Abrir el navegador y entrar en `http://<IP-del-servidor>:7000`
2. Pulsar **Registrarse** y crear una cuenta
3. Explorar los retos por categoría
4. Enviar la flag en el formato `CTF{...}`
5. Consultar el **Scoreboard** para ver el ranking

Los retos web tienen un enlace al servicio en vivo donde practicar.
Los retos de crypto, forense y reversing incluyen archivos descargables o datos en la descripción.

---

## Retos incluidos

| Categoría | Dificultad | Nombre                | Técnica                            | Puntos |
|-----------|------------|-----------------------|------------------------------------|--------|
| Crypto    | Fácil      | XOR Perezoso          | XOR + Known-Plaintext Attack       | 100    |
| Crypto    | Medio      | B64 no es Cifrado     | ROT13 + Base64 × 2                 | 200    |
| Crypto    | Medio      | RSA: Primer Contacto  | RSA con n pequeño (factorización)  | 250    |
| Crypto    | Difícil    | Vigenère Roto         | Vigenère + análisis de frecuencias | 400    |
| Forense   | Fácil      | Metadatos Reveladores | EXIF Artist con piexif             | 100    |
| Forense   | Medio      | Tráfico Sospechoso    | PCAP FTP en texto plano            | 200    |
| Web       | Fácil      | Robots Secretos       | robots.txt information disclosure  | 100    |
| Web       | Medio      | La Cookie Mentirosa   | Cookie Base64 tampering            | 200    |
| Web       | Medio      | SQLi: El Login Roto   | SQL Injection login bypass         | 200    |
| Web       | Avanzado   | Admin Roto (IDOR)     | IDOR — acceso no autorizado        | 300    |
| Reversing | Fácil      | PYC Misterioso        | Bytecode Python (.pyc) + marshal   | 150    |

**Puntuación:** cada reto resuelto suma sus puntos menos el coste de las pistas usadas.
En caso de empate gana quien resolvió el último reto antes.

---

## Estructura del repositorio

```
rum_CTFs/
├── install.sh                      # Instalador todo-en-uno
│
├── platform/                       # Plataforma CTF
│   ├── app.py                      # Flask — rutas, lógica, auto-importación de retos
│   ├── models.py                   # SQLAlchemy — User, Challenge, Solve, Hint...
│   ├── requirements.txt            # Dependencias Python de producción
│   ├── Dockerfile                  # Imagen de la plataforma
│   ├── docker-compose.yml          # Plataforma + 4 servicios web de retos
│   └── templates/                  # HTML Jinja2 + Bootstrap 5 (tema oscuro)
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── challenges.html
│       ├── scoreboard.html
│       └── admin.html
│
├── challenges/                     # Retos organizados por categoría y dificultad
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
├── conftest.py                     # Carga aislada de solution.py por reto
├── pytest.ini                      # Configuración pytest
└── requirements-dev.txt            # Dependencias para desarrollo y tests
```

### Estructura de cada reto

```
challenges/<categoria>/<dificultad>/<nombre>/
  challenge.yml       # Nombre, descripción, puntos, flag, pistas
  solution.py         # Solución docente (no se entrega a alumnos)
  gen.py              # (opcional) genera artefactos binarios
  tests/
    test_*.py         # Tests automáticos que validan la solución
  <artefactos>        # ej: ciphertext.hex, captura.pcap, foto_gato.jpg
```

---

## Variables de entorno

Se pueden pasar al instalador o definir en un archivo `.env` dentro de `platform/`.

| Variable         | Valor por defecto        | Descripción                          |
|------------------|--------------------------|--------------------------------------|
| `CTF_NAME`       | `CTF Docente`            | Nombre del CTF mostrado en la UI     |
| `CTF_PORT`       | `7000`                   | Puerto en el host para la plataforma |
| `ADMIN_PASSWORD` | `ctf_admin_2024`         | Contraseña del administrador         |
| `SECRET_KEY`     | (generada aleatoriamente)| Clave Flask para sesiones            |
| `DATABASE_URL`   | `sqlite:////data/ctf.db` | Ruta de la base de datos             |

Ejemplo de uso:

```bash
CTF_NAME="CTF Curso 2024-25" ADMIN_PASSWORD="miPasswordSegura" sudo ./install.sh
```

---

## Comandos útiles

Todos los comandos se ejecutan desde la carpeta `platform/`.

```bash
# Ver estado de los contenedores
docker compose ps

# Ver logs de la plataforma
docker compose logs -f ctf

# Ver logs de un reto web concreto
docker compose logs -f web-sqli

# Reiniciar solo la plataforma (sin perder la BD)
docker compose restart ctf

# Apagar todo
docker compose down

# Apagar y borrar la base de datos (empezar de cero)
docker compose down -v

# Reconstruir después de cambios en el código
docker compose build && docker compose up -d
```

---

## Tests de desarrollo

Para desarrollar o añadir nuevos retos:

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Generar artefactos binarios (solo la primera vez)
python3 challenges/forense/facil/metadatos_reveladores/gen.py
python3 challenges/forense/medio/trafico_sospechoso/gen.py
python3 challenges/reversing/facil/pyc_misterioso/gen.py

# Ejecutar todos los tests
pytest -q
# Esperado: 30 passed, 17 skipped (los web necesitan Docker activo)

# Con Docker activo, todos pasan
cd platform && docker compose up -d && cd ..
pytest -q
# Esperado: 47 passed
```

---

## Seguridad

- Cambia `ADMIN_PASSWORD` y `SECRET_KEY` antes de exponer la plataforma en una red no controlada.
- Los archivos `solution.py` y `gen.py` son solo para uso docente — no los distribuyas a los alumnos.
- Las flags se almacenan en texto plano en la base de datos (diseño educativo, no para producción real).
- La plataforma usa SQLite. Para entornos con muchos usuarios simultáneos considera migrar a PostgreSQL.
