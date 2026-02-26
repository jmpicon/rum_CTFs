#!/bin/bash
set -e

# Instalador automático: Plataforma CTF Docente (CTFd + Swarm + Whale)
# Se debe ejecutar como root

echo "=== Detectando privilegios ==="
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, ejecuta este script como root (sudo ./install.sh)"
  exit 1
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Directorio base: $BASE_DIR"

echo "=== Validando Docker ==="
if ! command -v docker &> /dev/null; then
    echo "Docker no instalado. Instalando dependencias necesarias..."
    apt-get update -y
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common git jq
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || true
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

echo "=== Configurando Daemon de Docker ==="
# Live-restore provoca fallos con Swarm, deshabilitarlo
DAEMON_JSON="/etc/docker/daemon.json"
if [ -f "$DAEMON_JSON" ] && grep -q "live-restore" "$DAEMON_JSON"; then
    echo "Deshabilitando live-restore en daemon.json (incompatible con Swarm)..."
    sed -i 's/"live-restore": true/"live-restore": false/g' "$DAEMON_JSON"
    systemctl restart docker
    sleep 3
fi

echo "=== Iniciando Docker Swarm ==="
if ! docker info | grep -q 'Swarm: active'; then
    echo "Inicializando Docker Swarm..."
    # Obtenemos ip primaria
    IP=$(hostname -I | awk '{print $1}')
    docker swarm init --advertise-addr "$IP" || echo "Swarm ya estaba inicializado."
else
    echo "Swarm ya activo."
fi

echo "=== Creando Redes ==="
docker network create --driver overlay proxy_net || true
docker network create --driver overlay ctf_internal || true
docker network create --driver overlay --attachable challenge_net || true

echo "=== Compilando Retos Vulnerables Base ==="
cd "$BASE_DIR"
if [ -d "challenges/web/avanzado/admin_roto/service" ]; then
    echo "Compilando ctf-web-admin..."
    docker build -t ctf-web-admin ./challenges/web/avanzado/admin_roto/service
fi

echo "=== Desplegando Plataforma CTFd ==="
cd "$BASE_DIR/platform"
docker stack deploy -c docker-compose.yml ctf

echo "=========================================="
echo "¡INSTALACIÓN COMPLETADA CON ÉXITO!"
echo "Accede al portal en http://localhost o el dominio asignado."
echo "IMPORTANTE: En la configuración inicial (Plugin Whale):"
echo "  - Docker API: unix:///var/run/docker.sock"
echo "  - Swarm Network: challenge_net"
echo "=========================================="
