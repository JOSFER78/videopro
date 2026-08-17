"""
learning_experience.py
Modelos de Datos para el Motor de Aprendizaje Continuo y Memoria de Experiencia — VideoPro Studio.
Estructuras para lecciones aprendidas, anti-patrones, estándares dorados, evaluaciones de proyectos
y métricas de proveedores (FLUX.3 Serverless Free vs Replicate vs RunPod vs Local).
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LessonCategory(str, Enum):
    VISUAL_PACING = "VISUAL_PACING"               # Ritmo de cortes, duración máxima de planos (3-5s), variedad de ángulos
    TYPOGRAPHY_DESIGN = "TYPOGRAPHY_DESIGN"       # Estética tipográfica, lower-thirds limpios, sin cajas invasivas
    ASSET_MATCHING = "ASSET_MATCHING"             # Correspondencia semántica exacta entre voz locutada y visual
    AUDIO_RHYTHM = "AUDIO_RHYTHM"                 # Locución, ritmo, ducking musical, sonorización foley
    PROVIDER_DISPATCH = "PROVIDER_DISPATCH"       # Selección de proveedor (Free ZeroGPU vs Replicate vs RunPod vs Local)
    INVESTIGATION_RESEARCH = "INVESTIGATION_RESEARCH" # Scraping de archivos, user-agents, autenticidad histórica
    EDITING_COMPOSITION = "EDITING_COMPOSITION"   # Transiciones, Ken-Burns, renderizado de motion graphics


class LessonSeverity(str, Enum):
    CRITICAL = "CRITICAL"         # Regla obligatoria; su incumplimiento arruina la producción
    STRICT = "STRICT"             # Regla estricta de estilo para canales profesionales
    BEST_PRACTICE = "BEST_PRACTICE" # Recomendación de optimización o refinamiento


class ProviderExecutionMode(str, Enum):
    FREE_SERVERLESS = "FREE_SERVERLESS"   # HuggingFace ZeroGPU, VibeVoice Free, Edge-TTS ($0)
    REPLICATE_API = "REPLICATE_API"       # Serverless Pay-per-second API (Replicate / Fal)
    RUNPOD_GPU = "RUNPOD_GPU"             # Pod dedicado ComfyUI / Modal GPU
    LOCAL_VPS = "LOCAL_VPS"               # GPU/CPU in-house VPS ($0)


class LearnedLesson(BaseModel):
    """Representa una lección aprendida o regla de calidad acumulada por la experiencia del sistema."""
    id: str = Field(..., description="Identificador canónico único (ej: rule_dynamic_visual_cutaways_3s)")
    title: str = Field(..., description="Título descriptivo de la lección")
    category: LessonCategory = Field(..., description="Categoría de la regla")
    severity: LessonSeverity = Field(default=LessonSeverity.STRICT, description="Nivel de exigencia")
    what_failed: str = Field(..., description="Anti-patrón: qué ocurrió mal en experiencias pasadas")
    golden_rule: str = Field(..., description="Estándar dorado: qué debe hacerse para asegurar la máxima calidad")
    applicable_nodes: List[str] = Field(default_factory=list, description="IDs de nodos donde aplica (ej: node_03_ingesta)")
    applicable_workflows: List[str] = Field(default_factory=lambda: ["ALL"], description="IDs de workflows donde aplica")
    experience_source_project: Optional[str] = Field(None, description="ID del proyecto donde se descubrió la lección")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    applied_count: int = Field(default=0, description="Número de veces aplicada con éxito")
    success_rating: float = Field(default=1.0, description="Calificación de efectividad (0.0 a 1.0)")


class ProjectCritiqueFeedback(BaseModel):
    """Representa la autoevaluación o feedback humano recibido tras una producción."""
    critique_id: str = Field(..., description="ID único de la crítica")
    project_id: str = Field(..., description="ID del proyecto evaluado")
    workflow_id: str = Field(..., description="ID del workflow utilizado")
    overall_score: int = Field(default=75, description="Puntuación global de calidad (0 a 100)")
    user_feedback_raw: str = Field(..., description="Transcripción exacta del feedback del usuario")
    critique_breakdown: Dict[str, Any] = Field(
        default_factory=dict,
        description="Desglose por área: {'visual_pacing': 30, 'typography': 20, 'asset_matching': 40, 'audio': 90}"
    )
    lessons_extracted: List[str] = Field(default_factory=list, description="IDs de lecciones creadas/reforzadas a partir de esta crítica")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ProviderExecutionMetric(BaseModel):
    """Métricas de rendimiento, latencia y coste por capacidad y proveedor."""
    provider_id: str = Field(..., description="ID del proveedor físico de Nivel 1")
    capability_id: str = Field(..., description="ID de la capacidad lógica de Nivel 2")
    provider_name: str = Field(..., description="Nombre del proveedor")
    mode: ProviderExecutionMode = Field(default=ProviderExecutionMode.FREE_SERVERLESS)
    latency_avg_sec: float = Field(default=0.0, description="Latencia media de ejecución en segundos")
    success_rate: float = Field(default=1.0, description="Tasa de éxito histórica (0.0 a 1.0)")
    cost_per_generation: float = Field(default=0.0, description="Coste estimado por generación en USD")
    total_calls: int = Field(default=0, description="Número total de llamadas")
    notes: str = Field(default="", description="Observaciones y particularidades técnicas")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
