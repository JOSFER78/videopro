#!/usr/bin/env python3
"""
inspect_storyboard_dom.py — Inspección DOM de Storyboard Studio con VideoStorageManager.
"""

import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager

os.environ['DISPLAY'] = os.getenv('DISPLAY', ':99')
os.system('pkill -f "brave-session-copy" 2>/dev/null; rm -f /home/ubuntu/.config/brave-session-copy/SingletonLock')


def main(project_ref: str = None):
    storage = VideoStorageManager(project_ref=project_ref, title="Storyboard DOM Inspection")
    screenshot_path = storage.get_screenshot_path("storyboard_dom_inspection.png")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir='/home/ubuntu/.config/brave-session-copy',
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navegando a Storyboard Studio...")
        page.goto('https://labs.google/fx/tools/flow/shared/tool/79c9d2e6-4ad6-4636-ad05-22022f8a5a74', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        elements_info = page.evaluate("""() => {
            const results = [];
            const all = document.querySelectorAll('button, input, textarea, div[contenteditable="true"], div[role="textbox"], [role="button"]');
            for (const el of all) {
                const rect = el.getBoundingClientRect();
                const visible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).display !== 'none';
                results.push({
                    tag: el.tagName,
                    type: el.getAttribute('type'),
                    placeholder: el.getAttribute('placeholder') || el.getAttribute('aria-label') || '',
                    text: el.innerText.trim().slice(0, 50),
                    className: el.className,
                    visible: visible,
                    rect: {x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height)}
                });
            }
            return results;
        }""")
        
        print(f"Total elementos encontrados: {len(elements_info)}")
        for i, e in enumerate(elements_info):
            if e['visible']:
                print(f"[{i}] {e['tag']} (visible: {e['rect']}): text='{e['text']}' placeholder='{e['placeholder']}'")
                
        page.screenshot(path=str(screenshot_path))
        print(f"Captura de DOM guardada en: {screenshot_path}")
        context.close()


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    main(proj)
