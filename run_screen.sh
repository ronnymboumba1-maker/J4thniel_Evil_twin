#!/usr/bin/env bash
# run_screen.sh - Lance evil_twin.py dans une session screen detachee
# Survit a la fermeture du terminal. Lab/CTF uniquement.
set -e

SESSION_NAME="eviltwin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Lance en root: sudo ./run_screen.sh"
    exit 1
fi

if screen -list | grep -q "\.${SESSION_NAME}"; then
    echo "⚠️  Session '${SESSION_NAME}' deja active."
    echo "   Attache-toi avec: sudo screen -r ${SESSION_NAME}"
    exit 1
fi

echo "🖥️  Lancement de evil_twin.py dans screen '${SESSION_NAME}'..."
cd "$SCRIPT_DIR"
screen -dmS "$SESSION_NAME" -L -Logfile "$LOG_DIR/screen_${SESSION_NAME}.log" \
    python3 evil_twin.py

sleep 1

if screen -list | grep -q "\.${SESSION_NAME}"; then
    echo "✅ Session '${SESSION_NAME}' lancee en arriere-plan."
    echo ""
    echo "Commandes utiles:"
    echo "  sudo screen -r ${SESSION_NAME}   # s'attacher"
    echo "  (dans screen) Ctrl+A puis D     # se detacher"
    echo "  sudo screen -X -S ${SESSION_NAME} quit  # tuer"
    echo ""
    echo "Log: $LOG_DIR/screen_${SESSION_NAME}.log"
else
    echo "❌ Echec du lancement"
    exit 1
fi
