#!/usr/bin/env bash
set -euo pipefail

# One-shot provisioning for a fresh Ubuntu VM
# - Installs Docker + Compose
# - Clones repo if not present
# - Creates .env interactively (or from existing env vars)
# - Builds and starts the stack

REPO_URL="https://github.com/your-org-or-user/factory.git"
APP_DIR="$(pwd)"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

echo "[1/6] Updating apt and installing prerequisites..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git

echo "[2/6] Installing Docker Engine..."
if ! command_exists docker; then
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER" || true
else
  echo "Docker already installed"
fi

echo "[3/6] Ensuring docker service is running..."
sudo systemctl enable --now docker

echo "[4/6] Cloning repository if needed..."
if [ ! -f "docker-compose.yml" ]; then
  git clone "$REPO_URL" factory || true
  cd factory
  APP_DIR="$(pwd)"
fi

echo "[5/6] Creating .env (interactive) if missing..."
if [ ! -f .env ]; then
  read -rp "Enter BOT_TOKEN: " BOT_TOKEN
  read -rp "Enter ADMIN_TELEGRAM_ID (digits): " ADMIN_TELEGRAM_ID
  cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_TELEGRAM_ID=${ADMIN_TELEGRAM_ID}
REDIS_URL=redis://redis:6379/0
PLATFORMS=vk,tiktok,instagram,telegram

# Optional:
AFFILIATE_APP_KEY=
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
HEYGEN_TOKEN=
CAPCUT_TOKEN=

VIDEO_FPS=24
VIDEO_DURATION_DEFAULT=15

TELEGRAM_CHANNEL_ID=
TELEGRAM_CHANNEL_USERNAME=

DRAFTS_DIR=/drafts
EOF
else
  echo ".env exists — using it"
fi

echo "[6/6] Building and starting containers..."
docker compose build
docker compose up -d

echo "Done. If this was the first Docker install, you may need to log out and log back in for docker group to take effect."
echo "Next: Talk to your bot from ADMIN_TELEGRAM_ID and send /start"

