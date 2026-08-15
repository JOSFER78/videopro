#!/usr/bin/env python3
"""
robust_flow_inspector.py — Inspección Robusta de Google Flow con VideoStorageManager.
"""

import os
import sys
import time
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager

os.environ['DISPLAY'] = os.getenv('DISPLAY', ':99')
os.system('pkill -f "brave-session-copy" 2>/dev/null; rm -f /home/ubuntu/.config/brave-session-copy/SingletonLock')


def main(project_ref: str = None):
    storage = VideoStorageManager(project_ref=project_ref, title="Flow Robust Inspection")
    screenshot_path = storage.get_screenshot_path("flow_robust_check.png")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir='/home/ubuntu/.config/brave-session-copy',
                headless=False,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            print("1. Cargando URL con domcontentloaded...", flush=True)
            page.goto('https://labs.google/fx/tools/flow', wait_until='domcontentloaded', timeout=20000)
            time.sleep(4)
            
            print(f"2. URL actual: {page.url}", flush=True)
            print(f"3. Titulo actual: {page.title()}", flush=True)
            
            page.screenshot(path=str(screenshot_path))
            print(f"4. Captura guardada en: {screenshot_path}", flush=True)
            
            context.close()
    except Exception as e:
        print(f"Error en Playwright: {e}", flush=True)
        traceback.print_exc()

    print("Fin del script de inspección robusta.", flush=True)


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    main(proj)
