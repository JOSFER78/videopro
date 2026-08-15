"""
Provider Registry & Factory for VideoPro
"""
from typing import Dict, Any, Optional
from app.core.providers.base import IVisualProvider, IVoiceProvider, IMusicProvider, ILLMProvider

class ProviderRegistry:
    _visual_providers: Dict[str, IVisualProvider] = {}
    _voice_providers: Dict[str, IVoiceProvider] = {}
    _music_providers: Dict[str, IMusicProvider] = {}
    _llm_providers: Dict[str, ILLMProvider] = {}

    @classmethod
    def register_visual(cls, name: str, provider: IVisualProvider):
        cls._visual_providers[name.lower()] = provider

    @classmethod
    def register_voice(cls, name: str, provider: IVoiceProvider):
        cls._voice_providers[name.lower()] = provider

    @classmethod
    def register_music(cls, name: str, provider: IMusicProvider):
        cls._music_providers[name.lower()] = provider

    @classmethod
    def register_llm(cls, name: str, provider: ILLMProvider):
        cls._llm_providers[name.lower()] = provider

    @classmethod
    def get_visual(cls, name: str) -> Optional[IVisualProvider]:
        return cls._visual_providers.get(name.lower())

    @classmethod
    def get_voice(cls, name: str) -> Optional[IVoiceProvider]:
        return cls._voice_providers.get(name.lower())

    @classmethod
    def get_music(cls, name: str) -> Optional[IMusicProvider]:
        return cls._music_providers.get(name.lower())

    @classmethod
    def get_llm(cls, name: str) -> Optional[ILLMProvider]:
        return cls._llm_providers.get(name.lower())

    @classmethod
    def list_available_visuals(cls) -> list:
        return list(cls._visual_providers.keys())

    @classmethod
    def list_available_voices(cls) -> list:
        return list(cls._voice_providers.keys())
