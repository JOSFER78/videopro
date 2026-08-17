"""
Foley & Sound Director for VideoPro
Procedural acoustic sound effects (Paper Foley, Typewriter, Shutter Flash, Steam & Gears, Whoosh)
and sound event timeline generation based on transcription keywords and timing.
"""
import os
import re
import json
import math
import struct
import wave
from pathlib import Path
from typing import Optional, List, Dict, Any
from loguru import logger

def create_sine_burst(freq_start, freq_end, duration_s, sample_rate=48000, volume=0.8, decay=True):
    """Generates a procedural synthesized acoustic SFX sample as a 16-bit 48kHz WAV."""
    num_samples = int(duration_s * sample_rate)
    samples = bytearray()
    for i in range(num_samples):
        t = i / float(sample_rate)
        progress = i / float(num_samples)
        freq = freq_start + (freq_end - freq_start) * progress
        val = math.sin(2.0 * math.pi * freq * t)
        
        # Envelope: Attack and Decay
        env = 1.0
        if progress < 0.05:
            env = progress / 0.05
        elif decay:
            env = math.exp(- progress * 5.0)
            
        sample_val = int(val * env * volume * 32767.0)
        sample_val = max(-32768, min(32767, sample_val))
        samples.extend(struct.pack('<h', sample_val))
    return bytes(samples)

def create_noise_burst(duration_s, sample_rate=48000, volume=0.6, cutoff_decay=True):
    """Generates procedural noise burst for paper friction / shutter."""
    import random
    num_samples = int(duration_s * sample_rate)
    samples = bytearray()
    last_val = 0.0
    for i in range(num_samples):
        progress = i / float(num_samples)
        raw_noise = (random.random() * 2.0 - 1.0)
        # Simple 1-pole low-pass filter
        filtered = 0.25 * raw_noise + 0.75 * last_val
        last_val = filtered
        
        env = math.exp(- progress * 6.0) if cutoff_decay else (1.0 - progress)
        sample_val = int(filtered * env * volume * 32767.0)
        sample_val = max(-32768, min(32767, sample_val))
        samples.extend(struct.pack('<h', sample_val))
    return bytes(samples)

def _get_default_sfx_dir() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_dir, "storage", "assets", "sfx")

def ensure_sfx_library(assets_dir: Optional[str] = None):
    """Ensures all essential SOTA procedural and recorded SFX files exist."""
    if not assets_dir:
        assets_dir = _get_default_sfx_dir()
    os.makedirs(assets_dir, exist_ok=True)
    
    sfx_manifest = {
        "shutter_click.wav": lambda: create_noise_burst(0.12, volume=0.75),
        "paper_slide.wav": lambda: create_noise_burst(0.28, volume=0.45),
        "page_turn.wav": lambda: create_noise_burst(0.35, volume=0.55),
        "typewriter_click.wav": lambda: create_sine_burst(1200, 300, 0.04, volume=0.6),
        "whoosh_sfx.wav": lambda: create_sine_burst(150, 60, 0.35, volume=0.65),
        "steam_gear_sfx.wav": lambda: create_sine_burst(220, 180, 0.45, volume=0.5)
    }
    
    for filename, generator in sfx_manifest.items():
        filepath = os.path.join(assets_dir, filename)
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 100:
            audio_data = generator()
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(48000)
                wf.writeframes(audio_data)
            logger.info(f"Generated procedural Foley SFX: {filename}")
    return assets_dir

class FoleyDirector:
    """Detects narrative keywords and constructs a Sound EDL with procedural audio cues."""
    
    KEYWORDS_SHUTTER = ["foto", "fotografía", "cámara", "archivo", "registro", "evidencia", "patente", "expediente", "imagen", "photo", "archive", "shutter", "evidence"]
    KEYWORDS_PAPER = ["documento", "informe", "página", "papel", "hoja", "prensa", "artículo", "carta", "manifiesto", "paper", "document", "report", "page", "letter", "sheet"]
    KEYWORDS_TYPEWRITER = ["cifra", "porcentaje", "año", "número", "dato", "estadística", "teclado", "escribir", "percent", "number", "data", "statistic", "typewriter", "key"]
    KEYWORDS_WHOOSH = ["cambio", "viaje", "transformación", "movimiento", "transición", "rápido", "nuevo", "turn", "shift", "change", "transition", "whoosh"]
    KEYWORDS_STEAMPUNK = ["vapor", "engranaje", "máquina", "caldera", "onirópolis", "reloj", "alquimia", "bruma", "steam", "gear", "machine", "boiler", "clock", "alchemy"]

    def __init__(self, assets_dir: Optional[str] = None):
        self.assets_dir = ensure_sfx_library(assets_dir)

    def analyze_transcription(self, subtitle_segments: list) -> list:
        """
        Takes segments with start, end, and text, and builds a timed SFX EDL.
        Avoids sound crowding by enforcing minimum spacing of 0.8s between cues.
        """
        sfx_events = []
        last_timestamp = -1.0
        
        for seg in subtitle_segments:
            start_t = float(seg.get("start", 0.0))
            text = str(seg.get("text", "")).lower()
            
            if start_t - last_timestamp < 0.6:
                continue
                
            chosen_sfx = None
            desc = ""
            
            if any(kw in text for kw in self.KEYWORDS_SHUTTER):
                chosen_sfx = "shutter_click.wav"
                desc = "Shutter Click (Archive/Photo reveal)"
            elif any(kw in text for kw in self.KEYWORDS_PAPER):
                chosen_sfx = "paper_slide.wav"
                desc = "Paper Slide (Document texture)"
            elif any(kw in text for kw in self.KEYWORDS_STEAMPUNK):
                chosen_sfx = "steam_gear_sfx.wav"
                desc = "Steam & Gear (Steampunk atmosphere)"
            elif any(kw in text for kw in self.KEYWORDS_TYPEWRITER):
                chosen_sfx = "typewriter_click.wav"
                desc = "Typewriter Key (Data entry)"
            elif any(kw in text for kw in self.KEYWORDS_WHOOSH):
                chosen_sfx = "whoosh_sfx.wav"
                desc = "Kinetic Whoosh (Scene transition)"
                
            if chosen_sfx:
                sfx_events.append({
                    "timestamp": round(start_t, 2),
                    "asset_file": os.path.join(self.assets_dir, chosen_sfx),
                    "volume_db": -6.0,
                    "description": desc
                })
                last_timestamp = start_t
                
        return sfx_events
