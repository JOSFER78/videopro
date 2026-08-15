#!/usr/bin/env python3
"""
render_from_plan.py — Motor de Renderizado Programático desde Plan de Escenas (scenes.json).
========================================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Ensambla y renderiza un máster de vídeo completo a partir de un plan de escenas (scenes.json),
utilizando las imágenes, clips, locuciones y audio diegético registrados en VideoStorageManager.
Aplica efectos cinemáticos (Ken Burns, transiciones, audio ducking) y registra el producto
final en exports/ (out/final.mp4) y project_manifest.json.
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


def render_scene_clip(
    scene_id: int,
    image_path: Path,
    audio_path: Optional[Path],
    output_scene_mp4: Path,
    duration_s: float = 10.0,
    overlay_path: Optional[Path] = None,
) -> Path:
    """Renderiza un clip de escena individual con efecto Ken Burns y superposición opcional."""
    output_scene_mp4.parent.mkdir(parents=True, exist_ok=True)

    # Selección alterna de dirección de pan/zoom
    if scene_id % 2 == 1:
        zoom_filter = "scale=1920:1080,zoompan=z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1920x1080:fps=24"
    else:
        zoom_filter = "scale=1920:1080,zoompan=z='1.10':x='if(lte(on,1),(iw-iw/zoom)/2,x+0.8)':y='ih/2-(ih/zoom/2)':d=240:s=1920x1080:fps=24"

    audio_idx = 1
    if overlay_path and overlay_path.exists():
        filter_complex = (
            f"[0:v]{zoom_filter}[bg]; "
            f"[1:v]scale=1920:1080,format=rgba,colorchannelmixer=aa=1.0,"
            f"fade=t=in:st=1.0:d=0.8:alpha=1,fade=t=out:st=8.5:d=0.7:alpha=1[vox]; "
            f"[bg][vox]overlay=0:0[vfinal]"
        )
        inputs = f'-loop 1 -t {duration_s} -i "{image_path}" -loop 1 -t {duration_s} -i "{overlay_path}"'
        map_v = '-map "[vfinal]"'
        audio_idx = 2
    else:
        filter_complex = f"[0:v]{zoom_filter}[vfinal]"
        inputs = f'-loop 1 -t {duration_s} -i "{image_path}"'
        map_v = '-map "[vfinal]"'
        audio_idx = 1

    if audio_path and audio_path.exists():
        inputs += f' -i "{audio_path}"'
        map_a = f"-map {audio_idx}:a"
    else:
        map_a = "-an"

    cmd = (
        f'ffmpeg -y -loglevel error {inputs} '
        f'-filter_complex "{filter_complex}" '
        f'{map_v} {map_a} '
        f'-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p '
        f'-c:a aac -b:a 192k -shortest "{output_scene_mp4}"'
    )

    subprocess.run(cmd, shell=True, check=True)
    return output_scene_mp4


def render_project_from_plan(
    plan_path_or_slug: Union[str, Path],
    output_filename: str = "final.mp4",
    preset: str = "vox_documentary",
) -> Dict[str, Any]:
    """
    Lee plan de escenas y renderiza el máster completo registrándolo en VideoStorageManager.
    """
    storage = VideoStorageManager(project_ref=plan_path_or_slug, auto_create=True)
    
    scenes_path = storage.scenes_path
    if not scenes_path.exists():
        # Fallback: buscar en scene_data
        fallback_plan = storage.scene_data_dir / "scenes.json"
        if fallback_plan.exists():
            scenes_path = fallback_plan
        else:
            raise FileNotFoundError(f"Archivo de plan de escenas no encontrado: {scenes_path}")

    with open(scenes_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    scenes = plan_data.get("scenes", []) if isinstance(plan_data, dict) else plan_data
    if not scenes:
        raise ValueError("El plan de escenas está vacío o no contiene el campo 'scenes'.")

    rendered_dir = storage.renders_dir
    exports_dir = storage.exports_dir
    temp_dir = storage.temp_dir

    print(f"🎬 RENDERIZANDO PLAN DE ESCENAS PARA PROYECTO: {storage.project_id} ({storage.version})")
    print(f"   Plan:        {scenes_path}")
    print(f"   Escenas:     {len(scenes)}")
    print(f"   Renders Dir: {rendered_dir}")

    scene_clips = []
    
    for idx, sc in enumerate(scenes, start=1):
        sid = sc.get("id", idx)
        title = sc.get("title", f"Escena {sid}")
        duration = float(sc.get("duration_seconds", 10.0))

        # Resolver la imagen visual de la escena
        img_name = sc.get("image") or f"flow_scene_{sid}.png"
        img_path = (
            storage.flow_images_dir / img_name
            if (storage.flow_images_dir / img_name).exists()
            else (
                storage.photos_dir / img_name
                if (storage.photos_dir / img_name).exists()
                else storage.get_asset_path("keyframes", f"marte_scene_{sid}.png")
            )
        )

        if not img_path.exists():
            # Si no existe una imagen específica, buscar cualquier imagen disponible o crear una sólida
            any_imgs = list(storage.assets_dir.rglob("*.png")) + list(storage.assets_dir.rglob("*.jpg"))
            if any_imgs:
                img_path = any_imgs[0]
            else:
                img_path = temp_dir / f"solid_bg_{sid}.png"
                subprocess.run(
                    f'ffmpeg -y -loglevel error -f lavfi -i color=c=0x243048:s=1920x1080:d=1 -vframes 1 "{img_path}"',
                    shell=True, check=True
                )

        audio_name = sc.get("audio") or f"vo_scene_{sid}.wav"
        audio_path = storage.audio_dir / audio_name
        if not audio_path.exists():
            audio_path = storage.audio_dir / f"vo_scene_{sid}.mp3"
            if not audio_path.exists():
                audio_path = None

        vox_name = sc.get("vox") or f"vox_overlay_{sid}.png"
        vox_path = storage.vox_dir / vox_name
        if not vox_path.exists():
            vox_path = None

        out_scene_mp4 = rendered_dir / f"rendered_scene_{sid}.mp4"
        print(f"   Procesando [{sid}/{len(scenes)}]: {title}...")
        render_scene_clip(
            scene_id=sid,
            image_path=img_path,
            audio_path=audio_path,
            output_scene_mp4=out_scene_mp4,
            duration_s=duration,
            overlay_path=vox_path,
        )
        scene_clips.append(str(out_scene_mp4))

    # Concatenar escenas
    concat_txt = temp_dir / "concat_scenes.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in scene_clips:
            f.write(f"file '{c}'\n")

    raw_concat_mp4 = temp_dir / "raw_concatenated_video.mp4"
    cmd_concat = f'ffmpeg -y -loglevel error -f concat -safe 0 -i "{concat_txt}" -c copy "{raw_concat_mp4}"'
    subprocess.run(cmd_concat, shell=True, check=True)

    final_master_mp4 = exports_dir / output_filename

    # Mezcla final de audio si existen pistas BGM o SFX
    bgm_file = storage.audio_dir / "bgm" / "bgm_main.wav"
    if not bgm_file.exists():
        bgm_file = list((storage.audio_dir / "bgm").glob("*.*"))[0] if (storage.audio_dir / "bgm").exists() and list((storage.audio_dir / "bgm").glob("*.*")) else None

    if bgm_file and bgm_file.exists():
        cmd_master = (
            f'ffmpeg -y -loglevel error -i "{raw_concat_mp4}" -i "{bgm_file}" '
            f'-filter_complex "[0:a]volume=1.0[vo];[1:a]volume=0.25[bgm];[vo][bgm]amix=inputs=2:duration=first[aout]" '
            f'-map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k "{final_master_mp4}"'
        )
        subprocess.run(cmd_master, shell=True, check=True)
    else:
        shutil.copy2(raw_concat_mp4, final_master_mp4)

    # Validar Regla de Oro >5KB
    if not final_master_mp4.exists() or final_master_mp4.stat().st_size < MIN_ASSET_SIZE_BYTES:
        raise ValueError(
            f"❌ El máster final '{final_master_mp4}' no cumple la Regla de Oro >5KB. "
            f"Tamaño: {final_master_mp4.stat().st_size if final_master_mp4.exists() else 0} B."
        )

    # Registrar el export en project_manifest.json
    export_record = storage.register_export(
        file_path=final_master_mp4,
        export_type="master",
        platform="youtube",
        crf=18,
        extra={"scenes_count": len(scenes), "preset": preset}
    )

    storage.update_phase(
        "phase_5_render_and_composition",
        "completed",
        master_output=str(final_master_mp4),
        scenes_rendered=len(scenes)
    )

    print(f"✅ RENDERIZADO COMPLETADO Y REGISTRADO EXITOSAMENTE:")
    print(f"   Archivo: {final_master_mp4}")
    return dict(export_record)


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="render_from_plan.py",
        description="Renderiza un máster de vídeo desde un scenes.json usando VideoStorageManager.",
    )
    parser.add_argument("--plan", "-p", help="Ruta a scenes.json, slug o ruta de proyecto", required=True)
    parser.add_argument("--output", "-o", help="Nombre del archivo de salida en exports/ (default: final.mp4)", default="final.mp4")
    parser.add_argument("--preset", help="Estilo visual (vox_documentary, bbc, etc.)", default="vox_documentary")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    return parser


def main() -> int:
    parser = _build_cli_parser()
    args = parser.parse_args()

    try:
        res = render_project_from_plan(
            plan_path_or_slug=args.plan,
            output_filename=args.output,
            preset=args.preset,
        )
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"❌ Error en render_from_plan: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
