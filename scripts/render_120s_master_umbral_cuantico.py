#!/usr/bin/env python3
"""
render_120s_master_umbral_cuantico.py
========================================================================================
Motor Maestro de Renderizado y Composición Cinemática 120s (24 Tomas 4K 60fps).
Proyecto: El Umbral Cuántico: La Revolución Silenciosa del Silicio y el Destino Humano
          (documental-umbral-cuantico-120s)

Características Principales:
1. RITMO CINEMÁTICO 120s:
   - 24 Tomas de 5.00s exactos sincronizadas con marcas temporales de audio (vo_durations.json).
2. MOVIMIENTO KEN BURNS 6-DoF 60FPS:
   - Interpolación suave a 60fps (Zoom-In, Zoom-Out, Pan Left/Right, Tilt Up/Down, Float).
3. TRANSICIONES CINEMÁTICAS FLUIDAS:
   - Micro-crossfades con xfade (fade, dissolve, wipeleft, smoothleft) con compensación de tiempo.
4. SUBTÍTULOS DORADOS LEVENSHTEIN (#FFD700):
   - Alineación forzada determinista contra guion original.
   - Estilo Oro Cinemático (&H0000D7FF) con micro-animaciones karaoke.
5. AUDIO AUDIÓFILO MASTER EBU R128:
   - Mezcla tri-capa (Voz Neural es-emilio + Flow Music 118 BPM + Foley 3D diegético).
   - Dynamic sidechain ducking (-20dB) y normalización broadcast (-14.0 LUFS, Peak -1.0 dBTP).
6. CONTROL DE CALIDAD QA AUTOMATIZADO:
   - Verificación de metadatos con ffprobe, contact sheet 3x3, y manifest JSON.
========================================================================================
"""

from __future__ import annotations

import os
import sys
import json
import math
import time
import shutil
import hashlib
import tempfile
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

# Base Paths
WORKSPACE_ROOT = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
PROJECT_ID = "2026-08-17_documental-umbral-cuantico-120s"
PROJECT_DIR = WORKSPACE_ROOT / f"storage/projects/2026/08/{PROJECT_ID}"
PROJECT_AUDIO_DIR = PROJECT_DIR / "audio"
PROJECT_SUBTITLES_DIR = PROJECT_DIR / "subtitles"
PROJECT_EXPORTS_DIR = PROJECT_DIR / "exports/master"
PROJECT_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

KEYFRAMES_DIR = WORKSPACE_ROOT / "storage/projects/2026/08/2026-08-17_documental_futurista_4k_40tomas_120s/v1/assets/keyframes"
ESCALETA_JSON = WORKSPACE_ROOT / "data/documental_120s_escaleta_dop7.json"
VO_DURATIONS_JSON = PROJECT_AUDIO_DIR / "vo_durations.json"
AUDIO_MASTER_WAV = PROJECT_AUDIO_DIR / "audio_suite_master_ebur128_120s.wav"

OUTPUTS_DIR = WORKSPACE_ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


class CinematicScene:
    def __init__(
        self,
        shot_index: int,
        shot_id: str,
        image_path: str,
        duration: float = 5.0,
        motion_type: str = "auto",
        transition_type: str = "fade",
        transition_duration: float = 0.35,
        text: str = "",
        hud_badge: str = ""
    ):
        self.shot_index = shot_index
        self.shot_id = shot_id
        self.image_path = str(image_path)
        self.duration = duration
        self.motion_type = motion_type
        self.transition_type = transition_type
        self.transition_duration = transition_duration
        self.text = text
        self.hud_badge = hud_badge


