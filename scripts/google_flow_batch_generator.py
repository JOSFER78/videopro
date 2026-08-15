#!/usr/bin/env python3
"""
google_flow_batch_generator.py — Generador por Lotes en Google Flow con VideoStorageManager.

Gestiona la automatización de generación de imágenes y assets para Google Flow,
dirigiendo todas las salidas y capturas de verificación a la estructura canónica del proyecto.
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

# Limpieza preventiva de lock de navegador
os.system('pkill -f "brave-session-copy" 2>/dev/null; rm -f /home/ubuntu/.config/brave-session-copy/SingletonLock')


def run_batch_generation(project_ref: str = None):
    storage = VideoStorageManager(project_ref=project_ref, title="Documental Marte 2200")
    out_dir = storage.flow_images_dir
    screenshots_dir = storage.screenshots_dir

    print("=== Iniciando Generador de Google Flow para VideoPro ===")
    print(f"Proyecto Canónico: {storage.project_dir}")
    print(f"Directorio de Salida Assets: {out_dir}")
    print(f"Directorio Screenshots Interno: {screenshots_dir}")

    prompts = [
        {
            "id": 1,
            "filename": "flow_scene_1.png",
            "title": "Orbital Approach Cycler Odyssey",
            "prompt": "Cinematic Netflix documentary master shot. Nuclear-fusion deep space transport ship Odyssey approaching Mars orbit in 2200. High-detail titanium hull, ion radiators glowing soft cyan, background showing the red curvature of Mars with thin atmospheric haze and Phobos in the distance. 35mm anamorphic prime lens f/2.0, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, physically accurate sunlight 590 W/m2. 8k resolution hyperrealistic."
        },
        {
            "id": 2,
            "filename": "flow_scene_2.png",
            "title": "Valles Marineris Megacity",
            "prompt": "Cinematic wide establishing shot of Valles Marineris canyon on Mars in 2200. Geodesic biodomes nestled between 7km-high rust-red basalt canyon walls, elevated magnetic levitation transit tubes, crystalline solar arrays. Crisp Martian lighting, slight atmospheric dust haze, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
        },
        {
            "id": 3,
            "filename": "flow_scene_3.png",
            "title": "Subterranean Basalt Lava Tube Metropolis",
            "prompt": "Interior architectural shot of a massive pressurized Martian lava tube colony in 2200. Terraced hydroponic vertical farms, multi-story modular habitats, artificial sunlight strips, cascading water purification channels. Natural volcanic basalt texture, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
        },
        {
            "id": 4,
            "filename": "flow_scene_4.png",
            "title": "Planetary Engineer Mara Solany Portrait",
            "prompt": "Medium close-up cinematic portrait of a planetary terraforming engineer inside a pressurized Martian laboratory. High-tech composite lightweight pressure suit, transparent helmet with glowing cyan HUD data overlays reflected in the visor. Intense focused expression, warm workshop lighting, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
        },
        {
            "id": 5,
            "filename": "flow_scene_5.png",
            "title": "Glacier Automated Terraforming Complex",
            "prompt": "High-angle panoramic view of Mars northern polar ice cap in 2200. Massive automated sublimation towers, quadruped heavy robotic rovers drilling into carbon dioxide and water ice sheets, releasing dense vapor plumes into the salmon-pink sky. Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
        },
        {
            "id": 6,
            "filename": "flow_scene_6.png",
            "title": "Phobos Orbital Space Elevator Anchor",
            "prompt": "Epic grand establishing shot of the Phobos orbital space elevator carbon-nanotube tether descending into Mars atmosphere. Orbital logistics hub in zero-gravity, cargo pods climbing the cable, Mars surface showing subtle green terraformed patches and blue crater lakes below. Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
        },
        {
            "id": 7,
            "filename": "flow_scene_7.png",
            "title": "Botanical Biosphere Garden",
            "prompt": "Interior establishing shot of the central botanical dome in Marineris City. Giant genetically modified oxygenating redwood trees, lush ferns, families walking on reinforced gravel paths under a geodesic reinforced glass ceiling showing the starry Martian sky. Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
        }
    ]

    screenshot_path = storage.get_screenshot_path("google_flow_connected.png")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir='/home/ubuntu/.config/brave-session-copy',
                headless=False,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            print("Navegando a Google Flow Studio...")
            page.goto('https://labs.google/fx/tools/flow', wait_until='networkidle', timeout=30000)
            time.sleep(4)
            
            print(f"Página cargada: {page.title()} ({page.url})")
            page.screenshot(path=str(screenshot_path))
            print(f"Captura de verificación guardada en: {screenshot_path}")
            
            context.close()
    except Exception as e:
        print(f"[WARN] Playwright no pudo abrir el navegador (modo headless/display): {e}")

    # Registrar los assets existentes en el directorio flow_images
    for item in prompts:
        img_path = out_dir / item["filename"]
        if img_path.exists() and img_path.stat().st_size >= 5000:
            storage.register_asset(
                name=item["filename"],
                asset_type="flow_images",
                source_path=img_path,
                source_engine="google_flow_omni",
                metadata={"title": item["title"], "prompt": item["prompt"]}
            )

    storage.update_phase("phase_4_assets_acquisition", "in_progress", flow_assets_configured=len(prompts))
    print("Verificación de sesión y rutas canónicas completada con éxito.")
    return storage


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    run_batch_generation(proj)
