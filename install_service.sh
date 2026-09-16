#!/usr/bin/env bash
# install_service.sh - Installe evil_twin en service systemd
# Lab/CTF uniquement.
set -e

if [ "$EUID" -ne 0 ]; then
    echo "❌ Lance en root: sudo ./install_service.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="/etc/systemd/system/eviltwin.service"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Evil Twin Ultime - JATHNIEL EDITION (Lab/CTF)
After=network.target

[Service]
Type=simple
WorkingDirectory=${SCRIPT_DIR}
ExecStart=/usr/bin/python3 ${SCRIPT_DIR}/evil_twin.py
Restart=on-failure
RestartSec=5
StandardOutput=append:${SCRIPT_DIR}/logs/service.log
StandardError=append:${SCRIPT_DIR}/logs/service.err
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

mkdir -p "${SCRIPT_DIR}/logs"

systemctl daemon-reload

echo "✅ Service installe: eviltwin.service"
echo ""
echo "Commandes:"
echo "  sudo systemctl start eviltwin"
echo "  sudo systemctl stop eviltwin"
echo "  sudo systemctl status eviltwin"
echo "  sudo journalctl -u eviltwin -f"
echo ""
echo "⚠️  Le service ne demarre PAS automatiquement au boot."
echo "   Active-le avec: sudo systemctl enable eviltwin"
echo ""
