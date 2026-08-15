#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$DIR/server:$DIR:$PYTHONPATH"

echo "=== [🚀 VideoPro Cinematic Studio v2.0] ==="
echo "📁 Directorio: $DIR"
echo "🌐 Puerto: 7001"

exec /home/ubuntu/vibevoice-venv/bin/python -m uvicorn videopro_server:app \
    --app-dir "$DIR/server" \
    --host 0.0.0.0 \
    --port 7001 \
    --reload
