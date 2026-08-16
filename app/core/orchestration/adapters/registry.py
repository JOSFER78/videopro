"""
Registro Central de Adaptadores de Motores (Adapter Registry) — VideoPro Studio
Mapea de forma dinámica cada engine_id con su instancia de adaptador concreta.
"""

from typing import Dict, Optional
from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.adapters.google_flow_adapter import GoogleFlowAdapter
from app.core.orchestration.adapters.flux_adapter import FluxAdapter
from app.core.orchestration.adapters.nanobanana_adapter import NanoBananaAdapter
from app.core.orchestration.adapters.vibevoice_adapter import VibeVoiceAdapter
from app.core.orchestration.adapters.whisper_adapter import WhisperAdapter
from app.core.orchestration.adapters.stock_adapter import StockAdapter
from app.core.orchestration.adapters.ffmpeg_adapter import FFmpegAdapter
from app.core.orchestration.adapters.comfyui_adapter import ComfyUIAdapter
from app.core.orchestration.adapters.hermes_adapter import HermesAdapter
from app.core.orchestration.adapters.music_adapter import MusicAdapter
from app.core.orchestration.adapters.subtitles_adapter import SubtitlesAdapter
from app.core.orchestration.adapters.r2_adapter import R2Adapter


class AdapterRegistry:
    """Registro singleton de instancias de adaptadores."""
    
    _adapters: Dict[str, BaseEngineAdapter] = {}

    @classmethod
    def initialize(cls):
        if not cls._adapters:
            cls.register(GoogleFlowAdapter())
            cls.register(FluxAdapter())
            cls.register(NanoBananaAdapter())
            cls.register(VibeVoiceAdapter())
            cls.register(WhisperAdapter())
            cls.register(StockAdapter())
            cls.register(FFmpegAdapter())
            cls.register(ComfyUIAdapter())
            cls.register(HermesAdapter())
            cls.register(MusicAdapter())
            cls.register(SubtitlesAdapter())
            cls.register(R2Adapter())

    @classmethod
    def register(cls, adapter: BaseEngineAdapter):
        cls._adapters[adapter.engine_id] = adapter

    @classmethod
    def get_adapter(cls, engine_id: str) -> Optional[BaseEngineAdapter]:
        cls.initialize()
        return cls._adapters.get(engine_id)


# Inicializar automáticamente al importar
AdapterRegistry.initialize()
