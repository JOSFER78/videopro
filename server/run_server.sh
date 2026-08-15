#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== Starting VideoPro Studio v2.0 Cinematic Engine ==="
exec /home/ubuntu/vibevoice-venv/bin/python videopro_server.py
