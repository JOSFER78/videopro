"""
Domain Enumerations for VideoPro Core
"""
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    IN_PRODUCTION = "in_production"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"

class SceneStatus(str, Enum):
    PENDING = "pending"
    VISUAL_READY = "visual_ready"
    AUDIO_READY = "audio_ready"
    COMPOSITING = "compositing"
    RENDERED = "rendered"
    FAILED = "failed"

class LockLevel(int, Enum):
    DEFAULT = 10
    DIRECTOR_SUGGESTION = 20
    PROJECT_DECISION = 30
    USER_LOCK = 40

class ProviderCategory(str, Enum):
    VISUAL = "visual"
    VOICE = "voice"
    MUSIC = "music"
    LLM = "llm"
    TRANSCRIPTION = "transcription"
    STOCK = "stock"

class VisualEngineType(str, Enum):
    LTX25 = "ltx25"
    FLUX3 = "flux3"
    GOOGLE_FLOW = "google_flow"
    REPLICATE_H100 = "replicate_h100"
    PEXELS_STOCK = "pexels_stock"
    PIXABAY_STOCK = "pixabay_stock"
    REAL_ARCHIVE = "real_archive"

class VoiceEngineType(str, Enum):
    KOKORO_HD = "kokoro_hd"
    VIBEVOICE = "vibevoice"
    ELEVENLABS = "elevenlabs"
    FISH_AUDIO = "fish_audio"
    EDGE_TTS = "edge_tts"

class KaraokeStyle(str, Enum):
    VOX_HARRIS = "vox_harris"
    TIKTOK_POP = "tiktok_pop"
    DOCUMENTARY = "documentary"
    STEAMPUNK = "steampunk"
