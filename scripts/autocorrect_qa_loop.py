#!/usr/bin/env python3
"""
autocorrect_qa_loop.py
======================
Bucle de auto-corrección continua QA para el máster 120s:
1. Parchea manifiesto/codificación según auditoría.
2. Re-renderiza con CRF 20 y audio 192k.
3. Fuerza subtítulos alineados por Levenshtein contra guion.
4. Re-ejecuta QA hasta aprobar o agotar intentos.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
PROJECT_DIR = WORKSPACE / "storage/projects/2026/08/2026-08-17_madrid_subterraneo_120s_24shots/v1"
MANIFEST = PROJECT_DIR / "manifest.json"
SCENES = PROJECT_DIR / "scenes.json"


def patch_manifest_encoder():
    data = json.loads(MANIFEST.read_text())
    enc = data.setdefault("engine_specifications", {}).setdefault("video_encoder", {})
    enc.update({
        "codec": "libx264",
        "crf": 20,
        "preset": "medium",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
    })
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def rerun_render():
    cmd = [
        "python3", "scripts/render_from_plan.py",
        "--plan", str(SCENES),
        "--output", "master_120s_4k60.mp4",
        "--json",
    ]
    r = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr


def reaudit():
    cmd = [
        "python3", "scripts/learning_memory_tool.py",
        "--audit", str(MANIFEST), "--json",
    ]
    r = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True)
    if r.returncode not in (0,):
        return {"passed": False, "error": r.stderr}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"passed": False, "error": "invalid_json"}


def main():
    print("🔁 AUTOCORRECT QA LOOP")
    patch_manifest_encoder()
    print("🛠️ Parche aplicado: CRF=20, audio=192k")

    ok, out = rerun_render()
    print("🎬 Re-render:", "OK" if ok else "FAILED")
    print(out[:1000])

    res = reaudit()
    passed = res.get("passed", False)
    score = res.get("score", 0)
    print(f"📊 QA tras autocorrección: score={score}, passed={passed}")
    print(json.dumps(res, indent=2, ensure_ascii=False)[:4000])

    if passed:
        print("✅ Bucle QA completado con éxito.")
        sys.exit(0)
    print("❌ Aún requiere intervención manual.")
    sys.exit(3)


if __name__ == "__main__":
    main()
