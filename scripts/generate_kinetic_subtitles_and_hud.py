#!/usr/bin/env python3
"""
generate_kinetic_subtitles_and_hud.py
================================================================================
CLI & Master Engine for Kinetic Subtitles & Modern HUD Overlays in VideoPro Studio:
1. Forced Deterministic Levenshtein Alignment against canonical script (Zero Whisper hallucinations).
2. Modern Kinetic Subtitles (Vox / MrBeast aesthetic: Gold #FFD700 / Pure White #FFFFFF, rounded pill boxes).
3. Diegetic Temporal Badges & 6-DoF Tactical HUD Overlays (4K UHD & 1080p).
4. Multi-format export: .ass, .srt, .vtt, .json, and .png overlay masks.
================================================================================
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.subtitles.forced_aligner import LevenshteinForcedAligner
from app.core.subtitles.kinetic_styler import KineticSubtitleStyler
from app.core.subtitles.hud_generator import ModernHUDGenerator
from app.core.subtitles.audio_transcriber import AudioTranscriber


def run_kinetic_subtitles_and_hud(
    script_path: Path,
    audio_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    resolution: str = "4k",
    highlight_color: str = "#FFD700",
    text_color: str = "#FFFFFF",
    whisper_model: str = "base",
    generate_overlays: bool = True
) -> Dict[str, Any]:
    """
    Main pipeline function to execute forced alignment, kinetic subtitle compilation, and HUD generation.
    """
    script_path = Path(script_path).resolve()
    if not script_path.exists():
        raise FileNotFoundError(f"Script / Escaleta not found: {script_path}")

    # Determine output directory
    if output_dir is None:
        output_dir = PROJECT_ROOT / "storage/projects/2026/08/2026-08-17_documental-umbral-cuantico-120s/subtitles"
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("🎬 [VideoPro Subtitle & HUD Suite] Kinetic Vox Styler & Levenshtein Engine")
    logger.info("=" * 80)
    logger.info(f"   Guión / Escaleta: {script_path}")
    logger.info(f"   Audio Master:     {audio_path or 'Synthesized / Canonical Timeline'}")
    logger.info(f"   Resolución:       {resolution.upper()}")
    logger.info(f"   Directorio Out:   {output_dir}")

    # 1. Load script / escaleta
    with open(script_path, "r", encoding="utf-8") as f:
        if script_path.suffix.lower() == ".json":
            script_data = json.load(f)
        else:
            script_data = f.read()

    # Extract shots if available
    shots = []
    project_title = "VideoPro Kinetic Master"
    if isinstance(script_data, dict):
        shots = script_data.get("shots", [])
        project_title = script_data.get("title", project_title)

    # 2. Transcribe Audio or use ASR cache
    asr_cache_file = output_dir / "whisper_raw_transcription.json"
    asr_data = None

    if asr_cache_file.exists():
        logger.info(f"Found cached ASR transcription: {asr_cache_file.name}")
        try:
            with open(asr_cache_file, "r", encoding="utf-8") as f:
                asr_data = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cached ASR data: {e}")

    if asr_data is None and audio_path and Path(audio_path).exists():
        audio_path = Path(audio_path).resolve()
        logger.info(f"Running Whisper '{whisper_model}' on {audio_path.name}...")
        transcriber = AudioTranscriber(model_size=whisper_model, language="es")
        asr_data = transcriber.transcribe(audio_path)
        # Cache raw transcription for instant reuse
        with open(asr_cache_file, "w", encoding="utf-8") as f:
            json.dump(asr_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Cached raw Whisper transcription to {asr_cache_file.name}.")
    elif asr_data is None:
        logger.info("No audio provided or ASR cached; performing escaleta-driven linear distribution.")
        asr_data = {"segments": []}

    # 3. Deterministic Levenshtein Forced Alignment
    logger.info("Performing dynamic Levenshtein & DTW alignment against canonical text...")
    aligner = LevenshteinForcedAligner()
    total_audio_duration = 120.0
    if isinstance(script_data, dict):
        total_audio_duration = float(script_data.get("total_duration_seconds", 120.0))

    alignment_res = aligner.align(script_data, asr_data, total_audio_duration=total_audio_duration)

    logger.info("-" * 80)
    logger.info(f"✓ Total Palabras Canónicas:   {alignment_res.total_canonical_words}")
    logger.info(f"✓ Palabras ASR Reconocidas:    {alignment_res.total_asr_words}")
    logger.info(f"✓ Palabras Emparejadas (DTW):  {alignment_res.matched_words} ({alignment_res.alignment_rate}%)")
    logger.info(f"✓ Alucinaciones Whisper Purgadas: {alignment_res.hallucinated_asr_dropped}")
    logger.info(f"✓ Palabras Interpoladas Suave: {alignment_res.interpolated_words}")
    logger.info(f"✓ Confianza Promedio:         {alignment_res.average_confidence:.2f}")
    logger.info("-" * 80)

    # 4. Kinetic Subtitle Styler (Vox / MrBeast Aesthetic)
    logger.info("Compiling Vox / MrBeast kinetic subtitles (Gold #FFD700 / White #FFFFFF)...")
    styler = KineticSubtitleStyler(
        target_resolution=resolution,
        highlight_color_hex=highlight_color,
        text_color_hex=text_color
    )
    chunks = styler.build_chunks(alignment_res.aligned_tokens)

    # File paths
    ass_file = output_dir / "subtitles_kinetic_vox.ass"
    srt_file = output_dir / "subtitles_kinetic.srt"
    vtt_file = output_dir / "subtitles_kinetic.vtt"
    json_file = output_dir / "kinetic_subtitles_manifest.json"

    ass_content = styler.generate_ass(chunks, title=project_title)
    srt_content = styler.generate_srt(chunks)
    vtt_content = styler.generate_vtt(chunks)
    json_manifest = styler.generate_json_manifest(
        chunks,
        metadata={
            "project_title": project_title,
            "resolution": resolution,
            "total_duration_sec": total_audio_duration,
            "alignment_rate": alignment_res.alignment_rate,
            "hallucinations_dropped": alignment_res.hallucinated_asr_dropped
        }
    )

    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_content)
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_content)
    with open(vtt_file, "w", encoding="utf-8") as f:
        f.write(vtt_content)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Subtítulos ASS generados:  {ass_file} ({len(chunks)} chunks)")
    logger.info(f"✓ Subtítulos SRT generados:  {srt_file}")
    logger.info(f"✓ Subtítulos VTT generados:  {vtt_file}")
    logger.info(f"✓ Manifiesto JSON generado:  {json_file}")

    # 5. Generate HUD Overlays & Diegetic Badges
    hud_overlays = []
    if shots and generate_overlays:
        logger.info(f"Generating {len(shots)} transparent HUD overlays ({resolution.upper()})...")
        hud_dir = output_dir / "hud_overlays"
        hud_gen = ModernHUDGenerator(resolution=resolution)
        overlay_paths = hud_gen.generate_all_shots_overlays(shots, hud_dir)
        hud_overlays = [str(p) for p in overlay_paths]
        logger.info(f"✓ {len(hud_overlays)} capas HUD generadas en: {hud_dir}")

    logger.info("=" * 80)
    logger.info("✅ Pipeline de Subtítulos Cinéticos y HUD completado con éxito.")
    logger.info("=" * 80)

    return {
        "status": "success",
        "output_dir": str(output_dir),
        "ass_path": str(ass_file),
        "srt_path": str(srt_file),
        "vtt_path": str(vtt_file),
        "json_path": str(json_file),
        "total_chunks": len(chunks),
        "alignment_rate": alignment_res.alignment_rate,
        "hallucinations_dropped": alignment_res.hallucinated_asr_dropped,
        "hud_overlays_count": len(hud_overlays),
        "hud_overlays_dir": str(output_dir / "hud_overlays") if hud_overlays else None
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generador de Subtítulos Cinéticos Vox con Alineación Levenshtein y HUD de Telemetría."
    )
    parser.add_argument(
        "--script", "-s",
        default="data/documental_120s_escaleta_dop7.json",
        help="Ruta al guion canónico o escaleta JSON/MD."
    )
    parser.add_argument(
        "--audio", "-a",
        default="storage/audio/suite_120s_master/voice_narrator_es_120s.wav",
        help="Ruta al archivo de audio de locución máster."
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Directorio de exportación de subtítulos y overlays."
    )
    parser.add_argument(
        "--resolution", "-r",
        default="4k",
        choices=["4k", "1080p"],
        help="Resolución de destino (4k o 1080p)."
    )
    parser.add_argument(
        "--highlight-color",
        default="#FFD700",
        help="Color hexadecimal de resalte de palabra activa (default: #FFD700 Oro)."
    )
    parser.add_argument(
        "--text-color",
        default="#FFFFFF",
        help="Color hexadecimal de texto base (default: #FFFFFF Blanco)."
    )
    parser.add_argument(
        "--whisper-model",
        default="base",
        help="Modelo de Whisper a utilizar ('tiny', 'base', 'small', etc.)."
    )
    parser.add_argument(
        "--no-overlays",
        action="store_true",
        help="Omitir la generación de capas gráficas HUD PNG."
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        res = run_kinetic_subtitles_and_hud(
            script_path=Path(args.script),
            audio_path=Path(args.audio) if args.audio and Path(args.audio).exists() else None,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            resolution=args.resolution,
            highlight_color=args.highlight_color,
            text_color=args.text_color,
            whisper_model=args.whisper_model,
            generate_overlays=not args.no_overlays
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        logger.error(f"Error fatal en el pipeline: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
