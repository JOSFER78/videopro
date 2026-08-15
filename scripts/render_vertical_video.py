#!/usr/bin/env python3
"""
render_vertical_video.py — Generador de Vídeo Vertical 9:16 (Shorts/TikTok/Reels) con VideoStorageManager.
======================================================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Crea un vídeo vertical MP4 9:16 (1080x1920) a partir de escenas/imágenes y locución de audio,
utilizando VideoStorageManager para gestionar directorios de proyecto, aislar temporales en .tmp/
y registrar la salida en exports/ (out/final_vertical.mp4) y project_manifest.json.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from video_storage_manager import (
        MIN_ASSET_SIZE_BYTES,
        VideoStorageManager,
    )
except ImportError:
    from scripts.video_storage_manager import (
        MIN_ASSET_SIZE_BYTES,
        VideoStorageManager,
    )


def get_audio_duration_seconds(audio_path: Path) -> float:
    """Obtiene la duración exacta de un archivo de audio usando ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def render_vertical_video(
    project_ref: Optional[Union[str, Path]] = None,
    asset_dir: Optional[Union[str, Path]] = None,
    audio_file: Optional[Union[str, Path]] = None,
    output_filename: str = "final_vertical.mp4",
) -> Dict[str, Any]:
    """
    Genera un vídeo vertical 9:16 normalizado y lo registra en el proyecto.
    """
    storage = VideoStorageManager(project_ref=project_ref or asset_dir, auto_create=True)
    
    input_asset_dir = Path(asset_dir).resolve() if asset_dir else storage.flow_images_dir
    if not input_asset_dir.exists() or not any(input_asset_dir.iterdir()):
        input_asset_dir = storage.photos_dir
        if not input_asset_dir.exists() or not any(input_asset_dir.iterdir()):
            input_asset_dir = storage.assets_dir

    # Buscar audio de locución
    if audio_file:
        input_audio_path = Path(audio_file).resolve()
    else:
        vo_candidates = [
            storage.audio_dir / "narration.mp3",
            storage.audio_dir / "narration.wav",
            storage.audio_dir / "vo_scene_1.wav",
            storage.audio_dir / "vo_scene_1.mp3",
        ]
        input_audio_path = next((a for a in vo_candidates if a.exists()), None)
        if not input_audio_path:
            audio_files = list(storage.audio_dir.glob("*.mp3")) + list(storage.audio_dir.glob("*.wav"))
            if audio_files:
                input_audio_path = audio_files[0]
            else:
                raise FileNotFoundError("No se encontró ningún archivo de locución de audio en el proyecto.")

    # Buscar imágenes de escenas
    scene_extensions = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    scene_images = []
    for ext in scene_extensions:
        scene_images.extend(list(input_asset_dir.glob(ext)))
    
    # Filtrar imágenes que cumplan la regla >5KB
    scene_images = sorted([img for img in scene_images if img.stat().st_size >= MIN_ASSET_SIZE_BYTES])
    if not scene_images:
        raise ValueError(f"No se encontraron imágenes válidas (>=5KB) en {input_asset_dir}")

    audio_dur = get_audio_duration_seconds(input_audio_path)
    count = len(scene_images)
    base_dur = round(audio_dur / count, 4)

    temp_dir = storage.get_temp_path(f"vertical_build_{os.getpid()}")
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"📱 GENERANDO VÍDEO VERTICAL 9:16 PARA PROYECTO: {storage.project_id} ({storage.version})")
    print(f"   Imágenes:    {count} en {input_asset_dir}")
    print(f"   Audio:       {input_audio_path} ({audio_dur:.2f}s)")
    print(f"   Salida MP4:  {storage.exports_dir / output_filename}")

    try:
        # Generar clips individuales 9:16 con padding
        clip_paths = []
        for idx, scene_img in enumerate(scene_images, start=1):
            dur = base_dur if idx < count else (audio_dur - (base_dur * (count - 1)))
            clip_path = temp_dir / f"clip_{idx}.mp4"
            cmd_clip = (
                f'ffmpeg -y -loglevel error -loop 1 -i "{scene_img}" -t {dur:.4f} '
                f'-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" '
                f'-r 25 -an "{clip_path}"'
            )
            subprocess.run(cmd_clip, shell=True, check=True)
            clip_paths.append(clip_path)

        # Crear concat list
        concat_txt = temp_dir / "concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for cp in clip_paths:
                f.write(f"file '{cp}'\n")

        video_only = temp_dir / "video_only.mp4"
        cmd_concat = f'ffmpeg -y -loglevel error -f concat -safe 0 -i "{concat_txt}" -c copy "{video_only}"'
        subprocess.run(cmd_concat, shell=True, check=True)

        dest_export_path = storage.exports_dir / output_filename
        cmd_final = (
            f'ffmpeg -y -loglevel error -i "{video_only}" -i "{input_audio_path}" '
            f'-c:v copy -c:a aac -b:a 128k -shortest "{dest_export_path}"'
        )
        subprocess.run(cmd_final, shell=True, check=True)

        # Validación Regla de Oro >5KB
        if not dest_export_path.exists() or dest_export_path.stat().st_size < MIN_ASSET_SIZE_BYTES:
            raise ValueError(
                f"❌ El vídeo vertical '{dest_export_path}' no cumple la Regla de Oro >5KB. "
                f"Tamaño: {dest_export_path.stat().st_size if dest_export_path.exists() else 0} B."
            )

        # Registrar el máster exportado en project_manifest.json
        export_record = storage.register_export(
            file_path=dest_export_path,
            export_type="vertical",
            platform="tiktok",
            crf=23,
            extra={
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "duration_seconds": audio_dur,
                "scenes_count": count
            }
        )

        storage.update_phase(
            "phase_5_render_and_composition",
            "completed",
            vertical_export=str(dest_export_path)
        )

        print(f"✅ VÍDEO VERTICAL 9:16 GENERADO Y REGISTRADO EXITOSAMENTE:")
        print(f"   Ruta: {dest_export_path}")
        return dict(export_record)
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="render_vertical_video.py",
        description="Genera vídeo vertical MP4 9:16 desde imágenes + locución usando VideoStorageManager.",
    )
    parser.add_argument("--project", "-p", help="Slug, ID o ruta del proyecto canónico", default=None)
    parser.add_argument("--asset-dir", "-a", help="Directorio de imágenes/escenas", default=None)
    parser.add_argument("--audio", help="Ruta al archivo de audio de locución", default=None)
    parser.add_argument("--output", "-o", help="Nombre de salida en exports/ (default: final_vertical.mp4)", default="final_vertical.mp4")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    return parser


def main() -> int:
    parser = _build_cli_parser()
    args = parser.parse_args()

    try:
        res = render_vertical_video(
            project_ref=args.project,
            asset_dir=args.asset_dir,
            audio_file=args.audio,
            output_filename=args.output,
        )
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"❌ Error en render_vertical_video: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
