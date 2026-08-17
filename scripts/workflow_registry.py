#!/usr/bin/env python3
"""
workflow_registry.py
====================
Registro Persistente, Versionado Semántico y Gestor Canónico de Workflows — VideoPro Studio.

Administra el ciclo de vida, almacenamiento persistente (JSON / YAML), versionado semántico (SemVer)
con sellado criptográfico SHA-256 y validación de las 10 Reglas de Oro para los 8 Arquetipos Canónicos:
  1. CHRONODRIFT_6DOF       (ChronoDrift 6-DoF Tritemporal Urban Master)
  2. FPV_URBAN              (FPV Urban Real Flow 4K)
  3. VOX_EXPLAINER          (VOX Investigative Documentary 4K)
  4. VIRAL_SHORTS_916       (Viral Shorts & High-Retention Hook 9:16)
  5. DOCUMENTAL_35MM        (Documental Histórico 35mm Master)
  6. NANOVERSE              (NanoVerse Cellular & Quantum Macro 4K)
  7. LIVING_CANVAS          (Living Canvas Fine Art 3D Animation)
  8. ASTRODRIFT             (AstroDrift Deep Space Relativistic 4K)
"""

from __future__ import annotations

import os
import sys
import json
import yaml
import hashlib
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pydantic import BaseModel, Field

# Añadir raíz del proyecto al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logger = logging.getLogger("videopro.workflow_registry")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s : %(message)s")


# ============================================================================
# 1. MODELOS PYDANTIC DEL ESQUEMA ESTRUCTURADO DE WORKFLOW
# ============================================================================

class Prompt7DManifest(BaseModel):
    """Manifiesto de Prompts en 7 Capas Físicas Cinemáticas."""
    layer1_subject: str = Field(..., description="Capa 1: Sujeto / Protagonista / Núcleo Dramático")
    layer2_environment: str = Field(..., description="Capa 2: Entorno / Época / Materialidad Física")
    layer3_lighting: str = Field(..., description="Capa 3: Iluminación / Atmósfera / Scattering")
    layer4_optics: str = Field(..., description="Capa 4: Óptica / Lente / Sensor")
    layer5_motion: str = Field(..., description="Capa 5: Movimiento de Cámara / Dinámica de Toma")
    layer6_colorimetry: str = Field(..., description="Capa 6: Colorimetría / Emulación de Película / LUT")
    layer7_render_engine: str = Field(..., description="Capa 7: Motor de Render / Frame Rate / Postprocesado")
    anti_cgi_negative_lexicon: List[str] = Field(
        default_factory=lambda: [
            "hyper-realistic", "photorealistic", "octane render", "unreal engine",
            "plastic smooth skin", "plastic metal", "blurry artifacts", "jpeg compression"
        ],
        description="Léxico Prohibido Anti-CGI"
    )
    custom_tokens: List[str] = Field(default_factory=list, description="Tokens de Estilo y Tags")


class CameraOpticsSpec(BaseModel):
    """Especificación Física y Óptica de Cámara."""
    focal_length_mm: float = Field(35.0, description="Distancia Focal en mm")
    sensor_profile: str = Field("ARRI_Alexa_35", description="Perfil de Sensor / Emulación")
    aperture_f_stop: float = Field(2.0, description="Apertura Diafragma f-stop")
    depth_of_field: str = Field("Cinematic shallow depth of field", description="Descripción del Bokeh")
    motion_type: str = Field("6-DoF Orbit", description="Tipo de Trayectoria de Cámara")
    stabilization: str = Field("Electronic 3-Axis Gimbal", description="Estabilización")
    shutter_angle_deg: float = Field(180.0, description="Ángulo de Obturador")
    fov_deg: float = Field(65.0, description="Campo de Visión (Field of View)")
    iso_target: int = Field(800, description="Sensibilidad ISO Objetivo")


class AudioSpec(BaseModel):
    """Especificaciones de Audio y Mastering Acústico Broadcast."""
    bpm: int = Field(118, description="Tempo / BPM de la Pista Musical")
    genre: str = Field("Flow Chillhop Lo-Fi", description="Género y Estilo Musical")
    ducking_db: float = Field(-18.0, description="Atenuación de Ducking en dB (<= -18dB requerido)")
    ducking_attack_ms: int = Field(30, description="Ataque de Ducking en ms")
    ducking_release_ms: int = Field(250, description="Liberación de Ducking en ms")
    voice_engine: str = Field("vibevoice", description="Motor de Locución (vibevoice / edgetts)")
    voice_preset_id: str = Field("es-emilio", description="Identificador de Voz")
    voice_speed: float = Field(1.0, description="Velocidad de Locución")
    voice_pitch: float = Field(0.0, description="Tono / Pitch")
    ebu_r128_target_lufs: float = Field(-14.0, description="Sonoridad Integrada Objetivo EBU R128 (-14.0 LUFS)")
    ebu_r128_true_peak_dbtp: float = Field(-1.0, description="True Peak Máximo en dBTP (-1.0 dBTP)")
    sub_80hz_mono: bool = Field(True, description="Procesamiento Sub-80Hz Mono para Graves Limpios")
    foley_presets: List[str] = Field(default_factory=list, description="Capas de Efectos Foley Acústicos")


class SubtitlesPacingSpec(BaseModel):
    """Reglas de Subtitulado Levenshtein y Ritmo de Montaje."""
    alignment_engine: str = Field("forced_levenshtein", description="Motor de Alineación Fonética")
    min_levenshtein_similarity: float = Field(0.85, description="Similitud Mínima Levenshtein (>= 0.85)")
    style: str = Field("modern_boxless_gold", description="Estilo Gráfico de Subtítulos")
    max_words_per_screen: int = Field(4, description="Palabras Máximas por Pantalla")
    font_family: str = Field("Montserrat", description="Familia Tipográfica")
    font_size: int = Field(42, description="Tamaño de Fuente")
    primary_color: str = Field("#FFFFFF", description="Color de Texto Principal")
    highlight_color: str = Field("#F59E0B", description="Color de Resaltado Dinámico / Karaoke")
    outline_color: str = Field("#1E293B", description="Color de Contorno")
    shadow_blur: int = Field(4, description="Desenfoque de Sombra")
    safe_zone_bottom_px: int = Field(80, description="Margen Inferior de Safe Zone en Píxeles")
    max_shot_duration_sec: float = Field(4.0, description="Duración Máxima de Toma Estática (s)")
    min_shot_duration_sec: float = Field(2.0, description="Duración Mínima de Toma (s)")
    cut_on_beat: bool = Field(True, description="Corte Sincronizado al Compás / Transientes")
    cut_every_bars: int = Field(2, description="Frecuencia de Corte por Compases")
    stagger_frames: int = Field(4, description="Micro-stagger Temporal de Entrada (Frames)")
    ken_burns_zoompan: bool = Field(True, description="Activación de Dinamismo Ken-Burns")


class RenderConfigSpec(BaseModel):
    """Configuración de Renderizado y Shaders Cinemáticos."""
    aspect_ratio: str = Field("16:9", description="Relación de Aspecto (16:9 / 9:16)")
    resolution_width: int = Field(3840, description="Ancho de Resolución en Píxeles")
    resolution_height: int = Field(2160, description="Alto de Resolución en Píxeles")
    fps: int = Field(60, description="Cuadros por Segundo (24 / 60 fps)")
    codec: str = Field("libx264", description="Códec de Vídeo (libx264 / libx265)")
    crf: int = Field(18, description="Factor de Calidad CRF (18 - 20)")
    preset: str = Field("slow", description="Preset de Compresión FFmpeg")
    pixel_format: str = Field("yuv420p", description="Formato de Píxel")
    color_space: str = Field("bt709", description="Espacio de Color (bt709 / bt2020 / aces)")
    transitions: List[str] = Field(default_factory=list, description="Transiciones Cinemáticas Permitidas")
    shaders: List[str] = Field(default_factory=list, description="Shaders de Post-procesado (Grano, Flare, Halide)")
    background_color: str = Field("#243048", description="Color de Fondo Anti-Blackdetect (#243048 / #101826)")
    anti_blackdetect: bool = Field(True, description="Protección Activa Anti-Blackdetect")


class WorkflowVersionInfo(BaseModel):
    """Metadatos de Versionado Semántico y Sellado Criptográfico."""
    semver: str = Field("v1.0.0", description="Versión Semántica (vX.Y.Z)")
    version_int: int = Field(1, description="Versión Entera Incremental")
    sha256_hash: str = Field("", description="Hash SHA-256 Determinista del Workflow")
    author: str = Field("VideoPro Core Studio", description="Autor o Agente Generador")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Fecha de Creación")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Fecha de Actualización")
    changelog: str = Field("Versión inicial canónica", description="Registro de Cambios")
    parent_hash: Optional[str] = Field(None, description="Hash SHA-256 de la Versión Precedente")
    tags: List[str] = Field(default_factory=list, description="Etiquetas de Despliegue")


class StructuredWorkflow(BaseModel):
    """Entidad Completa de Workflow Estructurado y Versionado."""
    id: str = Field(..., description="Identificador Canónico del Workflow")
    archetype_id: str = Field(..., description="ID del Arquetipo Canónico")
    name: str = Field(..., description="Nombre Comercial del Workflow")
    description: str = Field(..., description="Descripción Operativa del Pipeline")
    category: str = Field(..., description="Categoría Temática")
    target_audience: str = Field(..., description="Público Objetivo")
    tags: List[str] = Field(default_factory=list, description="Etiquetas de Clasificación")
    prompt_manifest: Prompt7DManifest = Field(..., description="Manifiesto 7D de Prompts")
    camera_optics: CameraOpticsSpec = Field(..., description="Parámetros de Óptica y Cámara")
    audio_spec: AudioSpec = Field(..., description="Especificaciones de Audio y Mastering")
    subtitles_pacing: SubtitlesPacingSpec = Field(..., description="Subtitulado y Ritmo de Montaje")
    render_config: RenderConfigSpec = Field(..., description="Configuración de Render")
    version_info: WorkflowVersionInfo = Field(..., description="Metadatos de Versión y SHA-256")
    required_capabilities: List[str] = Field(default_factory=list, description="Capacidades de Ejecución Requeridas")
    pipeline_nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Nodos del Grafo ComfyUI / Planner")
    pipeline_connections: List[Dict[str, Any]] = Field(default_factory=list, description="Conexiones entre Nodos")
    policies: Dict[str, Any] = Field(default_factory=lambda: {"retry_limit": 2, "auto_fallback": True, "strict_5kb_gate": True})
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos Adicionales y Canales Asociados")


# ============================================================================
# 2. DEFINICIONES DE LOS 8 ARQUETIPOS CANÓNICOS
# ============================================================================

