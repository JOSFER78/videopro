#!/usr/bin/env python3
"""
download_clips.py — Descarga y Registro de Clips y Activos con VideoStorageManager.
=============================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Descarga o copia clips de vídeo y recursos multimedia desde URLs o rutas locales
directamente a la estructura canónica del proyecto de vídeo, garantizando la
Regla de Oro (>5KB) y registrando el activo en manifest.json.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from video_storage_manager import (
        MIN_ASSET_SIZE_BYTES,
        VideoStorageManager,
        slugify,
    )
except ImportError:
    from scripts.video_storage_manager import (
        MIN_ASSET_SIZE_BYTES,
        VideoStorageManager,
        slugify,
    )


def download_clip(
    source: str,
    project_ref: Optional[Union[str, Path]] = None,
    filename: Optional[str] = None,
    category: str = "broll",
    engine: str = "gemini-omni-flash-preview",
    prompt: Optional[str] = None,
    node_id: Optional[int] = None,
    duration_s: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    min_size_bytes: int = MIN_ASSET_SIZE_BYTES,
) -> Dict[str, Any]:
    """
    Descarga o copia un clip/activo y lo registra en el VideoStorageManager del proyecto.

    Args:
        source: URL (http/https) o ruta de archivo local.
        project_ref: Slug, ID de proyecto o ruta del proyecto canónico.
        filename: Nombre del archivo destino (opcional, se infiere si no se provee).
        category: Categoría ('broll', 'raw_clips', 'photos', 'audio', etc.).
        engine: Nombre del motor generador/origen.
        prompt: Prompt de generación opcional.
        node_id: ID de nodo o escena opcional.
        duration_s: Duración en segundos opcional.
        metadata: Diccionario con metadatos adicionales.
        min_size_bytes: Umbral mínimo de tamaño en bytes (default: 5120 B / 5KB).

    Returns:
        Dict con los datos del activo/clip registrado.
    """
    storage = VideoStorageManager(project_ref=project_ref, auto_create=True)
    
    # Resolver nombre de archivo destino
    if not filename:
        if source.startswith("http://") or source.startswith("https://"):
            parsed_name = Path(source.split("?")[0]).name
            filename = parsed_name if parsed_name else "downloaded_clip.mp4"
        else:
            filename = Path(source).name

    dest_path = storage.get_asset_path(category, filename)
    temp_path = storage.get_temp_path(f"download_{slugify(filename)}")

    print(f"📥 Descargando/Copiando clip a proyecto: {storage.project_id} ({storage.version})")
    print(f"   Origen:  {source}")
    print(f"   Destino: {dest_path}")

    # Descarga o copia al directorio temporal del proyecto (.tmp)
    try:
        if source.startswith("http://") or source.startswith("https://"):
            req = urllib.request.Request(
                source,
                headers={"User-Agent": "Hermes-VideoPro-Downloader/4.0"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp, open(temp_path, "wb") as f:
                shutil.copyfileobj(resp, f)
        else:
            local_src = Path(source).resolve()
            if not local_src.exists():
                raise FileNotFoundError(f"Archivo de origen local no existe: {local_src}")
            shutil.copy2(local_src, temp_path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(f"Error descargando/copiando clip desde '{source}': {e}") from e

    # Validación de la Regla de Oro de 5KB
    file_size = temp_path.stat().st_size
    if file_size < min_size_bytes:
        temp_path.unlink()
        raise ValueError(
            f"❌ El clip descargado '{filename}' fue rechazado por la Regla de Oro >5KB. "
            f"Tamaño: {file_size} B < {min_size_bytes} B."
        )

    # Mover de .tmp a la ubicación canónica
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(temp_path), str(dest_path))

    # Registrar clip o activo según la categoría
    if category.lower() in ("broll", "raw_clips", "flow_videos", "video", "videos"):
        record = storage.register_clip(
            file_path=dest_path,
            prompt=prompt,
            node_id=node_id,
            duration_s=duration_s,
            engine=engine,
            extra=metadata,
        )
    else:
        record = storage.register_asset(
            file_path=dest_path,
            category=category,
            source_engine=engine,
            metadata=metadata,
            name=filename,
        )

    print(f"✅ Clip guardado y registrado exitosamente en project_manifest.json ({file_size} B).")
    return dict(record)


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="download_clips.py",
        description="Descarga y registra clips multimedia en el VideoStorageManager de videopro.",
    )
    parser.add_argument("source", help="URL o ruta de archivo local a descargar/copiar")
    parser.add_argument("--project", "-p", help="Slug, ID o ruta del proyecto", default=None)
    parser.add_argument("--filename", "-f", help="Nombre personalizado para el archivo guardado", default=None)
    parser.add_argument("--category", "-c", help="Categoría (broll, raw_clips, photos, audio, etc.)", default="broll")
    parser.add_argument("--engine", help="Motor generador / origen (default: gemini-omni-flash-preview)", default="gemini-omni-flash-preview")
    parser.add_argument("--prompt", help="Prompt de generación opcional", default=None)
    parser.add_argument("--node-id", type=int, help="ID de nodo/escena opcional", default=None)
    parser.add_argument("--duration", type=float, help="Duración en segundos opcional", default=None)
    parser.add_argument("--json", action="store_true", help="Imprimir respuesta en JSON")
    return parser


def main() -> int:
    parser = _build_cli_parser()
    args = parser.parse_args()

    try:
        record = download_clip(
            source=args.source,
            project_ref=args.project,
            filename=args.filename,
            category=args.category,
            engine=args.engine,
            prompt=args.prompt,
            node_id=args.node_id,
            duration_s=args.duration,
        )
        if args.json:
            print(json.dumps(record, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"❌ Error en download_clips: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
