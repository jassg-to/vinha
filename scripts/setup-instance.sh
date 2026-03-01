#!/usr/bin/env bash
set -euo pipefail

# Usage: sudo ./setup-instance.sh <instance> <port> <git-repo-url>
# Example: sudo ./setup-instance.sh dev 8081 https://github.com/jassg-to/vinha.git
# Example: sudo ./setup-instance.sh prod 8080 https://github.com/jassg-to/vinha.git

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <instance> <port> <git-repo-url>"
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi

INSTANCE="$1"
PORT="$2"
REPO_URL="$3"
SERVICE_USER="vinha-${INSTANCE}"
APP_DIR="/opt/vinha-${INSTANCE}"
DATA_DIR="/var/lib/vinha-${INSTANCE}"
UV_PYTHON_DIR="/opt/uv-python"

echo "=== Setting up vinha-${INSTANCE} ==="
echo "  Port:    ${PORT}"
echo "  App dir: ${APP_DIR}"
echo "  Data dir: ${DATA_DIR}"
echo ""

# --- deploy user (skip if exists) ---
if id deploy &>/dev/null; then
    echo "[ok] deploy user already exists"
else
    echo "[+] Creating deploy user..."
    adduser --disabled-password --gecos "Deploy" deploy
fi

# --- service user ---
if id "${SERVICE_USER}" &>/dev/null; then
    echo "[ok] ${SERVICE_USER} user already exists"
else
    echo "[+] Creating ${SERVICE_USER} system user..."
    adduser --system --group --no-create-home --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

# --- add deploy to service user's group ---
if id -nG deploy | grep -qw "${SERVICE_USER}"; then
    echo "[ok] deploy is already in ${SERVICE_USER} group"
else
    echo "[+] Adding deploy to ${SERVICE_USER} group..."
    usermod -aG "${SERVICE_USER}" deploy
fi

# --- app directory ---
if [[ -d "${APP_DIR}/.git" ]]; then
    echo "[ok] ${APP_DIR} already cloned"
else
    echo "[+] Cloning repo into ${APP_DIR}..."
    mkdir -p "${APP_DIR}"
    chown deploy:deploy "${APP_DIR}"
    sudo -u deploy git clone "${REPO_URL}" "${APP_DIR}"
fi

echo "[+] Setting app directory permissions..."
chown -R "deploy:${SERVICE_USER}" "${APP_DIR}"
chmod -R 2750 "${APP_DIR}"
# Ensure files are group-readable but not group-writable
find "${APP_DIR}" -type f -exec chmod 640 {} +
find "${APP_DIR}" -type d -exec chmod 2750 {} +

# --- data directory ---
echo "[+] Creating data directory ${DATA_DIR}..."
mkdir -p "${DATA_DIR}"
chown "${SERVICE_USER}:${SERVICE_USER}" "${DATA_DIR}"
chmod 750 "${DATA_DIR}"

# --- shared python installation ---
if [[ -d "${UV_PYTHON_DIR}" ]]; then
    echo "[ok] Shared Python directory already exists"
else
    echo "[+] Installing Python to shared location ${UV_PYTHON_DIR}..."
    UV_PYTHON_INSTALL_DIR="${UV_PYTHON_DIR}" uv python install 3.14
    chmod -R 755 "${UV_PYTHON_DIR}"
fi

# --- install dependencies ---
echo "[+] Installing dependencies with uv..."
sudo -u deploy bash -c "cd ${APP_DIR} && UV_PYTHON_INSTALL_DIR=${UV_PYTHON_DIR} uv sync --frozen --link-mode copy"
# Fix venv permissions (created by deploy, needs to be readable by service user)
chown -R "deploy:${SERVICE_USER}" "${APP_DIR}/.venv"
find "${APP_DIR}/.venv" -type f -exec chmod 640 {} +
find "${APP_DIR}/.venv" -type d -exec chmod 2750 {} +
# Entry point scripts need to be executable
find "${APP_DIR}/.venv/bin" -type f -exec chmod 750 {} +

# --- .env file ---
ENV_FILE="${APP_DIR}/.env"
if [[ -f "${ENV_FILE}" ]]; then
    echo "[ok] ${ENV_FILE} already exists, not overwriting"
else
    echo "[+] Creating .env template at ${ENV_FILE}..."
    cat > "${ENV_FILE}" << ENVEOF
GOOGLE_CLIENT_ID=change-me
GOOGLE_CLIENT_SECRET=change-me
STORAGE_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
DATABASE_URL=sqlite:///${DATA_DIR}/vinha.db
PORT=${PORT}
ENVEOF
    chown "deploy:${SERVICE_USER}" "${ENV_FILE}"
    chmod 640 "${ENV_FILE}"
    echo ""
    echo "  >>> IMPORTANT: Edit ${ENV_FILE} with real Google OAuth credentials <<<"
    echo ""
fi

# --- systemd service ---
SERVICE_FILE="/etc/systemd/system/vinha-${INSTANCE}.service"
echo "[+] Creating systemd service ${SERVICE_FILE}..."
cat > "${SERVICE_FILE}" << SVCEOF
[Unit]
Description=Vinha Digital (${INSTANCE})
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/.venv/bin/vinha
EnvironmentFile=${APP_DIR}/.env
Restart=on-failure
RestartSec=5

NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadOnlyPaths=${APP_DIR}
ReadWritePaths=${DATA_DIR}

[Install]
WantedBy=multi-user.target
SVCEOF

# --- sudoers ---
SUDOERS_FILE="/etc/sudoers.d/vinha-${INSTANCE}"
echo "[+] Creating sudoers drop-in ${SUDOERS_FILE}..."
cat > "${SUDOERS_FILE}" << SUDOEOF
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart vinha-${INSTANCE}
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl status vinha-${INSTANCE}
deploy ALL=(${SERVICE_USER}) NOPASSWD: ${APP_DIR}/.venv/bin/alembic upgrade head
SUDOEOF
chmod 440 "${SUDOERS_FILE}"

# --- run initial migration ---
echo "[+] Running initial migration..."
sudo -u "${SERVICE_USER}" bash -c "cd ${APP_DIR} && ${APP_DIR}/.venv/bin/alembic -c ${APP_DIR}/alembic.ini upgrade head"

# --- enable and start service ---
echo "[+] Enabling and starting vinha-${INSTANCE}..."
systemctl daemon-reload
systemctl enable "vinha-${INSTANCE}"
systemctl start "vinha-${INSTANCE}"

echo ""
echo "=== Done! ==="
echo "  Service: systemctl status vinha-${INSTANCE}"
echo "  Listening on: localhost:${PORT}"
echo ""
echo "  If .env still has placeholder credentials, edit it and restart:"
echo "    sudo systemctl restart vinha-${INSTANCE}"
