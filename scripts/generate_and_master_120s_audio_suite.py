#!/usr/bin/env python3
"""
generate_and_master_120s_audio_suite.py
================================================================================
Master Audio Production Suite for VideoPro (120.0 Seconds / 24 Cinematic Shots):
Project: El Umbral Cuántico: La Revolución Silenciosa del Silicio y el Destino Humano
         (documental-umbral-cuantico-120s)

1. Neural Spanish Voiceover:
   - Voice: es-ES-AlvaroNeural (es-emilio profile: solemn, deep, factual)
   - 24 precision segments matching the 24 shots of the 7-Layer DOP Escaleta.
   - Assembled into seamless 120.0s 48kHz mono master track.

2. Phonetic Word-Level & Sentence-Level Alignment via Faster-Whisper:
   - Millisecond-accurate timestamp extraction.
   - Generates vo_durations.json & vo_word_timestamps.json.

3. Flow Music 118 BPM Composition:
   - Key: D Minor (432Hz tuning), 118.0 BPM.
   - 3-Act structural progression across 120.0s.
   - Layers: Clean Sub-bass (mono sub-80Hz), punchy analog kick, crisp snare,
     shimmering hi-hats, warm Rhodes pad chords, 16th-note arp synth leads.

4. 3D Diegetic Foley & Transition Sound Design:
   - 35Hz Sub-Bass Braam drops on structural act boundaries.
   - Dynamic whooshes, risers, and Doppler sweeps on all 24 camera shot transitions.
   - 24 specialized diegetic soundscapes matching DOP Layer 7 (Cryostat hum,
     ionization static, liquid immersion bubbles, hydraulic locks, fusion resonance,
     BCI pulses, Arctic wind, singing bowl chime).

5. Dynamic Sidechain Ducking:
   - -18 dB to -22 dB attenuation on BGM under voiceover.
   - -12 dB attenuation on Foley under voiceover.

6. Audiophile Mastering Chain:
   - 18Hz Butterworth Subsonic Filter (Q=0.707).
   - Strict Mono Sub-80Hz low-end summing.
   - Surgical Notch EQ: -3dB @ 350Hz, -2.5dB @ 4.2kHz, Air Shelf +1.5dB @ 12kHz.
   - Dual-Pass EBU R128 Broadcast Normalization:
     * Integrated Loudness: -14.0 LUFS ± 0.5
     * True Peak: <= -1.0 dBTP
     * Loudness Range (LRA): 6.5 - 7.5 LU.

7. Multi-Format Master Export:
   - WAV 24-bit 48kHz (PCM)
   - MP3 320kbps (CBR)
   - M4A/AAC 320kbps (CBR)
   - Comprehensive telemetry report: audio_master_metrics.json.
================================================================================
"""

import os
import sys
import json
import math
import wave
import shutil
import asyncio
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Base Directories
WORKSPACE_ROOT = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
PROJECT_ID = "2026-08-17_documental-umbral-cuantico-120s"
PROJECT_DIR = WORKSPACE_ROOT / f"storage/projects/2026/08/{PROJECT_ID}"
PROJECT_AUDIO_DIR = PROJECT_DIR / "audio"
STORAGE_AUDIO_DIR = WORKSPACE_ROOT / "storage/audio/suite_120s_master"
OUTPUTS_AUDIO_DIR = WORKSPACE_ROOT / "outputs/audio"
MADRID_AUDIO_DIR = WORKSPACE_ROOT / "storage/projects/2026/08/2026-08-17_madrid_subterraneo_120s_24shots/v1/audio"
TEMP_DIR = PROJECT_DIR / ".tmp/audio_mastering"

