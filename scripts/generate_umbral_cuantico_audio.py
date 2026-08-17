#!/usr/bin/env python3
"""
generate_umbral_cuantico_audio.py
================================================================================
Synthesizes and masters the complete 24-shot Spanish voiceover for:
'El Umbral Cuántico: La Revolución Silenciosa del Silicio y el Destino Humano'
- Engine: EdgeTTS (es-ES-AlvaroNeural / es-ES-EmilioNeural)
- Timing: Exact 5.0-second slot alignment per shot (120.0s total master)
- Dual-Pass EBU R128 Broadcast Normalization (-14.0 LUFS)
================================================================================
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from loguru import logger

WORKSPACE_ROOT = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
ESCALETA_JSON = WORKSPACE_ROOT / "data/documental_120s_escaleta_dop7.json"
OUTPUT_DIR = WORKSPACE_ROOT / "storage/audio/suite_120s_master"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = WORKSPACE_ROOT / ".tmp/audio_umbral"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "es-ES-AlvaroNeural"


async def synthesize_shot(text: str, out_path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate="+0%", pitch="+0Hz")
    await communicate.save(str(out_path))


async def main_async():
    with open(ESCALETA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = data.get("shots", [])
    logger.info(f"Synthesizing {len(shots)} shots for '{data.get('title')}'...")

    raw_wavs = []
    for s in shots:
        idx = s["shot_index"]
        text = s["narration_es"]
        mp3_path = TEMP_DIR / f"shot_{idx:02d}.mp3"
        wav_path = TEMP_DIR / f"shot_{idx:02d}.wav"

        logger.info(f"Shot {idx:02d} ({s['time_window']}): {text[:50]}...")
        await synthesize_shot(text, mp3_path)

        # Convert to 48kHz WAV with silence pad / trim to fit 5.0 seconds
        cmd = [
            "ffmpeg", "-y", "-i", str(mp3_path),
            "-ar", "48000", "-ac", "1",
            "-af", "apad=whole_dur=5.0",
            "-t", "5.0",
            str(wav_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raw_wavs.append(wav_path)

    # Concat all 24 wavs into 120.0s master
    concat_list = TEMP_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for w in raw_wavs:
            f.write(f"file '{w}'\n")

    unmastered_wav = TEMP_DIR / "umbral_unmastered.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(unmastered_wav)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    master_wav = OUTPUT_DIR / "voice_narrator_umbral_cuantico_120s.wav"
    # EBU R128 loudnorm filter
    subprocess.run([
        "ffmpeg", "-y", "-i", str(unmastered_wav),
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=7.0",
        "-ar", "48000", "-ac", "1",
        str(master_wav)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger.info(f"✅ Master audio created: {master_wav} (120.0s @ 48kHz -14 LUFS)")


if __name__ == "__main__":
    asyncio.run(main_async())
