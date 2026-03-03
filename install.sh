#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Instalador automático – Plataforma CTF Docente
# CTFd 3.7+ · Docker Swarm · Plugin Whale · Traefik SSL
#
# USO:  sudo ./install.sh
# ============================================================

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[!!]${NC} $*"; }
die()  { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Privilegios ─────────────────────────────────────────
[ "$EUID" -eq 0 ] || die "Ejecuta como root: sudo ./install.sh"

# ── 2. Variables de entorno personalizables ────────────────
CTF_DOMAIN="${CTF_DOMAIN:-ctf.edu.gva.es}"
ACME_EMAIL="${ACME_EMAIL:-jm.picongimenez@edu.gva.es}"

warn "Dominio CTF: $CTF_DOMAIN"
warn "Email ACME:  $ACME_EMAIL"
echo ""

# ── 3. Docker ──────────────────────────────────────────────
log "Verificando Docker..."
if ! command -v docker &>/dev/null; then
    warn "Docker no encontrado. Instalando..."
    apt-get update -y
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common git jq
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        | tee /etc/apt/sources.list.d/docker.list >/dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    log "Docker instalado."
else
    log "Docker ya disponible: $(docker --version)"
fi

# ── 4. Daemon: deshabilitar live-restore (incompatible con Swarm) ──
DAEMON_JSON="/etc/docker/daemon.json"
if [ -f "$DAEMON_JSON" ] && grep -q '"live-restore": true' "$DAEMON_JSON"; then
    warn "Deshabilitando live-restore (incompatible con Swarm)..."
    sed -i 's/"live-restore": true/"live-restore": false/' "$DAEMON_JSON"
    systemctl restart docker
    sleep 5
fi

# ── 5. Docker Swarm ────────────────────────────────────────
log "Verificando Docker Swarm..."
if docker info 2>/dev/null | grep -q 'Swarm: active'; then
    log "Swarm ya activo."
else
    IP=$(hostname -I | awk '{print $1}')
    docker swarm init --advertise-addr "$IP"
    log "Swarm inicializado en $IP."
fi

# ── 6. Redes overlay ──────────────────────────────────────
log "Creando redes overlay..."
docker network create --driver overlay proxy_net    2>/dev/null || warn "proxy_net ya existe."
docker network create --driver overlay ctf_internal 2>/dev/null || warn "ctf_internal ya existe."
docker network create --driver overlay --attachable challenge_net 2>/dev/null || warn "challenge_net ya existe."

# ── 7. Construir imagen CTFd personalizada ─────────────────
log "Construyendo imagen ctfd-custom:latest..."
docker build -t ctfd-custom:latest "$BASE_DIR/platform/"

# ── 8. Construir imágenes de retos web ────────────────────
log "Construyendo imágenes de retos..."
build_image() {
    local service_dir="$1"
    local tag="$2"
    if [ -f "$service_dir/Dockerfile" ]; then
        log "  → Construyendo $tag"
        docker build -t "$tag" "$service_dir"
    fi
}

build_image "$BASE_DIR/challenges/web/facil/robots_secretos/service"    "ctf-web-robots"
build_image "$BASE_DIR/challenges/web/medio/cookie_falsa/service"       "ctf-web-cookie"
build_image "$BASE_DIR/challenges/web/medio/sqli_login/service"         "ctf-web-sqli"
build_image "$BASE_DIR/challenges/web/avanzado/admin_roto/service"      "ctf-web-admin"

# ── 9. Desplegar stack ────────────────────────────────────
log "Desplegando stack CTFd..."
cd "$BASE_DIR/platform"
CTF_DOMAIN="$CTF_DOMAIN" ACME_EMAIL="$ACME_EMAIL" \
    docker stack deploy -c docker-compose.yml ctf

# ── 10. Esperar servicios ─────────────────────────────────
log "Esperando que los servicios arranquen (puede tardar ~60 segundos)..."
for i in $(seq 1 30); do
    running=$(docker service ls --filter "name=ctf_ctfd" --format "{{.Replicas}}" 2>/dev/null || echo "0/1")
    [ "$running" = "1/1" ] && break
    sleep 2
done

echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  ${GREEN}¡PLATAFORMA CTF DESPLEGADA CON ÉXITO!${NC}"
echo "══════════════════════════════════════════════════════"
echo ""
echo "  Portal (Traefik):     https://$CTF_DOMAIN"
echo "  Fallback directo:     http://$(hostname -I | awk '{print $1}'):8000"
echo "  Nota DNS local:       añade '$CTF_DOMAIN' en /etc/hosts si no tienes DNS publico"
echo ""
echo "  CONFIGURACIÓN INICIAL del Plugin Whale:"
echo "    Docker API URL : unix:///var/run/docker.sock"
echo "    Swarm Network  : challenge_net"
echo "    Max containers : 50  (ajusta según RAM)"
echo ""
echo "  Para ver logs CTFd:"
echo "    docker service logs ctf_ctfd -f"
echo ""
warn "Cambia las contraseñas de BD en docker-compose.yml antes de producción."
echo ""