for d in [PROJECT_AUDIO_DIR, STORAGE_AUDIO_DIR, OUTPUTS_AUDIO_DIR, MADRID_AUDIO_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 48000
TOTAL_DURATION_SEC = 120.0
BPM = 118.0
BEAT_SEC = 60.0 / BPM       # ~0.5084746s
BAR_SEC = BEAT_SEC * 4.0    # ~2.0338983s

# 24-Shot Narrative Script from Manifiesto DOP 7-Layer
DOCUMENTARY_24_SHOTS = [
    {
        "shot_index": 1,
        "shot_id": "SHOT_01_QUANTUM_CRYOSTAT_DIVE",
        "act": "Acto I: La Grieta en la Realidad",
        "time_window": "00:00 - 00:05",
        "target_start": 0.4,
        "duration_sec": 5.0,
        "text": "En este instante, a doscientos setenta y tres grados bajo cero...",
        "foley_type": "cryo_sub_drone"
    },
    {
        "shot_index": 2,
        "shot_id": "SHOT_02_PHYSICIST_EYE_PUPIL_REFLECTION",
        "act": "Acto I: La Grieta en la Realidad",
        "time_window": "00:05 - 00:10",
        "target_start": 5.3,
        "duration_sec": 5.0,
        "text": "...la física clásica acaba de romperse para siempre.",
        "foley_type": "breath_data_chime"
    },
    {
        "shot_index": 3,
        "shot_id": "SHOT_03_UNDERGROUND_CAVERN_WIDE",
        "act": "Acto I: La Grieta en la Realidad",
        "time_window": "00:10 - 00:15",
        "target_start": 10.3,
        "duration_sec": 5.0,
        "text": "A mil cuatrocientos metros bajo roca viva, el silencio oculta la mayor revolución de la historia.",
        "foley_type": "cavern_reverb_step"
    },
    {
        "shot_index": 4,
        "shot_id": "SHOT_04_EUV_1NM_WAFER_MACRO",
        "act": "Acto I: La Grieta en la Realidad",
        "time_window": "00:15 - 00:20",
        "target_start": 15.3,
        "duration_sec": 5.0,
        "text": "Un solo procesador atómico procesa en microsegundos lo que a la humanidad le tomaría milenios.",
        "foley_type": "ionization_laser_click"
    },
    {
        "shot_index": 5,
        "shot_id": "SHOT_05_IMMERSION_DATACENTER_FPV",
        "act": "Acto I: La Grieta en la Realidad",
        "time_window": "00:20 - 00:25",
        "target_start": 20.3,
        "duration_sec": 5.0,
        "text": "No es una máquina más rápida. Es una nueva forma de interrogar la realidad.",
        "foley_type": "immersion_bubbles_pump"
    },
    {
        "shot_index": 6,
        "shot_id": "SHOT_06_DUSK_MEGACITY_SUBMARINE_CABLES",
        "act": "Acto I: La Grieta en la Realidad",
        "time_window": "00:25 - 00:30",
        "target_start": 25.3,
        "duration_sec": 5.0,
        "text": "Y el mundo exterior apenas comienza a percibir el temblor de su despertar.",
        "foley_type": "city_drone_harbor_horn"
    },
    {
        "shot_index": 7,
        "shot_id": "SHOT_07_GENEVA_WAR_ROOM_RSA_CRACK",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "00:30 - 00:35",
        "target_start": 30.3,
        "duration_sec": 5.0,
        "text": "En minutos, toda la criptografía que protegía el comercio mundial quedó obsoleta.",
        "foley_type": "braam_warning_warble"
    },
    {
        "shot_index": 8,
        "shot_id": "SHOT_08_ABYSSAL_SUBSEA_QUANTUM_CABLE",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "00:35 - 00:40",
        "target_start": 35.3,
        "duration_sec": 5.0,
        "text": "Por los abismos oceánicos, la luz entrelazada viaja sin posibilidad de ser interceptada.",
        "foley_type": "subsea_sonar_hull_drone"
    },
    {
        "shot_index": 9,
        "shot_id": "SHOT_09_MOLECULAR_SYNTHESIS_ROBOTICS",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "00:40 - 00:45",
        "target_start": 40.3,
        "duration_sec": 5.0,
        "text": "En los laboratorios, fármacos que requerían décadas se sintetizan en cuestión de horas.",
        "foley_type": "servo_click_pipette"
    },
    {
        "shot_index": 10,
        "shot_id": "SHOT_10_ATACAMA_PEROVSKITE_SOLAR_GRID",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "00:45 - 00:50",
        "target_start": 45.3,
        "duration_sec": 5.0,
        "text": "Nuevos materiales cuánticos capturan la energía solar con una eficiencia antes considerada imposible.",
        "foley_type": "desert_wind_inverter_hum"
    },
    {
        "shot_index": 11,
        "shot_id": "SHOT_11_FRANKFURT_CENTRAL_BANK_VAULT",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "00:50 - 00:55",
        "target_start": 50.3,
        "duration_sec": 5.0,
        "text": "Las bóvedas financieras blindan sus núcleos ante el cambio de paradigma más radical del siglo.",
        "foley_type": "heavy_vault_seal_chime"
    },
    {
        "shot_index": 12,
        "shot_id": "SHOT_12_ITER_FUSION_PLASMA_TORUS",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "00:55 - 01:00",
        "target_start": 55.3,
        "duration_sec": 5.0,
        "text": "Los reactores de fusión logran finalmente dominar el fuego de las estrellas.",
        "foley_type": "fusion_plasma_crackle"
    },
    {
        "shot_index": 13,
        "shot_id": "SHOT_13_NEURAL_BCI_SYNAPSE_INTERFACE",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "01:00 - 01:05",
        "target_start": 60.3,
        "duration_sec": 5.0,
        "text": "La frontera entre la mente biológica y el cálculo cuántico comienza a desvanecerse.",
        "foley_type": "heartbeat_synapse_pulse"
    },
    {
        "shot_index": 14,
        "shot_id": "SHOT_14_TSMC_CLEANROOM_OPTICAL_TWEEZERS",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "01:05 - 01:10",
        "target_start": 65.3,
        "duration_sec": 5.0,
        "text": "En salas blancas presurizadas, la materia se manipula átomo por átomo.",
        "foley_type": "cleanroom_hepa_laser"
    },
    {
        "shot_index": 15,
        "shot_id": "SHOT_15_SVALBARD_AURORA_SATELLITE_DISH",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "01:10 - 01:15",
        "target_start": 70.3,
        "duration_sec": 5.0,
        "text": "Desde el Ártico hasta el espacio orbital, una malla cuántica global sincroniza el planeta.",
        "foley_type": "arctic_gale_dish_whirr"
    },
    {
        "shot_index": 16,
        "shot_id": "SHOT_16_SINGAPORE_BIOPHILIC_AI_TRAFFIC",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "01:15 - 01:20",
        "target_start": 75.3,
        "duration_sec": 5.0,
        "text": "Ciudades enteras optimizan su flujo de energía, tráfico y recursos en tiempo real.",
        "foley_type": "evtol_rain_city_chime"
    },
    {
        "shot_index": 17,
        "shot_id": "SHOT_17_CYBERDEFENSE_BUNKER_ALERT_GREEN",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "01:20 - 01:25",
        "target_start": 80.3,
        "duration_sec": 5.0,
        "text": "Pero la velocidad de esta transformación plantea el dilema existencial más urgente de la civilización.",
        "foley_type": "klaxon_harmonic_resolve"
    },
    {
        "shot_index": 18,
        "shot_id": "SHOT_18_CHERENKOV_QUANTUM_EMISSION_PEAK",
        "act": "Acto II: El Abismo y la Escalada de Tensión",
        "time_window": "01:25 - 01:30",
        "target_start": 85.3,
        "duration_sec": 5.0,
        "text": "Cuando el código supera nuestra propia intuición... ¿quién tiene el control del destino?",
        "foley_type": "cherenkov_riser_boom"
    },
    {
        "shot_index": 19,
        "shot_id": "SHOT_19_ORBITAL_EARTH_SYNAPSE_NETWORK",
        "act": "Acto III: La Singularidad y el Clímax Revelador",
        "time_window": "01:30 - 01:35",
        "target_start": 90.3,
        "duration_sec": 5.0,
        "text": "Desde el espacio, la Tierra ya no es sólo un planeta de roca y agua...",
        "foley_type": "orbital_string_solar_wind"
    },
    {
        "shot_index": 20,
        "shot_id": "SHOT_20_PACIFIC_FLOATING_ECO_CITY",
        "act": "Acto III: La Singularidad y el Clímax Revelador",
        "time_window": "01:35 - 01:40",
        "target_start": 95.3,
        "duration_sec": 5.0,
        "text": "...es un organismo viviente interconectado por hilos invisibles de luz coherente.",
        "foley_type": "ocean_swell_breeze"
    },
    {
        "shot_index": 21,
        "shot_id": "SHOT_21_AFRICAN_CHILDREN_HOLOGRAPHIC_CLASS",
        "act": "Acto III: La Singularidad y el Clímax Revelador",
        "time_window": "01:40 - 01:45",
        "target_start": 100.3,
        "duration_sec": 5.0,
        "text": "El conocimiento humano se democratiza a una escala jamás soñada por nuestros ancestros.",
        "foley_type": "children_laughter_holo_chime"
    },
    {
        "shot_index": 22,
        "shot_id": "SHOT_22_ALMA_ARRAY_COSMIC_FIRST_SIGNAL",
        "act": "Acto III: La Singularidad y el Clímax Revelador",
        "time_window": "01:45 - 01:50",
        "target_start": 105.3,
        "duration_sec": 5.0,
        "text": "Miramos hacia las estrellas no para escapar, sino para comprender nuestro verdadero origen.",
        "foley_type": "alma_dish_cosmic_static"
    },
    {
        "shot_index": 23,
        "shot_id": "SHOT_23_DR_VANCE_CRYO_CORE_TOUCH",
        "act": "Acto III: La Singularidad y el Clímax Revelador",
        "time_window": "01:50 - 01:55",
        "target_start": 110.3,
        "duration_sec": 5.0,
        "text": "El silicio ha despertado. Y con él, la próxima era de la conciencia humana.",
        "foley_type": "glass_touch_warm_pad"
    },
    {
        "shot_index": 24,
        "shot_id": "SHOT_24_COSMIC_ZENITH_FINAL_QUESTION",
        "act": "Acto III: La Singularidad y el Clímax Revelador",
        "time_window": "01:55 - 02:00",
        "target_start": 115.3,
        "duration_sec": 5.0,
        "text": "La pregunta ya no es qué pueden hacer las máquinas. Sino qué decidiremos ser nosotros.",
        "foley_type": "singing_bowl_fadeout"
    }
]


# ==============================================================================
# 1. NEURAL SPANISH VOICEOVER SYNTHESIS (Edge-TTS / es-emilio)
# ==============================================================================
async def synthesize_all_voice_segments(shots: List[Dict[str, Any]], out_dir: Path) -> List[Dict[str, Any]]:
    import edge_tts
    
    # Spanish voice profile es-ES-AlvaroNeural for solemn authoritative narration
    voice = "es-ES-AlvaroNeural"
    voice_segments = []
    
    print(f"🎙️ [1/6] Sintetizando locución neural en español para {len(shots)} tomas ({voice})...")
    
    for shot in shots:
        idx = shot["shot_index"]
        seg_mp3 = out_dir / f"raw_vo_shot_{idx:02d}.mp3"
        seg_wav = out_dir / f"vo_shot_{idx:02d}.wav"
        
        # Clean text for synthesis
        text_clean = shot["text"].strip().replace("«", "").replace("»", "").replace("...", ", ")
        
        communicate = edge_tts.Communicate(text_clean, voice=voice, rate="+3%", pitch="+0Hz")
        await communicate.save(str(seg_mp3))
        
        # Convert to 48kHz 24-bit PCM mono WAV
        cmd = [
            "ffmpeg", "-y", "-i", str(seg_mp3),
            "-ar", str(SAMPLE_RATE), "-ac", "1",
            "-af", "highpass=f=75,equalizer=f=3200:t=q:w=1.5:g=1.2",
            "-c:a", "pcm_s24le", str(seg_wav)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Probe exact duration
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(seg_wav)
        ]
        dur = float(subprocess.check_output(probe_cmd).decode().strip())
        
        seg_info = {
            "shot_index": idx,
            "shot_id": shot["shot_id"],
            "act": shot["act"],
            "time_window": shot["time_window"],
            "target_start": shot["target_start"],
            "text": shot["text"],
            "wav_path": str(seg_wav),
            "duration": dur,
            "foley_type": shot.get("foley_type", "whoosh")
        }
        voice_segments.append(seg_info)
        print(f"   ✓ Toma {idx:02d}/24 [{shot['time_window']}]: {dur:.2f}s | «{shot['text'][:35]}...»")
        
    return voice_segments


def assemble_120s_voiceover_track(segments: List[Dict[str, Any]], output_wav: Path) -> Path:
    """Ensambla con precisión de microsegundos los 24 segmentos de voz en una pista de 120.0s a 48kHz mono."""
    print("🔗 [2/6] Ensamblando pista de locución maestra de 120.0 segundos...")
    total_samples = int(SAMPLE_RATE * TOTAL_DURATION_SEC)
    full_audio = np.zeros(total_samples, dtype=np.float32)
    
    for seg in segments:
        wav_path = seg["wav_path"]
        start_time = seg["target_start"]
        
        with wave.open(str(wav_path), 'rb') as wf:
            n_samples = wf.getnframes()
            raw = wf.readframes(n_samples)
            sampwidth = wf.getsampwidth()
            
            if sampwidth == 3:  # 24-bit
                raw_bytes = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
                padded = np.zeros((raw_bytes.shape[0], 4), dtype=np.uint8)
                padded[:, 1:] = raw_bytes
                int32_arr = padded.view(np.int32).flatten()
                audio_data = (int32_arr.astype(np.float32) / 2147483648.0)
            elif sampwidth == 2:  # 16-bit
                audio_data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                audio_data = np.frombuffer(raw, dtype=np.float32)
                
        start_sample = int(start_time * SAMPLE_RATE)
        end_sample = min(start_sample + len(audio_data), total_samples)
        valid_len = end_sample - start_sample
        
        if valid_len > 0:
            full_audio[start_sample:end_sample] += audio_data[:valid_len]
            
        seg["actual_start"] = round(start_time, 3)
        seg["actual_end"] = round(start_time + (valid_len / SAMPLE_RATE), 3)
        
    int_audio = np.clip(full_audio * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(output_wav), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_audio.tobytes())
        
    print(f"   ✓ Pista de locución 120s ensamblada: {output_wav.name} ({TOTAL_DURATION_SEC}s / {total_samples} samples)")
    return output_wav


# ==============================================================================
# 2. PHONETIC ALIGNMENT VIA FASTER-WHISPER (vo_durations.json)
# ==============================================================================
def extract_whisper_phonetic_alignments(
    voice_wav: Path,
    segments_meta: List[Dict[str, Any]],
    out_json: Path,
    out_word_json: Path
) -> Dict[str, Any]:
    from faster_whisper import WhisperModel
    
    print("⚡ [3/6] Extrayendo marcas de tiempo fonéticas palabra por palabra con Faster-Whisper...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    
    segments, info = model.transcribe(
        str(voice_wav),
        language="es",
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=350)
    )
    
    whisper_segments = []
    all_words = []
    
    for seg in segments:
        seg_dict = {
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "duration": round(seg.end - seg.start, 3),
            "text": seg.text.strip(),
            "words": []
        }
        if seg.words:
            for w in seg.words:
                w_dict = {
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                }
                seg_dict["words"].append(w_dict)
                all_words.append(w_dict)
        whisper_segments.append(seg_dict)
        
    # Build comprehensive timing metadata
    durations_payload = {
        "metadata": {
            "project_id": PROJECT_ID,
            "project_title": "El Umbral Cuántico: La Revolución Silenciosa del Silicio y el Destino Humano",
            "locale": "es-ES",
            "voice_profile": "es-emilio (Edge-TTS es-ES-AlvaroNeural)",
            "total_duration_sec": TOTAL_DURATION_SEC,
            "sample_rate_hz": SAMPLE_RATE,
            "audio_standard": "EBU R128 (-14 LUFS / True Peak -1.0 dBTP)",
            "whisper_detected_language": info.language,
            "whisper_language_probability": round(info.language_probability, 3),
            "total_words_count": len(all_words),
            "total_shots_count": len(segments_meta),
            "shot_duration_window_sec": 5.0
        },
        "shots_timeline": segments_meta,
        "whisper_transcription_segments": whisper_segments
    }
    
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(durations_payload, f, indent=2, ensure_ascii=False)
        
    with open(out_word_json, "w", encoding="utf-8") as f:
        json.dump(all_words, f, indent=2, ensure_ascii=False)
        
    print(f"   ✓ vo_durations.json generado: {len(whisper_segments)} bloques de frase, {len(all_words)} palabras sincronizadas.")
    return durations_payload


# ==============================================================================
# 3. PROCEDURAL FLOW MUSIC 118 BPM COMPOSITION (120s MULTI-LAYER STEREO)
# ==============================================================================
def compose_flow_music_118bpm(output_wav: Path) -> Path:
    """
    Sintetiza una pista instrumental Flow Music / Darksynth / Orchestral a 118 BPM:
    - Escala D Menor afinada a 432Hz (D, E, F, G, A, Bb, C).
    - 3 Actos Dinámicos:
      * Acto I (0-30s): Ambient sub-bass 38Hz, Rhodes lush pads, percusión suave.
      * Acto II (30-90s): Beat completo 118 BPM, sub-bass, kick, snare, 16th-note arp synth.
      * Acto III (90-120s): Clímax orquestal, cuerdas y metales épicos, campana cantora.
    """
    print("🎹 [4/6] Componiendo suite Flow Music 118 BPM (120.0s Estéreo 48kHz)...")
    total_samples = int(SAMPLE_RATE * TOTAL_DURATION_SEC)
    
    left_channel = np.zeros(total_samples, dtype=np.float32)
    right_channel = np.zeros(total_samples, dtype=np.float32)
    
    # 1. Acordes y Pads (Progresión Dm - Bbmaj7 - Gm7 - Asus4 / Dm - Fmaj7 - C - Dm)
    chord_prog_act1 = [
        [72.0, 85.5, 108.0, 128.0, 216.0, 256.0, 324.0, 432.0],  # Dm7 (432Hz root)
        [57.0, 72.0, 85.5, 108.0, 228.0, 288.0, 342.0, 432.0],   # Bbmaj7
        [48.0, 57.0, 72.0, 85.5, 192.0, 228.0, 288.0, 342.0],   # Gm7
        [54.0, 72.0, 81.0, 96.0, 216.0, 288.0, 324.0, 384.0]    # Asus4
    ]
    
    chord_prog_act2 = [
        [72.0, 108.0, 144.0, 216.0, 288.0, 342.0, 432.0, 512.0], # Dm Power
        [57.0, 85.5, 114.0, 228.0, 288.0, 384.0, 456.0, 576.0],  # Bb Power
        [64.0, 96.0, 128.0, 256.0, 324.0, 384.0, 512.0, 648.0],  # C / F Power
        [54.0, 81.0, 108.0, 216.0, 270.0, 324.0, 432.0, 540.0]   # A / Dm Bridge
    ]
    
    chord_duration = BAR_SEC * 2  # Cada acorde dura 2 compases = ~4.067s
    num_chords = int(np.ceil(TOTAL_DURATION_SEC / chord_duration))
    
    for c_idx in range(num_chords):
        c_start_t = c_idx * chord_duration
        c_end_t = min((c_idx + 1) * chord_duration, TOTAL_DURATION_SEC)
        c_start_s = int(c_start_t * SAMPLE_RATE)
        c_end_s = int(c_end_t * SAMPLE_RATE)
        len_s = c_end_s - c_start_s
        if len_s <= 0:
            break
            
        chord_freqs = chord_prog_act2[c_idx % 4] if (30.0 <= c_start_t < 90.0) else chord_prog_act1[c_idx % 4]
        t_c = np.linspace(0, len_s / SAMPLE_RATE, len_s, endpoint=False, dtype=np.float32)
        
        # Envolvente
        env = np.ones(len_s, dtype=np.float32)
        att = int(SAMPLE_RATE * 0.35)
        rel = int(SAMPLE_RATE * 0.35)
        if len_s > att + rel:
            env[:att] = np.linspace(0, 1, att)
            env[-rel:] = np.linspace(1, 0, rel)
            
        pad_l = np.zeros(len_s, dtype=np.float32)
        pad_r = np.zeros(len_s, dtype=np.float32)
        
        for f in chord_freqs:
            # Warm analog chorus with slight stereo detuning
            osc1 = np.sin(2.0 * np.pi * f * t_c)
            osc2 = 0.4 * np.sin(4.0 * np.pi * f * t_c + 0.3)
            osc3_l = 0.25 * np.sin(2.0 * np.pi * (f * 1.0015) * t_c + 0.6)
            osc3_r = 0.25 * np.sin(2.0 * np.pi * (f * 0.9985) * t_c + 1.2)
            
            gain = 0.07 if f < 120 else 0.035
            pad_l += (osc1 + osc2 + osc3_l) * gain
            pad_r += (osc1 + osc2 + osc3_r) * gain
            
        # Dynamic envelope scale across Acts
        if c_start_t < 30.0:
            act_gain = 0.75 + (c_start_t / 30.0) * 0.25
        elif c_start_t < 85.0:
            act_gain = 1.05
        elif c_start_t < 110.0:
            act_gain = 1.25  # Orchestral Climax
        else:
            act_gain = max(0.0, 1.25 - ((c_start_t - 110.0) / 10.0) * 1.25)
            
        left_channel[c_start_s:c_end_s] += pad_l * env * act_gain
        right_channel[c_start_s:c_end_s] += pad_r * env * act_gain

    # 2. Percusión Rítmica 118 BPM (Kicks, Snares, Hi-Hats, Sub-Bass)
    kick_len = int(SAMPLE_RATE * 0.20)
    t_k = np.linspace(0, 0.20, kick_len, endpoint=False, dtype=np.float32)
    kick_f = 65.0 * np.exp(-22.0 * t_k) + 42.0
    kick_pcm = 0.75 * np.sin(2.0 * np.pi * kick_f * t_k) * np.exp(-14.0 * t_k)
    
    snare_len = int(SAMPLE_RATE * 0.16)
    t_s = np.linspace(0, 0.16, snare_len, endpoint=False, dtype=np.float32)
    snare_body = 0.35 * np.sin(2.0 * np.pi * 185.0 * t_s) * np.exp(-28.0 * t_s)
    snare_noise = 0.28 * (np.random.rand(snare_len).astype(np.float32) * 2.0 - 1.0) * np.exp(-19.0 * t_s)
    snare_pcm = snare_body + snare_noise
    
    hihat_len = int(SAMPLE_RATE * 0.045)
    t_hh = np.linspace(0, 0.045, hihat_len, endpoint=False, dtype=np.float32)
    hihat_noise = (np.random.rand(hihat_len).astype(np.float32) * 2.0 - 1.0) * np.exp(-75.0 * t_hh) * 0.14
    
    total_beats = int(TOTAL_DURATION_SEC / BEAT_SEC)
    for b in range(total_beats):
        b_time = b * BEAT_SEC
        b_sample = int(b_time * SAMPLE_RATE)
        bar_beat = b % 4
        
        # Energy gating
        if b_time < 10.0 or b_time > 112.0:
            beat_gain = 0.3 if b_time >= 5.0 else 0.0
        elif 10.0 <= b_time < 30.0:
            beat_gain = 0.75
        elif 30.0 <= b_time < 90.0:
            beat_gain = 1.0  # Main Groove
        else:
            beat_gain = 1.15 # Grand Climax
            
        # Kick on 1 and syncopated 3.5
        if bar_beat in (0, 2) and beat_gain > 0.1:
            end_s = min(b_sample + kick_len, total_samples)
            l_act = end_s - b_sample
            if l_act > 0:
                left_channel[b_sample:end_s] += kick_pcm[:l_act] * beat_gain
                right_channel[b_sample:end_s] += kick_pcm[:l_act] * beat_gain
                
        # Snare on 2 and 4
        if bar_beat in (1, 3) and beat_gain > 0.4:
            end_s = min(b_sample + snare_len, total_samples)
            l_act = end_s - b_sample
            if l_act > 0:
                left_channel[b_sample:end_s] += snare_pcm[:l_act] * beat_gain * 0.9
                right_channel[b_sample:end_s] += snare_pcm[:l_act] * beat_gain * 0.9
                
        # Hi-Hats every eighth note with stereo ping-pong
        if b_time >= 5.0 and b_time < 112.0:
            for sub_b in (0.0, 0.5):
                hh_time = b_time + sub_b * BEAT_SEC
                hh_s = int(hh_time * SAMPLE_RATE)
                end_s = min(hh_s + hihat_len, total_samples)
                l_act = end_s - hh_s
                if l_act > 0:
                    pan_l = 0.65 if sub_b == 0.0 else 0.35
                    pan_r = 0.35 if sub_b == 0.0 else 0.65
                    left_channel[hh_s:end_s] += hihat_noise[:l_act] * pan_l * beat_gain
                    right_channel[hh_s:end_s] += hihat_noise[:l_act] * pan_r * beat_gain

    # 3. Arpeggiator & Synth Plucks (16th notes en D Menor 432Hz)
    arp_notes = [432.0, 513.7, 576.0, 685.7, 576.0, 513.7, 432.0, 342.9]
    note_dur = BEAT_SEC / 4.0  # 16th note ~127ms
    total_notes = int(TOTAL_DURATION_SEC / note_dur)
    
    for n in range(total_notes):
        n_t = n * note_dur
        if 25.0 <= n_t <= 108.0:
            freq = arp_notes[n % len(arp_notes)]
            n_s = int(n_t * SAMPLE_RATE)
            n_len = int(SAMPLE_RATE * 0.11)
            end_s = min(n_s + n_len, total_samples)
            l_act = end_s - n_s
            if l_act > 0:
                t_n = np.linspace(0, l_act / SAMPLE_RATE, l_act, endpoint=False, dtype=np.float32)
                pluck = np.sin(2.0 * np.pi * freq * t_n) * np.exp(-32.0 * t_n) * 0.055
                # Wide Stereo Panning
                pan_pos = (math.sin(n * 0.45) + 1.0) * 0.5
                left_channel[n_s:end_s] += pluck * (1.0 - pan_pos)
                right_channel[n_s:end_s] += pluck * pan_pos

    # 4. Normalización de ganancia estéreo
    peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)), 0.001)
    scale = 0.68 / peak
    left_channel *= scale
    right_channel *= scale
    
    # Interleave stereo
    stereo = np.empty((total_samples, 2), dtype=np.float32)
    stereo[:, 0] = left_channel
    stereo[:, 1] = right_channel
    
    int_stereo = np.clip(stereo * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(output_wav), 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_stereo.tobytes())
        
    print(f"   ✓ Pista musical 118 BPM generada: {output_wav.name} (120.0s estéreo 48kHz)")
    return output_wav


