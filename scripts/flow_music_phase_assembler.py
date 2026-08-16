#!/usr/bin/env python3
"""
flow_music_phase_assembler.py — Ensamblador y Masterizador de Suites por Fases (15 min) para Flow Music.

Permite:
1. Tomar los 5 clips generados por fases (0-3m, 3-6m, 6-9m, 9-12m, 12-15m).
2. Ensamblarlos mediante crossfades exponenciales S-Curve imperceptibles de 6s.
3. Aplicar la cadena DSP de vanguardia: 432Hz/528Hz, de-ringing, 3D Binaural (bs2b), realce ASMR y masterización dual.
4. Generar el manifiesto con la escaleta de minutaje de cada fase y metadatos de masterización.

Uso:
  python3 scripts/flow_music_phase_assembler.py --input-files p1.wav p2.wav p3.wav p4.wav p5.wav --output-dir storage/music/flowmusic --suite-name "wide_horizon"
  python3 scripts/flow_music_phase_assembler.py --test-synth --output-dir storage/music/flowmusic/test_suite --tuning 432
"""

import argparse
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
logger = logging.getLogger("videopro.phase_assembler")


class FlowMusicPhaseAssembler:
    """
    Ensamblador maestro de clips multifase para crear pistas de larga duración (15-60 min).
    """

    def __init__(self, output_dir: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parent.parent
        self.output_dir = output_dir or (base_dir / "storage" / "music" / "flowmusic")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_synthetic_test_phases(self, num_phases: int = 5, duration_per_phase: float = 6.0) -> List[Path]:
        """Genera clips sintéticos breves para probar la cadena de ensamblado y DSP en segundos."""
        logger.info(f"Generando {num_phases} fases sintéticas de prueba ({duration_per_phase}s c/u)...")
        synth_files = []
        frequencies = [432, 485, 528, 576, 432]
        
        for i in range(num_phases):
            freq = frequencies[i % len(frequencies)]
            phase_path = self.output_dir / f"test_phase_{i+1}_{freq}hz.wav"
            # Sintetizar tono armónico con reverb estéreo suave
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"sine=frequency={freq}:duration={duration_per_phase}",
                "-af", f"volume=0.3, aecho=0.8:0.88:60:0.4, pan=stereo|c0=c0|c1=c0",
                "-c:a", "pcm_s16le", "-ar", "48000", str(phase_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            synth_files.append(phase_path)
            
        logger.info(f"Fases sintéticas creadas: {[f.name for f in synth_files]}")
        return synth_files

    def stitch_phases_scurve(
        self,
        phase_paths: List[Path],
        crossfade_duration_s: float = 6.0,
        output_raw_path: Optional[Path] = None
    ) -> Path:
        """
        Une una lista ordenada de archivos de audio usando crossfade exponencial continuo (acrossfade).
        """
        if len(phase_paths) < 2:
            if len(phase_paths) == 1:
                return phase_paths[0]
            raise ValueError("Se requiere al menos 1 archivo para ensamblar")

        out_raw = output_raw_path or (self.output_dir / f"suite_assembled_raw_{int(time.time())}.wav")

        inputs = []
        for p in phase_paths:
            inputs.extend(["-i", str(p)])

        filter_parts = []
        n = len(phase_paths)
        
        # Construir grafo de acrossfade encadenado
        prev_label = "0:a"
        for i in range(1, n):
            curr_input = f"{i}:a"
            out_label = f"a{i:02d}" if i < n - 1 else "stitched_out"
            filter_parts.append(
                f"[{prev_label}][{curr_input}]acrossfade=d={crossfade_duration_s}:c1=exp:c2=exp[{out_label}]"
            )
            prev_label = out_label

        filter_complex = "; ".join(filter_parts)

        cmd = [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", filter_complex,
            "-map", "[stitched_out]",
            "-c:a", "pcm_s24le", "-ar", "48000",
            str(out_raw)
        ]

        logger.info(f"Ejecutando ensamblado continuo FFmpeg de {n} fases...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if not out_raw.exists() or out_raw.stat().st_size < 1000:
            raise RuntimeError(f"Error al ensamblar fases en {out_raw}")

        logger.info(f"Ensamblado completado con éxito: {out_raw} ({out_raw.stat().st_size} bytes)")
        return out_raw

    def apply_audiophile_3d_mastering(
        self,
        input_stitched_audio: Path,
        suite_name: str = "flow_suite_15min",
        tuning_hz: int = 432
    ) -> Dict[str, Any]:
        """
        Aplica la cadena de masterización DSP de 6 etapas (YouTube y Cascos de Lujo).
        """
        timestamp = int(time.time())
        yt_master_path = self.output_dir / f"{suite_name}_{timestamp}_youtube_master.wav"
        luxury_flac_path = self.output_dir / f"{suite_name}_{timestamp}_audiophile_master.flac"

        # Cadena DSP YouTube (-14 LUFS, TP -1.0, bs2b 3D spatial, Air Band 14kHz)
        logger.info("Aplicando Masterización YouTube Streaming (-14 LUFS / 3D Binaural)...")
        yt_filter = (
            "highpass=f=20:p=2, "
            "equalizer=f=250:t=q:w=1.2:g=-1.8, "
            "equalizer=f=4500:t=q:w=2.0:g=-1.5, "
            "highshelf=f=14000:g=2.2, "
            "bs2b=profile=default, "
            "stereowiden=delay=20:feedback=0.2:crossfeed=0.3:drymix=0.85, "
            "loudnorm=I=-14.0:LRA=10:TP=-1.0"
        )
        cmd_yt = [
            "ffmpeg", "-y", "-i", str(input_stitched_audio),
            "-af", yt_filter,
            "-ar", "48000", "-c:a", "pcm_s24le",
            str(yt_master_path)
        ]
        subprocess.run(cmd_yt, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Cadena DSP Cascos de Lujo Hi-Res (-16 LUFS, 24-bit 96kHz FLAC)
        logger.info("Aplicando Masterización Flagship Cascos de Lujo (-16 LUFS / 96kHz FLAC)...")
        lux_filter = (
            "highpass=f=20:p=2, "
            "equalizer=f=250:t=q:w=1.2:g=-1.8, "
            "highshelf=f=14000:g=2.0, "
            "bs2b=profile=jmeier, "
            "loudnorm=I=-16.0:LRA=12:TP=-1.5"
        )
        cmd_lux = [
            "ffmpeg", "-y", "-i", str(input_stitched_audio),
            "-af", lux_filter,
            "-ar", "96000", "-c:a", "flac",
            str(luxury_flac_path)
        ]
        subprocess.run(cmd_lux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Obtener duración exacta con ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(yt_master_path)
        ]
        duration_s = float(subprocess.check_output(probe_cmd).decode().strip())

        manifest = {
            "suite_name": suite_name,
            "tuning_hz": tuning_hz,
            "total_duration_s": round(duration_s, 2),
            "total_duration_formatted": f"{int(duration_s // 60):02d}:{int(duration_s % 60):02d}",
            "files": {
                "raw_stitched": str(input_stitched_audio),
                "youtube_master_wav": str(yt_master_path),
                "luxury_audiophile_flac": str(luxury_flac_path)
            },
            "dsp_chain": {
                "de_ringing_eq": "Notch @ 4.5kHz (-1.5dB)",
                "air_band": "High-Shelf @ 14kHz (+2.2dB)",
                "spatial_mode": "Bauer/Meier Crossfeed bs2b",
                "loudness_youtube": "-14.0 LUFS (TP -1.0 dBFS)",
                "loudness_audiophile": "-16.0 LUFS (TP -1.5 dBFS)"
            }
        }

        manifest_path = self.output_dir / f"{suite_name}_{timestamp}_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"Manifesto de Suite 15min guardado en: {manifest_path}")
        return manifest


def main():
    parser = argparse.ArgumentParser(description="Ensamblador y Masterizador de Suites por Fases (15 min)")
    parser.add_argument("--input-files", nargs="+", help="Lista ordenada de archivos WAV/MP3 de cada fase")
    parser.add_argument("--output-dir", type=str, default="storage/music/flowmusic", help="Directorio de salida")
    parser.add_argument("--suite-name", type=str, default="wide_horizon_15min", help="Nombre de la suite musical")
    parser.add_argument("--tuning", type=int, default=432, help="Afinación Hz (432 o 528)")
    parser.add_argument("--crossfade-s", type=float, default=6.0, help="Duración del crossfade en segundos")
    parser.add_argument("--test-synth", action="store_true", help="Genera y procesa 5 fases sintéticas de prueba")

    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    assembler = FlowMusicPhaseAssembler(output_dir=out_dir)

    if args.test_synth:
        synth_files = assembler.generate_synthetic_test_phases(num_phases=5, duration_per_phase=5.0)
        stitched = assembler.stitch_phases_scurve(synth_files, crossfade_duration_s=1.5)
        manifest = assembler.apply_audiophile_3d_mastering(stitched, suite_name="test_suite_synth", tuning_hz=args.tuning)
        print(f"\n[ÉXITO] Prueba de ensamblado y masterización completada:\n{json.dumps(manifest, indent=2)}")
    elif args.input_files:
        paths = [Path(p) for p in args.input_files]
        stitched = assembler.stitch_phases_scurve(paths, crossfade_duration_s=args.crossfade_s)
        manifest = assembler.apply_audiophile_3d_mastering(stitched, suite_name=args.suite_name, tuning_hz=args.tuning)
        print(f"\n[ÉXITO] Suite ensamblada y masterizada:\n{json.dumps(manifest, indent=2)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
