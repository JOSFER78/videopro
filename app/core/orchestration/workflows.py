"""
Registro Central de Workflows & Plantillas de Producción — VideoPro Studio
Define las estructuras de grafos, dependencias de capacidades, políticas de ejecución, fallbacks y vinculación con arquetipos.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import Capability
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG


class WorkflowNode(BaseModel):
    id: str
    title: str
    capability: Capability
    engine_id: Optional[str] = None       # Motor asignado o None si lo resuelve el Planner dinámicamente
    is_scene_loop: bool = False           # Si se ejecuta una vez por cada escena del guion
    enabled: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})


class WorkflowConnection(BaseModel):
    id: str
    from_node: str
    from_socket: str
    to_node: str
    to_socket: str
    payload_type: str = "any"


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: str
    version: int = 1
    version_label: str = "v1.0"
    archetype_id: Optional[str] = None
    required_capabilities: List[Capability] = Field(default_factory=list)
    nodes: List[WorkflowNode] = Field(default_factory=list)
    connections: List[WorkflowConnection] = Field(default_factory=list)
    pipeline_graph: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    policies: Dict[str, Any] = Field(default_factory=lambda: {"retry_limit": 2, "auto_fallback": True})
    fallbacks: Dict[str, List[str]] = Field(default_factory=dict)


# Catálogo Maestro de Plantillas de Workflows Oficiales
WORKFLOW_TEMPLATES: Dict[str, WorkflowDefinition] = {
    "DOCUMENTARY_MASTER": WorkflowDefinition(
        id="DOCUMENTARY_MASTER",
        name="Documental Maestro Híbrido (Vox Style)",
        description="Pipeline completo de producción: Investigación factual, Guion 5D, VibeVoice, STT Whisper, Selección Multimotor por escena (Stock + Flow + FLUX 3 + NanoBanana), Auto-Ducking acústico -22dB y Subtítulos Vox.",
        version=4,
        version_label="v4.0",
        archetype_id="HISTORICAL_SCRAPING",
        required_capabilities=[
            Capability.RESEARCH, Capability.SCRIPT, Capability.SCENE_PLANNING,
            Capability.VOICE_GENERATION, Capability.SPEECH_TO_TEXT, Capability.VIDEO_GENERATION,
            Capability.MUSIC_GENERATION, Capability.SUBTITLE_GENERATION, Capability.RENDERING
        ],
        nodes=[
            WorkflowNode(id="node_research", title="Investigación Factual & Subagentes", capability=Capability.RESEARCH, engine_id="hermes", position={"x": 50, "y": 100}),
            WorkflowNode(id="node_script", title="Director Creativo & Guion 5D", capability=Capability.SCRIPT, engine_id="hermes", position={"x": 350, "y": 100}),
            WorkflowNode(id="node_voice", title="VibeVoice 1.5B (Locución es-emilio)", capability=Capability.VOICE_GENERATION, engine_id="vibevoice", position={"x": 650, "y": 100}),
            WorkflowNode(id="node_stt", title="Whisper STT (Alineación Fonética)", capability=Capability.SPEECH_TO_TEXT, engine_id="whisper", position={"x": 950, "y": 100}),
            WorkflowNode(id="node_scene_router", title="Enrutador Inteligente de Escenas", capability=Capability.SCENE_PLANNING, engine_id="hermes", position={"x": 350, "y": 380}),
            WorkflowNode(id="node_visual_engine", title="Generador Visual Multimotor", capability=Capability.VIDEO_GENERATION, engine_id=None, is_scene_loop=True, position={"x": 650, "y": 380}),
            WorkflowNode(id="node_music_foley", title="Banda Sonora & Foley Acústico", capability=Capability.MUSIC_GENERATION, engine_id="flow_music", position={"x": 950, "y": 380}),
            WorkflowNode(id="node_subtitles", title="Subtítulos Dinámicos Vox Style", capability=Capability.SUBTITLE_GENERATION, engine_id="vox_subtitles", position={"x": 1250, "y": 100}),
            WorkflowNode(id="node_render", title="FFmpeg 6.x Master Render & Ducking", capability=Capability.RENDERING, engine_id="ffmpeg", position={"x": 1250, "y": 380}),
            WorkflowNode(id="node_storage", title="Cloudflare R2 (Subida Zero Egress)", capability=Capability.STORAGE, engine_id="r2_storage", position={"x": 1550, "y": 380})
        ],
        connections=[
            WorkflowConnection(id="c1", from_node="node_research", from_socket="dossier", to_node="node_script", to_socket="dossier", payload_type="dossier"),
            WorkflowConnection(id="c2", from_node="node_script", from_socket="script", to_node="node_voice", to_socket="text", payload_type="text"),
            WorkflowConnection(id="c3", from_node="node_script", from_socket="scenes", to_node="node_scene_router", to_socket="scenes", payload_type="scenes"),
            WorkflowConnection(id="c4", from_node="node_voice", from_socket="audio", to_node="node_stt", to_socket="audio", payload_type="audio"),
            WorkflowConnection(id="c5", from_node="node_stt", from_socket="timestamps", to_node="node_subtitles", to_socket="timestamps", payload_type="timestamps"),
            WorkflowConnection(id="c6", from_node="node_scene_router", from_socket="planned_scenes", to_node="node_visual_engine", to_socket="scenes", payload_type="scenes"),
            WorkflowConnection(id="c7", from_node="node_script", from_socket="music_mood", to_node="node_music_foley", to_socket="mood", payload_type="mood"),
            WorkflowConnection(id="c8", from_node="node_visual_engine", from_socket="video_clips", to_node="node_render", to_socket="clips", payload_type="clips"),
            WorkflowConnection(id="c9", from_node="node_voice", from_socket="audio", to_node="node_render", to_socket="voice_audio", payload_type="audio"),
            WorkflowConnection(id="c10", from_node="node_music_foley", from_socket="music", to_node="node_render", to_socket="bgm_audio", payload_type="audio"),
            WorkflowConnection(id="c11", from_node="node_subtitles", from_socket="ass_file", to_node="node_render", to_socket="subtitles", payload_type="subtitles"),
            WorkflowConnection(id="c12", from_node="node_render", from_socket="final_video", to_node="node_storage", to_socket="file", payload_type="video")
        ],
        pipeline_graph=ARCHETYPES_CATALOG["HISTORICAL_SCRAPING"].pipeline_graph
    ),
    "PIXAR_3D": WorkflowDefinition(
        id="PIXAR_3D",
        name="Cuentos & Animación 3D (Pixar Style)",
        description="Pipeline especializado en consistencia de personajes 3D, animación fotorrealista LoRA, VibeVoice estilo animado y música orquestal de cuento.",
        version=1,
        version_label="v1.0",
        archetype_id="PIXAR_3D_ANIMATION",
        required_capabilities=[Capability.SCRIPT, Capability.VOICE_GENERATION, Capability.IMAGE_GENERATION, Capability.VIDEO_GENERATION, Capability.MUSIC_GENERATION, Capability.RENDERING],
        pipeline_graph=ARCHETYPES_CATALOG["PIXAR_3D_ANIMATION"].pipeline_graph
    ),
    "HISTORICAL_SCRAPING": WorkflowDefinition(
        id="HISTORICAL_SCRAPING",
        name="Documental Histórico & Archivo Real",
        description="Investigación profunda con scraping en archivos históricos, restauración 4K de fotos reales antiguas, recreación de momentos ciegos con IA y citas estilo Vox.",
        version=1,
        version_label="v1.0",
        archetype_id="HISTORICAL_SCRAPING",
        required_capabilities=[Capability.RESEARCH, Capability.SCRIPT, Capability.VOICE_GENERATION, Capability.IMAGE_GENERATION, Capability.VIDEO_GENERATION, Capability.SUBTITLE_GENERATION, Capability.RENDERING],
        pipeline_graph=ARCHETYPES_CATALOG["HISTORICAL_SCRAPING"].pipeline_graph
    ),
    "CITY_ROUTES_BEATS": WorkflowDefinition(
        id="CITY_ROUTES_BEATS",
        name="Rutas Urbanas & Vídeos Musicales (City Beats)",
        description="Recorridos cinemáticos por ciudades con planos orbitales 4K (Google Flow), banda sonora generativa a tempo constante y superposición de datos curiosos.",
        version=1,
        version_label="v1.0",
        archetype_id="CITY_ROUTES_BEATS",
        required_capabilities=[Capability.SCRIPT, Capability.VIDEO_GENERATION, Capability.MUSIC_GENERATION, Capability.RENDERING],
        pipeline_graph=ARCHETYPES_CATALOG["CITY_ROUTES_BEATS"].pipeline_graph
    ),
    "VIRAL_SHORTS_HOOK": WorkflowDefinition(
        id="VIRAL_SHORTS_HOOK",
        name="Viral Shorts & Retención Extrema (TikTok / Reels)",
        description="Vídeos verticales de ritmo vertiginoso (1.8s por toma), gancho de choque en los primeros 3 segundos, subtítulos karaoke amarillo flúor y SFX de impacto.",
        version=1,
        version_label="v1.0",
        archetype_id="VIRAL_SHORTS_HOOK",
        required_capabilities=[Capability.SCRIPT, Capability.VOICE_GENERATION, Capability.VIDEO_GENERATION, Capability.SUBTITLE_GENERATION, Capability.MUSIC_GENERATION, Capability.RENDERING],
        pipeline_graph=ARCHETYPES_CATALOG["VIRAL_SHORTS_HOOK"].pipeline_graph
    ),
    "DEEP_EXPLAINER_ESSAY": WorkflowDefinition(
        id="DEEP_EXPLAINER_ESSAY",
        name="Deep Explainer & Videoensayo Dialéctico",
        description="Estructura argumentativa en tres actos (Tesis, Antítesis y Síntesis), gráficos animados generados con Remotion React y música minimalista de fondo.",
        version=1,
        version_label="v1.0",
        archetype_id="DEEP_EXPLAINER_ESSAY",
        required_capabilities=[Capability.SCRIPT, Capability.VOICE_GENERATION, Capability.POST_PROCESSING, Capability.RENDERING],
        pipeline_graph=ARCHETYPES_CATALOG["DEEP_EXPLAINER_ESSAY"].pipeline_graph
    ),
    "FLOW_ONLY": WorkflowDefinition(
        id="FLOW_ONLY",
        name="Google Flow Cinemático 4K Puro",
        description="Generación completa de vídeo visual utilizando exclusivamente Google Flow Playwright 4K con congelado orbital 3D.",
        version=1,
        version_label="v1.0",
        required_capabilities=[Capability.SCRIPT, Capability.VOICE_GENERATION, Capability.VIDEO_GENERATION, Capability.RENDERING],
        nodes=[
            WorkflowNode(id="node_script", title="Guion Cinemático", capability=Capability.SCRIPT, engine_id="hermes"),
            WorkflowNode(id="node_voice", title="Voz Neural", capability=Capability.VOICE_GENERATION, engine_id="vibevoice"),
            WorkflowNode(id="node_flow", title="Google Flow Playwright 4K", capability=Capability.VIDEO_GENERATION, engine_id="google_flow", is_scene_loop=True),
            WorkflowNode(id="node_render", title="FFmpeg Assembly", capability=Capability.RENDERING, engine_id="ffmpeg")
        ],
        connections=[]
    ),
    "FLUX_ONLY": WorkflowDefinition(
        id="FLUX_ONLY",
        name="FLUX 3 Video Serverless Puro",
        description="Generación de vídeo y personajes exclusivamente con FLUX 3 DiT en clúster Serverless ZeroGPU ($0).",
        version=1,
        version_label="v1.0",
        required_capabilities=[Capability.SCRIPT, Capability.VOICE_GENERATION, Capability.VIDEO_GENERATION, Capability.RENDERING],
        nodes=[
            WorkflowNode(id="node_script", title="Guion Cinemático", capability=Capability.SCRIPT, engine_id="hermes"),
            WorkflowNode(id="node_voice", title="Voz Neural", capability=Capability.VOICE_GENERATION, engine_id="vibevoice"),
            WorkflowNode(id="node_flux", title="FLUX 3 Video DiT", capability=Capability.VIDEO_GENERATION, engine_id="flux_video", is_scene_loop=True),
            WorkflowNode(id="node_render", title="FFmpeg Assembly", capability=Capability.RENDERING, engine_id="ffmpeg")
        ],
        connections=[]
    ),
    "CUSTOM_COMFY": WorkflowDefinition(
        id="CUSTOM_COMFY",
        name="Lienzo ComfyUI Personalizado",
        description="Grafo modular de nodos diseñado a medida en el Workflow Designer.",
        version=1,
        version_label="v1.0",
        required_capabilities=[],
        nodes=[],
        connections=[]
    )
}


def get_all_workflows() -> List[WorkflowDefinition]:
    """Retorna todas las plantillas de workflows oficiales."""
    return list(WORKFLOW_TEMPLATES.values())


def get_workflow(wf_id: str) -> Optional[WorkflowDefinition]:
    """Obtiene una definición de workflow por su ID."""
    return WORKFLOW_TEMPLATES.get(wf_id)


def get_workflow_by_archetype(archetype_id: str) -> Optional[WorkflowDefinition]:
    """Obtiene el workflow asociado a un arquetipo específico."""
    for wf in WORKFLOW_TEMPLATES.values():
        if wf.archetype_id == archetype_id:
            return wf
    return None
