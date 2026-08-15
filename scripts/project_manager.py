#!/usr/bin/env python3
"""
project_manager.py — Backward-compatible wrapper for video_storage_manager.py
=============================================================================
Delegates all project lifecycle, path resolution, and storage operations to
video_storage_manager.py.
"""

import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import video_storage_manager

if __name__ == "__main__":
    sys.exit(video_storage_manager.main())