CANONICAL_ARCHETYPES_DEFS: Dict[str, Dict[str, Any]] = {
    "CHRONODRIFT_6DOF": {
        "id": "CHRONODRIFT_6DOF",
        "archetype_id": "CHRONODRIFT_6DOF",
        "name": "ChronoDrift 6-DoF Tritemporal Urban Master",
        "description": "Recorridos orbitales continuos en 6 Grados de Libertad (6-DoF) a través de tres eras temporales (1626 -> 2026 -> 2226), morphing arquitectónico 4K, telemetría Remotion 3D HUD y banda sonora Flow Chillhop 118 BPM sincronizada al compás.",
        "category": "urban_time_travel",
        "target_audience": "Audiencias globales YouTube 4K interesadas en urbanismo futurista, viajes en el tiempo e historia visual inmersiva.",
        "tags": ["ChronoDrift", "6DoF", "Tritemporal", "4KUHD", "RemotionHUD", "Chillhop118BPM"],
        "prompt_manifest": {
            "layer1_subject": "Evolución morfológica de la arquitectura metropolitana, monumentos icónicos y transeúntes a través de 3 épocas históricas sincronizadas.",
            "layer2_environment": "Entorno urbano tritemporal: adoquinado del siglo XVII, asfalto y rascacielos contemporáneos de 2026, y metrópolis flotante ciber-ecológica de 2226 con transporte maglev.",
            "layer3_lighting": "Golden hour volumétrica con haces crepusculares a 45 grados, transicionando a iluminación nocturna de neón cian/ámbar y dispersión atmosférica Rayleigh.",
            "layer4_optics": "ARRI Alexa 35, lente anamórfica Cooke 35mm T1.8, bokeh ovalado, flare horizontal sutil azulado, profundidad de campo selectiva f/2.0.",
            "layer5_motion": "Cámara 6-DoF continuous drift, trayectoria orbital parabólica suave a 45 km/h, compensación giroscópica de 3 ejes, pitch +5 deg, yaw continuo.",
            "layer6_colorimetry": "ACEScg color space, emulación Kodak Vision3 5219 35mm, tonos cálidos en sombras, separación cromática teal & orange de grado cine.",
            "layer7_render_engine": "FLUX 3 DiT + LTX-2.5 6-DoF Flow Matching, 60fps high-motion interp, filtro Anti-CGI Cero Slop.",
            "anti_cgi_negative_lexicon": ["hyper-realistic", "photorealistic", "octane render", "unreal engine", "plastic smooth skin", "blurry artifacts", "floating limbs", "jpeg compression"],
            "custom_tokens": ["#ChronoDrift", "#6DoF", "#UrbanTimeTravel", "#ACEScg", "#4KUHD"]
        },
        "camera_optics": {
            "focal_length_mm": 35.0,
            "sensor_profile": "ARRI_Alexa_35_Super35",
            "aperture_f_stop": 2.0,
            "depth_of_field": "Medium shallow with cinematic falloff",
            "motion_type": "6-DoF Orbital Flight",
            "stabilization": "Triple-axis Electronic Gimbal + Optical Flow Smoothing",
            "shutter_angle_deg": 180.0,
            "fov_deg": 84.0,
            "iso_target": 800
        },
        "audio_spec": {
            "bpm": 118,
            "genre": "Flow Chillhop Lo-Fi Beats with 35Hz Sub-bass",
            "ducking_db": -18.0,
            "ducking_attack_ms": 30,
            "ducking_release_ms": 250,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-emilio",
            "voice_speed": 1.0,
            "voice_pitch": 0.0,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["wind_breeze_high_altitude", "clock_ticking_mechanical", "city_ambient_whoosh", "maglev_whoosh_future"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.85,
            "style": "modern_boxless_gold",
            "max_words_per_screen": 4,
            "font_family": "Montserrat",
            "font_size": 42,
            "primary_color": "#FFFFFF",
            "highlight_color": "#F59E0B",
            "outline_color": "#1E293B",
            "shadow_blur": 4,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 4.0,
            "min_shot_duration_sec": 2.5,
            "cut_on_beat": True,
            "cut_every_bars": 2,
            "stagger_frames": 4,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["temporal_morph_whip", "glitch_flash_2f", "dissolve_crossfade_30ms"],
            "shaders": ["anamorphic_flare_horizontal", "film_grain_fine_10pct", "chromatic_aberration_subtle"],
            "background_color": "#243048",
            "anti_blackdetect": True
        },
        "required_capabilities": ["research", "script", "voice_generation", "video_generation", "music_generation", "subtitle_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "01_CHRONODRIFT",
            "channel_handle": "@ChronoDriftOfficial",
            "target_rpm_usd": "$18.50 – $28.00 USD"
        }
    },
    "FPV_URBAN": {
        "id": "FPV_URBAN",
        "archetype_id": "FPV_URBAN",
        "name": "FPV Urban Real Flow 4K",
        "description": "Vuelo acrobático ultrarrápido en primera persona (FPV) a través de cañones urbanos, monumentos históricos y pasadizos estrechos con ráfagas de velocidad (speed-ramping) y banda sonora Darksynth 128 BPM.",
        "category": "fpv_acrobatic_urban",
        "target_audience": "Entusiastas de deportes de acción, drones FPV, arquitectura moderna y secuencias de alta adrenalina.",
        "tags": ["FPV", "UrbanFlow", "RealFlow4K", "Darksynth128BPM", "SpeedRamp", "ActionCamera"],
        "prompt_manifest": {
            "layer1_subject": "Vuelo rasante y acrobático FPV a través de estructuras emblemáticas, arcos de piedra, puentes colgantes y túneles iluminados.",
            "layer2_environment": "Metrópolis densa con arquitectura vertical, reflejos en cristaleras, avenidas con tráfico en time-lapse y callejones nocturnos.",
            "layer3_lighting": "Iluminación de hora azul contrastada con luces de tungsteno urbano y paneles de neón RGB de alto rango dinámico.",
            "layer4_optics": "Lente Ultra-Wide Fisheye 12mm f/2.8, sensor GoPro HERO12 Flat Log, corrección de distorsión óptica proporcional en los bordes.",
            "layer5_motion": "Maniobras extremas FPV: power-loops, barrel rolls, dive vertical de 200m y frenado cinemático con speed-ramping 200% a 50%.",
            "layer6_colorimetry": "Perfil D-LogM etalonado a LUT Cyberpunk Urbano con negros densos, saturación selectiva en rojos y cianes.",
            "layer7_render_engine": "Google Flow Playwright 4K + ComfyUI LTX-2.5 High-Speed Camera Engine, 60fps.",
            "anti_cgi_negative_lexicon": ["slow motion stutter", "plastic surfaces", "jittery camera artifacts", "flat lighting", "lowres textures"],
            "custom_tokens": ["#FPVDrone", "#SpeedRamp", "#RealFlow4K", "#UrbanDive"]
        },
        "camera_optics": {
            "focal_length_mm": 12.0,
            "sensor_profile": "GoPro_Hero12_Custom_Sensor",
            "aperture_f_stop": 2.8,
            "depth_of_field": "Deep infinite focus across full frame",
            "motion_type": "Acrobatic FPV Dive & Power-Loop",
            "stabilization": "ReelSteady GO Gyro Stabilization with Raw Roll Dynamics",
            "shutter_angle_deg": 180.0,
            "fov_deg": 122.0,
            "iso_target": 400
        },
        "audio_spec": {
            "bpm": 128,
            "genre": "Darksynth & Electronic Cyber-Trap",
            "ducking_db": -18.0,
            "ducking_attack_ms": 25,
            "ducking_release_ms": 200,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-mateo",
            "voice_speed": 1.05,
            "voice_pitch": 0.0,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["drone_rotor_propeller_wind", "high_speed_air_rush", "urban_traffic_subtle", "sub_impact_bassdrop"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.85,
            "style": "dynamic_speed_italic",
            "max_words_per_screen": 3,
            "font_family": "Bebas Neue",
            "font_size": 48,
            "primary_color": "#FFFFFF",
            "highlight_color": "#00F0FF",
            "outline_color": "#0A0A0A",
            "shadow_blur": 6,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 3.0,
            "min_shot_duration_sec": 1.8,
            "cut_on_beat": True,
            "cut_every_bars": 1,
            "stagger_frames": 3,
            "ken_burns_zoompan": False
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["speed_ramp_whip_pan", "directional_zoom_blur", "cut_on_transient"],
            "shaders": ["radial_motion_blur", "edge_glow_cyan", "lens_distortion_fisheye"],
            "background_color": "#243048",
            "anti_blackdetect": True
        },
        "required_capabilities": ["script", "video_generation", "music_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "02_FPV_URBAN",
            "channel_handle": "@FPVUrbanRealFlow",
            "target_rpm_usd": "$16.00 – $22.00 USD"
        }
    },
    "VOX_EXPLAINER": {
        "id": "VOX_EXPLAINER",
        "archetype_id": "VOX_EXPLAINER",
        "name": "VOX Investigative Documentary 4K (Paralaje 3D & Cartografía)",
        "description": "Documental de investigación periodística estilo Vox / Johnny Harris. Mapas vectoriales QGIS 4K con rutas punteadas animadas (Dash=78), paralaje 3D de documentos históricos con textura de papel prensa, micro-stagger temporal y audio ducking a -20dB.",
        "category": "investigative_documentary",
        "target_audience": "Espectadores de YouTube interesados en geopolítica, secretos históricos, ingeniería oculta y periodismo visual de alta retención.",
        "tags": ["VoxStyle", "Investigative", "Parallax3D", "QGIS4K", "Cartography", "AudioDucking20dB"],
        "prompt_manifest": {
            "layer1_subject": "Documentos desclasificados, planos arquitectónicos históricos, mapas topográficos y objetos de archivo analizados con lupa gráfica.",
            "layer2_environment": "Mesa de trabajo de investigación de hemeroteca, iluminación de flexo tenue, fondo con cuadrícula milimétrica sutil y textura de papel de prensa.",
            "layer3_lighting": "Luz puntual de estudio con claroscuro suave, sombras proyectadas sobre capas de papel y acento fluorescente de resaltador amarillo.",
            "layer4_optics": "Prime 35mm f/1.8 cine lens con paralaje 2.5D en capas Z (-50px a +150px), profundidad de campo focalizada en el documento clave.",
            "layer5_motion": "Vuelos suaves sobre mapas 3D QGIS (Dash=78, Z-offset +0.001), aperturas de carpetas, zooms sobre sellos oficiales y recortes con stagger.",
            "layer6_colorimetry": "Paleta sobria de investigación: fondo azul pizarra (#243048), papel marfil (#F4F1EA), resaltador flúor (#CCFF00) y tinta roja de sello.",
            "layer7_render_engine": "Remotion React 4K Motion Engine + FFmpeg Composite, 60fps.",
            "anti_cgi_negative_lexicon": ["3d plastic renders", "glossy surfaces", "neon overload", "unrealistic typography", "stock watermark"],
            "custom_tokens": ["#VoxStyle", "#QGIS4K", "#Parallax3D", "#InvestigativeDoc"]
        },
        "camera_optics": {
            "focal_length_mm": 35.0,
            "sensor_profile": "ARRI_Alexa_Mini_LF",
            "aperture_f_stop": 1.8,
            "depth_of_field": "Selective focus on textual evidence with 2.5D layer separation",
            "motion_type": "Multi-plane Parallax Glide & Topographic Flyover",
            "stabilization": "Camera Rig Precision Motion Control",
            "shutter_angle_deg": 180.0,
            "fov_deg": 63.0,
            "iso_target": 400
        },
        "audio_spec": {
            "bpm": 105,
            "genre": "Minimal Tension Investigative Soundtrack & Chamber Mallets",
            "ducking_db": -20.0,
            "ducking_attack_ms": 30,
            "ducking_release_ms": 300,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-narrador",
            "voice_speed": 1.0,
            "voice_pitch": 0.0,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["paper_handling_texture", "typewriter_keystrokes", "vintage_camera_shutter", "projector_ambient_hum"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.88,
            "style": "vox_highlight_yellow",
            "max_words_per_screen": 5,
            "font_family": "Helvetica Neue Bold",
            "font_size": 40,
            "primary_color": "#FFFFFF",
            "highlight_color": "#CCFF00",
            "outline_color": "#1E293B",
            "shadow_blur": 4,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 4.5,
            "min_shot_duration_sec": 2.5,
            "cut_on_beat": False,
            "cut_every_bars": 2,
            "stagger_frames": 4,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 19,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["paper_tear_stagger", "blink_black_2frames", "smooth_slide_left"],
            "shaders": ["paper_texture_overlay", "subtle_lens_blur_edges", "film_halide_grain_8pct"],
            "background_color": "#243048",
            "anti_blackdetect": True
        },
        "required_capabilities": ["research", "script", "voice_generation", "speech_to_text", "video_generation", "music_generation", "subtitle_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "00_VOX_DOCS",
            "channel_handle": "@VoxExplainerMaster",
            "target_rpm_usd": "$20.00 – $32.00 USD"
        }
    },
    "VIRAL_SHORTS_916": {
        "id": "VIRAL_SHORTS_916",
        "archetype_id": "VIRAL_SHORTS_916",
        "name": "Viral Shorts & High-Retention Hook 9:16",
        "description": "Vídeos verticales de ritmo vertiginoso (1.5s - 2.5s por toma), gancho psicológico demoledor en los primeros 3 segundos, subtítulos karaoke pop-in amarillo neón con safe-zones y SFX de impacto.",
        "category": "vertical_viral_shorts",
        "target_audience": "Usuarios móviles de TikTok, YouTube Shorts e Instagram Reels (consumo rápido, retención > 90%).",
        "tags": ["Shorts", "Viral916", "HighRetention", "TikTok", "Reels", "FastPacing"],
        "prompt_manifest": {
            "layer1_subject": "Gancho visual de alto impacto (revelación inesperada, objeto fascinante, transformación antes/después, pregunta intrigante).",
            "layer2_environment": "Escenario vertical optimizado para pantalla 9:16 con elementos centrados y sin distracciones en los bordes.",
            "layer3_lighting": "Iluminación de alto contraste, ring-light frontal nítida con luces laterales de acento de color saturado.",
            "layer4_optics": "Lente fija 28mm f/1.4 con encuadre vertical estricto, primeros planos extremos con gran detalle de textura.",
            "layer5_motion": "Movimientos continuos de cámara: zoom-in de impacto cada 2 segundos, whip transitions, sacudidas cinemáticas calculadas.",
            "layer6_colorimetry": "Grado de color hiper-saturado y brillante con balance de blancos perfecto y tonos de piel vibrantes.",
            "layer7_render_engine": "ComfyUI Multi-Engine Serverless + FFmpeg 9:16 Vertical Assembly, 60fps.",
            "anti_cgi_negative_lexicon": ["boring static shots", "low contrast", "washed out colors", "unreadable small text", "slow transitions"],
            "custom_tokens": ["#Shorts916", "#TikTokViral", "#RetentionHook", "#KaraokeSubtitles"]
        },
        "camera_optics": {
            "focal_length_mm": 28.0,
            "sensor_profile": "Vertical_Cinema_916_Sensor",
            "aperture_f_stop": 1.4,
            "depth_of_field": "Extreme subject isolation with dynamic pop",
            "motion_type": "Impact Whip Zoom & Dynamic Scale Pulses",
            "stabilization": "Active Dynamic Warp Stabilizer",
            "shutter_angle_deg": 180.0,
            "fov_deg": 75.0,
            "iso_target": 200
        },
        "audio_spec": {
            "bpm": 138,
            "genre": "High-Energy Brazilian Phonk / Hyper-Trap Beat",
            "ducking_db": -18.0,
            "ducking_attack_ms": 15,
            "ducking_release_ms": 180,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-mateo",
            "voice_speed": 1.10,
            "voice_pitch": 0.05,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["whoosh_impact_riser", "sub_boom_drop", "vinyl_scratch_stop", "pop_notification_chime"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.90,
            "style": "viral_tiktok_pop_yellow",
            "max_words_per_screen": 2,
            "font_family": "Komika Axis",
            "font_size": 62,
            "primary_color": "#FFFFFF",
            "highlight_color": "#FFE600",
            "outline_color": "#000000",
            "shadow_blur": 8,
            "safe_zone_bottom_px": 180,
            "max_shot_duration_sec": 2.5,
            "min_shot_duration_sec": 1.2,
            "cut_on_beat": True,
            "cut_every_bars": 1,
            "stagger_frames": 2,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "9:16",
            "resolution_width": 1080,
            "resolution_height": 1920,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["glitch_whip_snap", "zoom_punch_scale", "flash_white_1f"],
            "shaders": ["contrast_punch_lut", "subtle_vignette_bottom", "rgb_split_transient"],
            "background_color": "#243048",
            "anti_blackdetect": True
        },
        "required_capabilities": ["script", "voice_generation", "video_generation", "subtitle_generation", "music_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "00_VIRAL_FACTORY",
            "channel_handle": "@ViralShorts916",
            "target_rpm_usd": "$12.00 – $18.00 USD"
        }
    },
    "DOCUMENTAL_35MM": {
        "id": "DOCUMENTAL_35MM",
        "archetype_id": "DOCUMENTAL_35MM",
        "name": "Documental Histórico 35mm Master (Archival Restoration)",
        "description": "Pipeline de cine documental histórico de máxima calidad. Restauración 4K de archivos reales mediante NanoBanana, recreación IA rigurosa de momentos no fotografiados, etalonaje Kodak 35mm, subtitulado suizo sobrio y mezcla EBU R128 (-14 LUFS, ducking -20dB).",
        "category": "historical_cinema_documentary",
        "target_audience": "Espectadores de documentales de prestigio, canales de historia rigurosa, aficionados al cine clásico y bibliotecas educativas.",
        "tags": ["Documental35mm", "KodakVision3", "HistoricalRestoration", "Archival4K", "NanoBanana", "EBUMaster"],
        "prompt_manifest": {
            "layer1_subject": "Personajes históricos auténticos, acontecimientos documentados, artefactos de museo y planos de época recreados con estricto rigor cronológico.",
            "layer2_environment": "Entornos de los siglos XVIII al XX con fidelidad material absoluta: vestuario de época, arquitectura original y luz de gas o velas.",
            "layer3_lighting": "Iluminación naturalista inspirada en claroscuro de Rembrandt y luz de ventana lateral de Vermeer.",
            "layer4_optics": "Panavision Primo Anamorphic 35mm f/2.0, apertura suave, ligero viñeteado de época y micro-aberración en los bordes de la lente.",
            "layer5_motion": "Movimientos lentos y majestuosos de trípode y dolly sobre raíles, zooms ópticos suaves de aproximación.",
            "layer6_colorimetry": "Emulación fidedigna de negativo analógico Kodak Vision3 5219 500T, tonos sepia cálidos en material pre-1930, grano orgánico de sales de plata.",
            "layer7_render_engine": "NanoBanana 4K Upscaler + FLUX 3 Film Master + FFmpeg Photochemical Filter, 24fps filmic / 60fps broadcast.",
            "anti_cgi_negative_lexicon": ["modern digital sheen", "anachronisms", "oversaturated neon", "plastic 3d model", "synthetic blur"],
            "custom_tokens": ["#Documental35mm", "#KodakVision3", "#Archival4K", "#HistoricalCinema"]
        },
        "camera_optics": {
            "focal_length_mm": 50.0,
            "sensor_profile": "ARRI_Alexa_35_OpenGate_Filmic",
            "aperture_f_stop": 2.0,
            "depth_of_field": "Cinematic portrait falloff with organic bokeh",
            "motion_type": "Slow Studio Dolly Push-in & Panoramic Archival Pan",
            "stabilization": "Heavy Studio Tripod & Track Fluid Head",
            "shutter_angle_deg": 180.0,
            "fov_deg": 46.0,
            "iso_target": 500
        },
        "audio_spec": {
            "bpm": 88,
            "genre": "Neoclassical Orchestral Suite with Live String Quartet & French Horns",
            "ducking_db": -20.0,
            "ducking_attack_ms": 40,
            "ducking_release_ms": 350,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-emilio",
            "voice_speed": 0.95,
            "voice_pitch": -0.02,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["archival_film_projector_click", "vinyl_dust_crackle_soft", "orchestral_room_reverb", "historic_footsteps_cobblestone"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.85,
            "style": "swiss_museum_clean",
            "max_words_per_screen": 6,
            "font_family": "Cinzel / Cormorant Garamond",
            "font_size": 38,
            "primary_color": "#F4F1EA",
            "highlight_color": "#D4AF37",
            "outline_color": "#1E293B",
            "shadow_blur": 3,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 5.0,
            "min_shot_duration_sec": 3.0,
            "cut_on_beat": False,
            "cut_every_bars": 2,
            "stagger_frames": 5,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["slow_cross_dissolve_40f", "film_gate_weave", "dip_to_archival_sepia"],
            "shaders": ["photochemical_film_grain_15pct", "lens_vignette_12pct", "dust_and_scratches_subtle"],
            "background_color": "#243048",
            "anti_blackdetect": True
        },
        "required_capabilities": ["research", "script", "voice_generation", "image_generation", "video_generation", "subtitle_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "00_HISTORICAL_VAULT",
            "channel_handle": "@Documental35mmMaster",
            "target_rpm_usd": "$22.00 – $34.00 USD"
        }
    },
    "NANOVERSE": {
        "id": "NANOVERSE",
        "archetype_id": "NANOVERSE",
        "name": "NanoVerse Cellular & Quantum Macro 4K",
        "description": "Exploración hiper-detallada de biología celular, inmunología molecular y física cuántica con microscopía electrónica SEM 4K, zoom fractal infinito, bioluminiscencia y BSO ambiental envolvente.",
        "category": "cellular_microscopy_science",
        "target_audience": "Estudiantes, científicos, amantes de la divulgación biológica y entusiastas de la animación científica 4K.",
        "tags": ["NanoVerse", "Microscopy4K", "SEM", "CellularWarfare", "QuantumZoom", "BioScience"],
        "prompt_manifest": {
            "layer1_subject": "Linfocitos T atacando células tumorales, virus bacteriófagos aterrizando en membranas lipídicas, hélices de ADN y redes de sinapsis neuronales.",
            "layer2_environment": "Matriz extracelular fluida, citoplasma acuoso translúcido con microvesículas flotantes y gradientes de iones de calcio.",
            "layer3_lighting": "Bioluminiscencia interna en verde esmeralda y cian, iluminación electrónica lateral con scattering volumétrico en fluido biológico.",
            "layer4_optics": "Microscopio Electrónico de Barrido (SEM) con render volumétrico, apertura equivalente f/0.95, micro-profundidad de campo extrema.",
            "layer5_motion": "Zoom continuo infinito exponencial de escala milimétrica a nanométrica (1000x a 1,000,000x), rotación helicoidal 3D alrededor de moléculas.",
            "layer6_colorimetry": "False-color científico estético: turquesas profundos, magenta de marcadores fluorescentes y oro coloidal sobre fondo azul marino profundo.",
            "layer7_render_engine": "ComfyUI Quantum DiT + Volumetric Ray-Marcher + Remotion Deep Zoom, 60fps.",
            "anti_cgi_negative_lexicon": [
                "flat 2d drawings", "pixelated textures", "solid opaque colors",
                "stiff inorganic motion", "hyper-realistic", "octane render",
                "plastic textures", "blurry artifacts"
            ],
            "custom_tokens": ["#NanoVerse", "#SEM4K", "#CellularWarfare", "#QuantumZoom"]
        },
        "camera_optics": {
            "focal_length_mm": 100.0,
            "sensor_profile": "Scanning_Electron_Microscope_4K_Sensor",
            "aperture_f_stop": 0.95,
            "depth_of_field": "Microscopic slice depth with progressive volumetric blur",
            "motion_type": "Infinite Fractal Quantum Zoom & Molecular Orbit",
            "stabilization": "Atomic Precision Piezo-Electric Stabilization",
            "shutter_angle_deg": 180.0,
            "fov_deg": 35.0,
            "iso_target": 100
        },
        "audio_spec": {
            "bpm": 76,
            "genre": "Ambient Space Bio-Acoustic & Sub-bass Drone",
            "ducking_db": -18.0,
            "ducking_attack_ms": 30,
            "ducking_release_ms": 280,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-narrador",
            "voice_speed": 1.0,
            "voice_pitch": 0.0,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["cellular_fluid_squelch", "subatomic_drone_pulse", "membrane_permeability_whoosh", "electrical_synapse_crackle"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.85,
            "style": "scientific_hud_cyan",
            "max_words_per_screen": 4,
            "font_family": "Space Grotesk",
            "font_size": 40,
            "primary_color": "#FFFFFF",
            "highlight_color": "#00F5D4",
            "outline_color": "#0B132B",
            "shadow_blur": 5,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 4.5,
            "min_shot_duration_sec": 2.5,
            "cut_on_beat": False,
            "cut_every_bars": 2,
            "stagger_frames": 3,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["cellular_membrane_morph", "depth_dissolve_gaussian", "zoom_tunnel_blur"],
            "shaders": ["bioluminescence_glow", "chromatic_aberration_radial", "depth_fog_volumetric"],
            "background_color": "#101826",
            "anti_blackdetect": True
        },
        "required_capabilities": ["research", "script", "voice_generation", "video_generation", "music_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "03_NANOVERSE",
            "channel_handle": "@NanoVerseExplore",
            "target_rpm_usd": "$15.50 – $19.00 USD"
        }
    },
    "LIVING_CANVAS": {
        "id": "LIVING_CANVAS",
        "archetype_id": "LIVING_CANVAS",
        "name": "Living Canvas Fine Art 3D Animation",
        "description": "Cuadros clásicos e históricos cobrando vida en 3D (Renacimiento, Barroco, Impresionismo). Segmentación SAM-2 de capas pictóricas, inpainting de fondo, animación sutil de pinceladas y música clásica de cámara.",
        "category": "fine_art_3d_animation",
        "target_audience": "Amantes del arte, visitantes de museos, diseño visual sofisticado y narraciones culturales emotivas.",
        "tags": ["LivingCanvas", "FineArt", "SAM2", "OilPainting3D", "MuseumQuality", "ClassicalPiano"],
        "prompt_manifest": {
            "layer1_subject": "Personajes y elementos icónicos de obras maestras pictóricas (Velázquez, Rembrandt, Van Gogh, Monet, Da Vinci) animados con respiración y micro-gestos.",
            "layer2_environment": "Espacio tridimensional reconstruido a partir del lienzo original, manteniendo la textura visible de la tela y el empaste del óleo.",
            "layer3_lighting": "La iluminación original del cuadro respetada al 100%, con sombras proyectadas en capas Z y reflejos de barniz natural.",
            "layer4_optics": "Óptica Hasselblad Medium Format 80mm f/2.8, nitidez absoluta en detalles de textura con bokeh suave de galería.",
            "layer5_motion": "Cámara flotante en paralaje suave, avance sutil hacia el centro dramático del cuadro y animación fluida de telas y cabello.",
            "layer6_colorimetry": "Paleta de pigmentos originales de época restaurada (Lapis Lazuli, Ocre Oro, Carmín de Alizarina, Blanco de Plomo).",
            "layer7_render_engine": "SAM-2 Depth Layering + FLUX Inpainting + LTX Brushstroke Motion Engine, 60fps.",
            "anti_cgi_negative_lexicon": [
                "modern flat digital vector", "over-smoothed skin", "anime style",
                "unrealistic saturation", "hyper-realistic", "octane render",
                "plastic textures", "blurry artifacts"
            ],
            "custom_tokens": ["#LivingCanvas", "#FineArt3D", "#SAM2Layering", "#Museum4K"]
        },
        "camera_optics": {
            "focal_length_mm": 80.0,
            "sensor_profile": "Hasselblad_Medium_Format_100c",
            "aperture_f_stop": 2.8,
            "depth_of_field": "Fine art portrait depth with textured canvas falloff",
            "motion_type": "Slow Museum Glide & Multi-Layer Canvas Push",
            "stabilization": "Studio Counter-Weighted Jib Arm",
            "shutter_angle_deg": 180.0,
            "fov_deg": 38.0,
            "iso_target": 100
        },
        "audio_spec": {
            "bpm": 80,
            "genre": "Classical Solo Piano & Chamber Cello Suite",
            "ducking_db": -20.0,
            "ducking_attack_ms": 35,
            "ducking_release_ms": 320,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-narrador",
            "voice_speed": 0.98,
            "voice_pitch": 0.0,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["canvas_brushstroke_bristle", "gallery_wood_floor_echo", "museum_hall_ambient_reverb", "gentle_page_turn"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.85,
            "style": "curator_serif_gold",
            "max_words_per_screen": 5,
            "font_family": "Playfair Display / Bodoni",
            "font_size": 40,
            "primary_color": "#FFF8E7",
            "highlight_color": "#E5A93C",
            "outline_color": "#261C14",
            "shadow_blur": 4,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 5.5,
            "min_shot_duration_sec": 3.5,
            "cut_on_beat": False,
            "cut_every_bars": 2,
            "stagger_frames": 4,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["impasto_brush_wipe", "slow_fade_through_canvas", "paralaje_layer_reveal"],
            "shaders": ["oil_painting_relief_bump", "varnish_glaze_specular", "fine_linen_texture"],
            "background_color": "#1C1917",
            "anti_blackdetect": True
        },
        "required_capabilities": ["script", "voice_generation", "image_generation", "video_generation", "music_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "04_LIVING_CANVAS",
            "channel_handle": "@LivingCanvasArt",
            "target_rpm_usd": "$19.00 – $24.00 USD"
        }
    },
    "ASTRODRIFT": {
        "id": "ASTRODRIFT",
        "archetype_id": "ASTRODRIFT",
        "name": "AstroDrift Deep Space Relativistic 4K",
        "description": "Vuelos espaciales relativistas a través de agujeros negros supermasivos con lentes gravitacionales, discos de acreción 4K, nebulosas estelares y cosmología cuántica, acompañado por BSO orquestal épica espacial 70 BPM.",
        "category": "deep_space_astrophysics",
        "target_audience": "Apasionados de la astronomía, física teórica, Interestelar, exploración espacial y viajes cósmicos en 4K.",
        "tags": ["AstroDrift", "BlackHole", "Relativistic", "GravitationalLensing", "Cosmology", "IMAX70mm"],
        "prompt_manifest": {
            "layer1_subject": "Agujero negro supermasivo con disco de acreción incandescente hiper-relativista, jet relativista de plasma y sombra de Schwarzschild.",
            "layer2_environment": "Espacio interestelar profundo, nebulosas de emisión de hidrógeno alfa en tonos magenta y nubes de polvo molecular oscuro.",
            "layer3_lighting": "Resplandor cegador del disco Doppler relativista con corrimiento al azul en el lado aproximante y corrimiento al rojo en el lado recedente.",
            "layer4_optics": "IMAX 70mm Space Camera Optics f/1.4, distorsión gravitacional Ray-Marching 4K y flare anamórfico azul horizontal de 180°.",
            "layer5_motion": "Aproximación orbital relativista a 0.8c alrededor del horizonte de sucesos, efecto de dilatación temporal y curvatura espacial.",
            "layer6_colorimetry": "Negro estelar profundo (#0B0E14), dorados de acreción de plasma, cianes de ionización estelar y púrpuras de radiación sincrotrón.",
            "layer7_render_engine": "General Relativistic Ray-Marching Engine + FLUX 3 Cosmos DiT, 60fps.",
            "anti_cgi_negative_lexicon": [
                "cartoony stars", "simple 2d glow circles", "unrealistic flat accretion disk",
                "lowres noise", "hyper-realistic", "octane render", "plastic textures"
            ],
            "custom_tokens": ["#AstroDrift", "#BlackHole4K", "#GravitationalLensing", "#InterstellarScale"]
        },
        "camera_optics": {
            "focal_length_mm": 24.0,
            "sensor_profile": "IMAX_70mm_Cosmic_Optics",
            "aperture_f_stop": 1.4,
            "depth_of_field": "Cosmic scale infinite depth with optical gravitational warping",
            "motion_type": "Relativistic Orbit & Gravitational Escape Vector",
            "stabilization": "Inertial Gyro-Space Vector Control",
            "shutter_angle_deg": 180.0,
            "fov_deg": 92.0,
            "iso_target": 800
        },
        "audio_spec": {
            "bpm": 70,
            "genre": "Epic Cosmic Ambient Suite with Massive Low-Brass & Cathedral Organ",
            "ducking_db": -18.0,
            "ducking_attack_ms": 30,
            "ducking_release_ms": 300,
            "voice_engine": "vibevoice",
            "voice_preset_id": "es-emilio",
            "voice_speed": 0.96,
            "voice_pitch": -0.04,
            "ebu_r128_target_lufs": -14.0,
            "ebu_r128_true_peak_dbtp": -1.0,
            "sub_80hz_mono": True,
            "foley_presets": ["deep_space_sub_rumble_30hz", "pulsar_radio_signal_rhythm", "gravitational_distortion_whoosh", "cockpit_pressurization_hum"]
        },
        "subtitles_pacing": {
            "alignment_engine": "forced_levenshtein",
            "min_levenshtein_similarity": 0.85,
            "style": "cosmic_telemetry_hud",
            "max_words_per_screen": 4,
            "font_family": "Orbitron / Montserrat",
            "font_size": 42,
            "primary_color": "#FFFFFF",
            "highlight_color": "#38BDF8",
            "outline_color": "#0B0E14",
            "shadow_blur": 6,
            "safe_zone_bottom_px": 80,
            "max_shot_duration_sec": 5.0,
            "min_shot_duration_sec": 3.0,
            "cut_on_beat": True,
            "cut_every_bars": 2,
            "stagger_frames": 4,
            "ken_burns_zoompan": True
        },
        "render_config": {
            "aspect_ratio": "16:9",
            "resolution_width": 3840,
            "resolution_height": 2160,
            "fps": 60,
            "codec": "libx264",
            "crf": 18,
            "preset": "slow",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
            "transitions": ["gravitational_lens_warp", "cosmic_fade_to_nebula", "starlight_streak_dissolve"]
            ,
            "shaders": ["general_relativistic_lensing_glsl", "doppler_beaming_color_shift", "anamorphic_blue_streak_flare"],
            "background_color": "#0B0E14",
            "anti_blackdetect": True
        },
        "required_capabilities": ["research", "script", "voice_generation", "video_generation", "music_generation", "rendering", "storage"],
        "metadata": {
            "canonical_channel": "05_ASTRODRIFT",
            "channel_handle": "@AstroDriftCosmos",
            "target_rpm_usd": "$26.00 – $35.00 USD"
        }
    }
}

# Mapa de Alias para resolver nombres alternativos a los 8 IDs Canónicos
ARCHETYPE_ALIASES: Dict[str, str] = {
    # 1. ChronoDrift
    "CHRONODRIFT": "CHRONODRIFT_6DOF",
    "CHRONODRIFT_6DOF": "CHRONODRIFT_6DOF",
    "CHRONODRIFT_TRITEMPORAL": "CHRONODRIFT_6DOF",
    "01_CHRONODRIFT": "CHRONODRIFT_6DOF",
    
    # 2. FPV Urban
    "FPV_URBAN": "FPV_URBAN",
    "FPV_URBAN_REAL_FLOW": "FPV_URBAN",
    "FPV_URBAN_STORYTELLING": "FPV_URBAN",
    "CITY_ROUTES_BEATS": "FPV_URBAN",
    "02_FPV_URBAN": "FPV_URBAN",
    
    # 3. Vox Explainer
    "VOX_EXPLAINER": "VOX_EXPLAINER",
    "VOX_INVESTIGATIVE_DOC": "VOX_EXPLAINER",
    "DEEP_EXPLAINER_ESSAY": "VOX_EXPLAINER",
    "VOX_DOC": "VOX_EXPLAINER",
    
    # 4. Viral Shorts 9:16
    "VIRAL_SHORTS_916": "VIRAL_SHORTS_916",
    "VIRAL_SHORTS_HOOK": "VIRAL_SHORTS_916",
    "VIRAL_SHORTS": "VIRAL_SHORTS_916",
    "SHORTS_VERTICAL": "VIRAL_SHORTS_916",
    "TIKTOK_REELS_916": "VIRAL_SHORTS_916",
    
    # 5. Documental 35mm
    "DOCUMENTAL_35MM": "DOCUMENTAL_35MM",
    "DOCUMENTARY_MASTER": "DOCUMENTAL_35MM",
    "HISTORICAL_SCRAPING": "DOCUMENTAL_35MM",
    "MADRID_CURIOSITIES_REAL_FLOW": "DOCUMENTAL_35MM",
    "35MM_DOC": "DOCUMENTAL_35MM",
    
    # 6. NanoVerse
    "NANOVERSE": "NANOVERSE",
    "NANOVERSE_MACRO": "NANOVERSE",
    "03_NANOVERSE": "NANOVERSE",
    "QUANTUM_ZOOM": "NANOVERSE",
    
    # 7. Living Canvas
    "LIVING_CANVAS": "LIVING_CANVAS",
    "LIVING_CANVAS_ART": "LIVING_CANVAS",
    "04_LIVING_CANVAS": "LIVING_CANVAS",
    "PIXAR_3D_ANIMATION": "LIVING_CANVAS",
    "PIXAR_3D": "LIVING_CANVAS",
    
    # 8. AstroDrift
    "ASTRODRIFT": "ASTRODRIFT",
    "ASTRODRIFT_DEEP_SPACE": "ASTRODRIFT",
    "05_ASTRODRIFT": "ASTRODRIFT",
    "RELATIVISTIC_SPACE": "ASTRODRIFT"
}


# ============================================================================
# 3. CLASE PRINCIPAL: WorkflowRegistry
# ============================================================================

class WorkflowRegistry:
    """
    Gestor Central de Persistencia, Versionado Criptográfico SHA-256 y Registro
    de Workflows por Tipo de Vídeo en VideoPro Studio.
    """

    def __init__(
        self,
        storage_dir: Optional[Union[str, Path]] = None,
        workflows_dir: Optional[Union[str, Path]] = None
    ):
        self.base_dir = BASE_DIR
        self.storage_dir = Path(storage_dir) if storage_dir else self.base_dir / "storage"
        self.workflows_dir = Path(workflows_dir) if workflows_dir else self.storage_dir / "workflows"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        self.catalog_json_file = self.workflows_dir / "workflow_catalog.json"
        self.catalog_yaml_file = self.workflows_dir / "workflow_catalog.yaml"

        # Memoria en ejecución de workflows cargados {archetype_id: {semver: StructuredWorkflow}}
        self._registry: Dict[str, Dict[str, StructuredWorkflow]] = {}
        self._latest_pointers: Dict[str, str] = {}

        self.reload_from_storage()

    # ------------------------------------------------------------------------
    # 3.1 GESTIÓN DE ARQUETIPOS Y ALIAS
    # ------------------------------------------------------------------------
    @classmethod
    def get_canonical_archetypes(cls) -> List[str]:
        """Retorna la lista ordenada de los 8 arquetipos canónicos."""
        return list(CANONICAL_ARCHETYPES_DEFS.keys())

    @classmethod
    def resolve_archetype_id(cls, name_or_alias: str) -> str:
        """Resuelve cualquier variante o alias al ID Canónico correspondiente."""
        clean = str(name_or_alias or "").strip().upper()
        if clean in ARCHETYPE_ALIASES:
            return ARCHETYPE_ALIASES[clean]
        for alias_key, canon_id in ARCHETYPE_ALIASES.items():
            if alias_key in clean or clean in alias_key:
                return canon_id
        return "DOCUMENTAL_35MM"  # Fallback canónico seguro

    # ------------------------------------------------------------------------
    # 3.2 HASHING CRIPTOGRÁFICO DETERMINISTA SHA-256
    # ------------------------------------------------------------------------
    @classmethod
    def compute_workflow_hash(cls, workflow_dict: Dict[str, Any]) -> str:
        """
        Calcula el hash criptográfico SHA-256 determinista del contenido sustancial del workflow.
        Excluye metadatos volátiles como `sha256_hash`, `updated_at` y `created_at`.
        """
        # Crear copia superficial para sanitizar
        clean_copy = json.loads(json.dumps(workflow_dict, default=str))

        if "version_info" in clean_copy and isinstance(clean_copy["version_info"], dict):
            clean_copy["version_info"].pop("sha256_hash", None)
            clean_copy["version_info"].pop("updated_at", None)
            clean_copy["version_info"].pop("created_at", None)

        # Serialización canónica con orden estricto de claves
        canonical_json_bytes = json.dumps(clean_copy, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(canonical_json_bytes).hexdigest()

    # ------------------------------------------------------------------------
    # 3.3 CREACIÓN Y SELLADO DE WORKFLOWS
    # ------------------------------------------------------------------------
    def create_canonical_workflow(
        self,
        archetype_id: str,
        semver: str = "v1.0.0",
        version_int: int = 1,
        author: str = "VideoPro Core Studio",
        changelog: str = "Creación de workflow canónico inicial"
    ) -> StructuredWorkflow:
        """Construye e inicializa un StructuredWorkflow a partir de las definiciones maestras."""
        canon_id = self.resolve_archetype_id(archetype_id)
        raw_def = CANONICAL_ARCHETYPES_DEFS.get(canon_id)
        if not raw_def:
            raise ValueError(f"No existe definición canónica para '{canon_id}'")

        wf_data = json.loads(json.dumps(raw_def))
        
        # Inyectar versión inicial
        wf_data["version_info"] = {
            "semver": semver,
            "version_int": version_int,
            "sha256_hash": "",
            "author": author,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "changelog": changelog,
            "parent_hash": None,
            "tags": wf_data.get("tags", [])
        }

        # Instanciar modelo Pydantic y sellar hash sobre model_dump determinista
        wf = StructuredWorkflow(**wf_data)
        wf_dict = wf.model_dump() if hasattr(wf, "model_dump") else wf.dict()
        h = self.compute_workflow_hash(wf_dict)
        wf.version_info.sha256_hash = h
        return wf

    def register_workflow(
        self,
        workflow: StructuredWorkflow,
        auto_save: bool = True,
        formats: List[str] = ["json", "yaml"]
    ) -> StructuredWorkflow:
        """
        Registra un workflow en memoria, sella su hash SHA-256 y opcionalmente lo persiste en disco.
        """
        canon_id = workflow.archetype_id
        semver = workflow.version_info.semver

        # Asegurar hash correcto
        wf_dict = workflow.model_dump() if hasattr(workflow, "model_dump") else workflow.dict()
        calculated_hash = self.compute_workflow_hash(wf_dict)
        workflow.version_info.sha256_hash = calculated_hash
        workflow.version_info.updated_at = datetime.now().isoformat()

        if canon_id not in self._registry:
            self._registry[canon_id] = {}

        self._registry[canon_id][semver] = workflow
        self._latest_pointers[canon_id] = semver

        if auto_save:
            self.save_workflow_to_disk(workflow, formats=formats)
            self._update_catalog_manifest()

        logger.info(f"✅ Workflow '{canon_id}' {semver} registrado con éxito [SHA-256: {calculated_hash[:12]}...]")
        return workflow

    # ------------------------------------------------------------------------
    # 3.4 PERSISTENCIA EN DISCO (JSON & YAML)
    # ------------------------------------------------------------------------
    def save_workflow_to_disk(
        self,
        workflow: StructuredWorkflow,
        formats: List[str] = ["json", "yaml"]
    ) -> Dict[str, Path]:
        """
        Guarda el workflow en disco con formato dual (JSON / YAML) y actualiza el puntero `latest`.
        """
        canon_id = workflow.archetype_id
        semver = workflow.version_info.semver
        data = workflow.model_dump() if hasattr(workflow, "model_dump") else workflow.dict()

        saved_files = {}

        # 1. Guardar JSON Versionado y Latest
        if "json" in formats:
            ver_json_path = self.workflows_dir / f"{canon_id}_{semver}.json"
            latest_json_path = self.workflows_dir / f"{canon_id}_latest.json"
            
            with open(ver_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            with open(latest_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            saved_files["json_versioned"] = ver_json_path
            saved_files["json_latest"] = latest_json_path

        # 2. Guardar YAML Versionado y Latest
        if "yaml" in formats or "yml" in formats:
            ver_yaml_path = self.workflows_dir / f"{canon_id}_{semver}.yaml"
            latest_yaml_path = self.workflows_dir / f"{canon_id}_latest.yaml"
            
            with open(ver_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, sort_keys=False, allow_unicode=True, indent=2)
            with open(latest_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, sort_keys=False, allow_unicode=True, indent=2)

            saved_files["yaml_versioned"] = ver_yaml_path
            saved_files["yaml_latest"] = latest_yaml_path

        return saved_files

    def load_workflow_from_disk(self, file_path: Union[str, Path]) -> StructuredWorkflow:
        """Carga e inicializa un StructuredWorkflow a partir de un archivo JSON o YAML."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo de workflow no encontrado: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix.lower() in [".yaml", ".yml"]:
                raw_data = yaml.safe_load(f)
            else:
                raw_data = json.load(f)

        # Adaptar si proviene de formato legacy
        if "prompt_manifest" not in raw_data and "pipeline_graph" in raw_data:
            wf = self._convert_legacy_to_structured(raw_data)
        else:
            wf = StructuredWorkflow(**raw_data)

        # Verificar integridad
        valid, msg = self.verify_workflow_integrity(wf)
        if not valid:
            logger.warning(f"Aviso de integridad en '{path.name}': {msg}")

        return wf

    def reload_from_storage(self) -> int:
        """Escanea `storage/workflows/` y recarga todos los workflows versionados válidos."""
        loaded_count = 0
        if not self.workflows_dir.exists():
            return 0

        # Buscar todos los JSON versionados
        for f in self.workflows_dir.glob("*_v*.json"):
            if f.name == "workflow_catalog.json":
                continue
            try:
                wf = self.load_workflow_from_disk(f)
                canon_id = wf.archetype_id
                semver = wf.version_info.semver

                if canon_id not in self._registry:
                    self._registry[canon_id] = {}
                self._registry[canon_id][semver] = wf
                
                # Actualizar latest si es mayor
                current_latest = self._latest_pointers.get(canon_id)
                if not current_latest or self._compare_semver(semver, current_latest) > 0:
                    self._latest_pointers[canon_id] = semver

                loaded_count += 1
            except Exception as ex:
                logger.debug(f"Omitiendo archivo no conforme {f.name}: {ex}")

        return loaded_count

    # ------------------------------------------------------------------------
    # 3.5 CONSULTAS, BÚSQUEDAS Y VERSIONADO (BUMP & ROLLBACK)
    # ------------------------------------------------------------------------
    def get_workflow(
        self,
        archetype_id: str,
        version: Optional[str] = None
    ) -> Optional[StructuredWorkflow]:
        """
        Obtiene el workflow solicitado. Si no se especifica versión, retorna la más reciente.
        """
        canon_id = self.resolve_archetype_id(archetype_id)
        versions_map = self._registry.get(canon_id, {})

        if not versions_map:
            # Intentar cargar desde canonical default
            if canon_id in CANONICAL_ARCHETYPES_DEFS:
                wf = self.create_canonical_workflow(canon_id)
                self.register_workflow(wf, auto_save=True)
                return wf
            return None

        if version:
            v_key = version if version.startswith("v") else f"v{version}"
            return versions_map.get(v_key)

        latest_v = self._latest_pointers.get(canon_id)
        if latest_v and latest_v in versions_map:
            return versions_map[latest_v]

        # Si no hay puntero, buscar el semver más alto
        sorted_vers = sorted(versions_map.keys(), key=self._semver_sort_key)
        return versions_map[sorted_vers[-1]] if sorted_vers else None

    def get_latest_version(self, archetype_id: str) -> str:
        """Retorna la etiqueta SemVer de la última versión de un arquetipo."""
        wf = self.get_workflow(archetype_id)
        return wf.version_info.semver if wf else "v1.0.0"

    def list_workflows(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista los workflows registrados con sus metadatos y versiones disponibles."""
        result = []
        for canon_id in self.get_canonical_archetypes():
            wf = self.get_workflow(canon_id)
            if not wf:
                wf = self.create_canonical_workflow(canon_id)
                self.register_workflow(wf, auto_save=True)

            if category and wf.category.lower() != category.lower():
                continue

            available_versions = sorted(list(self._registry.get(canon_id, {}).keys()), key=self._semver_sort_key)
            result.append({
                "archetype_id": wf.archetype_id,
                "name": wf.name,
                "category": wf.category,
                "latest_version": wf.version_info.semver,
                "all_versions": available_versions if available_versions else [wf.version_info.semver],
                "sha256_hash": wf.version_info.sha256_hash,
                "audio_bpm": wf.audio_spec.bpm,
                "ducking_db": wf.audio_spec.ducking_db,
                "aspect_ratio": wf.render_config.aspect_ratio,
                "fps": wf.render_config.fps,
                "updated_at": wf.version_info.updated_at
            })
        return result

    def list_versions(self, archetype_id: str) -> List[WorkflowVersionInfo]:
        """Retorna el historial completo de versiones de un arquetipo."""
        canon_id = self.resolve_archetype_id(archetype_id)
        versions_map = self._registry.get(canon_id, {})
        sorted_keys = sorted(versions_map.keys(), key=self._semver_sort_key)
        return [versions_map[k].version_info for k in sorted_keys]

    def create_version(
        self,
        archetype_id: str,
        patch_data: Dict[str, Any],
        bump_type: str = "patch",
        author: str = "Hermes Agent Auto-Learner",
        changelog: str = "Optimización automática de parámetros"
    ) -> StructuredWorkflow:
        """
        Crea una nueva versión semántica (patch, minor, major) aplicando parches sobre la actual.
        """
        canon_id = self.resolve_archetype_id(archetype_id)
        current_wf = self.get_workflow(canon_id)
        if not current_wf:
            current_wf = self.create_canonical_workflow(canon_id)

        cur_semver = current_wf.version_info.semver
        cur_int = current_wf.version_info.version_int
        new_semver = self._bump_semver(cur_semver, bump_type)
        new_int = cur_int + 1
        parent_hash = current_wf.version_info.sha256_hash

        # Aplicar parches profundos sobre la estructura del workflow
        wf_dict = current_wf.model_dump() if hasattr(current_wf, "model_dump") else current_wf.dict()
        self._apply_deep_patch(wf_dict, patch_data)

        # Actualizar metadatos de versión
        wf_dict["version_info"] = {
            "semver": new_semver,
            "version_int": new_int,
            "sha256_hash": "",
            "author": author,
            "created_at": current_wf.version_info.created_at,
            "updated_at": datetime.now().isoformat(),
            "changelog": changelog,
            "parent_hash": parent_hash,
            "tags": wf_dict.get("tags", [])
        }

        # Sellar nuevo SHA-256
        new_hash = self.compute_workflow_hash(wf_dict)
        wf_dict["version_info"]["sha256_hash"] = new_hash

        new_wf = StructuredWorkflow(**wf_dict)
        self.register_workflow(new_wf, auto_save=True)

        logger.info(f"🚀 Creada versión {new_semver} para '{canon_id}' [Parent: {parent_hash[:8]} -> New: {new_hash[:8]}]")
        return new_wf

    def rollback_to_version(self, archetype_id: str, target_version: str) -> StructuredWorkflow:
        """Revierte la versión activa de un arquetipo a una versión previa existente."""
        canon_id = self.resolve_archetype_id(archetype_id)
        t_key = target_version if target_version.startswith("v") else f"v{target_version}"

        versions_map = self._registry.get(canon_id, {})
        if t_key not in versions_map:
            raise ValueError(f"La versión '{t_key}' no existe para el arquetipo '{canon_id}'")

        target_wf = versions_map[t_key]
        self._latest_pointers[canon_id] = t_key

        # Re-guardar archivos latest con la versión revertida
        self.save_workflow_to_disk(target_wf, formats=["json", "yaml"])
        self._update_catalog_manifest()

        logger.info(f"⏪ Rollback ejecutado: '{canon_id}' apuntando ahora a versión {t_key}")
        return target_wf

    def diff_versions(self, archetype_id: str, v1: str, v2: str) -> Dict[str, Any]:
        """Calcula el diff estructural entre dos versiones de un mismo arquetipo."""
        canon_id = self.resolve_archetype_id(archetype_id)
        wf1 = self.get_workflow(canon_id, version=v1)
        wf2 = self.get_workflow(canon_id, version=v2)

        if not wf1 or not wf2:
            raise ValueError(f"No se pudieron encontrar ambas versiones ({v1}, {v2}) para '{canon_id}'")

        d1 = wf1.model_dump() if hasattr(wf1, "model_dump") else wf1.dict()
        d2 = wf2.model_dump() if hasattr(wf2, "model_dump") else wf2.dict()

        diffs = self._compute_dict_diff(d1, d2)
        return {
            "archetype_id": canon_id,
            "v1": wf1.version_info.semver,
            "v1_hash": wf1.version_info.sha256_hash,
            "v2": wf2.version_info.semver,
            "v2_hash": wf2.version_info.sha256_hash,
            "total_differences": len(diffs),
            "differences": diffs
        }

    # ------------------------------------------------------------------------
    # 3.6 INTEGRIDAD Y AUDITORÍA CONTRA LAS 10 REGLAS DE ORO
    # ------------------------------------------------------------------------
    def verify_workflow_integrity(self, workflow: StructuredWorkflow) -> Tuple[bool, str]:
        """Comprueba que el hash SHA-256 almacenado coincida exactamente con el cálculo en vivo."""
        stored_hash = workflow.version_info.sha256_hash
        wf_dict = workflow.model_dump() if hasattr(workflow, "model_dump") else workflow.dict()
        live_hash = self.compute_workflow_hash(wf_dict)

        if not stored_hash:
            return False, "Falta el hash SHA-256 en version_info"
        if stored_hash != live_hash:
            return False, f"Hash SHA-256 corrupto o alterado (Almacenado: {stored_hash[:12]} != Calculado: {live_hash[:12]})"
        return True, "Integridad SHA-256 verificada al 100%"

    def verify_all_storage_integrity(self) -> Dict[str, Any]:
        """Verifica la integridad de todos los workflows almacenados en disco."""
        report = {"total_checked": 0, "passed": 0, "failed": 0, "details": []}
        for canon_id in self.get_canonical_archetypes():
            versions_map = self._registry.get(canon_id, {})
            for semver, wf in versions_map.items():
                report["total_checked"] += 1
                valid, msg = self.verify_workflow_integrity(wf)
                if valid:
                    report["passed"] += 1
                else:
                    report["failed"] += 1
                report["details"].append({
                    "archetype_id": canon_id,
                    "version": semver,
                    "sha256": wf.version_info.sha256_hash,
                    "valid": valid,
                    "message": msg
                })
        return report

    def validate_against_golden_rules(self, workflow: StructuredWorkflow) -> Dict[str, Any]:
        """
        Evalúa el cumplimiento de las 10 Reglas de Oro en la especificación del workflow.
        """
        violations = []
        scores = {}

        # R01: Audio-First Lifecycle & Timestamps
        if not workflow.audio_spec.voice_preset_id or workflow.audio_spec.bpm <= 0:
            violations.append({"rule": "R01_AUDIO_FIRST_LIFECYCLE", "penalty": 15, "msg": "Audio spec incompleta o BPM no configurado."})

        # R02: Strict >5KB Gate
        if not workflow.policies.get("strict_5kb_gate", False):
            violations.append({"rule": "R02_STRICT_5KB_GATE", "penalty": 20, "msg": "Política strict_5kb_gate no está habilitada."})

        # R03: Levenshtein Subtitle Alignment
        if workflow.subtitles_pacing.min_levenshtein_similarity < 0.85:
            violations.append({"rule": "R03_LEVENSHTEIN_CAPTIONS", "penalty": 12, "msg": "Umbral Levenshtein inferior a 0.85."})

        # R04: Rhythm Pacing (Cortes 2-3s o 3-5s)
        if workflow.subtitles_pacing.max_shot_duration_sec > 5.5:
            violations.append({"rule": "R04_RHYTHM_3_5S_CUT", "penalty": 15, "msg": f"Duración máxima de toma excesiva ({workflow.subtitles_pacing.max_shot_duration_sec}s > 5.5s)."})

        # R05: Anti-Blackdetect Palette
        bg = str(workflow.render_config.background_color).lower()
        if bg in ["#000000", "black", "rgb(0,0,0)"] or not workflow.render_config.anti_blackdetect:
            violations.append({"rule": "R05_ANTI_BLACKDETECT", "penalty": 15, "msg": f"Fondo negro digital puro '{bg}' prohibido. Usar #243048 o #101826."})

        # R06: DoP 7-Layer Prompts & Anti-CGI Lexicon
        if len(workflow.prompt_manifest.anti_cgi_negative_lexicon) < 5:
            violations.append({"rule": "R06_DOP_7LAYER_PROMPT", "penalty": 10, "msg": "Léxico Anti-CGI incompleto en manifiesto 7D."})

        # R07: EBU R128 Audio Mastering & Ducking <= -18dB
        if workflow.audio_spec.ducking_db > -18.0 or workflow.audio_spec.ebu_r128_target_lufs > -13.0:
            violations.append({"rule": "R07_EBU_R128_MASTERING", "penalty": 15, "msg": f"Ducking insuficiente ({workflow.audio_spec.ducking_db}dB > -18dB) o LUFS incorrecto."})

        # R08: Thumbnail Safe Zone
        if workflow.subtitles_pacing.safe_zone_bottom_px < 60:
            violations.append({"rule": "R08_THUMBNAIL_SAFE_ZONE", "penalty": 10, "msg": "Margen de safe zone inferior a 60px."})

        # R09: Dual Persistence & SHA-256 Traceability
        if not workflow.version_info.sha256_hash:
            violations.append({"rule": "R09_DUAL_PERSISTENCE", "penalty": 10, "msg": "Falta hash SHA-256 de trazabilidad."})

        # R10: Institutional Scraping
        # Validado en runtime, no penaliza directamente el workflow estático

        penalties = sum(v["penalty"] for v in violations)
        total_score = max(0.0, round(100.0 - penalties, 2))
        passed = total_score >= 85.0 and len([v for v in violations if v["penalty"] >= 15]) == 0

        return {
            "archetype_id": workflow.archetype_id,
            "version": workflow.version_info.semver,
            "score": total_score,
            "passed": passed,
            "violations_count": len(violations),
            "violations": violations
        }

    # ------------------------------------------------------------------------
    # 3.7 EXPORTACIÓN, IMPORTACIÓN E INICIALIZACIÓN CANÓNICA
    # ------------------------------------------------------------------------
    def init_all_canonical_workflows(self, force: bool = False) -> Dict[str, StructuredWorkflow]:
        """
        Inicializa, sella con SHA-256 y persiste los 8 Arquetipos Canónicos en JSON y YAML.
        """
        initialized = {}
        for canon_id in self.get_canonical_archetypes():
            existing = self.get_workflow(canon_id)
            if existing and not force:
                initialized[canon_id] = existing
                continue

            wf = self.create_canonical_workflow(
                archetype_id=canon_id,
                semver="v1.0.0",
                version_int=1,
                author="VideoPro Core Studio",
                changelog="Versión 1.0.0 Canónica Inicial sellada con SHA-256"
            )
            self.register_workflow(wf, auto_save=True, formats=["json", "yaml"])
            initialized[canon_id] = wf

        self._update_catalog_manifest()
        logger.info(f"✨ Inicializados con éxito los {len(initialized)} Arquetipos Canónicos en {self.workflows_dir}")
        return initialized

    def export_workflow(
        self,
        archetype_id: str,
        format: str = "json",
        version: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """Exporta un workflow a una cadena o archivo en disco en formato JSON o YAML."""
        wf = self.get_workflow(archetype_id, version=version)
        if not wf:
            raise ValueError(f"Workflow '{archetype_id}' no encontrado.")

        data = wf.model_dump() if hasattr(wf, "model_dump") else wf.dict()

        if format.lower() in ["yaml", "yml"]:
            content = yaml.dump(data, sort_keys=False, allow_unicode=True, indent=2)
        else:
            content = json.dumps(data, indent=2, ensure_ascii=False)

        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Exportado workflow '{archetype_id}' {wf.version_info.semver} a {p}")

        return content

    def import_workflow(self, file_path: Union[str, Path]) -> StructuredWorkflow:
        """Importa y registra un workflow desde cualquier archivo JSON o YAML externo."""
        wf = self.load_workflow_from_disk(file_path)
        self.register_workflow(wf, auto_save=True)
        return wf

    # ------------------------------------------------------------------------
    # 3.8 MÉTODOS PRIVADOS AUXILIARES
    # ------------------------------------------------------------------------
    def _update_catalog_manifest(self):
        """Genera y actualiza los archivos `workflow_catalog.json` y `workflow_catalog.yaml`."""
        catalog_entries = []
        for canon_id in self.get_canonical_archetypes():
            wf = self.get_workflow(canon_id)
            if wf:
                versions = sorted(list(self._registry.get(canon_id, {}).keys()), key=self._semver_sort_key)
                catalog_entries.append({
                    "archetype_id": wf.archetype_id,
                    "name": wf.name,
                    "description": wf.description,
                    "category": wf.category,
                    "target_audience": wf.target_audience,
                    "latest_version": wf.version_info.semver,
                    "available_versions": versions if versions else [wf.version_info.semver],
                    "sha256_hash": wf.version_info.sha256_hash,
                    "audio": {
                        "bpm": wf.audio_spec.bpm,
                        "genre": wf.audio_spec.genre,
                        "ducking_db": wf.audio_spec.ducking_db,
                        "voice_preset": wf.audio_spec.voice_preset_id
                    },
                    "pacing": {
                        "max_shot_sec": wf.subtitles_pacing.max_shot_duration_sec,
                        "min_levenshtein": wf.subtitles_pacing.min_levenshtein_similarity,
                        "subtitle_style": wf.subtitles_pacing.style
                    },
                    "render": {
                        "aspect_ratio": wf.render_config.aspect_ratio,
                        "resolution": f"{wf.render_config.resolution_width}x{wf.render_config.resolution_height}",
                        "fps": wf.render_config.fps,
                        "background_color": wf.render_config.background_color
                    },
                    "tags": wf.tags,
                    "updated_at": wf.version_info.updated_at
                })

        manifest = {
            "schema_version": "1.0.0",
            "total_canonical_archetypes": len(catalog_entries),
            "generated_at": datetime.now().isoformat(),
            "archetypes": catalog_entries
        }

        with open(self.catalog_json_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        with open(self.catalog_yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, sort_keys=False, allow_unicode=True, indent=2)

    def _bump_semver(self, semver_str: str, bump_type: str) -> str:
        """Incrementa una versión semántica (vX.Y.Z)."""
        m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)(.*)$", semver_str)
        if not m:
            return "v1.1.0"
        major, minor, patch, suffix = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        
        b = bump_type.lower()
        if b == "major":
            major += 1
            minor = 0
            patch = 0
        elif b == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        return f"v{major}.{minor}.{patch}"

    def _semver_sort_key(self, v_str: str) -> Tuple[int, int, int]:
        """Clave de ordenación para strings SemVer."""
        m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", v_str)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return (0, 0, 0)

    def _compare_semver(self, v1: str, v2: str) -> int:
        """Compara dos versiones SemVer: retorna >0 si v1 > v2, 0 si iguales, <0 si v1 < v2."""
        k1 = self._semver_sort_key(v1)
        k2 = self._semver_sort_key(v2)
        if k1 > k2:
            return 1
        elif k1 < k2:
            return -1
        return 0

    def _apply_deep_patch(self, target: dict, patch: dict):
        """Aplica modificaciones anidadas de forma recursiva sobre el diccionario del workflow."""
        for k, val in patch.items():
            if isinstance(val, dict) and k in target and isinstance(target[k], dict):
                self._apply_deep_patch(target[k], val)
            else:
                target[k] = val

    def _compute_dict_diff(self, d1: dict, d2: dict, prefix: str = "") -> List[Dict[str, Any]]:
        """Calcula las diferencias clave a clave entre dos diccionarios estructurados."""
        diffs = []
        all_keys = set(d1.keys()).union(set(d2.keys()))

        # Ignorar timestamps, hashes y metadatos de versión en la comparación de diferencias
        ignore_keys = {"sha256_hash", "updated_at", "created_at", "version_info"}

        for k in sorted(all_keys):
            if k in ignore_keys:
                continue
            path = f"{prefix}.{k}" if prefix else k
            v1 = d1.get(k)
            v2 = d2.get(k)

            if isinstance(v1, dict) and isinstance(v2, dict):
                diffs.extend(self._compute_dict_diff(v1, v2, prefix=path))
            elif v1 != v2:
                diffs.append({
                    "field": path,
                    "before": v1,
                    "after": v2
                })
        return diffs

    def _convert_legacy_to_structured(self, legacy_data: dict) -> StructuredWorkflow:
        """Convierte una definición legacy de WorkflowDefinition a StructuredWorkflow."""
        arch_id = self.resolve_archetype_id(legacy_data.get("archetype_id", legacy_data.get("id", "")))
        base_wf = self.create_canonical_workflow(arch_id)
        base_dict = base_wf.model_dump() if hasattr(base_wf, "model_dump") else base_wf.dict()

        if "name" in legacy_data:
            base_dict["name"] = legacy_data["name"]
        if "description" in legacy_data:
            base_dict["description"] = legacy_data["description"]
        if "nodes" in legacy_data:
            base_dict["pipeline_nodes"] = legacy_data["nodes"]
        if "connections" in legacy_data:
            base_dict["pipeline_connections"] = legacy_data["connections"]

        base_dict["version_info"]["changelog"] = f"Migrado desde workflow legacy {legacy_data.get('id')}"
        base_dict["version_info"]["sha256_hash"] = self.compute_workflow_hash(base_dict)
        return StructuredWorkflow(**base_dict)


# Instancia singleton predeterminada
workflow_registry = WorkflowRegistry()


# ============================================================================
# 4. INTERFAZ DE LÍNEA DE COMANDOS (CLI)
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Registro Persistente y Versionado de Workflows por Tipo de Vídeo — VideoPro Studio"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # init-canonical
    subparsers.add_parser("init-canonical", help="Inicializa y guarda en disco los 8 Arquetipos Canónicos en JSON y YAML")

    # list
    sub_list = subparsers.add_parser("list", help="Lista los workflows registrados y sus versiones")
    sub_list.add_argument("--category", type=str, help="Filtrar por categoría")

    # get
    sub_get = subparsers.add_parser("get", help="Obtiene la especificación completa de un workflow")
    sub_get.add_argument("archetype_id", type=str, help="ID o alias del arquetipo")
    sub_get.add_argument("--version", type=str, default=None, help="Versión SemVer específica (ej: v1.0.0)")
    sub_get.add_argument("--yaml", action="store_true", help="Mostrar salida en YAML en lugar de JSON")

    # verify
    subparsers.add_parser("verify", help="Verifica la integridad criptográfica SHA-256 de todos los workflows")

    # validate
    sub_val = subparsers.add_parser("validate", help="Valida un workflow contra las 10 Reglas de Oro")
    sub_val.add_argument("archetype_id", type=str, help="ID o alias del arquetipo")
    sub_val.add_argument("--version", type=str, default=None, help="Versión a evaluar")

    # bump
    sub_bump = subparsers.add_parser("bump", help="Genera una nueva versión de workflow con parche de parámetros")
    sub_bump.add_argument("archetype_id", type=str, help="ID o alias del arquetipo")
    sub_bump.add_argument("--type", choices=["patch", "minor", "major"], default="patch", help="Tipo de incremento")
    sub_bump.add_argument("--ducking", type=float, default=None, help="Nuevo nivel de ducking en dB")
    sub_bump.add_argument("--bpm", type=int, default=None, help="Nuevo BPM de audio")
    sub_bump.add_argument("--changelog", type=str, default="Ajuste manual de parámetros", help="Descripción del cambio")

    # diff
    sub_diff = subparsers.add_parser("diff", help="Compara dos versiones de un workflow")
    sub_diff.add_argument("archetype_id", type=str, help="ID o alias del arquetipo")
    sub_diff.add_argument("--v1", type=str, required=True, help="Versión base (ej: v1.0.0)")
    sub_diff.add_argument("--v2", type=str, required=True, help="Versión comparada (ej: v1.1.0)")

    # export
    sub_exp = subparsers.add_parser("export", help="Exporta un workflow a archivo o consola")
    sub_exp.add_argument("archetype_id", type=str, help="ID o alias del arquetipo")
    sub_exp.add_argument("--format", choices=["json", "yaml"], default="json", help="Formato de exportación")
    sub_exp.add_argument("--version", type=str, default=None, help="Versión SemVer a exportar")
    sub_exp.add_argument("--out", type=str, default=None, help="Ruta de archivo destino")

    args = parser.parse_args()
    reg = WorkflowRegistry()

    if args.command == "init-canonical":
        results = reg.init_all_canonical_workflows(force=True)
        print(f"\n✨ {len(results)} Arquetipos Canónicos inicializados y persistidos con éxito en:")
        print(f"   📂 {reg.workflows_dir}\n")
        for aid, wf in results.items():
            print(f"   • [{wf.version_info.semver}] {aid:<20} -> {wf.name} (SHA-256: {wf.version_info.sha256_hash[:12]}...)")
        print("")

    elif args.command == "list":
        items = reg.list_workflows(category=args.category)
        print(f"\n📋 Catálogo de Workflows Registrados ({len(items)} Arquetipos):\n")
        print(f"{'ARQUETIPO':<22} | {'VER':<8} | {'BPM':<4} | {'DUCK':<7} | {'ASPECT':<6} | {'FPS':<4} | {'SHA-256'}")
        print("-" * 80)
        for it in items:
            print(f"{it['archetype_id']:<22} | {it['latest_version']:<8} | {it['audio_bpm']:<4} | {it['ducking_db']}dB | {it['aspect_ratio']:<6} | {it['fps']:<4} | {it['sha256_hash'][:12]}...")
        print("")

    elif args.command == "get":
        wf = reg.get_workflow(args.archetype_id, version=args.version)
        if not wf:
            print(f"❌ Error: Workflow no encontrado para '{args.archetype_id}'", file=sys.stderr)
            sys.exit(1)
        if args.yaml:
            print(reg.export_workflow(args.archetype_id, format="yaml", version=args.version))
        else:
            print(reg.export_workflow(args.archetype_id, format="json", version=args.version))

    elif args.command == "verify":
        rep = reg.verify_all_storage_integrity()
        print(f"\n🔐 Verificación de Integridad Criptográfica SHA-256:")
        print(f"   Total Chequeados: {rep['total_checked']} | ✅ Válidos: {rep['passed']} | ❌ Corruptos: {rep['failed']}\n")
        for d in rep["details"]:
            status = "✅ OK" if d["valid"] else "❌ ERROR"
            print(f"   {status} {d['archetype_id']} ({d['version']}) -> {d['sha256'][:16]}... ({d['message']})")
        print("")

    elif args.command == "validate":
        wf = reg.get_workflow(args.archetype_id, version=args.version)
        if not wf:
            print(f"❌ Error: Workflow '{args.archetype_id}' no encontrado", file=sys.stderr)
            sys.exit(1)
        res = reg.validate_against_golden_rules(wf)
        print(f"\n🏆 Auditoría de 10 Reglas de Oro para {res['archetype_id']} ({res['version']}):")
        print(f"   Puntaje: {res['score']}/100 | {'🟢 APROBADO' if res['passed'] else '🔴 NO APROBADO'}")
        if res["violations"]:
            print(f"   Violaciones detectadas ({res['violations_count']}):")
            for v in res["violations"]:
                print(f"     - [{v['rule']}] -{v['penalty']} pts: {v['msg']}")
        else:
            print("   ✨ 100% Cumplimiento Estricto sin violaciones.")
        print("")

    elif args.command == "bump":
        patch = {}
        if args.ducking is not None:
            patch.setdefault("audio_spec", {})["ducking_db"] = args.ducking
        if args.bpm is not None:
            patch.setdefault("audio_spec", {})["bpm"] = args.bpm

        new_wf = reg.create_version(
            archetype_id=args.archetype_id,
            patch_data=patch,
            bump_type=args.type,
            changelog=args.changelog
        )
        print(f"\n🚀 Nueva versión creada: {new_wf.archetype_id} {new_wf.version_info.semver}")
        print(f"   SHA-256: {new_wf.version_info.sha256_hash}")
        print(f"   Changelog: {new_wf.version_info.changelog}\n")

    elif args.command == "diff":
        diff_res = reg.diff_versions(args.archetype_id, args.v1, args.v2)
        print(f"\n🔍 Diferencias entre {diff_res['v1']} y {diff_res['v2']} ({diff_res['archetype_id']}):")
        print(f"   Total Cambios: {diff_res['total_differences']}\n")
        for d in diff_res["differences"]:
            print(f"   • {d['field']}:")
            print(f"       - Antes:  {d['before']}")
            print(f"       + Después: {d['after']}")
        print("")

    elif args.command == "export":
        out = reg.export_workflow(args.archetype_id, format=args.format, version=args.version, output_path=args.out)
        if not args.out:
            print(out)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
