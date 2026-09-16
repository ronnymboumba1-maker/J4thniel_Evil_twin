#!/usr/bin/env bash
# install.sh - Installation de EVIL TWIN ULTIME v4.0 (JATHNIEL EDITION)
# Lab / CTF uniquement.
set -e

echo "================================================"
echo " EVIL TWIN ULTIME v4.0 - Installation"
echo "================================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Lance en root: sudo ./install.sh"
    exit 1
fi

echo "📦 Mise a jour des depots..."
apt update

echo "📦 Installation des outils systeme..."
apt install -y \
    aircrack-ng airbase-ng aireplay-ng airodump-ng \
    iw iwconfig wireless-tools macchanger \
    dnsmasq iptables iproute2 net-tools arp-scan \
    python3 python3-pip \
    screen systemd openssl curl wget

echo ""
echo "🔧 Verification des binaires..."
for tool in airbase-ng aireplay-ng airodump-ng airmon-ng iwconfig \
            macchanger dnsmasq arp-scan aircrack-ng screen openssl; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "  ✅ $tool"
    else
        echo "  ❌ $tool MANQUANT"
    fi
done

echo ""
echo "📥 Dependances Python (stdlib uniquement)..."
pip3 install --upgrade pip

chmod +x evil_twin.py
chmod +x run_screen.sh 2>/dev/null || true
chmod +x install_service.sh 2>/dev/null || true

echo ""
echo "✅ Installation terminee!"
echo ""
echo "Lance avec:"
echo "  sudo python3 evil_twin.py"
echo ""
echo "Ou en arriere-plan (survit a la fermeture du terminal):"
echo "  sudo ./run_screen.sh"
echo ""
echo "⚠️  Pour un evil twin complet, il faut DEUX interfaces WiFi:"
echo "   - wlan0 : airbase-ng (AP + phishing)"
echo "   - wlan1 : airodump-ng + aireplay-ng (scan/deauth/handshake)"
echo ""
