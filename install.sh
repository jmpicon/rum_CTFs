#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Instalador — CTF Docente (Plataforma propia)
# Flask + SQLite + Bootstrap 5 · Sin CTFd · Sin Swarm
#
# USO:
#   ./install.sh          → instala todo y arranca
#   ./install.sh --dev    → solo para desarrollo local (sin sudo)
# ============================================================

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $*"; }
info() { echo -e "${BLUE}[>>]${NC} $*"; }
warn() { echo -e "${YELLOW}[!!]${NC} $*"; }
die()  { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║         CTF DOCENTE — Instalador v2.0            ║"
echo "  ║   Plataforma educativa de ciberseguridad         ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Variables personalizables ──────────────────────────────
CTF_PORT="${CTF_PORT:-7000}"
CTF_NAME="${CTF_NAME:-CTF Docente}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-ctf_admin_2024}"
SECRET_KEY="${SECRET_KEY:-$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 48 2>/dev/null || echo 'clave_secreta_generada_por_defecto_2024')}"

info "Configuración:"
echo "    CTF_NAME       = $CTF_NAME"
echo "    CTF_PORT       = $CTF_PORT"
echo "    ADMIN_PASSWORD = $ADMIN_PASSWORD"
echo ""

# ── 1. Docker ──────────────────────────────────────────────
info "Verificando Docker..."
if ! command -v docker &>/dev/null; then
    if [ "$MODE" = "--dev" ]; then
        die "Docker no instalado. Instálalo con: https://docs.docker.com/get-docker/"
    fi
    [ "$EUID" -eq 0 ] || die "Se necesita root para instalar Docker. Usa: sudo ./install.sh"
    warn "Docker no encontrado. Instalando..."
    apt-get update -y && apt-get install -y curl
    curl -fsSL https://get.docker.com | sh
    log "Docker instalado."
else
    log "Docker: $(docker --version)"
fi

if ! docker compose version &>/dev/null 2>&1; then
    die "Docker Compose v2 no disponible. Actualiza Docker."
fi
log "Docker Compose: $(docker compose version --short)"

# ── 2. Construir imágenes ──────────────────────────────────
info "Construyendo imágenes Docker..."
cd "$BASE_DIR/platform"

CTF_NAME="$CTF_NAME" \
CTF_PORT="$CTF_PORT" \
ADMIN_PASSWORD="$ADMIN_PASSWORD" \
SECRET_KEY="$SECRET_KEY" \
  docker compose build --parallel

log "Imágenes construidas."

# ── 3. Generar artefactos de retos (si no existen) ────────
info "Generando artefactos de retos (EXIF, PCAP, PYC)..."

gen_if_missing() {
    local dir="$1"
    local output="$2"
    if [ -f "$BASE_DIR/challenges/$dir/gen.py" ] && \
       [ ! -f "$BASE_DIR/challenges/$dir/$output" ]; then
        warn "  Generando $dir/$output..."
        cd "$BASE_DIR/challenges/$dir"
        python3 gen.py 2>/dev/null && log "  ✓ $output generado" || \
            warn "  ⚠ No se pudo generar $output (instala dependencias con pip install Pillow piexif scapy)"
        cd "$BASE_DIR"
    fi
}

gen_if_missing "forense/facil/metadatos_reveladores" "foto_gato.jpg"
gen_if_missing "forense/medio/trafico_sospechoso"    "captura.pcap"
gen_if_missing "reversing/facil/pyc_misterioso"      "check.pyc"

# ── 4. Arrancar plataforma ─────────────────────────────────
info "Arrancando plataforma CTF..."
cd "$BASE_DIR/platform"

CTF_NAME="$CTF_NAME" \
CTF_PORT="$CTF_PORT" \
ADMIN_PASSWORD="$ADMIN_PASSWORD" \
SECRET_KEY="$SECRET_KEY" \
  docker compose up -d

# ── 5. Esperar a que la plataforma esté lista ──────────────
info "Esperando que la plataforma arranque..."
for i in $(seq 1 20); do
    if curl -sf "http://localhost:$CTF_PORT/" &>/dev/null; then
        break
    fi
    sleep 2
done

# ── 6. Summary ─────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║       ¡PLATAFORMA CTF LISTA PARA USAR!           ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo -e "${NC}"
IP_LOCAL="$(hostname -I | awk '{print $1}')"
echo -e "  🌐 Portal alumnos: ${BLUE}http://$IP_LOCAL:$CTF_PORT${NC}"
echo -e "  👤 Admin:          usuario=${BOLD}admin${NC}  contraseña=${BOLD}$ADMIN_PASSWORD${NC}"
echo -e "  🔧 Panel admin:    ${BLUE}http://$IP_LOCAL:$CTF_PORT/admin${NC}"
echo ""
echo "  ✅ Los retos se cargan automáticamente — no hay que hacer nada más."
echo "     Comparte la URL de portal con los alumnos y ¡a jugar!"
echo ""
echo "  🛠️  Comandos útiles (ejecutar desde la carpeta 'platform/'):"
echo "     docker compose logs -f ctf        # logs plataforma"
echo "     docker compose logs -f web-sqli   # logs reto SQLi"
echo "     docker compose down               # apagar todo"
echo "     docker compose restart ctf        # reiniciar plataforma"
echo ""
