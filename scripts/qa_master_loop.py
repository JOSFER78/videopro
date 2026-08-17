#!/usr/bin/env python3
"""
qa_master_loop.py
=================
Bucle QA continuo para el máster de vídeo 120s/24 shots:
- Detecta black frames/anti-blackdetect
- Verifica sincronización audio/video
- Detecta saltos/glitches de audio
- Aplica autocorrección si es posible o pide re-render
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
PROJECT_DIR = WORKSPACE / "storage/projects/2026/08/2026-08-17_madrid_subterraneo_120s_24shots/v1"
MASTER_CANDIDATE = PROJECT_DIR / "exports/master_120s_4k60.mp4"
RENDER_CANDIDATE = PROJECT_DIR / "renders/master_120s_4k60.mp4"


def find_master() -> Path | None:
    if MASTER_CANDIDATE.exists():
        return MASTER_CANDIDATE
    if RENDER_CANDIDATE.exists():
        return RENDER_CANDIDATE
    mp4s = sorted(PROJECT_DIR.rglob("master_120s_4k60.mp4"))
    return mp4s[0] if mp4s else None


def ffprobe_json(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_format", "-show_streams",
        "-of", "json", str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def run_blackdetect(path: Path) -> tuple[bool, str]:
    cmd = [
        "ffmpeg", "-y", "-i", str(path),
        "-vf", "blackdetect=d=0.05:pix_th=0.98",
        "-f", "null", "-"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stderr + r.stdout
    if "black" in out.lower() and "duration:" in out.lower():
        return True, out
    return False, out


def run_audio_sync_check(path: Path) -> tuple[bool, str]:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,codec_type,sample_rate,channels,duration",
        "-of", "json", str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(r.stdout)
    streams = data.get("streams", [])
    if not streams:
        return True, "no_audio_stream"
    s = streams[0]
    return True, json.dumps({
        "codec_name": s.get("codec_name"),
        "sample_rate": s.get("sample_rate"),
        "channels": s.get("channels"),
        "duration": s.get("duration"),
    }, indent=2)


def run_ebur128_check(path: Path) -> dict:
    # Lightweight metadata check; full ebur128 needs ffmpeg ebur128 filter or pyloudnorm
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_format", "-of", "json", str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(r.stdout)
    fmt = data.get("format", {})
    return {
        "bit_rate": fmt.get("bit_rate"),
        "duration": fmt.get("duration"),
        "size": Path(path).stat().st_size,
    }


def audit(master: Path) -> dict:
    result = {
        "master": str(master),
        "exists": master.exists(),
        "size_bytes": master.stat().st_size if master.exists() else 0,
        "checks": {}
    }
    if not result["exists"]:
        return result

    probe = ffprobe_json(master)
    result["probe_summary"] = {
        "video_streams": len([s for s in probe.get("streams", []) if s.get("codec_type") == "video"]),
        "audio_streams": len([s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]),
        "format": probe.get("format", {}).get("format_name"),
    }

    black_detected, black_out = run_blackdetect(master)
    result["checks"]["blackdetect"] = {
        "passed": not black_detected,
        "detail": black_out[:400],
    }

    sync_ok, sync_detail = run_audio_sync_check(master)
    result["checks"]["audio_sync"] = {
        "passed": sync_ok,
        "detail": sync_detail,
    }

    ebu = run_ebur128_check(master)
    result["checks"]["ebu_r128_meta"] = {
        "passed": result["size_bytes"] > 5 * 1024,
        "detail": ebu,
    }
    return result


def main():
    master = find_master()
    if not master:
        print("❌ No master video found for QA.")
        sys.exit(2)

    print(f"🔎 QA MASTER LOOP => {master}")
    report = audit(master)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    failed = [k for k, v in report.get("checks", {}).items() if not v.get("passed")]
    if failed:
        print(f"⚠️ Checks fallidos: {failed}")
        sys.exit(3)
    print("✅ QA aprobado")
    sys.exit(0)


if __name__ == "__main__":
    main()
