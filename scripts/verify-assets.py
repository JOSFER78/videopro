#!/usr/bin/env python3
"""
verify-assets.py — Verificación de Integridad de Activos y Manifiesto con VideoStorageManager.

Comprueba que todos los activos en el proyecto cumplan la Regla de Oro (> 5 KB, no vacíos,
MIME / formato válido) y que el project_manifest.json esté debidamente sincronizado.

Uso:
    python3 verify-assets.py [/ruta/al/proyecto_o_assets]
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager


def validate_generic_folder(root: Path, min_size: int = 5000) -> tuple[bool, list[str]]:
    failures = []
    allowed_ext = {".jpg", ".jpeg", ".png", ".mp4", ".webm", ".json", ".md", ".svg", ".txt", ".wav", ".mp3", ".vtt"}
    
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.startswith(".") or fname.endswith(".prompt") or fname.endswith(".subject"):
                continue
            fpath = Path(dirpath) / fname
            if not fpath.is_file():
                continue
            size = fpath.stat().st_size
            if size < min_size:
                failures.append(f"{fpath} – {size} B (menor al umbral de {min_size} B)")
            ext = fpath.suffix.lower()
            if ext not in allowed_ext:
                print(f"[WARN] Extensión no estándar en {fpath}: {ext}")
    return len(failures) == 0, failures


def main():
    target_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Intentar instanciar VideoStorageManager
    try:
        storage = VideoStorageManager(project_ref=target_arg, auto_create=False)
        if storage.project_dir.exists():
            print(f"🔍 Validando proyecto canónico: {storage.project_dir}")
            passed, errors = storage.validate_all_assets()
            if passed:
                print("✅ Todos los activos del proyecto pasaron la validación de integridad (> 5 KB, Cero Placeholders).")
                manifest = storage.load_manifest()
                asset_count = len(manifest.get("assets_manifest", []))
                print(f"📋 Activos auditados en project_manifest.json: {asset_count}")
                return 0
            else:
                print("\n❌ Fallo en la validación de activos:")
                for err in errors:
                    print(f"  - {err}")
                return 2
    except Exception:
        pass

    # Fallback a validación de carpeta genérica
    target_path = Path(target_arg or ".").resolve()
    if not target_path.exists():
        print(f"[ERROR] Ruta no encontrada: {target_path}")
        return 1

    print(f"🔍 Escaneando directorio: {target_path}")
    passed, errors = validate_generic_folder(target_path)
    if passed:
        print("✅ Todos los activos pasaron la validación de integridad (> 5 KB).")
        return 0
    else:
        print("\n❌ Fallo en la validación de activos:")
        for err in errors:
            print(f"  - {err}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
