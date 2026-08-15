#!/usr/bin/env python3
"""
dismiss_modal_flow.py — Cierre de modales de Google Flow con VideoStorageManager.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager

os.environ['DISPLAY'] = os.getenv('DISPLAY', ':99')
os.system('pkill -f "brave-session-copy" 2>/dev/null; rm -f /home/ubuntu/.config/brave-session-copy/SingletonLock')


def main(project_ref: str = None):
    storage = VideoStorageManager(project_ref=project_ref, title="Flow Modal Dismiss")
    screenshot_path = storage.get_screenshot_path("google_flow_modal_dismissed.png")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.config/brave-session-copy',
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Cargando Google Flow...")
        page.goto('https://labs.google/fx/tools/flow', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        page.keyboard.press('Escape')
        time.sleep(1)
        
        close_btns = page.query_selector_all('button:has-text("OK"), button:has-text("Got it"), button:has-text("Accept"), button:has-text("Dismiss"), button:has-text("Close"), button[aria-label="Close"]')
        for cb in close_btns:
            if cb.is_visible():
                print(f"Pulsando botón de cierre de modal: {cb.inner_text()}...")
                cb.click(force=True)
                time.sleep(1)
                
        print(f"URL tras limpiar modales: {page.url}")
        print(f"Título: {page.title()}")
        page.screenshot(path=str(screenshot_path))
        print(f"Captura guardada en: {screenshot_path}")
        context.close()

    print("Verificación de modales completada.")


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    main(proj)
