#!/usr/bin/env python3
"""
test_flow_keyframe_gen.py — Prueba de Storyboard Studio con VideoStorageManager.
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
    storage = VideoStorageManager(project_ref=project_ref, title="Storyboard Studio Test")
    screenshot_path = storage.get_screenshot_path("storyboard_studio_after_gen.png")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.config/brave-session-copy',
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navegando a Storyboard Studio en Google Flow...")
        page.goto('https://labs.google/fx/tools/flow/shared/tool/79c9d2e6-4ad6-4636-ad05-22022f8a5a74', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        textarea = page.query_selector('textarea, div[contenteditable="true"]')
        if textarea:
            prompt_text = "Sci-fi documentary: Cycler Odyssey transport ship approaching Mars orbit in 2200. Hyperrealistic, 35mm anamorphic prime lens, Kodak Vision3 500T 35mm film grain, ARRI Alexa LF color science, 8k."
            print(f"Introduciendo prompt de prueba en Storyboard Studio...")
            textarea.fill(prompt_text)
            time.sleep(2)
            
            gen_btn = page.query_selector('button:has-text("Generate"), button:has-text("Create"), button:has-text("Visualize"), button:has-text("Next"), button[type="submit"]')
            if gen_btn:
                print(f"Pulsando botón de generación: {gen_btn.inner_text()}...")
                gen_btn.click()
                time.sleep(8)
                
        page.screenshot(path=str(screenshot_path))
        print(f"Captura de pantalla guardada en: {screenshot_path}")
        context.close()

    print("Prueba de Storyboard Studio finalizada.")


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    main(proj)
