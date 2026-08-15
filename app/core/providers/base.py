"""
Abstract Provider Interfaces (Strategy Pattern Contracts)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.core.domain.specs import VisualSpec, AudioSpec, ProvenanceInfo

class IVisualProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def generate_video_clip(self, spec: VisualSpec, output_path: str) -> ProvenanceInfo:
        pass

class IVoiceProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def synthesize(self, spec: AudioSpec, output_path: str) -> str:
        pass

class IMusicProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def generate_soundtrack(self, genre: str, duration_s: float, output_path: str) -> str:
        pass

class ILLMProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def generate_script(self, prompt: str, style: str) -> List[Dict[str, Any]]:
        pass
