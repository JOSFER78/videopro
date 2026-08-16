#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/server"
exec /home/ubuntu/vibevoice-venv/bin/python -m uvicorn videopro_server:app --host 0.0.0.0 --port 7001
