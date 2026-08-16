"""
Catálogo Maestro de Arquetipos de Producción & Pipelines ComfyUI Especializados — VideoPro Studio
Cada arquetipo encapsula su propia Entrevista Adaptativa, su Grafo ComfyUI específico y sus motores óptimos.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import Capability
from app.core.orchestration.scene_router import VisualStrategy


class InterviewQuestion(BaseModel):
    key: str
    question: str
    description: str
    question_type: str = "select"       # select, text, number, multi_select
    options: List[str] = Field(default_factory=list)
    default_value: Any = None
    target_node_param: Optional[str] = None   # Mapeo directo al parámetro del nodo en el pipeline


class WorkflowArchetype(BaseModel):
    id: str
    name: str
    icon: str
    tag: str
    description: str
    category: str
    target_audience: str
    default_aspect_ratio: str = "9:16"
    visual_strategy: VisualStrategy = VisualStrategy.HYBRID
    default_voice_engine: str = "vibevoice"
    default_voice_id: str = "es-emilio"
    default_music_genre: str = "cinematic"
    interview_schema: List[InterviewQuestion] = Field(default_factory=list)
    pipeline_graph: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"
    author: str = "VideoPro Studio Core"


# =====================================================================
# 1. PIXAR 3D ANIMATION PIPELINE & INTERVIEW
# =====================================================================
PIXAR_3D_GRAPH = {
    "version": "1.0.0",
    "name": "Pixar 3D Storytelling & Character Pipeline",
    "nodes": [
        {
            "id": "node_character_sheet",
            "title": "🧸 Character Sheet & Diseño 3D",
            "category": "character",
            "color": "#f59e0b",
            "x": 50, "y": 140, "width": 280, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "char_out", "name": "character_ref", "label": "Referencia de Personaje"}],
            "parameters": [
                {"key": "protagonist_type", "label": "Diseño del Personaje (Libre)", "type": "text", "value": "Protagonista carismático definido por investigación/historia"},
                {"key": "art_style", "label": "Estilo de Render Óptico", "type": "text", "value": "Pixar 3D Cinematic (Subsurface Scattering, Anamorphic 35mm, Volumetric Glow)"}
            ]
        },
        {
            "id": "node_story_engine",
            "title": "📖 Guion Narrativo & Lección Emotiva",
            "category": "llm",
            "color": "#c084fc",
            "x": 370, "y": 140, "width": 290, "enabled": True,
            "inputs": [{"id": "char_in", "name": "character_ref", "label": "Referencia de Personaje"}],
            "outputs": [{"id": "script_out", "name": "script", "label": "Guion 3 Actos"}],
            "parameters": [
                {"key": "tone", "label": "Tono & Atmósfera Narrativa", "type": "text", "value": "Conmovedor, emotivo y con clímax cinematográfico"},
                {"key": "moral", "label": "Mensaje / Núcleo Dramático", "type": "text", "value": "Evolución personal y resolución del conflicto"}
            ]
        },
        {
            "id": "node_flux_pixar_dit",
            "title": "🎨 FLUX 3 LoRA 3D & NanoBanana Render",
            "category": "visual",
            "color": "#ec4899",
            "x": 700, "y": 140, "width": 310, "enabled": True, "is_loop": True,
            "inputs": [{"id": "script_in", "name": "script", "label": "Guion 3 Actos"}],
            "outputs": [{"id": "clips_out", "name": "video_clips", "label": "Clips 3D Render"}],
            "parameters": [
                {"key": "lora_model", "label": "Motor Visual & Keyframes", "type": "text", "value": "flux-pixar-story-v2 / nanobanana-3d-cinema"},
                {"key": "lighting", "label": "Esquema de Iluminación Óptica", "type": "text", "value": "Golden Hour suave, luz volumétrica de relleno y bokeh T1.8"}
            ]
        },
        {
            "id": "node_voice_animated",
            "title": "🎙️ VibeVoice 1.5B (Locución Expresiva Cuento)",
            "category": "voice",
            "color": "#10b981",
            "x": 370, "y": 420, "width": 290, "enabled": True,
            "inputs": [{"id": "script_in", "name": "script", "label": "Guion 3 Actos"}],
            "outputs": [{"id": "audio_out", "name": "voice_audio", "label": "Voz Narrador"}],
            "parameters": [
                {"key": "voice_style", "label": "Cadencia Vocal & Actuación", "type": "text", "value": "Cuentacuentos cinematográfico con cadencia expresiva profunda"}
            ]
        },
        {
            "id": "node_fairytale_music",
            "title": "🎵 Flow Music (Orquesta Cuento de Hadas)",
            "category": "music",
            "color": "#eab308",
            "x": 700, "y": 420, "width": 310, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "music_out", "name": "bgm_audio", "label": "Banda Sonora Orquestal"}],
            "parameters": [
                {"key": "genre", "label": "Partitura Sonora & BGM", "type": "text", "value": "Orquestal cinematográfica con cuerdas, vientos de madera y clímax melódico"}
            ]
        },
        {
            "id": "node_master_render",
            "title": "🎬 Ensamblador Máster 3D & Auto-Ducking",
            "category": "render",
            "color": "#06b6d4",
            "x": 1050, "y": 280, "width": 300, "enabled": True,
            "inputs": [
                {"id": "c_in", "name": "video_clips", "label": "Clips 3D"},
                {"id": "v_in", "name": "voice_audio", "label": "Voz Narrador"},
                {"id": "m_in", "name": "bgm_audio", "label": "BGM"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Vídeo Final"}],
            "parameters": [
                {"key": "color_grading", "label": "Grading de Color & Master", "type": "text", "value": "Vibrant Pixar Colors (+15% Sat, Master HDR 4K)"}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_character_sheet", "from_socket": "char_out", "to_node": "node_story_engine", "to_socket": "char_in"},
        {"id": "c2", "from_node": "node_story_engine", "from_socket": "script_out", "to_node": "node_flux_pixar_dit", "to_socket": "script_in"},
        {"id": "c3", "from_node": "node_story_engine", "from_socket": "script_out", "to_node": "node_voice_animated", "to_socket": "script_in"},
        {"id": "c4", "from_node": "node_flux_pixar_dit", "from_socket": "clips_out", "to_node": "node_master_render", "to_socket": "c_in"},
        {"id": "c5", "from_node": "node_voice_animated", "from_socket": "audio_out", "to_node": "node_master_render", "to_socket": "v_in"},
        {"id": "c6", "from_node": "node_fairytale_music", "from_socket": "music_out", "to_node": "node_master_render", "to_socket": "m_in"}
    ]
}


# =====================================================================
# 2. HISTORICAL SCRAPING & ARCHIVE DOCUMENTARY PIPELINE & INTERVIEW
# =====================================================================
HISTORICAL_SCRAPING_GRAPH = {
    "version": "1.0.0",
    "name": "Historical Scraping & Archival Restoration Pipeline",
    "nodes": [
        {
            "id": "node_hermes_scraping",
            "title": "🔬 Hermes Scraping & Archivos Históricos",
            "category": "programacion",
            "color": "#a855f7",
            "x": 50, "y": 140, "width": 310, "enabled": True,
            "inputs": [],
            "outputs": [
                {"id": "facts_out", "name": "facts_dossier", "label": "Dossier Fáctico & Citas"},
                {"id": "photos_out", "name": "archival_photos", "label": "Fotos de Archivo Reales"}
            ],
            "parameters": [
                {"key": "sources", "label": "Fuentes de Scraping & Archivo", "type": "text", "value": "Wikipedia + Wikimedia Commons + Hemerotecas y Archivos Web"},
                {"key": "min_facts", "label": "Datos Curiosos Mínimos", "type": "number", "value": 5}
            ]
        },
        {
            "id": "node_restoration_nanobanana",
            "title": "✨ NanoBanana 2K/4K Upscale & Photo Restorer",
            "category": "visual",
            "color": "#38bdf8",
            "x": 400, "y": 100, "width": 300, "enabled": True, "is_loop": True,
            "inputs": [{"id": "p_in", "name": "archival_photos", "label": "Fotos Antiguas"}],
            "outputs": [{"id": "restored_out", "name": "restored_clips", "label": "Metraje 4K Restaurado (Ken Burns 2.5D)"}],
            "parameters": [
                {"key": "grain_35mm", "label": "Emulación Óptica & Grano", "type": "text", "value": "Grano 35mm cinematográfico suave con movimiento multi-capa 2.5D"}
            ]
        },
        {
            "id": "node_gap_filler_flow",
            "title": "🎥 Google Flow Recreación de Momentos Clave",
            "category": "visual",
            "color": "#ec4899",
            "x": 400, "y": 380, "width": 300, "enabled": True, "is_loop": True,
            "inputs": [{"id": "f_in", "name": "facts_dossier", "label": "Hechos sin Registro"}],
            "outputs": [{"id": "recreation_out", "name": "recreation_clips", "label": "Planos Recreados 4K"}],
            "parameters": [
                {"key": "fidelity", "label": "Rigor Visual Histórico", "type": "text", "value": "Estricto rigor de época con etalonaje 35mm ARRI Alexa"}
            ]
        },
        {
            "id": "node_voice_solemn",
            "title": "🎙️ VibeVoice 1.5B (Locución Documental es-emilio)",
            "category": "voice",
            "color": "#10b981",
            "x": 740, "y": 140, "width": 290, "enabled": True,
            "inputs": [{"id": "f_in", "name": "facts_dossier", "label": "Dossier"}],
            "outputs": [{"id": "v_out", "name": "voice_audio", "label": "Voz Documental"}],
            "parameters": [
                {"key": "cadence", "label": "Cadencia Narrativa", "type": "text", "value": "Sobria, solemne e imparcial (Estilo BBC / Grandes Documentales)"}
            ]
        },
        {
            "id": "node_vox_quotes_subtitles",
            "title": "📜 Subtítulos Vox con Citas & Mapas",
            "category": "subtitles",
            "color": "#f59e0b",
            "x": 740, "y": 380, "width": 290, "enabled": True,
            "inputs": [{"id": "v_in", "name": "voice_audio", "label": "Audio"}],
            "outputs": [{"id": "sub_out", "name": "subtitles_ass", "label": "Subtítulos Dinámicos ASS"}],
            "parameters": [
                {"key": "quote_highlight", "label": "Resaltado de Citas Textuales", "type": "text", "value": "Tipografía Serif Italic con animaciones de entrada suaves"}
            ]
        },
        {
            "id": "node_doc_render",
            "title": "🎞️ FFmpeg Máster Histórico & Ducking -22dB",
            "category": "render",
            "color": "#06b6d4",
            "x": 1070, "y": 240, "width": 290, "enabled": True,
            "inputs": [
                {"id": "c1_in", "name": "restored_clips", "label": "Fotos Restauradas"},
                {"id": "c2_in", "name": "recreation_clips", "label": "Recreaciones"},
                {"id": "v_in", "name": "voice_audio", "label": "Locución"},
                {"id": "s_in", "name": "subtitles_ass", "label": "Subtítulos"}
            ],
            "outputs": [{"id": "master_out", "name": "final_video", "label": "Vídeo Final"}],
            "parameters": [
                {"key": "ducking_db", "label": "Nivel de Ducking (dB)", "type": "number", "value": -22}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_hermes_scraping", "from_socket": "photos_out", "to_node": "node_restoration_nanobanana", "to_socket": "p_in"},
        {"id": "c2", "from_node": "node_hermes_scraping", "from_socket": "facts_out", "to_node": "node_gap_filler_flow", "to_socket": "f_in"},
        {"id": "c3", "from_node": "node_hermes_scraping", "from_socket": "facts_out", "to_node": "node_voice_solemn", "to_socket": "f_in"},
        {"id": "c4", "from_node": "node_voice_solemn", "from_socket": "v_out", "to_node": "node_vox_quotes_subtitles", "to_socket": "v_in"},
        {"id": "c5", "from_node": "node_restoration_nanobanana", "from_socket": "restored_out", "to_node": "node_doc_render", "to_socket": "c1_in"},
        {"id": "c6", "from_node": "node_gap_filler_flow", "from_socket": "recreation_out", "to_node": "node_doc_render", "to_socket": "c2_in"},
        {"id": "c7", "from_node": "node_voice_solemn", "from_socket": "v_out", "to_node": "node_doc_render", "to_socket": "v_in"},
        {"id": "c8", "from_node": "node_vox_quotes_subtitles", "from_socket": "sub_out", "to_node": "node_doc_render", "to_socket": "s_in"}
    ]
}


# =====================================================================
# 3. CITY ROUTES & MUSIC BEATS PIPELINE & INTERVIEW
# =====================================================================
CITY_ROUTES_GRAPH = {
    "version": "1.0.0",
    "name": "City Routes & Music Beats 4K Pipeline",
    "nodes": [
        {
            "id": "node_route_mapper",
            "title": "📍 Mapeador de Ruta Urbana & Coordenadas",
            "category": "programacion",
            "color": "#38bdf8",
            "x": 50, "y": 140, "width": 300, "enabled": True,
            "inputs": [],
            "outputs": [
                {"id": "waypoints_out", "name": "waypoints", "label": "Puntos de Interés GPS"},
                {"id": "facts_out", "name": "city_facts", "label": "Datos Curiosos Urbanos"}
            ],
            "parameters": [
                {"key": "city_name", "label": "Ruta / Puntos GPS (Libre)", "type": "text", "value": "Puntos de paso y arquitectura definidos por el usuario o investigación"},
                {"key": "vibe", "label": "Atmósfera Urbana", "type": "text", "value": "Moderna, vanguardista y con iluminación cinemática"}
            ]
        },
        {
            "id": "node_flow_orbital_sweeps",
            "title": "🚁 Google Flow Playwright 4K Vuelos Orbitales",
            "category": "visual",
            "color": "#ec4899",
            "x": 400, "y": 100, "width": 320, "enabled": True, "is_loop": True,
            "inputs": [{"id": "w_in", "name": "waypoints", "label": "Puntos GPS"}],
            "outputs": [{"id": "sweeps_out", "name": "orbital_clips", "label": "Tomas Aéreas 4K"}],
            "parameters": [
                {"key": "camera_motion", "label": "Movimiento de Cámara Óptico", "type": "text", "value": "Vuelo orbital suave 360° continuo a 60 fps"}
            ]
        },
        {
            "id": "node_flow_music_beats",
            "title": "🎧 Flow Music Lyria 3 (Beats & BPM Sync)",
            "category": "music",
            "color": "#eab308",
            "x": 400, "y": 380, "width": 320, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "music_out", "name": "beats_audio", "label": "Banda Sonora a Tempo Constante"}],
            "parameters": [
                {"key": "genre", "label": "Estilo de Beat & Tempo", "type": "text", "value": "Electronic City Synthwave a tempo constante (BPM sincronizado)"}
            ]
        },
        {
            "id": "node_factoids_lower_thirds",
            "title": "🏷️ Overlays Gráficos Vox (Datos Curiosos)",
            "category": "programacion",
            "color": "#a855f7",
            "x": 750, "y": 140, "width": 300, "enabled": True,
            "inputs": [{"id": "f_in", "name": "city_facts", "label": "Datos Curiosos"}],
            "outputs": [{"id": "overlays_out", "name": "graphics_overlay", "label": "Capa Gráfica HTML5/Remotion"}],
            "parameters": [
                {"key": "card_style", "label": "Diseño de Rótulos & Datos", "type": "text", "value": "Minimalista Glassmorphism con telemetría HUD"}
            ]
        },
        {
            "id": "node_beat_cutter_render",
            "title": "⚡ FFmpeg Beat-Cutter & Render 4K 60fps",
            "category": "render",
            "color": "#06b6d4",
            "x": 1090, "y": 240, "width": 300, "enabled": True,
            "inputs": [
                {"id": "v_in", "name": "orbital_clips", "label": "Tomas Aéreas"},
                {"id": "m_in", "name": "beats_audio", "label": "BGM Beats"},
                {"id": "g_in", "name": "graphics_overlay", "label": "Gráficos"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Vídeo Musical Final"}],
            "parameters": [
                {"key": "cut_every_bars", "label": "Pauta de Montaje & Corte", "type": "text", "value": "Corte de plano sincronizado con compases musicales y transiciones suaves"}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_route_mapper", "from_socket": "waypoints_out", "to_node": "node_flow_orbital_sweeps", "to_socket": "w_in"},
        {"id": "c2", "from_node": "node_route_mapper", "from_socket": "facts_out", "to_node": "node_factoids_lower_thirds", "to_socket": "f_in"},
        {"id": "c3", "from_node": "node_flow_orbital_sweeps", "from_socket": "sweeps_out", "to_node": "node_beat_cutter_render", "to_socket": "v_in"},
        {"id": "c4", "from_node": "node_flow_music_beats", "from_socket": "music_out", "to_node": "node_beat_cutter_render", "to_socket": "m_in"},
        {"id": "c5", "from_node": "node_factoids_lower_thirds", "from_socket": "overlays_out", "to_node": "node_beat_cutter_render", "to_socket": "g_in"}
    ]
}


# =====================================================================
# 4. VIRAL SHORTS & HOOKS PIPELINE & INTERVIEW
# =====================================================================
VIRAL_SHORTS_GRAPH = {
    "version": "1.0.0",
    "name": "Viral Shorts & Retention Hooks Pipeline",
    "nodes": [
        {
            "id": "node_hook_generator",
            "title": "🪝 Generador de Gancho Inicial (3s)",
            "category": "llm",
            "color": "#c084fc",
            "x": 50, "y": 140, "width": 280, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "hook_out", "name": "hook_script", "label": "Gancho A/B & Guion Rápido"}],
            "parameters": [
                {"key": "hook_type", "label": "Estrategia del Gancho", "type": "text", "value": "Gancho de impacto adaptado a la temática investigada"}
            ]
        },
        {
            "id": "node_fast_visuals",
            "title": "⚡ Generador Visual Acelerado (Stock + FLUX 3)",
            "category": "visual",
            "color": "#ec4899",
            "x": 370, "y": 100, "width": 310, "enabled": True, "is_loop": True,
            "inputs": [{"id": "h_in", "name": "hook_script", "label": "Guion"}],
            "outputs": [{"id": "clips_out", "name": "fast_clips", "label": "Clips de 1.5s - 2.5s"}],
            "parameters": [
                {"key": "cut_speed", "label": "Velocidad de Corte", "type": "text", "value": "Tomas rápidas de 1.8s con alto dinamismo visual"}
            ]
        },
        {
            "id": "node_karaoke_subtitles",
            "title": "🔤 Subtítulos Karaoke Flúor (.ass)",
            "category": "subtitles",
            "color": "#f59e0b",
            "x": 370, "y": 380, "width": 310, "enabled": True,
            "inputs": [{"id": "h_in", "name": "hook_script", "label": "Guion"}],
            "outputs": [{"id": "subs_out", "name": "karaoke_ass", "label": "Subtítulos Karaoke"}],
            "parameters": [
                {"key": "font_color", "label": "Estilo de Subtítulos", "type": "text", "value": "Amarillo flúor palabra por palabra con rebote sutil"}
            ]
        },
        {
            "id": "node_sfx_impacts",
            "title": "💥 Generador de SFX & Impactos Acústicos",
            "category": "music",
            "color": "#eab308",
            "x": 720, "y": 380, "width": 300, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "sfx_out", "name": "sfx_audio", "label": "Pista de Efectos Sonoros"}],
            "parameters": [
                {"key": "interval_sfx", "label": "Frecuencia de Impactos", "type": "text", "value": "Whooshes, swooshes e impactos de campana cada 3 segundos"}
            ]
        },
        {
            "id": "node_shorts_render",
            "title": "📱 Render 9:16 Vertical 60fps",
            "category": "render",
            "color": "#06b6d4",
            "x": 1050, "y": 240, "width": 300, "enabled": True,
            "inputs": [
                {"id": "v_in", "name": "fast_clips", "label": "Clips"},
                {"id": "s_in", "name": "karaoke_ass", "label": "Karaoke"},
                {"id": "sfx_in", "name": "sfx_audio", "label": "SFX"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Vídeo Final 9:16"}],
            "parameters": [
                {"key": "framerate", "label": "Tasa de Cuadros", "type": "text", "value": "60 fps ultra-fluido para plataformas móviles"}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_hook_generator", "from_socket": "hook_out", "to_node": "node_fast_visuals", "to_socket": "h_in"},
        {"id": "c2", "from_node": "node_hook_generator", "from_socket": "hook_out", "to_node": "node_karaoke_subtitles", "to_socket": "h_in"},
        {"id": "c3", "from_node": "node_fast_visuals", "from_socket": "clips_out", "to_node": "node_shorts_render", "to_socket": "v_in"},
        {"id": "c4", "from_node": "node_karaoke_subtitles", "from_socket": "subs_out", "to_node": "node_shorts_render", "to_socket": "s_in"},
        {"id": "c5", "from_node": "node_sfx_impacts", "from_socket": "sfx_out", "to_node": "node_shorts_render", "to_socket": "sfx_in"}
    ]
}


# =====================================================================
# 5. DEEP EXPLAINER & VIDEO ESSAY PIPELINE & INTERVIEW
# =====================================================================
DEEP_EXPLAINER_GRAPH = {
    "version": "1.0.0",
    "name": "Deep Explainer & Video Essay Pipeline",
    "nodes": [
        {
            "id": "node_dialectical_script",
            "title": "🧠 Guion Dialéctico en 3 Actos (Tesis-Antítesis-Síntesis)",
            "category": "llm",
            "color": "#c084fc",
            "x": 50, "y": 140, "width": 310, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "script_out", "name": "essay_script", "label": "Guion Estructurado"}],
            "parameters": [
                {"key": "structure", "label": "Estructura Narrativa", "type": "text", "value": "Tesis profunda, análisis de contraargumentos y síntesis prospectiva"}
            ]
        },
        {
            "id": "node_remotion_charts",
            "title": "📊 Infografías Animadas Remotion React TSX",
            "category": "programacion",
            "color": "#a855f7",
            "x": 400, "y": 100, "width": 320, "enabled": True, "is_loop": True,
            "inputs": [{"id": "s_in", "name": "essay_script", "label": "Datos"}],
            "outputs": [{"id": "charts_out", "name": "motion_charts", "label": "Clips de Gráficos 4K"}],
            "parameters": [
                {"key": "chart_theme", "label": "Estilo de Infografía", "type": "text", "value": "Dark Glassmorphism con curvas spline animadas y tipografía Inter"}
            ]
        },
        {
            "id": "node_voice_contemplative",
            "title": "🎙️ VibeVoice 1.5B (Locución Pensativa / Ensayo)",
            "category": "voice",
            "color": "#10b981",
            "x": 400, "y": 380, "width": 320, "enabled": True,
            "inputs": [{"id": "s_in", "name": "essay_script", "label": "Guion"}],
            "outputs": [{"id": "v_out", "name": "essay_voice", "label": "Audio Reflexivo"}],
            "parameters": [
                {"key": "pacing", "label": "Ritmo de Locución", "type": "text", "value": "Cadencia pausada, articulada y reflexiva"}
            ]
        },
        {
            "id": "node_essay_render",
            "title": "🎬 Ensamblaje Master Videoensayo 4K",
            "category": "render",
            "color": "#06b6d4",
            "x": 760, "y": 240, "width": 300, "enabled": True,
            "inputs": [
                {"id": "ch_in", "name": "motion_charts", "label": "Infografías"},
                {"id": "v_in", "name": "essay_voice", "label": "Voz"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Vídeo Final"}],
            "parameters": [
                {"key": "aspect", "label": "Relación de Aspecto", "type": "text", "value": "16:9 Panorámico Master 4K"}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_dialectical_script", "from_socket": "script_out", "to_node": "node_remotion_charts", "to_socket": "s_in"},
        {"id": "c2", "from_node": "node_dialectical_script", "from_socket": "script_out", "to_node": "node_voice_contemplative", "to_socket": "s_in"},
        {"id": "c3", "from_node": "node_remotion_charts", "from_socket": "charts_out", "to_node": "node_essay_render", "to_socket": "ch_in"},
        {"id": "c4", "from_node": "node_voice_contemplative", "from_socket": "v_out", "to_node": "node_essay_render", "to_socket": "v_in"}
    ]
}


# =====================================================================
# 6. TOURS FPV Y STORYTELLING URBANO 4K PIPELINE & INTERVIEW
# =====================================================================
FPV_URBAN_GRAPH = {
    "version": "1.0.0",
    "name": "Tours FPV y Storytelling Urbano 4K/60fps Pipeline",
    "nodes": [
        {
            "id": "node_flight_planner",
            "title": "🚁 Plan de Vuelo 3D, Splines & Shotlist",
            "category": "programacion",
            "color": "#38bdf8",
            "x": 50, "y": 140, "width": 300, "enabled": True,
            "inputs": [],
            "outputs": [
                {"id": "waypoints_out", "name": "waypoints", "label": "Waypoints 3D GPS/Z"},
                {"id": "shotlist_out", "name": "shotlist", "label": "Shotlist Canónico 7 Planos"}
            ],
            "parameters": [
                {"key": "city_route", "label": "Ruta y Puntos Emblemáticos", "type": "text", "value": "Puntos de paso GPS definidos por el usuario e investigación"},
                {"key": "flight_physics", "label": "Dinámica de Vuelo FPV", "type": "text", "value": "Acrobático & Extremo (Dives de 140 km/h y slaloms 6-ejes)"}
            ]
        },
        {
            "id": "node_real_scraper",
            "title": "🌐 Scraper 4K/8K & Grounding Factual",
            "category": "scraping",
            "color": "#10b981",
            "x": 380, "y": 80, "width": 320, "enabled": True,
            "inputs": [{"id": "w_in", "name": "waypoints", "label": "Waypoints 3D"}],
            "outputs": [{"id": "ground_out", "name": "ground_images", "label": "Fotos Reales Auditadas >5KB"}],
            "parameters": [
                {"key": "min_resolution", "label": "Resolución Mínima", "type": "text", "value": "3840x2160 (4K UHD)"},
                {"key": "laplacian_threshold", "label": "Umbral de Nitidez", "type": "number", "value": 100.0}
            ]
        },
        {
            "id": "node_7kf_reimaginer",
            "title": "🎨 Nano Banana Pro: 7 Keyframes Consistentes",
            "category": "image",
            "color": "#f59e0b",
            "x": 730, "y": 80, "width": 320, "enabled": True,
            "inputs": [
                {"id": "g_in", "name": "ground_images", "label": "Fotos Reales"},
                {"id": "s_in", "name": "shotlist", "label": "Shotlist"}
            ],
            "outputs": [{"id": "kf_out", "name": "kf_packs", "label": "Packs de 7 Keyframes por Plano"}],
            "parameters": [
                {"key": "color_science", "label": "Ciencia de Color y Grano", "type": "text", "value": "ARRI Alexa LF + Kodak Vision3 500T 35mm Grain"},
                {"key": "optics", "label": "Simulación Óptica", "type": "text", "value": "Ultra-wide Anamorphic 14mm f/2.8"}
            ]
        },
        {
            "id": "node_google_flow_omni",
            "title": "⚡ Google Flow Gemini Omni Flash (60fps & Foley)",
            "category": "visual",
            "color": "#ec4899",
            "x": 1080, "y": 80, "width": 340, "enabled": True, "is_loop": True,
            "inputs": [
                {"id": "k_in", "name": "kf_packs", "label": "7 Keyframes"},
                {"id": "sh_in", "name": "shotlist", "label": "Shotlist"}
            ],
            "outputs": [{"id": "clips_out", "name": "fpv_clips", "label": "Clips FPV 60fps con Foley"}],
            "parameters": [
                {"key": "engine", "label": "Motor de Vídeo", "type": "text", "value": "gemini-omni-flash-preview"},
                {"key": "foley_doppler", "label": "Foley & Doppler Nativo", "type": "boolean", "value": True}
            ]
        },
        {
            "id": "node_audio_flow_narrator",
            "title": "🎙️ Locución TTS & Flow Beat Sync (118 BPM)",
            "category": "music",
            "color": "#eab308",
            "x": 730, "y": 380, "width": 320, "enabled": True,
            "inputs": [{"id": "sh_audio_in", "name": "shotlist", "label": "Guion & Timings"}],
            "outputs": [{"id": "audio_out", "name": "master_audio_track", "label": "Audio Master Ducking -18dB"}],
            "parameters": [
                {"key": "music_bpm", "label": "Tempo de la Música", "type": "number", "value": 118},
                {"key": "master_lufs", "label": "Normalización EBU R128", "type": "number", "value": -14.0}
            ]
        },
        {
            "id": "node_remotion_3d_hud_master",
            "title": "🏷️ Remotion Master: Overlays 3D & Telemetría HUD",
            "category": "render",
            "color": "#06b6d4",
            "x": 1450, "y": 200, "width": 340, "enabled": True,
            "inputs": [
                {"id": "v_in", "name": "fpv_clips", "label": "Clips FPV 60fps"},
                {"id": "a_in", "name": "master_audio_track", "label": "Audio Master"},
                {"id": "s_in", "name": "shotlist", "label": "Plan de Vuelo"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Vídeo Master 4K 60fps"}],
            "parameters": [
                {"key": "hud_theme", "label": "Estilo HUD Telemetría", "type": "text", "value": "Glassmorphism Cyberpunk con Altímetro/Velocímetro"},
                {"key": "spatial_3d_titles", "label": "Rótulos Anclados en Espacio 3D", "type": "boolean", "value": True}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_flight_planner", "from_socket": "waypoints_out", "to_node": "node_real_scraper", "to_socket": "w_in"},
        {"id": "c2", "from_node": "node_flight_planner", "from_socket": "shotlist_out", "to_node": "node_7kf_reimaginer", "to_socket": "s_in"},
        {"id": "c3", "from_node": "node_real_scraper", "from_socket": "ground_out", "to_node": "node_7kf_reimaginer", "to_socket": "g_in"},
        {"id": "c4", "from_node": "node_7kf_reimaginer", "from_socket": "kf_out", "to_node": "node_google_flow_omni", "to_socket": "k_in"},
        {"id": "c5", "from_node": "node_flight_planner", "from_socket": "shotlist_out", "to_node": "node_google_flow_omni", "to_socket": "sh_in"},
        {"id": "c6", "from_node": "node_flight_planner", "from_socket": "shotlist_out", "to_node": "node_audio_flow_narrator", "to_socket": "sh_audio_in"},
        {"id": "c7", "from_node": "node_google_flow_omni", "from_socket": "clips_out", "to_node": "node_remotion_3d_hud_master", "to_socket": "v_in"},
        {"id": "c8", "from_node": "node_audio_flow_narrator", "from_socket": "audio_out", "to_node": "node_remotion_3d_hud_master", "to_socket": "a_in"},
        {"id": "c9", "from_node": "node_flight_planner", "from_socket": "shotlist_out", "to_node": "node_remotion_3d_hud_master", "to_socket": "s_in"}
    ]
}


# =====================================================================
# 7. TOURS URBANOS FLOW REAL 4K & BEAT SYNC (METRAJE REAL + PANELES HUD)
# =====================================================================
FPV_REAL_FLOW_GRAPH = {
    "version": "1.0.0",
    "name": "Tours Urbanos Flow Real 4K & Beat-Sync Pipeline",
    "nodes": [
        {
            "id": "node_music_beat_analyzer",
            "title": "🎵 Flow Music Beat-Detector & Transientes",
            "category": "music",
            "color": "#8b5cf6",
            "x": 50, "y": 140, "width": 300, "enabled": True,
            "inputs": [],
            "outputs": [
                {"id": "beat_grid_out", "name": "beat_grid", "label": "Grid de Beats & Transientes (118-128 BPM)"},
                {"id": "audio_track_out", "name": "master_audio", "label": "Pista de Audio Procesada"}
            ],
            "parameters": [
                {"key": "audio_source", "label": "Fuente de Audio", "type": "text", "value": "Audio subido por el usuario o Flow Music generado"},
                {"key": "bpm_target", "label": "Detección de BPM", "type": "number", "value": 118}
            ]
        },
        {
            "id": "node_real_footage_downloader",
            "title": "🏙️ Ingesta de Vídeos & Fotos Reales 4K",
            "category": "scraping",
            "color": "#10b981",
            "x": 400, "y": 80, "width": 320, "enabled": True,
            "inputs": [{"id": "bg_in", "name": "beat_grid", "label": "Beat Grid"}],
            "outputs": [{"id": "footage_out", "name": "real_4k_clips", "label": "Metraje Real 4K UHD Filtrado"}],
            "parameters": [
                {"key": "stock_source", "label": "Fuentes de Metraje", "type": "text", "value": "Pexels 4K UHD + Drones Urbanos + Street View 360 HD"},
                {"key": "min_quality", "label": "Calidad Mínima", "type": "text", "value": "3840x2160 @ 60fps"}
            ]
        },
        {
            "id": "node_flow_speed_cutter",
            "title": "⚡ Montaje Rítmico, Speed-Ramps & Transiciones",
            "category": "visual",
            "color": "#f59e0b",
            "x": 760, "y": 80, "width": 340, "enabled": True,
            "inputs": [
                {"id": "clips_in", "name": "real_4k_clips", "label": "Clips Reales"},
                {"id": "beats_in", "name": "beat_grid", "label": "Beats"}
            ],
            "outputs": [{"id": "synced_video_out", "name": "synced_cut", "label": "Línea de Tiempo Cortada al Beat"}],
            "parameters": [
                {"key": "cut_mode", "label": "Modo de Corte", "type": "text", "value": "Al golpe de Kick/Snare con Speed-Ramps dinámicos"},
                {"key": "transitions", "label": "Efectos de Transición", "type": "text", "value": "Whip Pan, Zoom Glitch & Flash Cut"}
            ]
        },
        {
            "id": "node_explainer_panels_hud",
            "title": "🏷️ Paneles Explicativos Gráficos & Subtítulos Flow",
            "category": "render",
            "color": "#06b6d4",
            "x": 1140, "y": 140, "width": 340, "enabled": True,
            "inputs": [
                {"id": "v_cut_in", "name": "synced_cut", "label": "Corte Sincronizado"},
                {"id": "a_proc_in", "name": "master_audio", "label": "Audio Master"}
            ],
            "outputs": [{"id": "final_video_out", "name": "final_video", "label": "Vídeo Musical Master 4K"}],
            "parameters": [
                {"key": "panel_style", "label": "Diseño de Paneles", "type": "text", "value": "Glassmorphism Moderno con Datos Urbanos y Callouts"},
                {"key": "subtitle_sync", "label": "Alineación de Letras/Subtítulos", "type": "text", "value": "Word-by-word kinetic highlight"}
            ]
        }
    ],
    "connections": [
        {"id": "rf_c1", "from_node": "node_music_beat_analyzer", "from_socket": "beat_grid_out", "to_node": "node_real_footage_downloader", "to_socket": "bg_in"},
        {"id": "rf_c2", "from_node": "node_real_footage_downloader", "from_socket": "footage_out", "to_node": "node_flow_speed_cutter", "to_socket": "clips_in"},
        {"id": "rf_c3", "from_node": "node_music_beat_analyzer", "from_socket": "beat_grid_out", "to_node": "node_flow_speed_cutter", "to_socket": "beats_in"},
        {"id": "rf_c4", "from_node": "node_flow_speed_cutter", "from_socket": "synced_video_out", "to_node": "node_explainer_panels_hud", "to_socket": "v_cut_in"},
        {"id": "rf_c5", "from_node": "node_music_beat_analyzer", "from_socket": "audio_track_out", "to_node": "node_explainer_panels_hud", "to_socket": "a_proc_in"}
    ]
}


# =====================================================================
# CATÁLOGO MAESTRO DE ARQUETIPOS DE PRODUCCIÓN
# =====================================================================
ARCHETYPES_CATALOG: Dict[str, WorkflowArchetype] = {
    "PIXAR_3D_ANIMATION": WorkflowArchetype(
        id="PIXAR_3D_ANIMATION",
        name="Cuentos & Animación 3D (Pixar Style)",
        icon="🧸",
        tag="ANIMACIÓN 3D",
        description="Producción de historias animadas con consistencia de personajes, iluminación cinematográfica 3D, banda sonora orquestal de cuento y foley cómico.",
        category="storytelling",
        target_audience="Familiar, Infantil, Creativo",
        default_aspect_ratio="16:9",
        visual_strategy=VisualStrategy.SINGLE_ENGINE,
        default_voice_engine="vibevoice",
        default_voice_id="es-emilio",
        default_music_genre="pixar_orchestral",
        interview_schema=[
            InterviewQuestion(key="character_name", question="¿Cómo se llama el personaje principal y qué criatura o persona es?", description="Ejemplo: 'Lupo, un pequeño lobo curioso con bufanda roja'", question_type="text", default_value="Lupo el lobezno curioso"),
            InterviewQuestion(key="story_conflict", question="¿Cuál es el conflicto o aventura de la historia?", description="Ejemplo: 'Quiere aprender a pintar auroras boreales en el cielo'", question_type="text", default_value="Descubrir cómo encender las estrellas apagadas"),
            InterviewQuestion(key="emotional_tone", question="¿Qué emoción predomina en el cuento?", description="Selecciona el tono emotivo", question_type="select", options=["Tierno y Conmovedor", "Divertido y Cómico", "Aventurero y Épico"], default_value="Tierno y Conmovedor"),
            InterviewQuestion(key="visual_environment", question="¿En qué mundo o escenario ocurre la historia?", description="Selecciona el entorno visual", question_type="select", options=["Bosque Mágico de Cuento", "Ciudad Futurista Flotante", "Fondo Marino Luminoso", "Pueblo Nevado Acogedor"], default_value="Bosque Mágico de Cuento")
        ],
        pipeline_graph=PIXAR_3D_GRAPH
    ),

    "HISTORICAL_SCRAPING": WorkflowArchetype(
        id="HISTORICAL_SCRAPING",
        name="Documental Histórico & Archivo Real",
        icon="📜",
        tag="DOCUMENTAL RIGUROSO",
        description="Investigación profunda con scraping en archivos históricos, restauración 4K de fotos reales antiguas, recreación de momentos ciegos con IA y citas estilo Vox.",
        category="documentary",
        target_audience="Divulgación, Historia, Académico",
        default_aspect_ratio="16:9",
        visual_strategy=VisualStrategy.HYBRID,
        default_voice_engine="vibevoice",
        default_voice_id="es-emilio",
        default_music_genre="historical_strings",
        interview_schema=[
            InterviewQuestion(key="historical_subject", question="¿Qué personaje, batalla o época histórica deseas documentar?", description="Ejemplo: 'La construcción secreta del Metro de Madrid en 1919'", question_type="text", default_value="La construcción secreta del Metro de Madrid en 1919"),
            InterviewQuestion(key="scraping_depth", question="¿Qué nivel de investigación y scraping deseas aplicar?", description="Selecciona el rigor documental", question_type="select", options=["Exhaustiva (Wikipedia + Commons + Hemerotecas)", "Rápida (Puntos Clave y Citas Principales)", "Enfoque en Curiosidades Poco Conocidas"], default_value="Exhaustiva (Wikipedia + Commons + Hemerotecas)"),
            InterviewQuestion(key="gap_filling_policy", question="¿Cómo tratar momentos históricos sin fotografías existentes?", description="Política de generación visual", question_type="select", options=["Recrear con Google Flow 4K e Imagen 3", "Usar solo ilustraciones históricas y mapas", "Híbrido Restauración + Recreación 35mm"], default_value="Híbrido Restauración + Recreación 35mm")
        ],
        pipeline_graph=HISTORICAL_SCRAPING_GRAPH
    ),

    "CITY_ROUTES_BEATS": WorkflowArchetype(
        id="CITY_ROUTES_BEATS",
        name="Rutas Urbanas & Vídeos Musicales (City Beats)",
        icon="🏙️",
        tag="VÍDEO MUSICAL URBANO",
        description="Recorridos cinemáticos por ciudades con planos orbitales 4K (Google Flow), banda sonora generativa a tempo constante y superposición de datos curiosos.",
        category="music_travel",
        target_audience="Música, Turismo Urbano, Lifestyle",
        default_aspect_ratio="9:16",
        visual_strategy=VisualStrategy.SINGLE_ENGINE,
        default_voice_engine="edge_tts",
        default_voice_id="es-ES-AlvaroNeural",
        default_music_genre="synthwave",
        interview_schema=[
            InterviewQuestion(key="city_and_spots", question="¿Qué ciudad y qué puntos emblemáticos formarán la ruta?", description="Ejemplo: 'Barcelona: Sagrada Familia, Barrio Gótico, Paseo de Gracia, Bunkers'", question_type="text", default_value="Madrid: Gran Vía, Malasaña, Templo de Debod y Cuatro Torres"),
            InterviewQuestion(key="music_beat_style", question="¿Qué estilo musical marcará el ritmo del vídeo?", description="Selecciona el género del beat", question_type="select", options=["Electronic City Synthwave (118 BPM)", "Chill Lo-Fi Hip-Hop (85 BPM)", "Urban Trap / Drill Melódico (135 BPM)", "Nu-Jazz Street (92 BPM)"], default_value="Electronic City Synthwave (118 BPM)"),
            InterviewQuestion(key="facts_focus", question="¿Qué tipo de datos curiosos resaltar en los gráficos Vox?", description="Enfoque de las tarjetas de datos", question_type="select", options=["Secretos Arquitectónicos & Récords", "Gastronomía & Lugares Escondidos", "Historia Urbana & Leyendas", "Moda & Cultura Callejera"], default_value="Secretos Arquitectónicos & Récords")
        ],
        pipeline_graph=CITY_ROUTES_GRAPH
    ),

    "VIRAL_SHORTS_HOOK": WorkflowArchetype(
        id="VIRAL_SHORTS_HOOK",
        name="Viral Shorts & Retención Extrema (TikTok / Reels)",
        icon="⚡",
        tag="ALTA RETENCIÓN",
        description="Vídeos verticales de ritmo vertiginoso (1.8s por toma), gancho de choque en los primeros 3 segundos, subtítulos karaoke amarillo flúor y SFX de impacto.",
        category="social_media",
        target_audience="TikTok, Instagram Reels, YouTube Shorts",
        default_aspect_ratio="9:16",
        visual_strategy=VisualStrategy.HYBRID,
        default_voice_engine="vibevoice",
        default_voice_id="es-emilio",
        default_music_genre="energetic_bass",
        interview_schema=[
            InterviewQuestion(key="hook_theme", question="¿Cuál es el tema central o la curiosidad impactante?", description="Ejemplo: 'Los 3 lugares de la Tierra donde la gravedad parece no funcionar'", question_type="text", default_value="Las 3 tecnologías secretas que cambiarán el mundo este año"),
            InterviewQuestion(key="hook_style", question="¿Qué fórmula de gancho inicial prefieres?", description="Tipo de apertura", question_type="select", options=["Pregunta Shock ('¿Sabías que...?')", "Desafío de Creencia ('Todo lo que creías sobre esto es mentira')", "Dato Prohibido ('Lo que las empresas no quieren que sepas')"], default_value="Pregunta Shock ('¿Sabías que...?')"),
            InterviewQuestion(key="call_to_action", question="¿Qué llamada a la acción incluir al final?", description="Cierre para engagement", question_type="select", options=["Pregunta a los comentarios ('¿Qué opinas tú?')", "Sígueme para parte 2", "Guarda este vídeo antes de que lo borren"], default_value="Pregunta a los comentarios ('¿Qué opinas tú?')")
        ],
        pipeline_graph=VIRAL_SHORTS_GRAPH
    ),

    "DEEP_EXPLAINER_ESSAY": WorkflowArchetype(
        id="DEEP_EXPLAINER_ESSAY",
        name="Deep Explainer & Videoensayo Dialéctico",
        icon="📊",
        tag="VIDEOENSAYO VOX",
        description="Estructura argumentativa en tres actos (Tesis, Antítesis y Síntesis), gráficos animados generados con Remotion React y música minimalista de fondo.",
        category="educational",
        target_audience="YouTube Largo, Análisis Económico/Tecnológico",
        default_aspect_ratio="16:9",
        visual_strategy=VisualStrategy.HYBRID,
        default_voice_engine="vibevoice",
        default_voice_id="es-emilio",
        default_music_genre="minimal_ambient",
        interview_schema=[
            InterviewQuestion(key="essay_thesis", question="¿Cuál es la tesis central o la pregunta de fondo?", description="Ejemplo: '¿Por qué las baterías de estado sólido tardan tanto en comercializarse?'", question_type="text", default_value="¿Por qué la crisis de los semiconductores redefinió la geopolítica global?"),
            InterviewQuestion(key="data_points", question="¿Qué datos estadísticos o evoluciones temporales son clave?", description="Ejemplo: 'Evolución de costes de 2015 a 2026 y cuotas de mercado'", question_type="text", default_value="Cuotas de mercado de fundiciones (TSMC vs Intel) y aumento de costes por nodo"),
            InterviewQuestion(key="visual_infographics_style", question="¿Qué estética prefieres para las infografías?", description="Estilo de diseño animado", question_type="select", options=["Estilo Vox Minimalista (Fondo Oscuro + Acentos Neón)", "Estilo Bloomberg Terminal / Cuantitativo", "Estilo Editorial New York Times"], default_value="Estilo Vox Minimalista (Fondo Oscuro + Acentos Neón)")
        ],
        pipeline_graph=DEEP_EXPLAINER_GRAPH
    ),

    "FPV_URBAN_REAL_FLOW": WorkflowArchetype(
        id="FPV_URBAN_REAL_FLOW",
        name="Tours Urbanos Flow Real 4K & Beat-Sync",
        icon="🏙️",
        tag="FLOW MUSIC & VÍDEO REAL 4K",
        description="Vídeos rítmicos y musicales sincronizados con Flow Music. Ingesta de vídeos y fotos reales 4K (stock/scraping), montaje al golpe de beat (118-128 BPM), paneles explicativos, speed-ramps, transiciones de impacto y telemetría visual.",
        category="travel_fpv_action",
        target_audience="Reels Musicales, Turismo Urbano 4K, Viral Shorts, Lifestyle & Beats",
        default_aspect_ratio="9:16",
        visual_strategy=VisualStrategy.SINGLE_ENGINE,
        default_voice_engine="edge_tts",
        default_voice_id="es-ES-AlvaroNeural",
        default_music_genre="flow_synthwave",
        interview_schema=[
            InterviewQuestion(
                key="audio_source_and_bpm",
                question="¿Qué pista de audio o ritmo musical liderará el montaje?",
                description="Indica si usarás un audio propio (.mp3) o generarás Flow Music a 118-128 BPM",
                question_type="select",
                options=[
                    "Audio Personal Subido (Sincronización automática de transientes y beats)",
                    "Flow Chillhop 118 BPM (Relajado, rítmico con bajos profundos)",
                    "Cyber Darksynth 128 BPM (Alta energía, sintes potentes y cortes rápidos)",
                    "Trap / Hip-Hop Instrumental (Pegada de bombo/caja para cortes secos)"
                ],
                default_value="Audio Personal Subido (Sincronización automática de transientes y beats)"
            ),
            InterviewQuestion(
                key="city_and_visual_spots",
                question="¿Qué ciudad y localizaciones reales 4K protagonizan el vídeo?",
                description="Ejemplo: 'Tokio: Shibuya Crossing, Shinjuku Neón, Torre de Tokio y Akihabara'",
                question_type="text",
                default_value="Tokio: Shibuya Crossing, Shinjuku Neón, Torre de Tokio y Akihabara"
            ),
            InterviewQuestion(
                key="explainer_panels_style",
                question="¿Qué estilo de paneles explicativos y efectos premium deseas?",
                description="Define la apariencia de los datos, callouts y subtítulos cinemáticos",
                question_type="select",
                options=[
                    "Glassmorphism Moderno (Tarjetas translúcidas con bordes de luz y datos clave)",
                    "Cyberpunk HUD (Telemetría de coordenadas, velocidad y tipografía neón)",
                    "Minimalista Editorial (Rótulos limpios, tipografía sans-serif y zoom suave)",
                    "Dinámico Viral (Subtítulos palabra por palabra con emojis y resaltado de color)"
                ],
                default_value="Glassmorphism Moderno (Tarjetas translúcidas con bordes de luz y datos clave)"
            )
        ],
        pipeline_graph=FPV_REAL_FLOW_GRAPH
    ),

    "CHRONODRIFT_TRITEMPORAL": WorkflowArchetype(
        id="CHRONODRIFT_TRITEMPORAL",
        name="CHRONODRIFT: Urban Time Travel 4K (1626 ➔ 2026 ➔ 2226)",
        icon="🛰️",
        tag="CHRONODRIFT TRITEMPORAL 4K",
        description="Pipeline oficial de CHRONODRIFT: viajes temporales urbanos 4K 60fps con Gemini Omni Flash 6-DoF en Google Flow, 7 keyframes consistentes con Nano Banana Pro, anclaje Street View 360° + OSM, audio 118 BPM con Foley Doppler y HUD Remotion tritemporal.",
        category="travel_fpv_action",
        target_audience="Audiovisual Premium, Historia y Futuro, Viral YouTube 4K, Ciencia & Arquitectura",
        default_aspect_ratio="9:16",
        visual_strategy=VisualStrategy.SINGLE_ENGINE,
        default_voice_engine="edge_tts",
        default_voice_id="es-ES-AlvaroNeural",
        default_music_genre="flow_synthwave",
        interview_schema=[
            InterviewQuestion(
                key="target_city_and_timeline",
                question="¿Qué ciudad y qué puntos emblemáticos compondrán la transformación tritemporal?",
                description="Ejemplo: 'Nueva York: Manhattan / Wall Street (1626 Nuevo Ámsterdam ➔ 2026 Rascacielos ➔ 2226 Mega-Estructuras Flotantes)'",
                question_type="text",
                default_value="Nueva York: Manhattan / Wall Street (1626 Nuevo Ámsterdam ➔ 2026 Rascacielos ➔ 2226 Mega-Estructuras Flotantes)"
            ),
            InterviewQuestion(
                key="temporal_contrast_style",
                question="¿Qué dinámica de transición y match-cut temporal deseas aplicar?",
                description="Define cómo la cámara 6-DoF salta entre siglos manteniendo el mismo vector",
                question_type="select",
                options=[
                    "Match-Cut Fotogramétrico Continuo (La cámara no frena y el mundo cambia a su alrededor)",
                    "Warp Temporal con Glitch y Telemetría HUD (Efecto distorsión cuántica al cruzar años)",
                    "Split-Screen Dinámico Tritemporal (3 épocas visibles en paralelo antes del dive)",
                    "Aceleración FPV a 140 km/h con Foley Doppler Temporal"
                ],
                default_value="Match-Cut Fotogramétrico Continuo (La cámara no frena y el mundo cambia a su alrededor)"
            ),
            InterviewQuestion(
                key="audio_groove_style",
                question="¿Qué diseño de audio y tempo deseas para el viaje temporal?",
                description="BGM rítmico, ducking -18dB y efectos Foley 3D sincronizados",
                question_type="select",
                options=[
                    "Flow Darksynth 118 BPM (Bajo profundo 35Hz, síntesis analógica y foley de viento)",
                    "Chillhop Tritemporal (Batería lo-fi 118 BPM combinada con instrumentos de época)",
                    "Cinematic Hybrid Orchestra (Metales pesados, percusión híbrida y riser temporal)",
                    "Audio Personal Subido (Masterización y ducking automático bajo voz)"
                ],
                default_value="Flow Darksynth 118 BPM (Bajo profundo 35Hz, síntesis analógica y foley de viento)"
            )
        ],
        pipeline_graph=FPV_URBAN_GRAPH
    ),

    "FPV_URBAN_STORYTELLING": WorkflowArchetype(
        id="FPV_URBAN_STORYTELLING",
        name="Tours FPV y Storytelling Urbano 4K",
        icon="🚁",
        tag="TOURS FPV & STORYTELLING",
        description="Vuelos FPV cinemáticos de alta velocidad por metrópolis globales: plan de vuelo 3D, scraping real, 7 keyframes para Gemini Omni Flash, sincronización flow beat y telemetría HUD.",
        category="travel_fpv_action",
        target_audience="Audiovisual Premium, Turismo Urbano, Récords de Arquitectura, Viral Reels",
        default_aspect_ratio="9:16",
        visual_strategy=VisualStrategy.SINGLE_ENGINE,
        default_voice_engine="edge_tts",
        default_voice_id="es-ES-AlvaroNeural",
        default_music_genre="flow_synthwave",
        interview_schema=[
            InterviewQuestion(
                key="target_city_and_landmarks",
                question="¿Qué ciudad y qué puntos emblemáticos compondrán la ruta FPV?",
                description="Ejemplo: 'Tokio: Azotea Scramble Square, Cruce Shibuya, Fachada 109, Callejón Yokocho y Parque Miyashita'",
                question_type="text",
                default_value="Tokio: Azotea Scramble Square, Cruce de Shibuya, Fachada 109, Callejón Yokocho y Parque Miyashita"
            ),
            InterviewQuestion(
                key="fpv_flight_style",
                question="¿Qué estilo y agresividad de vuelo FPV deseas imprimir?",
                description="Define la física de movimiento, aceleraciones y acrobacias de la cámara",
                question_type="select",
                options=[
                    "Acrobático & Extremo (Dives de 140 km/h, slaloms cerrados y giros de 360°)",
                    "Cinemático & Fluido (Vuelos suaves, curvas amplias y paneos majestuosos)",
                    "Cyberpunk Nocturno (Alta velocidad entre luces de neón y lluvia)",
                    "Histórico & Arquitectónico (Aproximaciones de detalle y traspaso de monumentos)"
                ],
                default_value="Acrobático & Extremo (Dives de 140 km/h, slaloms cerrados y giros de 360°)"
            ),
            InterviewQuestion(
                key="narrative_subtext_focus",
                question="¿Cuál es el ángulo narrativo o misterio central de la historia urbana?",
                description="El gancho documental que aportará subtexto a los planos aéreos",
                question_type="select",
                options=[
                    "Secretos de Ingeniería & Rascacielos Invisibles",
                    "Contraste Urbano: Tradición Oculta vs Hipermodernidad",
                    "La Metrópolis que Nunca Duerme (Pulso Nocturno 24/7)",
                    "Historia Olvidada bajo el Asfalto"
                ],
                default_value="Secretos de Ingeniería & Rascacielos Invisibles"
            )
        ],
        pipeline_graph=FPV_URBAN_GRAPH
    ),

    "MADRID_CURIOSITIES_REAL_FLOW": WorkflowArchetype(
        id="MADRID_CURIOSITIES_REAL_FLOW",
        name="Madrid Secreto 4K: Curiosidades Reales & Beat-Sync (3 min)",
        icon="🇪🇸",
        tag="SCRAPING REAL 4K + FLOW MUSIC + 3D HUD",
        description="Vídeo documental y musical de 3 minutos sobre Madrid: investigación profunda de curiosidades ocultas con fuentes verificadas, scraping de metraje real 4K de alta exigencia, sincronización al beat de Flow Music y paneles dinámicos 3D / Glassmorphism en Remotion.",
        category="documentary",
        target_audience="Divulgación Urbana, Curiosidades Históricas, YouTube 4K, Turismo Alternativo",
        default_aspect_ratio="16:9",
        visual_strategy=VisualStrategy.HYBRID,
        default_voice_engine="edge_tts",
        default_voice_id="es-ES-AlvaroNeural",
        default_music_genre="flow_chillhop",
        interview_schema=[
            InterviewQuestion(
                key="madrid_spots_and_secrets",
                question="¿Qué lugares curiosos y secretos de Madrid deseas incluir en el vídeo de 3 minutos?",
                description="Ejemplo: 'Cámara Acorazada Cibeles (oro sumergible), Búnker del Capricho, Estación Fantasma Chamberí, Reloj de Gobernación y Pasadizo Real de la Encarnación'",
                question_type="text",
                default_value="Cámara de Oro Cibeles, Estación Fantasma Chamberí, Búnker Capricho, Ermita San Antonio de la Florida y Pasadizo Real Encarnación"
            ),
            InterviewQuestion(
                key="media_scraping_quality",
                question="¿Qué nivel de exigencia y filtros de scraping deseas aplicar a las imágenes y vídeos reales?",
                description="Filtro laplaciano de nitidez, resolución mínima 4K UHD y descarte automático de marcas de agua / baja calidad",
                question_type="select",
                options=[
                    "Exigencia Máxima 4K/8K (Filtro laplaciano >100, >5MB por foto, bitrate alto en vídeo)",
                    "Híbrido Alta Calidad (Scraping real 4K + Recreación Nano Banana Pro en puntos sin metraje)",
                    "Archivo Histórico & Actual (Contraste hemerotecas 1900 vs 4K 2026)"
                ],
                default_value="Exigencia Máxima 4K/8K (Filtro laplaciano >100, >5MB por foto, bitrate alto en vídeo)"
            ),
            InterviewQuestion(
                key="flow_audio_plan",
                question="¿Qué diseño y estructura musical deseas para el plan de audio de 3 minutos?",
                description="Estructura por compases (Intro -> Beat Drop -> Desarrollo -> Clímax -> Outro) con ducking dinámico -18dB",
                question_type="select",
                options=[
                    "Flow Chillhop 118 BPM (Bajo 35Hz envolvente, ritmo rítmico pausado para locución clara)",
                    "Flow Darksynth 120 BPM (Sintetizadores dinámicos para misterio y ritmo enérgico)",
                    "Audio Personal Subido (Detección de transientes y beat grid automática)"
                ],
                default_value="Flow Chillhop 118 BPM (Bajo 35Hz envolvente, ritmo rítmico pausado para locución clara)"
            ),
            InterviewQuestion(
                key="explainer_panels_3d_style",
                question="¿Qué estilo de paneles explicativos 3D y telemetría deseas para mostrar los datos y fuentes?",
                description="Callouts con coordenadas GPS, datos curiosos, fecha de origen y enlace de fuente verificada",
                question_type="select",
                options=[
                    "Glassmorphism 3D Moderno (Tarjetas translúcidas flotantes con datos técnicos y badges de fuentes)",
                    "Cyberpunk Holographic HUD (Vectores 3D, líneas de tracking y coordenadas en pantalla)",
                    "Minimalista Museo Contemporáneo (Tipografía limpia, acentos dorados y citas bibliográficas)"
                ],
                default_value="Glassmorphism 3D Moderno (Tarjetas translúcidas flotantes con datos técnicos y badges de fuentes)"
            )
        ],
        pipeline_graph=FPV_REAL_FLOW_GRAPH
    )
}


def get_all_archetypes() -> List[WorkflowArchetype]:
    """Retorna todos los arquetipos de producción disponibles."""
    return list(ARCHETYPES_CATALOG.values())


def get_archetype(archetype_id: str) -> Optional[WorkflowArchetype]:
    """Obtiene un arquetipo específico por su ID."""
    return ARCHETYPES_CATALOG.get(archetype_id)
