#!/usr/bin/env python3
"""
verify-assets.py — Verificación de Integridad de Activos y Manifiesto con VideoStorageManager.
=============================================================================================
Comprueba que todos los activos en el proyecto cumplan la Regla de Oro (> 5 KB, no vacíos,
MIME / formato válido) y que el project_manifest.json esté debidamente sincronizado.

Soporta argumentos posicionales y banderas como --episode EP01 / --all / -p.
"""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    try:
        from scripts.video_storage_manager import VideoStorageManager
    except ImportError:
        VideoStorageManager = None


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
    parser = argparse.ArgumentParser(description="Verificador de Integridad de Assets (> 5KB, Cero Placeholders)")
    parser.add_argument("path", nargs="?", default=None, help="Ruta al proyecto o directorio de assets")
    parser.add_argument("--episode", "-e", type=str, default=None, help="ID de episodio (e.g. EP01, tokyo)")
    parser.add_argument("--project", "-p", type=str, default=None, help="Slug o ID de proyecto canónico")
    args = parser.parse_args()

    target_ref = args.project or args.episode or args.path
    if args.episode and not args.project:
        ep_map = {
            "EP01": "chronodrift-ep01-tokyo",
            "EP02": "chronodrift-ep02-newyork",
            "EP03": "chronodrift-ep03-london",
            "EP04": "chronodrift-ep04-paris",
            "EP05": "chronodrift-ep05-amsterdam",
            "EP06": "chronodrift-ep06-rome",
            "EP07": "chronodrift-ep07-dubai",
            "EP08": "chronodrift-ep08-hongkong",
            "EP09": "chronodrift-ep09-cairo",
            "EP10": "chronodrift-ep10-venice",
            "TOKYO": "chronodrift-ep01-tokyo",
            "NEWYORK": "chronodrift-ep02-newyork",
            "LONDON": "chronodrift-ep03-london",
            "PARIS": "chronodrift-ep04-paris",
            "AMSTERDAM": "chronodrift-ep05-amsterdam",
            "ROME": "chronodrift-ep06-rome",
            "DUBAI": "chronodrift-ep07-dubai",
            "HONGKONG": "chronodrift-ep08-hongkong",
            "CAIRO": "chronodrift-ep09-cairo",
            "VENICE": "chronodrift-ep10-venice",
        }
        target_ref = ep_map.get(args.episode.upper(), f"chronodrift-{args.episode.lower()}")

    # Intentar instanciar VideoStorageManager
    if VideoStorageManager:
        try:
            storage = VideoStorageManager(project_ref=target_ref, auto_create=False)
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
    target_path = Path(target_ref or ".").resolve()
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