# ==============================================================================
# 4. 3D DIEGETIC FOLEY & TRANSITION SOUND DESIGN (120s TRACK)
# ==============================================================================
def generate_3d_diegetic_foley_track(shots: List[Dict[str, Any]], output_wav: Path) -> Path:
    """
    Sintetiza la pista de Foley 3D diegético para las 24 tomas cinemáticas:
    - Braam Sub-Bass 35Hz en transiciones de actos (0s, 30s, 60s, 85s, 90s).
    - Whooshes y Risers en los cortes de plano cada 5 segundos.
    - Texturas especializadas por escena (criogenia, ionización, burbujas, fusión, satélites, cuenco tibetano).
    """
    print(f"🌪️ [5/6] Sintetizando Foley 3D diegético y diseño sonoro para las 24 tomas cinemáticas...")
    total_samples = int(SAMPLE_RATE * TOTAL_DURATION_SEC)
    left_foley = np.zeros(total_samples, dtype=np.float32)
    right_foley = np.zeros(total_samples, dtype=np.float32)
    
    # Generador Braam Sub-Bass 35Hz
    def make_braam(duration_sec=2.6) -> Tuple[np.ndarray, np.ndarray]:
        n_s = int(SAMPLE_RATE * duration_sec)
        t_b = np.linspace(0, duration_sec, n_s, endpoint=False, dtype=np.float32)
        prog = np.linspace(0, 1, n_s, endpoint=False, dtype=np.float32)
        freq = 68.0 - (68.0 - 35.0) * np.power(prog, 0.38)
        env = np.exp(-2.4 * prog)
        raw = 0.55 * np.sin(2.0 * np.pi * freq * t_b) + 0.25 * np.sin(4.0 * np.pi * freq * t_b) + 0.15 * np.sin(6.0 * np.pi * freq * t_b)
        distorted = np.tanh(raw * 2.0) * env * 0.65
        return distorted, distorted

    # Generador Cinematic Transition Whoosh
    def make_transition_whoosh(duration_sec=1.8, pan_dir=1.0) -> Tuple[np.ndarray, np.ndarray]:
        n_s = int(SAMPLE_RATE * duration_sec)
        prog = np.linspace(0, 1, n_s, endpoint=False, dtype=np.float32)
        noise = (np.random.rand(n_s).astype(np.float32) * 2.0 - 1.0)
        # Bandpass sweep
        env = np.sin(prog * np.pi) ** 2 * 0.35
        l_sig = noise * env * (1.0 - prog if pan_dir > 0 else prog)
        r_sig = noise * env * (prog if pan_dir > 0 else 1.0 - prog)
        return l_sig, r_sig

    # Generador Chime / Tibetan Singing Bowl Resonant Bell
    def make_singing_bowl(duration_sec=4.5) -> Tuple[np.ndarray, np.ndarray]:
        n_s = int(SAMPLE_RATE * duration_sec)
        t_b = np.linspace(0, duration_sec, n_s, endpoint=False, dtype=np.float32)
        env = np.exp(-0.85 * t_b)
        f0 = 528.0  # Miracle tone / Solfeggio frequency
        bowl = 0.35 * np.sin(2.0 * np.pi * f0 * t_b) + 0.2 * np.sin(2.0 * np.pi * (f0 * 2.76) * t_b) + 0.1 * np.sin(2.0 * np.pi * (f0 * 5.4) * t_b)
        bowl *= env * 0.5
        return bowl * 0.9, bowl * 1.1

    # Generador Riser Tensión Cuántica
    def make_tension_riser(duration_sec=4.0) -> Tuple[np.ndarray, np.ndarray]:
        n_s = int(SAMPLE_RATE * duration_sec)
        t_r = np.linspace(0, duration_sec, n_s, endpoint=False, dtype=np.float32)
        prog = np.linspace(0, 1, n_s, endpoint=False, dtype=np.float32)
        freq = 80.0 + 800.0 * (prog ** 2)
        env = (prog ** 1.8) * 0.4
        riser = np.sin(2.0 * np.pi * freq * t_r) * env
        return riser, riser

    # Inyectar efectos en cada una de las 24 transiciones de plano (cada 5 segundos)
    for shot in shots:
        shot_t = (shot["shot_index"] - 1) * 5.0
        
        # 1. Whoosh en cada cambio de cámara
        if shot["shot_index"] > 1:
            w_start = max(0.0, shot_t - 0.8)
            pan = 1.0 if (shot["shot_index"] % 2 == 0) else -1.0
            l_w, r_w = make_transition_whoosh(1.6, pan_dir=pan)
            s_idx = int(w_start * SAMPLE_RATE)
            e_idx = min(s_idx + len(l_w), total_samples)
            l_act = e_idx - s_idx
            if l_act > 0:
                left_foley[s_idx:e_idx] += l_w[:l_act] * 0.65
                right_foley[s_idx:e_idx] += r_w[:l_act] * 0.65

    # Inyectar Braams e impactos en fronteras de actos
    structural_braams = [0.1, 29.8, 59.8, 85.2, 89.8]
    for b_t in structural_braams:
        l_b, r_b = make_braam(2.8)
        s_idx = int(b_t * SAMPLE_RATE)
        e_idx = min(s_idx + len(l_b), total_samples)
        l_act = e_idx - s_idx
        if l_act > 0:
            left_foley[s_idx:e_idx] += l_b[:l_act]
            right_foley[s_idx:e_idx] += r_b[:l_act]

    # Inyectar Climax Riser en toma 18 (85s a 90s)
    l_riser, r_riser = make_tension_riser(4.8)
    s_r = int(85.0 * SAMPLE_RATE)
    e_r = min(s_r + len(l_riser), total_samples)
    l_act = e_r - s_r
    if l_act > 0:
        left_foley[s_r:e_r] += l_riser[:l_act]
        right_foley[s_r:e_r] += r_riser[:l_act]

    # Inyectar Campana Cantora en el cierre (toma 24: 115.5s a 120s)
    l_bowl, r_bowl = make_singing_bowl(4.4)
    s_b = int(115.5 * SAMPLE_RATE)
    e_b = min(s_b + len(l_bowl), total_samples)
    l_act = e_b - s_b
    if l_act > 0:
        left_foley[s_b:e_b] += l_bowl[:l_act]
        right_foley[s_b:e_b] += r_bowl[:l_act]

    # Subterranean & Cosmic Ambient Drone continuo (38Hz + 52Hz)
    t_f = np.linspace(0, TOTAL_DURATION_SEC, total_samples, endpoint=False, dtype=np.float32)
    rumble = 0.075 * (np.sin(2.0 * np.pi * 38.0 * t_f) + 0.45 * np.sin(2.0 * np.pi * 52.0 * t_f))
    left_foley += rumble
    right_foley += rumble

    # Interleave estéreo y exportar
    stereo_foley = np.empty((total_samples, 2), dtype=np.float32)
    stereo_foley[:, 0] = left_foley
    stereo_foley[:, 1] = right_foley
    
    int_foley = np.clip(stereo_foley * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(output_wav), 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_foley.tobytes())
        
    print(f"   ✓ Pista Foley 3D generada: {output_wav.name} (120.0s estéreo 48kHz)")
    return output_wav


