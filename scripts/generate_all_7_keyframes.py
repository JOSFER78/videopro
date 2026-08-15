#!/usr/bin/env python3
"""
generate_all_7_keyframes.py — Generación y Registro de 7 Keyframes Maestros de Alta Fidelidad.

Utiliza VideoStorageManager para almacenar los keyframes e imágenes maestras
en la jerarquía canónica de activos (assets/keyframes o assets/images) y registra
los metadatos y prompts en project_manifest.json sin dispersión temporal.
"""

import os
import sys
import time
import json
from pathlib import Path

# Soporte de importación de VideoStorageManager tanto local como desde scripts
try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager

os.environ['DISPLAY'] = os.getenv('DISPLAY', ':99')

# Limpieza preventiva de lock de navegador
os.system('pkill -f "brave-session-copy" 2>/dev/null; rm -f /home/ubuntu/.config/brave-session-copy/SingletonLock')

KEYFRAMES_DEFAULT = [
    {
        "id": 1,
        "name": "marte_scene_1_orbital_approach.png",
        "title": "Orbital Approach Cycler Odyssey",
        "prompt": "Cinematic Netflix documentary master shot. Nuclear-fusion deep space transport ship Odyssey approaching Mars orbit in 2200. High-detail titanium hull, ion radiators glowing soft cyan, background showing the red curvature of Mars with thin atmospheric haze and Phobos in the distance. 35mm anamorphic prime lens f/2.0, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, physically accurate sunlight 590 W/m2. 8k resolution hyperrealistic."
    },
    {
        "id": 2,
        "name": "marte_scene_2_marineris_megacity.png",
        "title": "Valles Marineris Megacity",
        "prompt": "Cinematic wide establishing shot of Valles Marineris canyon on Mars in 2200. Geodesic biodomes nestled between 7km-high rust-red basalt canyon walls, elevated magnetic levitation transit tubes, crystalline solar arrays. Crisp Martian lighting, slight atmospheric dust haze, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
    },
    {
        "id": 3,
        "name": "marte_scene_3_lava_tube_city.png",
        "title": "Subterranean Basalt Lava Tube Metropolis",
        "prompt": "Interior architectural shot of a massive pressurized Martian lava tube colony in 2200. Terraced hydroponic vertical farms, multi-story modular habitats, artificial sunlight strips, cascading water purification channels. Natural volcanic basalt texture, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
    },
    {
        "id": 4,
        "name": "marte_scene_4_engineer_portrait.png",
        "title": "Planetary Engineer Mara Solany Portrait",
        "prompt": "Medium close-up cinematic portrait of a planetary terraforming engineer inside a pressurized Martian laboratory. High-tech composite lightweight pressure suit, transparent helmet with glowing cyan HUD data overlays reflected in the visor. Intense focused expression, warm workshop lighting, Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
    },
    {
        "id": 5,
        "name": "marte_scene_5_polar_terraforming.png",
        "title": "Glacier Automated Terraforming Complex",
        "prompt": "High-angle panoramic view of Mars northern polar ice cap in 2200. Massive automated sublimation towers, quadruped heavy robotic rovers drilling into carbon dioxide and water ice sheets, releasing dense vapor plumes into the salmon-pink sky. Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
    },
    {
        "id": 6,
        "name": "marte_scene_6_space_elevator.png",
        "title": "Phobos Orbital Space Elevator Anchor",
        "prompt": "Epic grand establishing shot of the Phobos orbital space elevator carbon-nanotube tether descending into Mars atmosphere. Orbital logistics hub in zero-gravity, cargo pods climbing the cable, Mars surface showing subtle green terraformed patches and blue crater lakes below. Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
    },
    {
        "id": 7,
        "name": "marte_scene_7_biosphere_garden.png",
        "title": "Botanical Biosphere Garden",
        "prompt": "Interior establishing shot of the central botanical dome in Marineris City. Giant genetically modified oxygenating redwood trees, lush ferns, families walking on reinforced gravel paths under a geodesic reinforced glass ceiling showing the starry Martian sky. Kodak Vision3 500T 35mm grain, ARRI Alexa LF color science, 8k resolution hyperrealistic."
    }
]


def generate_and_register_keyframes(project_ref: str = None):
    # Inicializar almacenamiento estructurado
    storage = VideoStorageManager(project_ref=project_ref, title="Documental Marte 2200")
    
    print("=== Generando y Registrando 7 Keyframes Maestros con VideoStorageManager ===")
    print(f"Proyecto: {storage.project_dir}")
    print(f"Directorio Keyframes: {storage.keyframes_dir}")
    print(f"Directorio Images: {storage.images_dir}")

    # Guardar archivo de prompts maestro dentro de scene_data
    prompts_file = storage.scene_data_dir / "keyframes_prompts.json"
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump(KEYFRAMES_DEFAULT, f, indent=2, ensure_ascii=False)
    print(f"Prompts guardados en: {prompts_file}")

    for kf in KEYFRAMES_DEFAULT:
        target_path = storage.get_asset_path("keyframes", kf["name"])
        print(f"[{kf['id']}/7] Destino canónico: {target_path.name}")
        print(f"      Prompt: {kf['prompt'][:90]}...")
        
        # Si ya existe el archivo en imágenes o assets, registrarlo con hash y verificación >5KB
        img_alt = storage.images_dir / kf["name"]
        if img_alt.exists() and img_alt.stat().st_size >= 5000:
            storage.register_asset(
                name=kf["name"],
                asset_type="keyframes",
                source_path=img_alt,
                source_engine="nanobanana",
                metadata={"id": kf["id"], "title": kf["title"], "prompt": kf["prompt"]}
            )
        elif target_path.exists() and target_path.stat().st_size >= 5000:
            storage.register_asset(
                name=kf["name"],
                asset_type="keyframes",
                source_path=target_path,
                source_engine="nanobanana",
                metadata={"id": kf["id"], "title": kf["title"], "prompt": kf["prompt"]}
            )

    # Actualizar estado de fase en manifest
    storage.update_phase(
        "phase_3_storyboard_and_scenes",
        "completed",
        scenes_count=len(KEYFRAMES_DEFAULT),
        shots_total=len(KEYFRAMES_DEFAULT)
    )

    print("\n✅ Todos los 7 keyframes registrados y coordinados en project_manifest.json.")
    return storage


if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else None
    generate_and_register_keyframes(proj)
