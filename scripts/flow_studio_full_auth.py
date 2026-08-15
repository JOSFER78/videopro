#!/usr/bin/env python3
"""
flow_studio_full_auth.py — Autenticación y verificación de sesión en Google Flow con VideoStorageManager.
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
    storage = VideoStorageManager(project_ref=project_ref, title="Flow Auth Verification")
    screenshot_path = storage.get_screenshot_path("flow_studio_auth_done.png")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.config/brave-session-copy',
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("1. Cargando Google Flow...")
        page.goto('https://labs.google/fx/tools/flow/shared/tool/79c9d2e6-4ad6-4636-ad05-22022f8a5a74', wait_until='networkidle', timeout=30000)
        time.sleep(4)
        
        print("2. Buscando botón de Sign in...")
        signin_btn = page.query_selector('button:has-text("Sign in to Flow"), button:has-text("Sign in")')
        if signin_btn:
            print(f"Pulsando: {signin_btn.inner_text()}...")
            signin_btn.click()
            time.sleep(6)
            
        print(f"URL actual: {page.url}")
        print(f"Título actual: {page.title()}")
        
        acc_btn = page.query_selector('div:has-text("josferestudio@gmail.com"), li:has-text("josferestudio@gmail.com")')
        if acc_btn:
            print("Pulsando cuenta josferestudio@gmail.com...")
            acc_btn.click()
            time.sleep(6)
            print(f"URL tras cuenta: {page.url}")
            
        page.screenshot(path=str(screenshot_path))
        print(f"Captura guardada en: {screenshot_path}")
        context.close()

    print("Proceso de autenticación verificado.")


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    main(proj)
