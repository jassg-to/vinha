#!/usr/bin/env bash
set -euo pipefail

# Usage: sudo ./teardown-instance.sh <instance>
# Example: sudo ./teardown-instance.sh dev

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <instance>"
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi

INSTANCE="$1"
SERVICE_USER="vinha-${INSTANCE}"
APP_DIR="/opt/vinha-${INSTANCE}"
DATA_DIR="/var/lib/vinha-${INSTANCE}"

echo "=== Tearing down vinha-${INSTANCE} ==="
echo "  App dir:  ${APP_DIR}"
echo "  Data dir: ${DATA_DIR}"
echo "  User:     ${SERVICE_USER}"
echo ""

# --- stop and disable service ---
if systemctl is-active "vinha-${INSTANCE}" &>/dev/null; then
    echo "[-] Stopping vinha-${INSTANCE}..."
    systemctl stop "vinha-${INSTANCE}"
fi
if systemctl is-enabled "vinha-${INSTANCE}" &>/dev/null; then
    echo "[-] Disabling vinha-${INSTANCE}..."
    systemctl disable "vinha-${INSTANCE}"
fi

# --- remove systemd service ---
SERVICE_FILE="/etc/systemd/system/vinha-${INSTANCE}.service"
if [[ -f "${SERVICE_FILE}" ]]; then
    echo "[-] Removing ${SERVICE_FILE}..."
    rm "${SERVICE_FILE}"
    systemctl daemon-reload
fi

# --- remove sudoers ---
SUDOERS_FILE="/etc/sudoers.d/vinha-${INSTANCE}"
if [[ -f "${SUDOERS_FILE}" ]]; then
    echo "[-] Removing ${SUDOERS_FILE}..."
    rm "${SUDOERS_FILE}"
fi

# --- remove app directory ---
if [[ -d "${APP_DIR}" ]]; then
    echo "[-] Removing ${APP_DIR}..."
    rm -rf "${APP_DIR}"
fi

# --- remove data directory ---
if [[ -d "${DATA_DIR}" ]]; then
    echo "[-] Removing ${DATA_DIR} (database)..."
    rm -rf "${DATA_DIR}"
fi

# --- remove system user ---
if id "${SERVICE_USER}" &>/dev/null; then
    echo "[-] Removing user ${SERVICE_USER}..."
    deluser "${SERVICE_USER}"
    # Remove the group too if it still exists
    getent group "${SERVICE_USER}" &>/dev/null && delgroup "${SERVICE_USER}" || true
fi

# --- remove deploy from the group ---
# (group is already gone after deluser/delgroup, nothing to do)

echo ""
echo "=== Done! ==="
