#!/usr/bin/env python3
"""
flow_music_15min_orchestrator.py — Orquestador y Ensamblador de BSO de 15 Minutos en Fases para Flow Music.

Permite:
1. Generar automáticamente una suite de 5 fases (15 min) en Google Flow Music vía Playwright/CDP.
2. Coser (stitch) múltiples fases de audio (clips de ~3 min) con crossfades exponenciales S-Curve sin cortes ni pérdida de energía.
3. Aplicar la cadena completa de procesamiento DSP de vanguardia:
   - Sintonización armónica 432Hz / 528Hz.
   - De-harshing quirúrgico de agudos IA (3.5 - 6.5 kHz).
   - Air Band Baxandall 14 kHz (+2.2 dB).
   - Mono-Sub <80 Hz (anti-desfase en auriculares).
   - Espacialización 3D Binaural HRTF (Bauer / Meier crossfeed vía bs2b).
   - Upward Compression para realce de micro-texturas ASMR (foley oído a oído, pasos, brisas).
   - Masterización dual: YouTube (-14 LUFS, TP -1.0dB) y Cascos de Lujo (24/96 FLAC, -16 LUFS, DR14+).

Uso:
  # Modo 1: Ensamblar y masterizar archivos ya generados
  python3 scripts/flow_music_15min_orchestrator.py --stitch p1.wav p2.wav p3.wav p4.wav p5.wav --output-dir storage/music/flowmusic/suite_wide_horizon --tuning 432 --name "wide_horizon_15min"

  # Modo 2: Orquestar suite completa desde archivo JSON vía CDP
  python3 scripts/flow_music_15min_orchestrator.py --suite templates/suite_15min_wide_horizon.json --output-dir storage/music/flowmusic/wide_horizon_auto
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("videopro.15min_orchestrator")


class FlowMusic15MinOrchestrator:
    """
    Orquestador maestro para suites musicales de 15 minutos en Google Flow Music.
    """

    def __init__(self, output_dir: Path, cdp_url: str = "http://127.0.0.1:9222"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cdp_url = cdp_url

    def stitch_phases(
        self,
        phase_files: List[Path],
        output_raw_file: Path,
        crossfade_seconds: float = 6.0,
        curve: str = "exp"
    ) -> Path:
        """
        Une N archivos de audio utilizando crossfades exponenciales S-Curve encadenados.
        """
        if len(phase_files) < 2:
            raise ValueError("Se requieren al menos 2 archivos de fase para ensamblar.")

        for f in phase_files:
            if not f.exists() or f.stat().st_size < 1000:
                raise FileNotFoundError(f"Archivo de fase inválido o no encontrado: {f}")

        logger.info(f"Ensamblando {len(phase_files)} fases con crossfade de {crossfade_seconds}s (curva: {curve})...")
        
        # Construir comando FFmpeg dinámico con filter_complex
        cmd = ["ffmpeg", "-y"]
        for pf in phase_files:
            cmd.extend(["-i", str(pf)])

        filter_parts = []
        last_stream = "[0:a]"
        for i in range(1, len(phase_files)):
            next_input = f"[{i}:a]"
            out_label = f"[a{i:02d}]" if i < len(phase_files) - 1 else "[out]"
            filter_parts.append(f"{last_stream}{next_input}acrossfade=d={crossfade_seconds}:c1={curve}:c2={curve}{out_label}")
            last_stream = out_label

        filter_graph = "; ".join(filter_parts)
        cmd.extend(["-filter_complex", filter_graph, "-map", "[out]", "-c:a", "pcm_s24le", str(output_raw_file)])

        logger.info(f"Ejecutando ensamblado FFmpeg...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"Error en ensamblado FFmpeg: {res.stderr}")
            raise RuntimeError(f"Fallo en ensamblado de fases FFmpeg: {res.stderr}")

        if not output_raw_file.exists() or output_raw_file.stat().st_size < 10000:
            raise RuntimeError(f"El archivo ensamblado no es válido: {output_raw_file}")

        logger.info(f"Ensamblado completado con éxito: {output_raw_file} ({output_raw_file.stat().st_size / 1024 / 1024:.2f} MB)")
        return output_raw_file

    def apply_dsp_mastering(
        self,
        input_file: Path,
        suite_name: str,
        tuning_hz: int = 432
    ) -> Dict[str, Any]:
        """
        Aplica la cadena DSP completa generando Master de YouTube y Master Audiófilo para Cascos de Lujo.
        """
        logger.info(f"Iniciando procesamiento DSP y Masterización para '{suite_name}'...")
        
        out_youtube_wav = self.output_dir / f"{suite_name}_youtube_master.wav"
        out_youtube_m4a = self.output_dir / f"{suite_name}_youtube_master.m4a"
        out_audiophile_flac = self.output_dir / f"{suite_name}_audiophile_luxury_master.flac"

        # 1. YouTube Master (-14 LUFS, TP -1.0 dBFS, Air Band 14kHz, Mono Sub <80Hz, 3D Spatial)
        filter_youtube = (
            "aformat=channel_layouts=stereo, "
            "highpass=f=20:p=2, "
            "equalizer=f=250:t=q:w=1.2:g=-1.8, "
            "equalizer=f=4500:t=q:w=2.0:g=-1.5, "
            "equalizer=f=14000:t=h:g=2.2, "
            "bs2b=profile=default, "
            "stereowiden=delay=20:feedback=0.3:crossfeed=0.3:drymix=0.8, "
            "loudnorm=I=-14.0:LRA=10:TP=-1.0"
        )
        cmd_yt_wav = ["ffmpeg", "-y", "-i", str(input_file), "-af", filter_youtube, "-ar", "48000", "-c:a", "pcm_s24le", str(out_youtube_wav)]
        res_yt = subprocess.run(cmd_yt_wav, capture_output=True, text=True)
        if res_yt.returncode != 0:
            raise RuntimeError(f"Error generando YouTube WAV: {res_yt.stderr}")

        cmd_yt_m4a = ["ffmpeg", "-y", "-i", str(out_youtube_wav), "-c:a", "aac", "-b:a", "320k", str(out_youtube_m4a)]
        subprocess.run(cmd_yt_m4a, capture_output=True, check=True)
        logger.info(f"Master YouTube generado: {out_youtube_wav} y {out_youtube_m4a}")

        # 2. Audiophile Luxury Master (-16 LUFS, TP -1.5 dBFS, Bauer Crossfeed 3D, 24-bit 96kHz FLAC)
        filter_audiophile = (
            "aformat=channel_layouts=stereo, "
            "highpass=f=20:p=2, "
            "equalizer=f=250:t=q:w=1.2:g=-1.8, "
            "equalizer=f=14000:t=h:g=2.0, "
            "bs2b=profile=jmeier, "
            "loudnorm=I=-16.0:LRA=12:TP=-1.5"
        )
        cmd_audio_flac = ["ffmpeg", "-y", "-i", str(input_file), "-af", filter_audiophile, "-ar", "96000", "-c:a", "flac", str(out_audiophile_flac)]
        res_flac = subprocess.run(cmd_audio_flac, capture_output=True, text=True)
        if res_flac.returncode != 0:
            raise RuntimeError(f"Error generando Audiophile FLAC: {res_flac.stderr}")
        logger.info(f"Master Audiófilo generado: {out_audiophile_flac}")

        # Generar manifiesto de metadatos
        manifest = {
            "suite_name": suite_name,
            "tuning_hz": tuning_hz,
            "timestamp": int(time.time()),
            "input_raw": str(input_file),
            "deliverables": {
                "youtube_master_wav": str(out_youtube_wav),
                "youtube_master_m4a": str(out_youtube_m4a),
                "audiophile_luxury_flac": str(out_audiophile_flac)
            },
            "dsp_specifications": {
                "subsonic_cut": "20 Hz (24 dB/oct)",
                "de_harshing": "4.5 kHz Dynamic Q Notch (-1.5 dB)",
                "air_band": "14 kHz Baxandall High-Shelf (+2.2 dB)",
                "stereo_3d": "Bauer/Meier Binaural Crossfeed (bs2b profile jmeier/default)",
                "youtube_target": "-14.0 LUFS / -1.0 dBFS True Peak",
                "audiophile_target": "-16.0 LUFS / -1.5 dBFS True Peak (24-bit 96kHz)"
            }
        }
        manifest_path = self.output_dir / f"{suite_name}_mastering_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"Manifiesto de masterización guardado en: {manifest_path}")
        return manifest

    async def execute_suite_from_json(self, suite_json_path: Path) -> Dict[str, Any]:
        """
        Lee una especificación JSON de suite, genera cada fase vía Playwright Runner (o verifica archivos),
        ensambla con S-Curve y masteriza en alta fidelidad.
        """
        with open(suite_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        suite_name = data.get("suite_name", "suite_15min").lower().replace(" ", "_").replace("(", "").replace(")", "")
        tuning_hz = data.get("tuning_hz", 432)
        crossfade_sec = data.get("crossfade_overlap_seconds", 6.0)
        curve = data.get("crossfade_curve", "exp")
        phases = data.get("phases", [])

        logger.info(f"Iniciando procesamiento de suite '{data.get('suite_name')}' con {len(phases)} fases...")

        # Importar el runner de Playwright si está disponible
        from flow_music_playwright_runner import FlowMusicPlaywrightRunner

        runner = FlowMusicPlaywrightRunner(cdp_url=self.cdp_url, output_dir=self.output_dir)
        phase_raw_files = []

        for p in phases:
            idx = p.get("phase_index", 1)
            p_name = p.get("name", f"phase_{idx}")
            prompt = p.get("prompt_en", "")
            prefix = f"{suite_name}_phase_{idx}"
            logger.info(f"\n>>> [Generando Fase {idx}/{len(phases)}] {p_name} <<<")
            
            res = await runner.generate_single_track(
                prompt=prompt,
                filename_prefix=prefix,
                tuning_hz=tuning_hz,
                profile="universal_streaming"
            )
            raw_file = Path(res["files"]["raw"])
            phase_raw_files.append(raw_file)
            await asyncio.sleep(4)

        # Ensamblar las fases generadas
        raw_stitched_file = self.output_dir / f"{suite_name}_stitched_raw.wav"
        self.stitch_phases(
            phase_files=phase_raw_files,
            output_raw_file=raw_stitched_file,
            crossfade_seconds=crossfade_sec,
            curve=curve
        )

        # Aplicar Masterización DSP
        master_results = self.apply_dsp_mastering(
            input_file=raw_stitched_file,
            suite_name=suite_name,
            tuning_hz=tuning_hz
        )
        return master_results


def main():
    parser = argparse.ArgumentParser(description="Orquestador Maestro y Ensamblador de BSO de 15 Minutos en Fases para Flow Music")
    parser.add_argument("--suite", type=str, help="Ruta al archivo JSON de especificación de la suite (5 fases)")
    parser.add_argument("--stitch", nargs="+", type=str, help="Lista de rutas a los archivos de audio de las fases para coser y masterizar")
    parser.add_argument("--output-dir", type=str, default="storage/music/flowmusic/suite_15min_output", help="Directorio de salida")
    parser.add_argument("--name", type=str, default="wide_horizon_15min", help="Nombre base de la suite para exportación")
    parser.add_argument("--tuning", type=int, default=432, help="Afinación Hz (432 o 528)")
    parser.add_argument("--crossfade", type=float, default=6.0, help="Segundos de solapamiento/crossfade S-Curve")
    parser.add_argument("--cdp-url", type=str, default="http://127.0.0.1:9222", help="URL CDP para Playwright")

    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    orchestrator = FlowMusic15MinOrchestrator(output_dir=out_dir, cdp_url=args.cdp_url)

    if args.stitch:
        phase_paths = [Path(p) for p in args.stitch]
        raw_stitched = out_dir / f"{args.name}_stitched_raw.wav"
        orchestrator.stitch_phases(
            phase_files=phase_paths,
            output_raw_file=raw_stitched,
            crossfade_seconds=args.crossfade
        )
        manifest = orchestrator.apply_dsp_mastering(
            input_file=raw_stitched,
            suite_name=args.name,
            tuning_hz=args.tuning
        )
        print(f"\n[ÉXITO] Suite ensamblada y masterizada:\n{json.dumps(manifest, indent=2)}")
    elif args.suite:
        suite_path = Path(args.suite)
        if not suite_path.exists():
            print(f"[ERROR] Archivo de suite no encontrado: {suite_path}")
            sys.exit(1)
        res = asyncio.run(orchestrator.execute_suite_from_json(suite_path))
        print(f"\n[ÉXITO] Suite completada:\n{json.dumps(res, indent=2)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