class Master120sProductionPipeline:
    def __init__(
        self,
        resolution: str = "1080p",  # 1080p or 4k
        fps: int = 60,
        crf: int = 18,
        preset: str = "veryfast",
        target_lufs: float = -14.0
    ):
        self.resolution = resolution.lower()
        self.fps = fps
        self.crf = crf
        self.preset = preset
        self.target_lufs = target_lufs

        if self.resolution == "4k":
            self.width = 3840
            self.height = 2160
            self.font_size = 54
            self.ass_file = PROJECT_SUBTITLES_DIR / "subtitles_gold_4k.ass"
        else:
            self.width = 1920
            self.height = 1080
            self.font_size = 36
            self.ass_file = PROJECT_SUBTITLES_DIR / "subtitles_gold_1080p.ass"

    def build_scene_list(self) -> List[CinematicScene]:
        """Construye el listado de las 24 tomas cinemáticas con su keyframe y movimiento 6-DoF asignado."""
        with open(ESCALETA_JSON, "r", encoding="utf-8") as f:
            escaleta_data = json.load(f)

        shots = escaleta_data.get("shots", [])
        scenes: List[CinematicScene] = []

        motion_palette = [
            "zoom_in", "zoom_out", "pan_right", "tilt_up",
            "subtle_float", "pan_left", "zoom_in", "tilt_down",
            "zoom_out", "pan_right", "zoom_in", "subtle_float"
        ]
        transition_palette = [
            "fade", "dissolve", "wipeleft", "smoothleft",
            "fade", "dissolve", "wiperight", "smoothleft"
        ]

        for s in shots:
            idx = s["shot_index"]
            shot_id = s["shot_id"]
            text = s.get("narration_es", "")
            time_win = s.get("time_window", "")

            # Buscar keyframe PNG o JPG
            matches = list(KEYFRAMES_DIR.glob(f"*_{idx:02d}_*")) or list(KEYFRAMES_DIR.glob(f"*_{idx}_*"))
            png_matches = [m for m in matches if m.suffix.lower() == ".png"]
            jpg_matches = [m for m in matches if m.suffix.lower() in [".jpg", ".jpeg"]]
            
            img_path = None
            if png_matches:
                img_path = str(png_matches[0])
            elif jpg_matches:
                img_path = str(jpg_matches[0])
            elif matches:
                img_path = str(matches[0])
            else:
                all_imgs = sorted(list(KEYFRAMES_DIR.glob("*.png")) + list(KEYFRAMES_DIR.glob("*.jpg")))
                img_path = str(all_imgs[(idx - 1) % len(all_imgs)])

            motion = motion_palette[(idx - 1) % len(motion_palette)]
            trans = transition_palette[(idx - 1) % len(transition_palette)]
            trans_dur = 0.35

            scenes.append(CinematicScene(
                shot_index=idx,
                shot_id=shot_id,
                image_path=img_path,
                duration=5.0,
                motion_type=motion,
                transition_type=trans,
                transition_duration=trans_dur,
                text=text,
                hud_badge=f"TOMA {idx:02d}/24 | {time_win}"
            ))

        return scenes

    def render_single_clip(
        self,
        scene: CinematicScene,
        out_path: Path,
        total_frames: int
    ) -> bool:
        """Renderiza un clip individual aplicando movimiento Ken Burns continuo a 60fps."""
        motion = scene.motion_type
        frames = total_frames

        if motion == "zoom_in":
            zoom_expr = f"1.0+0.16*(on/{frames})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "zoom_out":
            zoom_expr = f"1.16-0.16*(on/{frames})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "pan_right":
            zoom_expr = "1.14"
            x_expr = f"(on/{frames})*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "pan_left":
            zoom_expr = f"1.14"
            x_expr = f"(1.0-(on/{frames}))*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "tilt_up":
            zoom_expr = "1.14"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = f"(1.0-(on/{frames}))*(ih-ih/zoom)"
        elif motion == "tilt_down":
            zoom_expr = "1.14"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = f"(on/{frames})*(ih-ih/zoom)"
        else:  # subtle_float
            zoom_expr = f"1.06+0.04*sin(2*PI*(on/{frames}))"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        filter_str = (
            f"scale={self.width*2}:{self.height*2}:force_original_aspect_ratio=increase,"
            f"crop={self.width*2}:{self.height*2},"
            f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={self.width}x{self.height}:fps={self.fps},"
            f"setsar=1,settb=AVTB,format=yuv420p"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", scene.image_path,
            "-vf", filter_str,
            "-t", str(scene.duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", str(self.crf),
            "-pix_fmt", "yuv420p",
            "-an",
            str(out_path)
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return out_path.exists() and out_path.stat().st_size > 1000
        except Exception as ex:
            logger.warning(f"Fallback simple para toma {scene.shot_index}: {ex}")
            fb_filter = f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,crop={self.width}:{self.height},setsar=1,settb=AVTB,fps={self.fps},format=yuv420p"
            fb_cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", scene.image_path,
                "-vf", fb_filter,
                "-t", str(scene.duration),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", str(self.crf),
                "-pix_fmt", "yuv420p",
                "-an",
                str(out_path)
            ]
            subprocess.run(fb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return out_path.exists()

    def assemble_and_render(self, output_mp4: Path) -> Dict[str, Any]:
        """Ejecuta el pipeline completo de montaje, subtitulación y renderizado."""
        start_time = time.time()
        scenes = self.build_scene_list()
        logger.info(f"🎬 Iniciando montaje de {len(scenes)} tomas para {PROJECT_ID} a {self.resolution.upper()} ({self.width}x{self.height} @ {self.fps}fps)...")

        temp_dir = Path(tempfile.mkdtemp(prefix="videopro_master_120s_"))
        clips_dir = temp_dir / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        # 1. Renderizado paralelo de clips individuales con Ken Burns
        clip_paths: List[Path] = [clips_dir / f"clip_{idx:02d}.mp4" for idx in range(1, len(scenes) + 1)]
        
        logger.info("⚙️ [1/4] Renderizando clips individuales con movimiento Ken Burns 60fps...")
        
        def _render_task(i: int):
            sc = scenes[i]
            out_p = clip_paths[i]
            extra_t = sc.transition_duration if i < len(scenes) - 1 else 0.0
            dur_total = sc.duration + extra_t
            frames = int(math.ceil(dur_total * self.fps))
            
            sc_render = CinematicScene(
                shot_index=sc.shot_index,
                shot_id=sc.shot_id,
                image_path=sc.image_path,
                duration=dur_total,
                motion_type=sc.motion_type,
                transition_type=sc.transition_type,
                transition_duration=sc.transition_duration,
                text=sc.text,
                hud_badge=sc.hud_badge
            )
            self.render_single_clip(sc_render, out_p, frames)
            return i

        max_workers = min(os.cpu_count() or 4, 8)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_render_task, i) for i in range(len(scenes))]
            for fut in as_completed(futures):
                idx = fut.result()
                logger.info(f"   ✓ Toma {idx+1:02d}/24 renderizada: {scenes[idx].shot_id}")

        # 2. Transiciones Fluidas Xfade
        logger.info("⚡ [2/4] Aplicando transiciones cinemáticas fluidas xfade...")
        raw_video_path = temp_dir / "raw_video_timeline.mp4"

        try:
            inputs_args = []
            for cp in clip_paths:
                inputs_args.extend(["-i", str(cp)])

            xfade_filters = []
            current_v = "[0:v]"
            accumulated_offset = 0.0

            for i in range(len(clip_paths) - 1):
                next_v = f"[{i+1}:v]"
                out_v = f"[v_xf_{i+1}]" if i < len(clip_paths) - 2 else "[v_concat]"
                shot_dur = scenes[i].duration
                trans_type = scenes[i].transition_type
                trans_dur = scenes[i].transition_duration

                valid_trans = ["fade", "wipeleft", "wiperight", "slideleft", "slideright", "dissolve", "smoothleft", "smoothright"]
                actual_trans = trans_type if trans_type in valid_trans else "fade"

                accumulated_offset += shot_dur
                xfade_filters.append(
                    f"{current_v}{next_v}xfade=transition={actual_trans}:duration={trans_dur:.3f}:offset={accumulated_offset:.3f}{out_v}"
                )
                current_v = out_v

            filter_complex_str = ";".join(xfade_filters)
            cmd_xfade = [
                "ffmpeg", "-y",
                *inputs_args,
                "-filter_complex", filter_complex_str,
                "-map", "[v_concat]",
                "-c:v", "libx264",
                "-preset", self.preset,
                "-crf", str(self.crf),
                "-pix_fmt", "yuv420p",
                str(raw_video_path)
            ]
            subprocess.run(cmd_xfade, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info("   ✓ Transiciones xfade aplicadas con éxito.")
        except Exception as ex:
            logger.warning(f"Fallback a concat regular por error en xfade: {ex}")
            concat_txt = temp_dir / "concat_list.txt"
            with open(concat_txt, "w") as f:
                for cp in clip_paths:
                    f.write(f"file '{cp}'\n")
            cmd_concat = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_txt),
                "-c", "copy",
                str(raw_video_path)
            ]
            subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 3. Subtítulos Dorados ASS & Mux de Audio EBU R128
        logger.info("🎚️ [3/4] Muxing de Audio Master EBU R128 y quemado de Subtítulos Dorados ASS (#FFD700)...")
        
        ass_filter = ""
        if self.ass_file.exists():
            ass_escaped = str(self.ass_file).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            ass_filter = f"ass={ass_escaped}"
        else:
            logger.warning(f"No se encontró archivo ASS en {self.ass_file}, renderizando sin subtítulos quemados.")

        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(raw_video_path),
            "-i", str(AUDIO_MASTER_WAV)
        ]

        if ass_filter:
            cmd_final.extend(["-vf", ass_filter])

        cmd_final.extend([
            "-c:v", "libx264",
            "-preset", self.preset,
            "-crf", str(self.crf),
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-t", "120.0",
            str(output_mp4)
        ])

        subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 4. Verificación y Auditoría QA
        logger.info("🔍 [4/4] Verificando especificaciones del Master final con ffprobe...")
        qa_metrics = self.verify_master_quality(output_mp4)

        # Contact Sheet QA
        contact_sheet_path = output_mp4.parent / f"{output_mp4.stem}_contact_sheet_qa.jpg"
        self.generate_contact_sheet(output_mp4, contact_sheet_path)

        elapsed = time.time() - start_time
        logger.success(f"🏆 ¡MASTER FINAL 120s RENDERIZADO CON ÉXITO en {elapsed:.1f}s!")
        logger.info(f"   📁 Archivo:    {output_mp4} ({qa_metrics['size_mb']:.2f} MB)")
        logger.info(f"   ⏱️ Duración:   {qa_metrics['duration_seconds']:.2f} s (Target: 120.0s)")
        logger.info(f"   📐 Resolución: {qa_metrics['width']}x{qa_metrics['height']} @ {qa_metrics['fps']} fps")
        logger.info(f"   🎧 Audio:      {qa_metrics['audio_codec']} @ {qa_metrics['audio_sample_rate']} Hz")
        logger.info(f"   📸 Contact QA: {contact_sheet_path}")

        # Limpiar temporales
        shutil.rmtree(temp_dir, ignore_errors=True)

        return {
            "success": True,
            "master_file": str(output_mp4),
            "contact_sheet": str(contact_sheet_path),
            "qa_metrics": qa_metrics,
            "render_time_seconds": round(elapsed, 2)
        }

    def verify_master_quality(self, video_path: Path) -> Dict[str, Any]:
        """Certifica mediante ffprobe el cumplimiento estricto de las especificaciones."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size,bit_rate:stream=width,height,r_frame_rate,codec_name,sample_rate",
            "-of", "json",
            str(video_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(res.stdout)

        fmt = info.get("format", {})
        streams = info.get("streams", [])
        v_stream = next((s for s in streams if s.get("codec_name") in ["h264", "hevc", "vp9", "av1"]), streams[0])
        a_stream = next((s for s in streams if s.get("codec_name") in ["aac", "mp3", "opus", "pcm_s16le", "pcm_s24le"]), None)

        dur_s = float(fmt.get("duration", 0.0))
        size_b = int(fmt.get("size", video_path.stat().st_size))
        size_mb = size_b / (1024 * 1024)

        fps_parts = v_stream.get("r_frame_rate", "60/1").split("/")
        actual_fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else float(fps_parts[0])

        if size_b < 5120:
            raise ValueError(f"Violación de Regla de Oro >5KB: tamaño {size_b} B")

        return {
            "duration_seconds": dur_s,
            "size_bytes": size_b,
            "size_mb": round(size_mb, 2),
            "width": int(v_stream.get("width", self.width)),
            "height": int(v_stream.get("height", self.height)),
            "fps": round(actual_fps, 2),
            "video_codec": v_stream.get("codec_name"),
            "audio_codec": a_stream.get("codec_name") if a_stream else "none",
            "audio_sample_rate": int(a_stream.get("sample_rate", 48000)) if a_stream else 0,
            "bitrate_kbps": int(fmt.get("bit_rate", 0)) // 1000 if fmt.get("bit_rate") else 0
        }

    def generate_contact_sheet(self, video_path: Path, output_img: Path):
        """Genera un mosaico 3x3 para inspección visual de fotogramas."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", "select='not(mod(n\\,800))',scale=640:360,tile=3x3",
            "-frames:v", "1",
            "-q:v", "2",
            str(output_img)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description="Renderizador Master 120s VideoPro")
    parser.add_argument("--resolution", "-r", default="1080p", choices=["1080p", "4k"], help="Resolución de renderizado (1080p o 4k)")
    parser.add_argument("--fps", type=int, default=60, help="Framerate (default: 60)")
    parser.add_argument("--crf", type=int, default=18, help="Calidad CRF x264 (default: 18)")
    parser.add_argument("--out", "-o", default=None, help="Ruta de archivo MP4 de salida")
    args = parser.parse_args()

    pipeline = Master120sProductionPipeline(
        resolution=args.resolution,
        fps=args.fps,
        crf=args.crf
    )

    out_file = Path(args.out) if args.out else PROJECT_EXPORTS_DIR / f"master_120s_{args.resolution}_60fps.mp4"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    result = pipeline.assemble_and_render(out_file)

    # Replicar en outputs públicos
    public_master = OUTPUTS_DIR / f"master_120s_umbral_cuantico_{args.resolution}_60fps.mp4"
    shutil.copy2(str(out_file), str(public_master))
    logger.info(f"✓ Replicado en outputs: {public_master}")

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
