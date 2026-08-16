"""
videopro_ontology.py
Definición Formal de la Arquitectura de 4 Niveles de VideoPro Studio & Hermes:
1. API / Provider: Recursos, servidores y servicios base (i&v_pixabay_api, serverless_replicate, etc.)
2. Capacidad (Capability): Unidad atómica ejecutable que usa una o más APIs (cap_image_flux3, cap_tts_vibevoice, etc.)
3. Nodo (Node): Agrupación lógica de capacidades que resuelven una etapa funcional.
4. Workflow / Pipeline: Relación ordenada de nodos optimizada para un canal de YouTube concreto.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ============================================================================
# NIVEL 1: APIs, Servidores y Recursos Externos (Providers & APIs)
# ============================================================================
class ProviderCategory(str, Enum):
    AI_IMAGE = "AI_IMAGE"
    AI_VIDEO = "AI_VIDEO"
    AI_VOICE_TTS = "AI_VOICE_TTS"
    AI_LLM = "AI_LLM"
    STOCK_MEDIA = "STOCK_MEDIA"
    CODE_ENGINE = "CODE_ENGINE"
    CLOUD_DB = "CLOUD_DB"


class ProviderAPI(BaseModel):
    id: str = Field(..., description="Identificador único (ej: api_pexels, serverless_replicate)")
    name: str = Field(..., description="Nombre amigable")
    category: ProviderCategory
    base_url: Optional[str] = None
    is_serverless_free: bool = False
    status: str = "ACTIVE"
    credentials_key: Optional[str] = None


# ============================================================================
# NIVEL 2: Capacidades Atómicas (Capabilities)
# ============================================================================
class Capability(BaseModel):
    id: str = Field(..., description="ID de la capacidad (ej: cap_flux3_serverless, cap_vibevoice_1_5b)")
    name: str = Field(..., description="Nombre descriptivo de la capacidad")
    description: str
    required_apis: List[str] = Field(default_factory=list, description="IDs de ProviderAPI que utiliza")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    output_type: str = Field(..., description="TEXT, IMAGE, VIDEO_CLIP, AUDIO_TRACK, MOTION_OVERLAY, QA_REPORT")


# ============================================================================
# NIVEL 3: Nodos de Producción (Nodes)
# ============================================================================
class Node(BaseModel):
    id: str = Field(..., description="ID del nodo (ej: node_01_investigacion, node_04_titulacion)")
    number: int
    name: str
    role_description: str
    capabilities: List[str] = Field(default_factory=list, description="IDs de las capacidades agrupadas")
    input_artifacts: List[str] = Field(default_factory=list)
    output_artifacts: List[str] = Field(default_factory=list)


# ============================================================================
# NIVEL 4: Workflows / Pipelines para Canales de YouTube
# ============================================================================
class YouTubeChannelTarget(BaseModel):
    channel_name: str
    niche: str
    format: str = "16:9 4K 60FPS"
    visual_style: str
    target_audience: str


class WorkflowPipeline(BaseModel):
    id: str = Field(..., description="ID del workflow (ej: workflow_vox_documentary_3min)")
    name: str
    description: str
    channel_target: YouTubeChannelTarget
    ordered_nodes: List[str] = Field(default_factory=list, description="Secuencia ordenada de IDs de nodos")
    estimated_duration_sec: float
    output_specs: Dict[str, Any] = Field(default_factory=dict)
