"""
Motor de Subtítulos y HUD Cinematográfico: Vox Dynamic Kinetic Styler & Levenshtein Forced Aligner
==================================================================================================
Integra:
1. Alineación forzada determinista por distancia Levenshtein contra guion original.
2. Generación de subtítulos cinéticos Vox/MrBeast con cajas redondeadas, texto dorado (#FFD700) y blanco (#FFFFFF).
3. Generación de overlays HUD de telemetría y badges temporales diegéticos (4K/1080p).
4. Exportación simultánea a ASS, SRT, VTT, JSON y capas de overlay PNG transparentes.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.job import JobStep
from app.core.subtitles.forced_aligner import LevenshteinForcedAligner
from app.core.subtitles.kinetic_styler import KineticSubtitleStyler
from app.core.subtitles.hud_generator import ModernHUDGenerator
from app.core.subtitles.audio_transcriber import AudioTranscriber


class SubtitlesAdapter(BaseEngineAdapter):
    """
    Adaptador unificado para subtítulos cinéticos dinámicos y HUD de alto impacto.
    """

    @property
    def engine_id(self) -> str:
        return "vox_subtitles"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        # Require either script_data, escaleta_path or text
        return any(k in input_data for k in ["script_data", "escaleta_path", "text", "shots"])

    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        task_dir = Path(context.get("task_dir", "/tmp"))
        task_dir.mkdir(parents=True, exist_ok=True)

        step_params = getattr(step, "input_payload", {}) or getattr(step, "params", {}) or {}

        step.log("Iniciando motor de subtítulos cinéticos Vox & HUD telemetría...")

        # 1. Recuperar o extraer guión canónico
        script_data = step_params.get("script_data")
        escaleta_path = step_params.get("escaleta_path")
        audio_path = step_params.get("audio_path") or context.get("audio_path")
        target_resolution = step_params.get("resolution", "4k")

        if not script_data and escaleta_path and Path(escaleta_path).exists():
            with open(escaleta_path, "r", encoding="utf-8") as f:
                script_data = json.load(f)

        if not script_data:
            script_data = step_params.get("text", "El Umbral Cuántico: La Revolución Silenciosa del Silicio.")

        # 2. Transcripción ASR (Whisper) o timestamps existentes
        asr_data = step_params.get("asr_data") or context.get("asr_data")
        total_audio_duration = step_params.get("total_duration") or context.get("total_duration", 120.0)

        if not asr_data and audio_path and Path(audio_path).exists():
            step.log(f"Extrayendo timestamps fonéticos a nivel de palabra con Whisper desde {Path(audio_path).name}...")
            transcriber = AudioTranscriber(model_size=step_params.get("whisper_model", "base"), language="es")
            asr_data = transcriber.transcribe(Path(audio_path))
            step.log(f"Transcripción Whisper completada.")
        elif not asr_data:
            step.log("No se proporcionó audio físico; generando alineación determinista basada en escaleta.")
            asr_data = {"segments": []}

        # 3. Alineación forzada determinista por distancia Levenshtein
        step.log("Ejecutando alineación forzada Levenshtein & DTW contra guion canónico...")
        aligner = LevenshteinForcedAligner()
        alignment_res = aligner.align(script_data, asr_data, total_audio_duration=total_audio_duration)

        step.log(
            f"Alineación finalizada: {alignment_res.matched_words}/{alignment_res.total_canonical_words} palabras emparejadas "
            f"({alignment_res.alignment_rate}% tasa de alineación, {alignment_res.hallucinated_asr_dropped} alucinaciones Whisper purgadas)."
        )

        # 4. Generación de subtítulos cinéticos Vox / MrBeast
        step.log("Compilando subtítulos cinéticos con estética Vox (oro #FFD700 / blanco #FFFFFF)...")
        styler = KineticSubtitleStyler(
            target_resolution=target_resolution,
            highlight_color_hex=step_params.get("highlight_color", "#FFD700"),
            text_color_hex=step_params.get("text_color", "#FFFFFF")
        )
        chunks = styler.build_chunks(alignment_res.aligned_tokens)

        # Archivos de salida
        ass_path = task_dir / "subtitles_kinetic_vox.ass"
        srt_path = task_dir / "subtitles.srt"
        vtt_path = task_dir / "subtitles.vtt"
        json_path = task_dir / "kinetic_subtitles_manifest.json"

        ass_content = styler.generate_ass(chunks, title=context.get("title", "VideoPro Master"))
        srt_content = styler.generate_srt(chunks)
        vtt_content = styler.generate_vtt(chunks)
        json_manifest = styler.generate_json_manifest(chunks, metadata={"resolution": target_resolution})

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write(vtt_content)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_manifest, f, indent=2, ensure_ascii=False)

        step.log(f"Subtítulos ASS, SRT, VTT y JSON compilados en {task_dir}.")

        # 5. Generación de Overlays HUD y Badges Diegéticos si hay planos
        hud_overlays = []
        shots = []
        if isinstance(script_data, dict) and "shots" in script_data:
            shots = script_data["shots"]
        elif isinstance(script_data, list):
            shots = script_data

        if shots and step_params.get("generate_hud_overlays", True):
            step.log(f"Generando {len(shots)} overlays gráficos HUD y badges diegéticos ({target_resolution.upper()})...")
            hud_dir = task_dir / "hud_overlays"
            hud_gen = ModernHUDGenerator(resolution=target_resolution)
            hud_overlays = [str(p) for p in hud_gen.generate_all_shots_overlays(shots, hud_dir)]
            step.log(f"{len(hud_overlays)} capas HUD generadas exitosamente en {hud_dir}.")

        return {
            "engine": self.engine_id,
            "status": "success",
            "ass_path": str(ass_path),
            "srt_path": str(srt_path),
            "vtt_path": str(vtt_path),
            "json_path": str(json_path),
            "total_chunks": len(chunks),
            "alignment_rate_pct": alignment_res.alignment_rate,
            "hallucinations_dropped": alignment_res.hallucinated_asr_dropped,
            "hud_overlays_count": len(hud_overlays),
            "hud_overlays_dir": str(task_dir / "hud_overlays") if hud_overlays else None
        }
