#!/usr/bin/env bash
set -e

echo "=== Installing VideoPro Studio Service ==="
sudo cp /home/ubuntu/workspace/pro/hermes/10_videopro/deploy/videopro-v2.service /etc/systemd/system/videopro-v2.service
sudo systemctl daemon-reload
sudo systemctl restart videopro-v2.service
sudo systemctl status videopro-v2.service --no-pager
echo "=== VideoPro Studio Service Active ==="