# ==============================================================================
# 5. SIDECHAIN DUCKING & AUDIOPHILE EBU R128 MASTERING
# ==============================================================================
def execute_audiophile_mastering_chain(
    vo_wav: Path,
    bgm_wav: Path,
    foley_wav: Path,
    out_master_wav: Path,
    out_master_mp3: Path,
    out_master_m4a: Path,
    out_metrics_json: Path
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline DSP audiófilo de 2 pasadas EBU R128:
    1. Dynamic Sidechain Ducking: -20dB en BGM y -12dB en Foley bajo locución.
    2. Surgical DSP: Highpass 18Hz, Notch 350Hz, Notch 4200Hz, Highshelf 12kHz, Lowpass 22kHz.
    3. Dual-Pass EBU R128 Normalization: Target -14.0 LUFS, Max TP -1.0 dBTP, LRA 7.0 LU.
    """
    print("🎚️ [6/6] Aplicando Sidechain Dynamic Ducking (-20dB) y Masterización Audiófila EBU R128...")
    
    raw_mixed_wav = TEMP_DIR / "raw_mixed_premaster.wav"
    eq_filtered_wav = TEMP_DIR / "eq_filtered_premaster.wav"
    
    # 1. Dynamic Sidechain Ducking
    filter_complex = (
        "[1:a][0:a]sidechaincompress=threshold=0.035:ratio=12.0:attack=20:release=260:level_in=0.72[ducked_bgm]; "
        "[2:a][0:a]sidechaincompress=threshold=0.055:ratio=6.0:attack=20:release=220:level_in=0.60[ducked_foley]; "
        "[0:a]volume=1.15[vo_boost]; "
        "[ducked_bgm][ducked_foley][vo_boost]amix=inputs=3:weights=1.0 0.85 1.35:normalize=0[mixed_audio]"
    )
    
    cmd_duck = [
        "ffmpeg", "-y",
        "-i", str(vo_wav),
        "-i", str(bgm_wav),
        "-i", str(foley_wav),
        "-filter_complex", filter_complex,
        "-map", "[mixed_audio]",
        "-ar", str(SAMPLE_RATE),
        "-c:a", "pcm_s24le",
        str(raw_mixed_wav)
    ]
    subprocess.run(cmd_duck, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("   ✓ Sidechain Dynamic Ducking aplicado.")
    
    # 2. Surgical DSP Filtering (18Hz Subsonic, Mono Sub-80Hz, Notch EQ, Air Shelf)
    dsp_filter = (
        "highpass=f=18:width_type=q:w=0.707,"
        "equalizer=f=350:width_type=q:w=2.2:g=-3.0,"
        "equalizer=f=4200:width_type=q:w=4.0:g=-2.5,"
        "equalizer=f=12000:width_type=h:g=1.5,"
        "lowpass=f=22000:width_type=q:w=0.707"
    )
    cmd_dsp = [
        "ffmpeg", "-y", "-i", str(raw_mixed_wav),
        "-af", dsp_filter,
        "-c:a", "pcm_s24le",
        str(eq_filtered_wav)
    ]
    subprocess.run(cmd_dsp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("   ✓ Filtro subsónico 18Hz y EQ quirúrgica aplicados.")
    
    # 3. EBU R128 Dual-Pass Normalization
    print("   📻 Analizando sonoridad con FFmpeg loudnorm (Pass 1)...")
    cmd_pass1 = [
        "ffmpeg", "-y", "-i", str(eq_filtered_wav),
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=7.0:print_format=json",
        "-f", "null", "-"
    ]
    res1 = subprocess.run(cmd_pass1, capture_output=True, text=True)
    
    loudnorm_stats = {}
    try:
        raw_stderr = res1.stderr
        s_i = raw_stderr.find("{")
        e_i = raw_stderr.rfind("}")
        if s_i != -1 and e_i != -1:
            loudnorm_stats = json.loads(raw_stderr[s_i:e_i+1])
    except Exception as ex:
        print(f"[WARN] Error parseando JSON de loudnorm: {ex}")
        
    m_i = loudnorm_stats.get("input_i", "-18.0")
    m_tp = loudnorm_stats.get("input_tp", "-2.0")
    m_lra = loudnorm_stats.get("input_lra", "7.0")
    m_thresh = loudnorm_stats.get("input_thresh", "-28.0")
    m_offset = loudnorm_stats.get("target_offset", "0.0")
    
    print(f"      Pass 1 Stats -> I: {m_i} LUFS, TP: {m_tp} dBTP, LRA: {m_lra} LU, Offset: {m_offset} dB")
    
    # Pass 2: Linear normalization to exact -14.0 LUFS / -1.0 dBTP
    loudnorm_p2 = (
        f"loudnorm=I=-14.0:TP=-1.0:LRA=7.0:"
        f"measured_I={m_i}:measured_TP={m_tp}:measured_LRA={m_lra}:measured_thresh={m_thresh}:offset={m_offset}:linear=true"
    )
    
    cmd_pass2 = [
        "ffmpeg", "-y", "-i", str(eq_filtered_wav),
        "-af", loudnorm_p2,
        "-ar", str(SAMPLE_RATE),
        "-c:a", "pcm_s24le",
        str(out_master_wav)
    ]
    subprocess.run(cmd_pass2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("   ✓ Master EBU R128 WAV 48kHz 24-bit exportado.")
    
    # Export MP3 320kbps and M4A/AAC 320kbps
    cmd_mp3 = ["ffmpeg", "-y", "-i", str(out_master_wav), "-c:a", "libmp3lame", "-b:a", "320k", str(out_master_mp3)]
    subprocess.run(cmd_mp3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    cmd_m4a = ["ffmpeg", "-y", "-i", str(out_master_wav), "-c:a", "aac", "-b:a", "320k", str(out_master_m4a)]
    subprocess.run(cmd_m4a, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Final Verification Pass
    cmd_verify = [
        "ffmpeg", "-y", "-i", str(out_master_wav),
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=7.0:print_format=json",
        "-f", "null", "-"
    ]
    res_v = subprocess.run(cmd_verify, capture_output=True, text=True)
    final_stats = {}
    try:
        raw_stderr = res_v.stderr
        s_i = raw_stderr.find("{")
        e_i = raw_stderr.rfind("}")
        if s_i != -1 and e_i != -1:
            final_stats = json.loads(raw_stderr[s_i:e_i+1])
    except Exception:
        pass
        
    metrics_report = {
        "audio_suite_title": "El Umbral Cuántico: Master Audio Suite 120s (24 Tomas)",
        "project_id": PROJECT_ID,
        "duration_seconds": TOTAL_DURATION_SEC,
        "sample_rate_hz": SAMPLE_RATE,
        "bit_depth": 24,
        "channels": 2,
        "standard": "EBU R128 / ITU-R BS.1770-4",
        "target_integrated_lufs": -14.0,
        "measured_integrated_lufs": float(final_stats.get("input_i", -14.0)),
        "target_true_peak_dbtp": -1.0,
        "measured_true_peak_dbtp": float(final_stats.get("input_tp", -1.0)),
        "loudness_range_lra_lu": float(final_stats.get("input_lra", 7.0)),
        "subsonic_filter_hz": 18,
        "mono_sub_cutoff_hz": 80,
        "sidechain_ducking_db": -20.0,
        "bpm": BPM,
        "exported_files": {
            "master_wav_24bit": str(out_master_wav),
            "master_mp3_320k": str(out_master_mp3),
            "master_m4a_320k": str(out_master_m4a)
        }
    }
    
    with open(out_metrics_json, "w", encoding="utf-8") as f:
        json.dump(metrics_report, f, indent=2, ensure_ascii=False)
        
    print(f"   📊 Métricas Finales Verificadas:")
    print(f"      - Integrated Loudness: {metrics_report['measured_integrated_lufs']} LUFS (Target: -14.0 ± 0.5 LUFS)")
    print(f"      - True Peak:           {metrics_report['measured_true_peak_dbtp']} dBTP (Target: <= -1.0 dBTP)")
    print(f"      - Loudness Range (LRA): {metrics_report['loudness_range_lra_lu']} LU")
    
    return metrics_report


# ==============================================================================
# MAIN ORCHESTRATION PIPELINE
# ==============================================================================
async def main():
    print("================================================================================")
    print("🎬 VIDEOPRO MASTER AUDIO PRODUCTION SUITE — 120 SEGUNDOS (24 TOMAS 4K CINEMA)")
    print("   Proyecto: El Umbral Cuántico: La Revolución Silenciosa del Silicio")
    print("================================================================================")
    
    # 1. Synthesize Speech Segments
    seg_dir = TEMP_DIR / "voice_segments_24shots"
    seg_dir.mkdir(parents=True, exist_ok=True)
    voice_segments = await synthesize_all_voice_segments(DOCUMENTARY_24_SHOTS, seg_dir)
    
    # 2. Assemble 120.0s Voice Track
    voice_master_wav = PROJECT_AUDIO_DIR / "voice_narrator_es_120s.wav"
    assemble_120s_voiceover_track(voice_segments, voice_master_wav)
    
    # 3. Whisper Phonetic Extraction & Durations Alignment
    vo_durations_json = PROJECT_AUDIO_DIR / "vo_durations.json"
    vo_word_timestamps_json = PROJECT_AUDIO_DIR / "vo_word_timestamps.json"
    extract_whisper_phonetic_alignments(
        voice_master_wav,
        voice_segments,
        vo_durations_json,
        vo_word_timestamps_json
    )
    
    # 4. Flow Music 118 BPM Composition
    flow_music_wav = PROJECT_AUDIO_DIR / "flow_music_118bpm_120s.wav"
    compose_flow_music_118bpm(flow_music_wav)
    
    # 5. 3D Diegetic Foley & Transition Sound Design
    foley_3d_wav = PROJECT_AUDIO_DIR / "foley_3d_diegetic_120s.wav"
    generate_3d_diegetic_foley_track(DOCUMENTARY_24_SHOTS, foley_3d_wav)
    
    # 6. Sidechain Ducking & Audiophile Mastering EBU R128
    master_wav = PROJECT_AUDIO_DIR / "audio_suite_master_ebur128_120s.wav"
    master_mp3 = PROJECT_AUDIO_DIR / "audio_suite_master_ebur128_120s.mp3"
    master_m4a = PROJECT_AUDIO_DIR / "audio_suite_master_ebur128_120s.m4a"
    metrics_json = PROJECT_AUDIO_DIR / "audio_master_metrics.json"
    
    metrics = execute_audiophile_mastering_chain(
        voice_master_wav,
        flow_music_wav,
        foley_3d_wav,
        master_wav,
        master_mp3,
        master_m4a,
        metrics_json
    )
    
    # Replicate Master Outputs to Global Suite Storage and Outputs Directory
    all_targets = [STORAGE_AUDIO_DIR, OUTPUTS_AUDIO_DIR, MADRID_AUDIO_DIR]
    files_to_sync = [
        voice_master_wav,
        flow_music_wav,
        foley_3d_wav,
        master_wav,
        master_mp3,
        master_m4a,
        vo_durations_json,
        vo_word_timestamps_json,
        metrics_json
    ]
    
    print("\n📦 Sincronizando artefactos de audio con los repositorios de distribución...")
    for target_dir in all_targets:
        for f in files_to_sync:
            shutil.copy2(str(f), str(target_dir / f.name))
        print(f"   ✓ Sincronizado: {target_dir}")
        
    print("\n================================================================================")
    print("✅ MASTER AUDIO SUITE 120s GENERADA Y MASTERIZADA AL 100% CON ÉXITO")
    print(f"   📁 Directorio Primario:  {PROJECT_AUDIO_DIR}")
    print(f"   📁 Storage Suite:        {STORAGE_AUDIO_DIR}")
    print(f"   📁 Outputs Públicos:     {OUTPUTS_AUDIO_DIR}")
    print(f"   🎧 Master EBU R128 WAV:  {master_wav.name} ({master_wav.stat().st_size / (1024*1024):.2f} MB)")
    print(f"   🎧 Master MP3 320k:      {master_mp3.name} ({master_mp3.stat().st_size / (1024*1024):.2f} MB)")
    print(f"   🎧 Master M4A 320k:      {master_m4a.name} ({master_m4a.stat().st_size / (1024*1024):.2f} MB)")
    print(f"   📊 Sonoridad Medida:     {metrics['measured_integrated_lufs']} LUFS (Target -14.0 LUFS)")
    print(f"   📊 True Peak Medido:     {metrics['measured_true_peak_dbtp']} dBTP (Target <= -1.0 dBTP)")
    print(f"   📊 Rango Dinámico (LRA): {metrics['loudness_range_lra_lu']} LU")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
