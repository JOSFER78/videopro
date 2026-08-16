"""
Registro Central de Capacidades (Capabilities) — VideoPro Studio
Define el "QUÉ" se desea realizar en el pipeline, desacoplado de cómo o dónde se ejecuta.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class Capability(str, Enum):
    RESEARCH = "research"
    SCRIPT = "script"
    SCENE_PLANNING = "scene_planning"
    VOICE_GENERATION = "voice_generation"
    SPEECH_TO_TEXT = "speech_to_text"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    MUSIC_GENERATION = "music_generation"
    FOLEY_SFX = "foley_sfx"
    SUBTITLE_GENERATION = "subtitle_generation"
    POST_PROCESSING = "post_processing"
    RENDERING = "rendering"
    STORAGE = "storage"
    NOTIFICATION = "notification"


class CapabilitySpec(BaseModel):
    id: Capability
    name: str
    description: str
    input_contract: Dict[str, str] = Field(default_factory=dict)
    output_contract: Dict[str, str] = Field(default_factory=dict)
    category: str = "core"
    is_required_for_video: bool = False


# Catálogo Maestro de Capacidades de VideoPro
CAPABILITIES_CATALOG: Dict[Capability, CapabilitySpec] = {
    Capability.RESEARCH: CapabilitySpec(
        id=Capability.RESEARCH,
        name="Investigación Factual & Subagentes",
        description="Búsqueda profunda en web, dossiers fácticos y verificación de afirmaciones históricas o documentales.",
        input_contract={"prompt": "str", "depth": "str"},
        output_contract={"dossier": "dict", "facts": "list"},
        category="intelligence"
    ),
    Capability.SCRIPT: CapabilitySpec(
        id=Capability.SCRIPT,
        name="Dirección Creativa & Guion",
        description="Estructuración de narrativa cinemática en tres actos, especificaciones de cámara y diálogos por escena.",
        input_contract={"theme": "str", "style": "str", "duration": "int", "dossier": "dict"},
        output_contract={"script": "dict", "scenes": "list"},
        category="intelligence",
        is_required_for_video=True
    ),
    Capability.SCENE_PLANNING: CapabilitySpec(
        id=Capability.SCENE_PLANNING,
        name="Planificación y Ruteo de Escenas",
        description="Asignación óptima de motores visuales (Stock, Keyframe, Video DiT, Flow) por escena según estilo y coste.",
        input_contract={"scenes": "list", "visual_strategy": "str"},
        output_contract={"planned_scenes": "list"},
        category="planning",
        is_required_for_video=True
    ),
    Capability.VOICE_GENERATION: CapabilitySpec(
        id=Capability.VOICE_GENERATION,
        name="Síntesis Vocal Neural (TTS)",
        description="Locución expresiva de guion con prosodia continua, clonación zero-shot y masterizado a 24kHz/48kHz.",
        input_contract={"text": "str", "voice_id": "str", "emotion": "str"},
        output_contract={"audio_path": "str", "sample_rate": "int"},
        category="audio",
        is_required_for_video=True
    ),
    Capability.SPEECH_TO_TEXT: CapabilitySpec(
        id=Capability.SPEECH_TO_TEXT,
        name="Transcripción Fonética & Word Timestamps (STT)",
        description="Alineación milimétrica fonética palabra por palabra para subtítulos sincronizados con la voz.",
        input_contract={"audio_path": "str"},
        output_contract={"word_timestamps": "list", "language": "str"},
        category="audio",
        is_required_for_video=True
    ),
    Capability.IMAGE_GENERATION: CapabilitySpec(
        id=Capability.IMAGE_GENERATION,
        name="Síntesis de Imágenes & Keyframes 4K",
        description="Generación de fotogramas clave fotorrealistas en 2K/4K con consistencia de personajes e iluminación 35mm.",
        input_contract={"prompt": "str", "resolution": "str", "aspect_ratio": "str"},
        output_contract={"image_path": "str"},
        category="visual"
    ),
    Capability.VIDEO_GENERATION: CapabilitySpec(
        id=Capability.VIDEO_GENERATION,
        name="Generación de Vídeo Cinemático (T2V / I2V)",
        description="Generación de clips de vídeo a 24fps con movimiento continuo, coherencia física y cámara orbital 3D.",
        input_contract={"prompt": "str", "image_ref": "str", "duration": "float", "aspect_ratio": "str"},
        output_contract={"video_clip_path": "str", "has_audio": "bool"},
        category="visual",
        is_required_for_video=True
    ),
    Capability.MUSIC_GENERATION: CapabilitySpec(
        id=Capability.MUSIC_GENERATION,
        name="Composición Musical & Banda Sonora",
        description="Generación o selección de banda sonora armónica adaptada a la tensión dramática del guion.",
        input_contract={"genre": "str", "duration": "float", "mood": "str"},
        output_contract={"music_path": "str"},
        category="audio"
    ),
    Capability.FOLEY_SFX: CapabilitySpec(
        id=Capability.FOLEY_SFX,
        name="Efectos Acústicos Foley & Ambiente",
        description="Síntesis acústica de pasos, ambiente espacial y efectos de impacto sincronizados con la acción.",
        input_contract={"action_prompt": "str", "duration": "float"},
        output_contract={"sfx_path": "str"},
        category="audio"
    ),
    Capability.SUBTITLE_GENERATION: CapabilitySpec(
        id=Capability.SUBTITLE_GENERATION,
        name="Estilizado de Subtítulos Animados Vox",
        description="Generación de subtítulos dinámicos ASS/Karaoke con resaltado palabra por palabra (Highlight amarillo/blanco).",
        input_contract={"word_timestamps": "list", "font": "str", "font_size": "int", "position": "str"},
        output_contract={"ass_path": "str", "srt_path": "str"},
        category="assembly"
    ),
    Capability.POST_PROCESSING: CapabilitySpec(
        id=Capability.POST_PROCESSING,
        name="Post-Procesado & Efectos 2.5D",
        description="Efecto Ken Burns cinemático, estabilización de color, LUT 35mm y overlays gráficos de soporte.",
        input_contract={"clips": "list", "lut": "str"},
        output_contract={"processed_clips": "list"},
        category="visual"
    ),
    Capability.RENDERING: CapabilitySpec(
        id=Capability.RENDERING,
        name="Ensamblaje Máster & Auto-Ducking (FFmpeg/Remotion)",
        description="Mezcla multicapa de pistas de vídeo, audio normalizado a -16 LUFS, ducking a -22dB y quemado de subtítulos.",
        input_contract={"clips": "list", "voice_audio": "str", "bgm_audio": "str", "subtitles": "str", "crf": "int"},
        output_contract={"final_video_path": "str", "duration": "float"},
        category="assembly",
        is_required_for_video=True
    ),
    Capability.STORAGE: CapabilitySpec(
        id=Capability.STORAGE,
        name="Almacenamiento Cloud Zero Egress & Presigned URLs",
        description="Subida multipart a Cloudflare R2 con presigned URLs de 24h y CDN pública opcional.",
        input_contract={"file_path": "str", "bucket": "str", "key": "str"},
        output_contract={"storage_url": "str", "etag": "str"},
        category="infrastructure"
    ),
    Capability.NOTIFICATION: CapabilitySpec(
        id=Capability.NOTIFICATION,
        name="Notificación & Webhooks",
        description="Notificación en tiempo real de finalización de render hacia Firebase, Telegram o Webhooks.",
        input_contract={"job_id": "str", "status": "str", "result_url": "str"},
        output_contract={"notified": "bool"},
        category="infrastructure"
    )
}


def get_all_capabilities() -> List[CapabilitySpec]:
    """Retorna todas las capacidades registradas en el Studio."""
    return list(CAPABILITIES_CATALOG.values())


def get_capability(cap_id: Capability) -> Optional[CapabilitySpec]:
    """Obtiene la especificación de una capacidad dada."""
    return CAPABILITIES_CATALOG.get(cap_id)
