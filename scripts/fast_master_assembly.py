#!/usr/bin/env python3
"""
fast_master_assembly.py
=======================
Montaje rápido del máster 120s/24 shots:
- Usa assets existentes: keyframes + photo plates.
- Genera clips con zoompan/ken burns 4K 60fps.
- Aplica xfade micro-crossfades 30ms entre tomas.
- Mezcla audio VO + BGM + SFX con EBU R128 loudnorm.
- Entrega máster en exports/master_120s_4k60.mp4.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
PROJECT_DIR = WORKSPACE / "storage/projects/2026/08/2026-08-17_madrid_subterraneo_120s_24shots/v1"
SCENES = PROJECT_DIR / "scenes.json"
ASSETS = PROJECT_DIR / "assets"
AUDIO_DIR = PROJECT_DIR / "audio"
RENDERS = PROJECT_DIR / "renders"
EXPORTS = PROJECT_DIR / "exports"
TMP = PROJECT_DIR / ".tmp/fast_assembly"

TMP.mkdir(parents=True, exist_ok=True)
RENDERS.mkdir(parents=True, exist_ok=True)
EXPORTS.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT, FPS = 3840, 2160, 60
TRANSITION = "fade"
TRANSITION_DURATION = 0.03  # 30ms micro-crossfade


def ensure_clip(img_path: Path, out_path: Path, duration: float, motion_idx: int) -> Path:
    if out_path.exists() and out_path.stat().st_size > 5 * 1024:
        return out_path
    frames = max(1, int(round(duration * FPS)))
    if motion_idx % 2 == 0:
        zoom_expr = f"1.0+0.15*(on/{frames})"
    else:
        zoom_expr = f"1.15-0.15*(on/{frames})"
    x_expr = "iw/2-(iw/zoom/2)"
    y_expr = "ih/2-(ih/zoom/2)"
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d=1:s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-i", str(img_path),
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path


def build_master():
    scenes = json.loads(SCENES.read_text())["scenes"]
    clips = []
    for idx, sc in enumerate(scenes, start=1):
        rel = sc.get("visual_keyframe") or sc.get("photo_plate") or ""
        img = PROJECT_DIR / rel if rel else ASSETS / f"keyframes/shot_{idx:02d}_*.png"
        if not img.exists():
            img = PROJECT_DIR / sc.get("photo_plate", "")
        if not img.exists():
            matches = sorted(ASSETS.glob(f"keyframes/shot_{idx:02d}_*.png"))
            img = matches[0] if matches else ASSETS / f"keyframes/shot_{idx:02d}_*.png"
        if not img.exists():
            raise FileNotFoundError(f"Missing image for scene {idx}: {rel}")
        out = RENDERS / f"fast_scene_{idx:03d}.mp4"
        clips.append(ensure_clip(img, out, float(sc["duration_s"]), idx))

    # Build xfade chain
    inputs = []
    for c in clips:
        inputs.extend(["-i", str(c)])

    xfade_parts = []
    cur = "[0:v]"
    offset = 0.0
    for i in range(len(clips) - 1):
        dur = float(json.loads(SCENES.read_text())["scenes"][i]["duration_s"])
        offset += dur
        nxt = f"[{i+1}:v]"
        out = f"[v{i+1}]" if i < len(clips) - 2 else "[vout]"
        xfade_parts.append(
            f"{cur}{nxt}xfade=transition={TRANSITION}:duration={TRANSITION_DURATION:.3f}:offset={offset:.3f}{out}"
        )
        cur = out
    filter_complex = ";".join(xfade_parts)

    raw = TMP / "concatenated_raw.mp4"
    cmd_xfade = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        str(raw),
    ]
    subprocess.run(cmd_xfade, check=True)

    # Audio mix with EBU R128 loudnorm
    voice = AUDIO_DIR / "voice_narrator_es_120s.wav"
    bgm = AUDIO_DIR / "bgm" / "flow_music_118bpm_120s.wav"
    sfx = AUDIO_DIR / "sfx" / "foley_3d_spatial_120s.wav"

    cmd_audio = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(raw),
    ]
    audio_inputs = []
    audio_filters = []
    idx = 1
    if voice.exists():
        cmd_audio.extend(["-i", str(voice)])
        audio_inputs.append(f"[{idx}:a]volume=1.0[vo]")
        idx += 1
    if bgm.exists():
        cmd_audio.extend(["-i", str(bgm)])
        audio_inputs.append(f"[{idx}:a]volume=0.25,aloop=loop=-1:size=2e+09[bgm]")
        idx += 1
    if sfx.exists():
        cmd_audio.extend(["-i", str(sfx)])
        audio_inputs.append(f"[{idx}:a]volume=0.35[sfx]")
        idx += 1

    if not audio_inputs:
        out = EXPORTS / "master_120s_4k60.mp4"
        shutil.copy2(raw, out)
        print(f"✅ Máster sin audio copiado: {out}")
        return out

    mix_inputs = "[vo]" if voice.exists() else ""
    if bgm.exists():
        mix_inputs += "[bgm]" if voice.exists() else "[bgm]"
    if sfx.exists():
        mix_inputs += "[sfx]"
    n_inputs = (1 if voice.exists() else 0) + (1 if bgm.exists() else 0) + (1 if sfx.exists() else 0)
    mix = f"{mix_inputs}amix=inputs={n_inputs}:duration=first:dropout_transition=2,highpass=f=20:poles=2,loudnorm=I=-14.0:LRA=7.0:TP=-1.0[aout]"
    filter_complex_final = ";".join(audio_inputs) + ";" + mix
    cmd_audio.extend([
        "-filter_complex", filter_complex_final,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(EXPORTS / "master_120s_4k60.mp4"),
    ])
    subprocess.run(cmd_audio, check=True)
    out = EXPORTS / "master_120s_4k60.mp4"
    print(f"✅ Máster renderizado: {out}")
    return out


if __name__ == "__main__":
    try:
        build_master()
    except Exception as exc:
        print(f"❌ Error en fast_master_assembly: {exc}")
        sys.exit(2)
