#!/usr/bin/env bash
# ==============================================================================
# MyHospital Backend — One-Command First-Time Setup
# ==============================================================================
# This script handles everything on a fresh server:
#   1. Installs Docker & Docker Compose (if not already installed)
#   2. Automatically creates backend/.env with secure random keys & passwords
#   3. Builds and launches all production containers
#   4. Verifies container health
#
# Usage:
#   chmod +x scripts/init.sh
#   ./scripts/init.sh
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
step()  { echo -e "\n${CYAN}══════════════════════════════════════════════════${NC}\n${CYAN}  $*${NC}\n${CYAN}══════════════════════════════════════════════════${NC}"; }

cd "$PROJECT_DIR"

# ── 1. Install Docker & Compose (if missing) ──────────────────────────────────
step "Step 1/4: Checking Docker Installation"
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    info "Docker and Docker Compose are already installed:"
    docker --version
    docker compose version
else
    info "Installing Docker and Docker Compose plugin..."
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg git
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker "$USER"
    info "Docker installed successfully."
fi

# ── 2. Create and Configure backend/.env ──────────────────────────────────────
step "Step 2/4: Configuring Production Environment (.env)"
ENV_FILE="$PROJECT_DIR/backend/.env"
EXAMPLE_FILE="$PROJECT_DIR/backend/.env.production.example"

if [ -f "$ENV_FILE" ]; then
    info "backend/.env already exists — keeping existing file."
    sed -i "s|CREATE_TABLES_ON_STARTUP=false|CREATE_TABLES_ON_STARTUP=true|" "$ENV_FILE"
else
    if [ ! -f "$EXAMPLE_FILE" ]; then
        error "Template file not found at: $EXAMPLE_FILE"
        exit 1
    fi

    info "Creating backend/.env from template..."
    cp "$EXAMPLE_FILE" "$ENV_FILE"

    # Generate secure random secret key and postgres password
    SECRET_KEY=$(openssl rand -hex 32)
    PG_PASSWORD=$(openssl rand -hex 24)

    sed -i "s|<generate-a-64-char-hex-string>|${SECRET_KEY}|" "$ENV_FILE"
    sed -i "s|<strong-random-password>|${PG_PASSWORD}|" "$ENV_FILE"
    sed -i "s|<https://your-frontend-domain.com>|*|" "$ENV_FILE"

    chmod 600 "$ENV_FILE"
    info "Generated backend/.env with random SECRET_KEY and POSTGRES_PASSWORD."
fi

# ── 3. Build & Launch Docker Services ─────────────────────────────────────────
step "Step 3/4: Building and Starting Production Stack"
info "Starting containers using docker-compose.prod.yml..."

DOCKER_CMD="docker compose -f docker-compose.prod.yml"
if ! groups | grep -q docker; then
    DOCKER_CMD="sudo docker compose -f docker-compose.prod.yml"
fi

$DOCKER_CMD up -d --build

# ── 4. Verify Services ────────────────────────────────────────────────────────
step "Step 4/4: Verifying Service Status"
info "Waiting for containers to initialize..."
sleep 5

$DOCKER_CMD ps

echo ""
info "Testing health endpoint..."
if curl -fsS http://localhost:8000/api/v1/health &>/dev/null; then
    info "Health check passed: API is responding on port 8000!"
else
    warn "API is still starting up. You can check logs using:"
    warn "  $DOCKER_CMD logs -f api"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅  First-Time Setup Complete!                  ${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo "From now on, GitHub Actions will automatically deploy when you push to main."
echo ""
