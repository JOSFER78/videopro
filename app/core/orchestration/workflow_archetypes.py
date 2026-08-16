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
                {"key": "protagonist_type", "label": "Tipo de Personaje", "type": "select", "options": ["Animal Antropomórfico", "Niño Aventurero", "Robot Emotivo", "Criatura Mágica"], "value": "Animal Antropomórfico"},
                {"key": "art_style", "label": "Estilo de Render", "type": "select", "options": ["Pixar 3D Cinematic (Subsurface Scattering)", "Claymation 3D", "Stylized Chibi 4K"], "value": "Pixar 3D Cinematic (Subsurface Scattering)"}
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
                {"key": "tone", "label": "Tono de la Historia", "type": "select", "options": ["Conmovedor / Emotivo", "Comedia Divertida", "Aventura Épica"], "value": "Conmovedor / Emotivo"},
                {"key": "moral", "label": "Moraleja", "type": "text", "value": "La perseverancia y el valor de la amistad"}
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
                {"key": "lora_model", "label": "Modelo LoRA", "type": "select", "options": ["flux-pixar-story-v2", "nanobanana-3d-cinema"], "value": "flux-pixar-story-v2"},
                {"key": "lighting", "label": "Iluminación", "type": "select", "options": ["Golden Hour Suave", "Nocturno Neón Mágico", "Estudio Cálido"], "value": "Golden Hour Suave"}
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
                {"key": "voice_style", "label": "Estilo de Narración", "type": "select", "options": ["Cuentacuentos Emotivo", "Voz Infantil Alegre", "Narrador Épico"], "value": "Cuentacuentos Emotivo"}
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
                {"key": "genre", "label": "Género Musical", "type": "select", "options": ["Pixar Orchestral Waltz", "Whimsical Piano & Strings", "Adventure Brass & Chimes"], "value": "Pixar Orchestral Waltz"}
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
                {"key": "color_grading", "label": "Grading de Color", "type": "select", "options": ["Vibrant Pixar Colors (+15% Sat)", "Pastel Dreamy", "Neutral Cinema"], "value": "Vibrant Pixar Colors (+15% Sat)"}
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
                {"key": "sources", "label": "Fuentes de Scraping", "type": "select", "options": ["Wikipedia + Wikimedia Commons + Web Archive", "Archivos de Noticias Históricas", "Exhaustiva Multi-Fuente"], "value": "Wikipedia + Wikimedia Commons + Web Archive"},
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
                {"key": "grain_35mm", "label": "Emulación Grano 35mm", "type": "select", "options": ["Activado (Cinemático)", "Desactivado (Limpio)"], "value": "Activado (Cinemático)"}
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
                {"key": "fidelity", "label": "Rigor Visual Histórico", "type": "select", "options": ["Estricto Época", "Cinematográfico Dramático"], "value": "Estricto Época"}
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
                {"key": "cadence", "label": "Cadencia Narrativa", "type": "select", "options": ["Sobria e Imparcial (BBC / Canal Historia)", "Dramática Tensa"], "value": "Sobria e Imparcial (BBC / Canal Historia)"}
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
                {"key": "quote_highlight", "label": "Resaltado de Citas Textuales", "type": "select", "options": ["Activado (Tipografía Serif Italic)", "Estándar"], "value": "Activado (Tipografía Serif Italic)"}
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
                {"key": "ducking_db", "label": "Nivel de Ducking", "type": "number", "value": -22}
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
                {"key": "city_name", "label": "Ciudad / Barrio", "type": "text", "value": "Madrid (Gran Vía, Malasaña, Retiro, Cuatro Torres)"},
                {"key": "vibe", "label": "Atmósfera Urbana", "type": "select", "options": ["Moderna & Vanguardista", "Histórica Bohemia", "Nocturna Cyberpunk / Luces"], "value": "Moderna & Vanguardista"}
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
                {"key": "camera_motion", "label": "Movimiento de Cámara", "type": "select", "options": ["Orbital 360° Continuo", "Vuelo Rasante Acelerado", "Dron FPV Cinemático"], "value": "Orbital 360° Continuo"}
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
                {"key": "genre", "label": "Estilo de Beat", "type": "select", "options": ["Chill Lo-Fi Hip-Hop (85 BPM)", "Electronic City Synthwave (118 BPM)", "Urban Trap / Drill Melódico (135 BPM)", "Nu-Jazz Street Beat (92 BPM)"], "value": "Electronic City Synthwave (118 BPM)"}
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
                {"key": "card_style", "label": "Estilo de Tarjeta", "type": "select", "options": ["Minimalista Glassmorphism", "Brutalista Neón", "Mapa Interactivo con Pin"], "value": "Minimalista Glassmorphism"}
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
                {"key": "cut_every_bars", "label": "Corte de Plano", "type": "select", "options": ["Cada 4 compases (Dinámico)", "Cada 8 compases (Relajado)", "En cada drop musical"], "value": "Cada 4 compases (Dinámico)"}
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
                {"key": "hook_type", "label": "Fórmula del Gancho", "type": "select", "options": ["Pregunta Shock ('¿Sabías que...?')", "Desafío de Creencia ('Todo lo que te dijeron es mentira')", "Dato Prohibido / Revelación"], "value": "Pregunta Shock ('¿Sabías que...?')"}
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
                {"key": "cut_speed", "label": "Duración por Toma", "type": "select", "options": ["1.8 segundos (Ultra Dinámico)", "2.5 segundos (Equilibrado)"], "value": "1.8 segundos (Ultra Dinámico)"}
            ]
        },
        {
            "id": "node_karaoke_subtitles",
            "title": "🔤 Subtítulos Karaoke Dinámicos (Amarillo Flúor)",
            "category": "subtitles",
            "color": "#f59e0b",
            "x": 370, "y": 380, "width": 310, "enabled": True,
            "inputs": [{"id": "h_in", "name": "hook_script", "label": "Guion"}],
            "outputs": [{"id": "sub_out", "name": "karaoke_ass", "label": "Subtítulos con Resaltado"}],
            "parameters": [
                {"key": "style", "label": "Animación", "type": "select", "options": ["Palabra Activa Amarillo + Escala Pop", "Rebote Tipo MrBeast", "Caja Blanca con Texto Negro"], "value": "Palabra Activa Amarillo + Escala Pop"}
            ]
        },
        {
            "id": "node_sfx_impacts",
            "title": "💥 Efectos de Impacto SFX (Cada 3s)",
            "category": "music",
            "color": "#eab308",
            "x": 720, "y": 380, "width": 290, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "sfx_out", "name": "sfx_track", "label": "Pista de Efectos Whoosh & Pop"}],
            "parameters": [
                {"key": "density", "label": "Densidad de Efectos", "type": "select", "options": ["Alto (Cada 2-3 segundos)", "Moderado (Solo en transiciones clave)"], "value": "Alto (Cada 2-3 segundos)"}
            ]
        },
        {
            "id": "node_viral_render",
            "title": "📱 Render 9:16 Optimizado para Móviles",
            "category": "render",
            "color": "#06b6d4",
            "x": 1050, "y": 240, "width": 280, "enabled": True,
            "inputs": [
                {"id": "c_in", "name": "fast_clips", "label": "Clips"},
                {"id": "s_in", "name": "karaoke_ass", "label": "Subtítulos"},
                {"id": "x_in", "name": "sfx_track", "label": "SFX"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Short Final"}],
            "parameters": [
                {"key": "fps", "label": "Cuadros por Segundo", "type": "select", "options": ["60 fps (Fluidez Máxima)", "30 fps"], "value": "60 fps (Fluidez Máxima)"}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_hook_generator", "from_socket": "hook_out", "to_node": "node_fast_visuals", "to_socket": "h_in"},
        {"id": "c2", "from_node": "node_hook_generator", "from_socket": "hook_out", "to_node": "node_karaoke_subtitles", "to_socket": "h_in"},
        {"id": "c3", "from_node": "node_fast_visuals", "from_socket": "clips_out", "to_node": "node_viral_render", "to_socket": "c_in"},
        {"id": "c4", "from_node": "node_karaoke_subtitles", "from_socket": "sub_out", "to_node": "node_viral_render", "to_socket": "s_in"},
        {"id": "c5", "from_node": "node_sfx_impacts", "from_socket": "sfx_out", "to_node": "node_viral_render", "to_socket": "x_in"}
    ]
}


# =====================================================================
# 5. DEEP EXPLAINER & VIDEO ESSAY PIPELINE & INTERVIEW
# =====================================================================
DEEP_EXPLAINER_GRAPH = {
    "version": "1.0.0",
    "name": "Deep Explainer & Dialectic Essay Pipeline",
    "nodes": [
        {
            "id": "node_dialectic_script",
            "title": "🧠 Guion Dialéctico (Tesis, Antítesis, Síntesis)",
            "category": "llm",
            "color": "#c084fc",
            "x": 50, "y": 140, "width": 300, "enabled": True,
            "inputs": [],
            "outputs": [{"id": "script_out", "name": "essay_script", "label": "Guion Estructurado"}],
            "parameters": [
                {"key": "structure", "label": "Estructura Argumentativa", "type": "select", "options": ["Dialéctica 3 Actos (Tesis-Antítesis-Síntesis)", "Análisis Causal Profundo", "Estudio de Caso Bloomberg"], "value": "Dialéctica 3 Actos (Tesis-Antítesis-Síntesis)"}
            ]
        },
        {
            "id": "node_remotion_charts",
            "title": "📊 Infografías & Gráficos React (Remotion / HyperFrames)",
            "category": "programacion",
            "color": "#38bdf8",
            "x": 400, "y": 100, "width": 320, "enabled": True, "is_loop": True,
            "inputs": [{"id": "s_in", "name": "essay_script", "label": "Datos a Graficar"}],
            "outputs": [{"id": "charts_out", "name": "infographic_clips", "label": "Clips de Gráficos Animados"}],
            "parameters": [
                {"key": "chart_type", "label": "Tipo de Gráfico", "type": "select", "options": ["Líneas Temporales & Datos Evolutivos", "Gráficos de Barras Comparativos", "Mapas de Redes / Diagramas"], "value": "Líneas Temporales & Datos Evolutivos"}
            ]
        },
        {
            "id": "node_voice_intellectual",
            "title": "🎙️ VibeVoice 1.5B (Locución Pensativa)",
            "category": "voice",
            "color": "#10b981",
            "x": 400, "y": 380, "width": 320, "enabled": True,
            "inputs": [{"id": "s_in", "name": "essay_script", "label": "Guion"}],
            "outputs": [{"id": "voice_out", "name": "voice_audio", "label": "Voz Explicativa"}],
            "parameters": [
                {"key": "tone", "label": "Tono", "type": "select", "options": ["Analítico Riguroso (Vox/Veritasium)", "Cálido Pedagógico", "Periodístico Formal"], "value": "Analítico Riguroso (Vox/Veritasium)"}
            ]
        },
        {
            "id": "node_essay_render",
            "title": "🎞️ FFmpeg / Remotion Composite Master",
            "category": "render",
            "color": "#06b6d4",
            "x": 780, "y": 240, "width": 300, "enabled": True,
            "inputs": [
                {"id": "g_in", "name": "infographic_clips", "label": "Gráficos"},
                {"id": "v_in", "name": "voice_audio", "label": "Voz"}
            ],
            "outputs": [{"id": "final_out", "name": "final_video", "label": "Vídeo Final"}],
            "parameters": [
                {"key": "bgm_level", "label": "Volumen de Música Minimalista", "type": "select", "options": ["Muy Bajo / Sutil (-24 dB)", "Moderado (-18 dB)"], "value": "Muy Bajo / Sutil (-24 dB)"}
            ]
        }
    ],
    "connections": [
        {"id": "c1", "from_node": "node_dialectic_script", "from_socket": "script_out", "to_node": "node_remotion_charts", "to_socket": "s_in"},
        {"id": "c2", "from_node": "node_dialectic_script", "from_socket": "script_out", "to_node": "node_voice_intellectual", "to_socket": "s_in"},
        {"id": "c3", "from_node": "node_remotion_charts", "from_socket": "charts_out", "to_node": "node_essay_render", "to_socket": "g_in"},
        {"id": "c4", "from_node": "node_voice_intellectual", "from_socket": "voice_out", "to_node": "node_essay_render", "to_socket": "v_in"}
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
    )
}


def get_all_archetypes() -> List[WorkflowArchetype]:
    """Retorna todos los arquetipos de producción disponibles."""
    return list(ARCHETYPES_CATALOG.values())


def get_archetype(archetype_id: str) -> Optional[WorkflowArchetype]:
    """Obtiene un arquetipo específico por su ID."""
    return ARCHETYPES_CATALOG.get(archetype_id)
