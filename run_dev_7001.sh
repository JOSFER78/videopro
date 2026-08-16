#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

export PYTHONPATH="$DIR${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

VIDEOPRO_WEBUI_HOST="${VIDEOPRO_WEBUI_HOST:-0.0.0.0}"
VIDEOPRO_WEBUI_PORT="${VIDEOPRO_WEBUI_PORT:-7001}"

PYTHON_BIN="/home/ubuntu/MoneyPrinterTurbo/.venv/bin/python"

echo "=================================================="
echo "🎬 VideoPro Studio — Unified Production Environment"
echo "   Directory:    $DIR"
echo "   URL:          http://127.0.0.1:$VIDEOPRO_WEBUI_PORT/"
echo "   Mode:         Hot-Reload (runOnSave=true)"
echo "=================================================="

exec "$PYTHON_BIN" -m streamlit run "$DIR/webui/Main.py" \
    --server.address="$VIDEOPRO_WEBUI_HOST" \
    --server.port="$VIDEOPRO_WEBUI_PORT" \
    --server.headless=true \
    --server.runOnSave=false \
    --server.fileWatcherType=none \
    --runner.fastReruns=true \
    --browser.gatherUsageStats=false \
    --client.toolbarMode=minimal \
    --logger.hideWelcomeMessage=true \
    --server.showEmailPrompt=false \
    --server.enableCORS=true
