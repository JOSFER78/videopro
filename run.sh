#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$DIR:$PYTHONPATH"
cd "$DIR"
exec /home/ubuntu/MoneyPrinterTurbo/.venv/bin/python -m streamlit run "$DIR/webui/Main.py" \
    --server.address=0.0.0.0 \
    --server.port=7001 \
    --server.headless=true \
    --server.runOnSave=true \
    --browser.gatherUsageStats=false \
    --client.toolbarMode=minimal \
    --logger.hideWelcomeMessage=true \
    --server.showEmailPrompt=false \
    --server.enableCORS=true
