#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Starting VideoPro Studio (Development Mode on Port 7001 with Hot-Reload)..."
exec "$DIR/run_dev_7001.sh"
