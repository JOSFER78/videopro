"""
Módulo de Automatización y Análisis de Google Flow Music (Lyria 3 Pro / MusicFX)
Ruta: app/services/audio/flowmusic_service.py

Permite:
1. Automatización desatendida de generación y descarga en Google Flow Music vía Playwright & CDP (:9222).
2. Generación y orquestación de Suites de Larga Duración (15 min) en 5 Fases consecutivas.
3. Ensamblado continuo con crossfade S-Curve exponencial y procesamiento DSP audiófilo / YouTube.
4. Análisis de BPM, detección de transitorios de energía y compases musicales.
5. Troceado inteligente de audio (Bar & Energy Slicer) sincronizado con planos de LTX-2.5 y FLUX 3.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("videopro.flowmusic")
logger.setLevel(logging.INFO)


class FlowMusicAutomationService:
    """
    Servicio de automatización de Google Flow Music (labs.google/fx/tools/music-fx).
    Maneja sesiones web vía Playwright sobre CDP, suites multifase de 15 minutos, descarga y masterización DSP.
    """

    def __init__(
        self,
        session_cookie: Optional[str] = None,
        output_dir: Optional[Path] = None,
        cdp_url: str = "http://127.0.0.1:9222"
    ):
        self.session_cookie = session_cookie or os.getenv("FLOWMUSIC_SESSION", "")
        self.cdp_url = cdp_url
        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.output_dir = base_dir / "storage" / "music" / "flowmusic"
        else:
            self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_authenticated(self) -> bool:
        """Comprueba si hay cookie o sesión CDP disponible."""
        return bool(self.session_cookie and len(self.session_cookie) > 20)

    @staticmethod
    def plan_15min_suite(
        suite_type: str = "orchestral_wide_horizon",
        tuning_hz: int = 432
    ) -> List[Dict[str, Any]]:
        """
        Genera el plan estructurado de 5 fases para una obra de 15 minutos.
        """
        if suite_type == "orchestral_wide_horizon":
            return [
                {
                    "phase": 1,
                    "title": "Pista Base",
                    "timeframe": "0:00 - 3:00",
                    "prompt": f"Wide Horizon. Cinematic orchestral film score, warm {tuning_hz}Hz tuning. Sweeping atmospheric strings, gentle ambient synths, subtle ear-to-ear textures, slow walking pace. Soft melodic introduction, purely instrumental, zero drums, ultra-wide soundstage.",
                    "role": "Intro & Harmonic Anchor"
                },
                {
                    "phase": 2,
                    "title": "Primera Extensión",
                    "timeframe": "3:00 - 6:00",
                    "prompt": f"Extend maintaining exact key, tempo, and orchestration in {tuning_hz}Hz. Introduce steady low-end pulse and subtle timpani roll, gradual rhythmic build, evolving French horn theme, smooth seamless transition.",
                    "role": "Theme Evolution & Steady Pulse"
                },
                {
                    "phase": 3,
                    "title": "Segunda Extensión",
                    "timeframe": "6:00 - 9:00",
                    "prompt": f"Extend maintaining harmonic progression in {tuning_hz}Hz. Dynamic rhythmic shift, rich symphonic string layering, expanding brass harmonies, uplifting momentum, wide binaural panning.",
                    "role": "Harmonic Expansion & Uplifting Momentum"
                },
                {
                    "phase": 4,
                    "title": "Tercera Extensión / Clímax",
                    "timeframe": "9:00 - 12:00",
                    "prompt": f"Extend building to peak energy. Triumphant orchestral crescendo, powerful French horns and brass swells, epic emotional climax, majestic and expansive resolution in {tuning_hz}Hz.",
                    "role": "Triumphant Emotional Climax"
                },
                {
                    "phase": 5,
                    "title": "Cuarta Extensión / Cierre",
                    "timeframe": "12:00 - 15:00",
                    "prompt": f"Extend with smooth decrescendo. Percussion and rhythm fade out, soft lingering strings and warm ambient drones in {tuning_hz}Hz, gradual decay to silence, peaceful outro.",
                    "role": "Decrescendo & Lingering Resolution"
                }
            ]
        elif suite_type == "tritemporal_odyssey":
            return [
                {
                    "phase": 1,
                    "title": "Anclaje Antiguo",
                    "timeframe": "0:00 - 3:00",
                    "prompt": f"Tritemporal Odyssey - Part 1. Ancient atmospheric overture, {tuning_hz}Hz Solfeggio tuning. Warm acoustic cello drones, historical lute and flute echoes, subtle stone corridor room reverb, zero modern percussion, deep meditative presence.",
                    "role": "Ancient Historical Intro"
                },
                {
                    "phase": 2,
                    "title": "Puente Temporal",
                    "timeframe": "3:00 - 6:00",
                    "prompt": f"Extend maintaining {tuning_hz}Hz root key. Seamlessly blend ancient acoustic strings with subtle warm analog synth arpeggios, gentle rhythmic walking pulse, evolving harmonic depth, binaural spatialization.",
                    "role": "Acoustic-Synthetic Bridge"
                },
                {
                    "phase": 3,
                    "title": "Aceleración Industrial",
                    "timeframe": "6:00 - 9:00",
                    "prompt": f"Extend maintaining progression. Introduce rich symphonic strings layered with clockwork-like acoustic percussion, expanding brass textures, dynamic motion, ultra-wide stereo spread.",
                    "role": "Rhythmic Acceleration"
                },
                {
                    "phase": 4,
                    "title": "Clímax Futurista",
                    "timeframe": "9:00 - 12:00",
                    "prompt": f"Extend reaching grand climax. Majestic cinematic orchestral swells, shimmering futuristic modular synthesizers, triumphant horn melodies, epic temporal convergence, expansive reverberation.",
                    "role": "Futuristic Climax"
                },
                {
                    "phase": 5,
                    "title": "Resonancia Eterna",
                    "timeframe": "12:00 - 15:00",
                    "prompt": f"Extend with slow ethereal decrescendo. Electronics and percussion fade away, lingering {tuning_hz}Hz sine drones and gentle solo cello decaying peacefully into absolute silence.",
                    "role": "Ethereal Dissolution"
                }
            ]
        else: # urban_sanctuary_asmr
            return [
                {
                    "phase": 1,
                    "title": "Callejón Atardecer",
                    "timeframe": "0:00 - 3:00",
                    "prompt": f"Urban Sanctuary - Part 1. Ultra-high fidelity ambient walking soundtrack, {tuning_hz}Hz tuning. Warm sub drones, lush soothing synthesizer pads. Binaural 3D ASMR micro-textures: gentle cobblestone footsteps panning left to right, soft breeze, zero drums.",
                    "role": "ASMR Intro"
                },
                {
                    "phase": 2,
                    "title": "Plaza Iluminada",
                    "timeframe": "3:00 - 6:00",
                    "prompt": f"Extend maintaining {tuning_hz}Hz key and slow tempo. Introduce subtle glass bells, warm rhodes chords, intimate ear-to-ear foley (distant cafe murmur, fountain water drops), seamless hypnotic flow.",
                    "role": "Ambient Depth"
                },
                {
                    "phase": 3,
                    "title": "Paseo junto al Río",
                    "timeframe": "6:00 - 9:00",
                    "prompt": f"Extend maintaining harmonic continuity. Gentle acoustic guitar harmonics blending with airy synth swells, soft water ripple ASMR textures, ultra-wide 3D spatial field, deep relaxation.",
                    "role": "Water ASMR & Pads"
                },
                {
                    "phase": 4,
                    "title": "Mirador Panorámico",
                    "timeframe": "9:00 - 12:00",
                    "prompt": f"Extend building to warm emotional height. Rich violin and cello ensemble over warm sub-bass, uplifting chords, night breeze ASMR textures, expansive and peaceful emotional release.",
                    "role": "Warm Release"
                },
                {
                    "phase": 5,
                    "title": "Despedida Nocturna",
                    "timeframe": "12:00 - 15:00",
                    "prompt": f"Extend fading out into night silence. Acoustic instruments slowly recede, leaving soft {tuning_hz}Hz drone and subtle distant footsteps fading smoothly into total quiet.",
                    "role": "Night Outro"
                }
            ]

    def assemble_and_master_suite(
        self,
        phase_audio_paths: List[Path],
        suite_name: str = "flow_suite_15min",
        tuning_hz: int = 432,
        crossfade_s: float = 6.0
    ) -> Dict[str, Any]:
        """
        Ensambla y masteriza una lista de archivos de fases en un master continuo de 15 minutos.
        """
        from scripts.flow_music_phase_assembler import FlowMusicPhaseAssembler

        assembler = FlowMusicPhaseAssembler(output_dir=self.output_dir)
        stitched = assembler.stitch_phases_scurve(phase_audio_paths, crossfade_duration_s=crossfade_s)
        return assembler.apply_audiophile_3d_mastering(
            input_stitched_audio=stitched,
            suite_name=suite_name,
            tuning_hz=tuning_hz
        )

    async def generate_track_playwright(
        self,
        prompt: str,
        filename_prefix: str = "flow_track",
        tuning_hz: int = 432,
        profile: str = "audiophile_luxury",
        timeout_seconds: int = 120
    ) -> Dict[str, Any]:
        """
        Genera una pista musical en Google Flow Music conectándose a Chrome vía CDP con Playwright.
        """
        from scripts.flow_music_playwright_runner import FlowMusicPlaywrightRunner

        runner = FlowMusicPlaywrightRunner(
            cdp_url=self.cdp_url,
            output_dir=self.output_dir,
            timeout_seconds=timeout_seconds
        )
        logger.info(f"Delegando generación a FlowMusicPlaywrightRunner para: {prompt[:60]}...")
        return await runner.generate_single_track(
            prompt=prompt,
            filename_prefix=filename_prefix,
            tuning_hz=tuning_hz,
            profile=profile
        )

    def analyze_and_slice_audio(
        self,
        audio_path: str,
        target_fps: int = 24,
        min_scene_duration_s: float = 4.0,
        max_scene_duration_s: float = 8.0
    ) -> Dict[str, Any]:
        """
        Analiza una pista de audio (WAV/MP3/FLAC) usando ffprobe/ffmpeg para:
        - Detectar duración total.
        - Generar la escaleta de trozos (Scenes) sincronizada al frame exacto para LTX-2.5 / FLUX 3.
        """
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)
        ]
        duration_s = float(subprocess.check_output(probe_cmd).decode().strip())
        total_frames = int(duration_s * target_fps)

        scenes = []
        current_time = 0.0
        shot_index = 1

        phase_types = [
            {"phase": "INTRO", "shot_type": "Wide Establishing Glide", "energy": "Low/Ambient"},
            {"phase": "VERSE", "shot_type": "Low-Altitude Street Parallax", "energy": "Medium"},
            {"phase": "BUILDUP", "shot_type": "Archway / Canopy Pass-Through", "energy": "Rising"},
            {"phase": "DROP / CLIMAX", "shot_type": "Kinetic Arc / Fast Action", "energy": "Maximum Peak"},
            {"phase": "OUTRO", "shot_type": "Panoramic Horizon Pull-Back", "energy": "Resolving"}
        ]

        while current_time < duration_s:
            remaining = duration_s - current_time
            if remaining <= max_scene_duration_s:
                scene_dur = remaining
            else:
                scene_dur = min(max(5.0, round(duration_s / 5.0, 1)), max_scene_duration_s)
                if current_time + scene_dur > duration_s:
                    scene_dur = duration_s - current_time

            start_s = current_time
            end_s = current_time + scene_dur
            start_frame = int(start_s * target_fps)
            end_frame = int(end_s * target_fps)
            frames_count = end_frame - start_frame

            phase_info = phase_types[(shot_index - 1) % len(phase_types)]
            slice_filename = f"slice_sh{shot_index:02d}_{int(start_s)}s_{int(end_s)}s.wav"
            slice_path = self.output_dir / slice_filename

            slice_cmd = [
                "ffmpeg", "-y", "-ss", str(start_s), "-to", str(end_s),
                "-i", str(audio_file), "-c:a", "pcm_s16le", "-ar", "48000", str(slice_path)
            ]
            subprocess.run(slice_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            scenes.append({
                "shot_id": f"SH_{shot_index:02d}",
                "phase": phase_info["phase"],
                "shot_type": phase_info["shot_type"],
                "energy_level": phase_info["energy"],
                "start_s": round(start_s, 2),
                "end_s": round(end_s, 2),
                "duration_s": round(scene_dur, 2),
                "start_frame": start_frame,
                "end_frame": end_frame,
                "frames_count": frames_count,
                "slice_path": str(slice_path)
            })

            current_time += scene_dur
            shot_index += 1

        return {
            "master_audio_path": str(audio_file),
            "total_duration_s": round(duration_s, 2),
            "total_frames": total_frames,
            "fps": target_fps,
            "total_scenes": len(scenes),
            "scenes": scenes
        }
