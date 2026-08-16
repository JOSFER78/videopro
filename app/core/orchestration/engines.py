"""
Registro Central de Motores (Engines) — VideoPro Studio
Define el "CÓMO" se realiza una Capability. Totalmente desacoplado del Provider ("DÓNDE").
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import Capability


class CostType(str, Enum):
    ZERO_COST = "zero_cost"          # $0 (Local VPS o Serverless ZeroGPU Gratis)
    TOKEN_POOL = "token_pool"        # $0 con cuotas mensuales incluidas (Google Flow 30k)
    PAY_PER_USE = "pay_per_use"      # Coste por segundo / GPU dedicada (RunPod / Replicate)


class EngineHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class EngineSpec(BaseModel):
    id: str
    name: str
    description: str
    capabilities: List[Capability]
    cost_type: CostType = CostType.ZERO_COST
    estimated_cost_per_scene: float = 0.0
    input_types: List[str] = Field(default_factory=list)
    output_types: List[str] = Field(default_factory=list)
    configuration_schema: Dict[str, Any] = Field(default_factory=dict)
    health: EngineHealthStatus = EngineHealthStatus.HEALTHY
    limits: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 100              # Menor número = mayor prioridad de elección
    fallbacks: List[str] = Field(default_factory=list)
    enabled: bool = True


# Catálogo Maestro de Motores (Engines)
ENGINES_CATALOG: Dict[str, EngineSpec] = {
    "google_flow": EngineSpec(
        id="google_flow",
        name="Google Flow 4K Playwright Engine",
        description="Generación cinemática 4K, congelado orbital 3D y planos continuos con 30.000 créditos/mes incluidos ($0).",
        capabilities=[Capability.VIDEO_GENERATION, Capability.IMAGE_GENERATION],
        cost_type=CostType.TOKEN_POOL,
        estimated_cost_per_scene=0.0,
        input_types=["prompt", "duration", "aspect_ratio"],
        output_types=["mp4", "webm"],
        configuration_schema={"model": "flow-cinematic-4k", "headless": True},
        limits={"max_duration_seconds": 15.0, "max_concurrent": 2},
        priority=10,
        fallbacks=["flux_video", "nanobanana", "stock_db"]
    ),
    "flux_video": EngineSpec(
        id="flux_video",
        name="FLUX 3 Video Engine (Flow Matching DiT)",
        description="Generación de vídeo y diálogos nativos en alta definición sin consumo de CPU del host.",
        capabilities=[Capability.VIDEO_GENERATION, Capability.IMAGE_GENERATION],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["prompt", "image_ref", "duration"],
        output_types=["mp4"],
        configuration_schema={"steps": 24, "guidance_scale": 6.5, "resolution": "1080p"},
        limits={"max_duration_seconds": 10.0, "max_concurrent": 4},
        priority=20,
        fallbacks=["ltx25", "stock_db"]
    ),
    "nanobanana": EngineSpec(
        id="nanobanana",
        name="NanoBanana Pro 2 Engine (Imagen 3 2K/4K)",
        description="Fotogramas clave 2K/4K, vistas multi-ángulo y texturas fotorrealistas 35mm vía Antigravity Bridge ($0).",
        capabilities=[Capability.IMAGE_GENERATION, Capability.POST_PROCESSING],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["prompt", "resolution", "camera_angle"],
        output_types=["png", "jpg"],
        configuration_schema={"model": "gemini-3.1-flash-image", "endpoint": "http://127.0.0.1:8742/v1"},
        limits={"max_resolution": "4096x4096", "max_concurrent": 6},
        priority=10,
        fallbacks=["stock_db"]
    ),
    "ltx25": EngineSpec(
        id="ltx25",
        name="LTX-2.5 MMDiT 22B Engine (Audio + Vídeo 24fps)",
        description="Síntesis unificada de vídeo 24fps con audio sincronizado y lip-sync nativo a 48kHz.",
        capabilities=[Capability.VIDEO_GENERATION, Capability.FOLEY_SFX],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["prompt", "duration"],
        output_types=["mp4"],
        configuration_schema={"frame_rate": 24, "audio_sample_rate": 48000},
        limits={"max_duration_seconds": 8.0},
        priority=30,
        fallbacks=["flux_video", "stock_db"]
    ),
    "stock_db": EngineSpec(
        id="stock_db",
        name="Stock 4K Documentary Engine (Pexels / Pixabay / Local DB)",
        description="Búsqueda semántica y extracción de material de archivo 4K libre de derechos.",
        capabilities=[Capability.VIDEO_GENERATION, Capability.IMAGE_GENERATION],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["search_terms", "orientation", "min_resolution"],
        output_types=["mp4", "jpg"],
        configuration_schema={"source_priority": ["pexels", "pixabay", "local"]},
        limits={"max_concurrent": 10},
        priority=40,
        fallbacks=[]
    ),
    "vibevoice": EngineSpec(
        id="vibevoice",
        name="VibeVoice 1.5B Continuous-Prosody TTS",
        description="Locución documental de expresividad ultra-humana con voz es-emilio a coste $0.",
        capabilities=[Capability.VOICE_GENERATION],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["text", "voice", "cfg_scale"],
        output_types=["wav", "mp3"],
        configuration_schema={"voice": "es-emilio", "cfg_scale": 1.3, "sample_rate": 24000},
        limits={"max_chars": 5000},
        priority=10,
        fallbacks=["edge_tts"]
    ),
    "edge_tts": EngineSpec(
        id="edge_tts",
        name="Edge-TTS Neural Cloud Engine",
        description="Locución multilingüe instantánea con voces neuronales de Microsoft sin coste.",
        capabilities=[Capability.VOICE_GENERATION],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["text", "voice"],
        output_types=["mp3"],
        configuration_schema={"voice": "es-ES-AlvaroNeural"},
        limits={"max_chars": 10000},
        priority=30,
        fallbacks=[]
    ),
    "whisper": EngineSpec(
        id="whisper",
        name="Faster-Whisper STT Engine",
        description="Alineación fonética milimétrica y transcripción palabra por palabra para subtítulos Vox.",
        capabilities=[Capability.SPEECH_TO_TEXT],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["audio_file"],
        output_types=["word_timestamps_json"],
        configuration_schema={"model_size": "base", "device": "auto"},
        limits={"max_audio_duration_seconds": 3600.0},
        priority=10,
        fallbacks=[]
    ),
    "flow_music": EngineSpec(
        id="flow_music",
        name="Google Flow Music & Foley Engine (Lyria 3)",
        description="Composición de pistas sonoras dinámicas y foley acústico sincronizado a la acción.",
        capabilities=[Capability.MUSIC_GENERATION, Capability.FOLEY_SFX],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["genre", "duration", "mood"],
        output_types=["wav", "mp3"],
        configuration_schema={"sample_rate": 48000, "stereo": True},
        limits={"max_duration_seconds": 600.0},
        priority=10,
        fallbacks=["stock_songs"]
    ),
    "stock_songs": EngineSpec(
        id="stock_songs",
        name="Stock Royalty-Free Audio Vault",
        description="Catálogo interno de 30 bandas sonoras masterizadas con selección armónica.",
        capabilities=[Capability.MUSIC_GENERATION],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["genre"],
        output_types=["mp3"],
        configuration_schema={},
        limits={},
        priority=50,
        fallbacks=[]
    ),
    "vox_subtitles": EngineSpec(
        id="vox_subtitles",
        name="Vox Dynamic Subtitle Styler (ASS / FFmpeg)",
        description="Estilizado de subtítulos cinemáticos con karaoke y palabra activa en amarillo dinámico.",
        capabilities=[Capability.SUBTITLE_GENERATION],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["word_timestamps", "font_name", "font_size"],
        output_types=["ass", "srt"],
        configuration_schema={"highlight_color": "&H0022FFFF", "font": "BeVietnamPro-Bold.ttf"},
        limits={},
        priority=10,
        fallbacks=[]
    ),
    "ffmpeg": EngineSpec(
        id="ffmpeg",
        name="FFmpeg 6.x Multitrack Assembly & Auto-Ducking",
        description="Mezclado multicapa de vídeo, normalización acústica -16 LUFS y ducking a -22dB.",
        capabilities=[Capability.RENDERING, Capability.POST_PROCESSING],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["clips", "audio", "subtitles"],
        output_types=["mp4"],
        configuration_schema={"crf": 19, "preset": "fast", "ducking_db": -22},
        limits={"max_resolution": "3840x2160"},
        priority=10,
        fallbacks=["remotion"]
    ),
    "remotion": EngineSpec(
        id="remotion",
        name="Remotion (React Video-as-Code Engine)",
        description="Renderizado programático de componentes React (.tsx), gráficos cinéticos y animaciones Spring estilo Vox.",
        capabilities=[Capability.RENDERING, Capability.POST_PROCESSING],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["tsx_composition", "props_json"],
        output_types=["mp4"],
        configuration_schema={"concurrency": 4, "fps": 30},
        limits={},
        priority=20,
        fallbacks=["ffmpeg"]
    ),
    "hyperframes": EngineSpec(
        id="hyperframes",
        name="HyperFrames (HTML5 Declarative Timeline Engine)",
        description="Renderizado de timelines web declarativos con animaciones GSAP y shaders WebGL en tiempo real.",
        capabilities=[Capability.RENDERING, Capability.POST_PROCESSING],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["html_timeline", "manifest"],
        output_types=["mp4"],
        configuration_schema={"renderer": "chromium_gpu"},
        limits={},
        priority=30,
        fallbacks=["ffmpeg"]
    ),
    "comfyui": EngineSpec(
        id="comfyui",
        name="ComfyUI Custom Workflow Engine",
        description="Ejecución de grafos modulares ComfyUI arbitrarios para generación de vídeo y post-producción.",
        capabilities=[Capability.VIDEO_GENERATION, Capability.IMAGE_GENERATION, Capability.POST_PROCESSING],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["comfy_graph_json", "inputs_dict"],
        output_types=["mp4", "png"],
        configuration_schema={"endpoint": "http://127.0.0.1:8188"},
        limits={"max_concurrent": 2},
        priority=25,
        fallbacks=["flux_video"]
    ),
    "hermes": EngineSpec(
        id="hermes",
        name="Hermes Agentic Creative Director (Gemini 3.7 Flash High)",
        description="Investigación profunda factual con subagentes y dirección cinematográfica $0.",
        capabilities=[Capability.RESEARCH, Capability.SCRIPT, Capability.SCENE_PLANNING],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["prompt", "history"],
        output_types=["script_json", "scenes_json"],
        configuration_schema={"endpoint": "http://127.0.0.1:8742/v1", "model": "gemini-3.7-flash-high"},
        limits={"max_tokens": 16000},
        priority=10,
        fallbacks=[]
    ),
    "r2_storage": EngineSpec(
        id="r2_storage",
        name="Cloudflare R2 Object Storage (Zero Egress)",
        description="Depósito en la nube S3-compatible con $0 de coste por ancho de banda de descarga.",
        capabilities=[Capability.STORAGE],
        cost_type=CostType.ZERO_COST,
        estimated_cost_per_scene=0.0,
        input_types=["local_file_path", "target_key"],
        output_types=["presigned_url", "cdn_url"],
        configuration_schema={"bucket": "videopro/videos/"},
        limits={},
        priority=10,
        fallbacks=[]
    )
}


def get_all_engines() -> List[EngineSpec]:
    """Retorna la lista de todos los motores disponibles."""
    return list(ENGINES_CATALOG.values())


def get_engine(engine_id: str) -> Optional[EngineSpec]:
    """Obtiene un motor por su identificador."""
    return ENGINES_CATALOG.get(engine_id)


def get_engines_by_capability(cap: Capability) -> List[EngineSpec]:
    """Retorna los motores capaces de ejecutar una Capability concreta, ordenados por prioridad."""
    matching = [e for e in ENGINES_CATALOG.values() if cap in e.capabilities and e.enabled]
    return sorted(matching, key=lambda x: x.priority)
