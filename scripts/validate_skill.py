#!/usr/bin/env python3
"""
validate_skill.py — Validador integral de la estructura de la skill videopro.
"""

import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

def main():
    errors = []
    
    # 1. Verificar SKILL.md
    if not (SKILL_DIR / "SKILL.md").exists():
        errors.append("Falta SKILL.md en la raíz de la skill")

    # 2. Verificar Referencias
    refs = list((SKILL_DIR / "references").glob("*.md"))
    if len(refs) < 3:
        errors.append(f"Muy pocas referencias encontradas ({len(refs)} < 3)")

    # 3. Verificar Scripts
    scripts = list((SKILL_DIR / "scripts").glob("*.py"))
    if not scripts:
        errors.append("No se encontraron scripts Python en scripts/")

    # 4. Verificar VideoStorageManager
    storage_script = SKILL_DIR / "scripts" / "video_storage_manager.py"
    if not storage_script.exists():
        errors.append("Falta video_storage_manager.py en scripts/")
    else:
        try:
            sys.path.insert(0, str(SKILL_DIR / "scripts"))
            from video_storage_manager import VideoStorageManager
            mgr = VideoStorageManager(auto_create=False)
            assert hasattr(mgr, "register_asset")
            assert hasattr(mgr, "get_asset_path")
            assert hasattr(mgr, "validate_all_assets")
        except Exception as e:
            errors.append(f"Error al importar o validar VideoStorageManager: {e}")

    # 5. Verificar Plantillas
    templates = list((SKILL_DIR / "templates").glob("*.json"))
    if not templates:
        errors.append("No se encontraron plantillas JSON en templates/")

    if errors:
        print("❌ VALIDACIÓN DE SKILL FALLIDA:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("✅ SKILL VIDEOPRO V4.0 OK: Estructura, scripts, plantillas y VideoStorageManager validados.")
    sys.exit(0)

if __name__ == "__main__":
    main()
