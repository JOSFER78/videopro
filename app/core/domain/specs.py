"""
Pure Value Objects & Specifications for Scenes and Projects
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.core.domain.enums import VisualEngineType, VoiceEngineType, KaraokeStyle

@dataclass(frozen=True)
class ProvenanceInfo:
    asset_id: str
    origin_type: str            # "generated", "stock", "real_archive", "user_upload"
    provider_name: str
    prompt_used: str = ""
    seed: int = -1
    reference_urls: List[str] = field(default_factory=list)
    scene_id: str = ""
    project_id: str = ""
    created_at: str = ""
    checksum_md5: str = ""

@dataclass
class VisualSpec:
    subject: str = ""
    action: str = ""
    environment: str = ""
    lighting: str = ""
    camera_motion: str = ""
    color_palette: str = ""
    aspect_ratio: str = "9:16"   # "9:16", "16:9", "1:1"
    duration_s: float = 5.0
    engine: VisualEngineType = VisualEngineType.LTX25
    character_tags: List[str] = field(default_factory=list)
    negative_prompt: str = "blurry, low quality, artifacts, distorted, morphing"
    locked: bool = False

    def build_structured_prompt(self) -> str:
        """Assembles 5D cinematographic prompt from decoupled attributes."""
        parts = []
        if self.subject: parts.append(self.subject)
        if self.action: parts.append(self.action)
        if self.environment: parts.append(f"in {self.environment}")
        if self.lighting: parts.append(f"lit by {self.lighting}")
        if self.camera_motion: parts.append(f"camera: {self.camera_motion}")
        if self.color_palette: parts.append(f"palette: {self.color_palette}")
        return ", ".join(parts)

@dataclass
class AudioSpec:
    voice_text: str = ""
    voice_engine: VoiceEngineType = VoiceEngineType.KOKORO_HD
    voice_id: str = "es_male_1"
    voice_volume: float = 1.0
    bgm_genre: str = "ambient"
    bgm_volume: float = 0.35
    auto_ducking: bool = True
    ducking_db: float = -22.0
    foley_enabled: bool = True
    locked: bool = False

@dataclass
class SubtitleSpec:
    enabled: bool = True
    style: KaraokeStyle = KaraokeStyle.VOX_HARRIS
    max_words_per_line: int = 2
    highlight_color: str = "#FFC924"
    locked: bool = False

@dataclass
class RenderSpec:
    resolution: str = "1080x1920"
    fps: int = 24
    codec: str = "libx264"
    bitrate_k: int = 8000
    burned_subtitles: bool = True
