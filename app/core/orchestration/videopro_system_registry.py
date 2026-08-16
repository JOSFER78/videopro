"""
videopro_system_registry.py
Registro Maestro del Sistema de 4 Niveles de VideoPro Studio & Hermes.
Mapea y sincroniza en Firebase Firestore:
1. APIs / Providers
2. Capacidades (Capabilities)
3. Nodos (Nodes)
4. Workflows / Pipelines para Canales de YouTube
"""

import json
import requests
from typing import Dict, Any
from app.models.videopro_ontology import (
    ProviderAPI, ProviderCategory,
    Capability, Node,
    WorkflowPipeline, YouTubeChannelTarget
)
from app.config import config
from app.services import firebase_sync

# ============================================================================
# 1. CATÁLOGO DE APIS Y PROVEEDORES (NIVEL 1)
# ============================================================================
SYSTEM_APIS: Dict[str, ProviderAPI] = {
    # --- VISUAL & VÍDEO ---
    "api_google_ai_imagen": ProviderAPI(
        id="api_google_ai_imagen",
        name="Google AI Studio Imagen 3 API",
        category=ProviderCategory.AI_IMAGE,
        base_url="https://generativelanguage.googleapis.com/v1beta",
        status="ACTIVE"
    ),
    "local_antigravity_bridge_8742": ProviderAPI(
        id="local_antigravity_bridge_8742",
        name="NanoBanana Pro 2 (Antigravity Bridge Puerto 8742 $0)",
        category=ProviderCategory.AI_IMAGE,
        base_url="http://127.0.0.1:8742/v1",
        is_serverless_free=True,
        status="ACTIVE"
    ),
    "browser_playwright_flow": ProviderAPI(
        id="browser_playwright_flow",
        name="Google Flow 3D Canvas (Playwright Browser Headless)",
        category=ProviderCategory.AI_VIDEO,
        status="ACTIVE"
    ),
    "serverless_zerogpu_flux": ProviderAPI(
        id="serverless_zerogpu_flux",
        name="FLUX.3 Video / LoRA (HuggingFace ZeroGPU Pool $0)",
        category=ProviderCategory.AI_IMAGE,
        is_serverless_free=True,
        status="ACTIVE"
    ),
    "serverless_replicate_flux": ProviderAPI(
        id="serverless_replicate_flux",
        name="FLUX.3 Pro / Schnell (Serverless Replicate API)",
        category=ProviderCategory.AI_IMAGE,
        base_url="https://api.replicate.com/v1",
        status="ACTIVE"
    ),
    "comfyui_runpod_flux": ProviderAPI(
        id="comfyui_runpod_flux",
        name="FLUX.3 ComfyUI Dedicated (RunPod / Modal GPU)",
        category=ProviderCategory.AI_VIDEO,
        status="ACTIVE"
    ),
    "comfyui_local_flux": ProviderAPI(
        id="comfyui_local_flux",
        name="FLUX.3 ComfyUI Local Bridge ($0 In-House VPS)",
        category=ProviderCategory.AI_VIDEO,
        base_url="http://127.0.0.1:8188",
        status="ACTIVE"
    ),
    "api_pexels_stock": ProviderAPI(
        id="api_pexels_stock",
        name="Pexels Video & Photo API",
        category=ProviderCategory.STOCK_MEDIA,
        base_url="https://api.pexels.com/v1",
        status="ACTIVE"
    ),
    "api_wikimedia_commons": ProviderAPI(
        id="api_wikimedia_commons",
        name="Wikimedia Commons Archive API",
        category=ProviderCategory.STOCK_MEDIA,
        base_url="https://commons.wikimedia.org/w/api.php",
        is_serverless_free=True,
        status="ACTIVE"
    ),
    # --- VOZ & AUDIO ---
    "serverless_vibevoice_tts": ProviderAPI(
        id="serverless_vibevoice_tts",
        name="VibeVoice 1.5B (Serverless Free TTS)",
        category=ProviderCategory.AI_VOICE_TTS,
        is_serverless_free=True,
        status="ACTIVE"
    ),
    "local_vibevoice_onnx": ProviderAPI(
        id="local_vibevoice_onnx",
        name="VibeVoice 1.5B In-House (Local ONNX/GPU VPS $0)",
        category=ProviderCategory.AI_VOICE_TTS,
        is_serverless_free=True,
        status="ACTIVE"
    ),
    "api_edge_tts_free": ProviderAPI(
        id="api_edge_tts_free",
        name="Microsoft Edge Neural TTS ($0 Free Stream)",
        category=ProviderCategory.AI_VOICE_TTS,
        is_serverless_free=True,
        status="ACTIVE"
    ),
    "api_elevenlabs_cloud": ProviderAPI(
        id="api_elevenlabs_cloud",
        name="ElevenLabs Voice Cloning Studio API",
        category=ProviderCategory.AI_VOICE_TTS,
        base_url="https://api.elevenlabs.io/v1",
        status="ACTIVE"
    ),
    "browser_playwright_flowmusic": ProviderAPI(
        id="browser_playwright_flowmusic",
        name="Google Flow Music Studio (Playwright Headless)",
        category=ProviderCategory.AI_MUSIC,
        status="ACTIVE"
    ),
    # --- DIRECTORES LLM ---
    "api_google_gemini_llm": ProviderAPI(
        id="api_google_gemini_llm",
        name="Google Gemini 2.5 / 3.0 Pro API",
        category=ProviderCategory.AI_LLM,
        base_url="https://generativelanguage.googleapis.com/v1beta",
        status="ACTIVE"
    ),
    "local_antigravity_agent_orchestrator": ProviderAPI(
        id="local_antigravity_agent_orchestrator",
        name="Antigravity Deep Agentic Orchestrator (CoT Subagents)",
        category=ProviderCategory.AI_LLM,
        is_serverless_free=True,
        status="ACTIVE"
    ),
    # --- ENSAMBLAJE & NUBE ---
    "local_remotion_cli": ProviderAPI(
        id="local_remotion_cli",
        name="Remotion 4.x React Render Engine (Local CLI)",
        category=ProviderCategory.CODE_ENGINE,
        status="ACTIVE"
    ),
    "cloud_remotion_lambda": ProviderAPI(
        id="cloud_remotion_lambda",
        name="Remotion Cloud AWS Lambda Cluster (60 FPS Multi-Core)",
        category=ProviderCategory.CODE_ENGINE,
        status="ACTIVE"
    ),
    "local_ffmpeg_engine": ProviderAPI(
        id="local_ffmpeg_engine",
        name="FFmpeg 6.x Hardware Accelerated Audio/Video DSP",
        category=ProviderCategory.CODE_ENGINE,
        status="ACTIVE"
    ),
    "firebase_firestore": ProviderAPI(
        id="firebase_firestore",
        name="Google Cloud Firebase Firestore (ayuda-emilio-83261)",
        category=ProviderCategory.CLOUD_DB,
        status="ACTIVE"
    ),
    "api_cloudflare_r2": ProviderAPI(
        id="api_cloudflare_r2",
        name="Cloudflare R2 Zero-Egress Storage S3 API",
        category=ProviderCategory.CLOUD_STORAGE,
        status="ACTIVE"
    )
}

# ============================================================================
# 2. CATÁLOGO DE CAPACIDADES ATÓMICAS (NIVEL 2)
# ============================================================================
SYSTEM_CAPABILITIES: Dict[str, Capability] = {
    # --- CAPACIDADES NANOBANANA PRO (DIFERENTES VÍAS) ---
    "cap_nanobanana_antigravity_bridge": Capability(
        id="cap_nanobanana_antigravity_bridge",
        name="NanoBanana Pro 2 via Antigravity Bridge ($0 Local :8742)",
        description="Generación de fotogramas 2K/4K y keyframes sin coste de API vía puerto local 8742.",
        required_apis=["local_antigravity_bridge_8742"],
        output_type="IMAGE"
    ),
    "cap_nanobanana_google_api": Capability(
        id="cap_nanobanana_google_api",
        name="NanoBanana Pro 2 via Google AI Studio API",
        description="Inferencia directa en Imagen 3 vía API Key de Google con máxima resolución nativa.",
        required_apis=["api_google_ai_imagen"],
        output_type="IMAGE"
    ),
    "cap_nanobanana_flow_browser": Capability(
        id="cap_nanobanana_flow_browser",
        name="NanoBanana Pro 2 via Google Flow Canvas (Playwright)",
        description="Captura de texturas y planos 3D interactivos en tiempo real vía automatización de navegador.",
        required_apis=["browser_playwright_flow"],
        output_type="IMAGE"
    ),
    # --- CAPACIDADES FLUX.3 (DIFERENTES VÍAS) ---
    "cap_flux3_serverless_free": Capability(
        id="cap_flux3_serverless_free",
        name="FLUX.3 Serverless ZeroGPU ($0 Free Pool)",
        description="Generación serverless distribuida a coste cero en espacios ZeroGPU con rotación de tokens.",
        required_apis=["serverless_zerogpu_flux"],
        output_type="IMAGE"
    ),
    "cap_flux3_replicate_cloud": Capability(
        id="cap_flux3_replicate_cloud",
        name="FLUX.3 Replicate Cloud Dedicated (H100 On-Demand)",
        description="Inferencia directa vía API Replicate en GPU H100 para generación prioritaria y rápida.",
        required_apis=["serverless_replicate_flux"],
        output_type="IMAGE"
    ),
    "cap_flux3_comfyui_runpod": Capability(
        id="cap_flux3_comfyui_runpod",
        name="FLUX.3 ComfyUI Node Graph (RunPod / Modal GPU)",
        description="Control total de grafo modular en ComfyUI con ControlNet, apilado de LoRAs y Latent Upscaling 4K.",
        required_apis=["comfyui_runpod_flux"],
        output_type="VIDEO_CLIP"
    ),
    "cap_flux3_comfyui_local": Capability(
        id="cap_flux3_comfyui_local",
        name="FLUX.3 ComfyUI Local VPS Bridge ($0 In-House)",
        description="Ejecución local en servidor VPS vía API Bridge puerto 8188 sin consumo de nube externa.",
        required_apis=["comfyui_local_flux"],
        output_type="IMAGE"
    ),
    # --- CAPACIDADES VOZ & AUDIO (DIFERENTES VÍAS) ---
    "cap_vibevoice_serverless_free": Capability(
        id="cap_vibevoice_serverless_free",
        name="VibeVoice 1.5B via Serverless ZeroGPU ($0)",
        description="Generación de voz neural de alta expresividad en espacios serverless libres.",
        required_apis=["serverless_vibevoice_tts"],
        output_type="AUDIO_TRACK"
    ),
    "cap_vibevoice_local_vps": Capability(
        id="cap_vibevoice_local_vps",
        name="VibeVoice 1.5B In-House Local VPS ($0 ONNX)",
        description="Inferencia de voz en hardware propio sin latencia de red.",
        required_apis=["local_vibevoice_onnx"],
        output_type="AUDIO_TRACK"
    ),
    "cap_elevenlabs_voice_cloning": Capability(
        id="cap_elevenlabs_voice_cloning",
        name="Clonación de Voz de Estudio (ElevenLabs Cloud API)",
        description="Voz fotorrealista clonada con entonación cinemática profesional.",
        required_apis=["api_elevenlabs_cloud"],
        output_type="AUDIO_TRACK"
    ),
    "cap_edgetts_fast_narration": Capability(
        id="cap_edgetts_fast_narration",
        name="Locución Instantánea ($0 Edge Neural TTS)",
        description="Generación ultrarrápida de narración multi-idioma a coste cero.",
        required_apis=["api_edge_tts_free"],
        output_type="AUDIO_TRACK"
    ),
    "cap_flowmusic_browser_gen": Capability(
        id="cap_flowmusic_browser_gen",
        name="Composición Musical via Google Flow Music (Browser)",
        description="Generación y descarga de bandas sonoras a compás exacto vía navegador automatizado.",
        required_apis=["browser_playwright_flowmusic"],
        output_type="AUDIO_TRACK"
    ),
    # --- CAPACIDADES STORYTELLING & INVESTIGACIÓN ---
    "cap_llm_story_director": Capability(
        id="cap_llm_story_director",
        name="Director Semántico & Storytelling (Google Gemini API)",
        description="Genera el arco narrativo coherente (descenso por niveles) y metadatos con fuentes.",
        required_apis=["api_google_gemini_llm", "firebase_firestore"],
        output_type="TEXT"
    ),
    "cap_llm_antigravity_agentic": Capability(
        id="cap_llm_antigravity_agentic",
        name="Director Agentic Hermes (Antigravity CoT Bridge)",
        description="Planificación multicapa, verificación cruzada de hechos y co-creación iterativa.",
        required_apis=["local_antigravity_agent_orchestrator"],
        output_type="TEXT"
    ),
    "cap_web_search_scrappers": Capability(
        id="cap_web_search_scrappers",
        name="Scrappers 04 & Hemerotecas",
        description="Scrapea Reddit, archivos históricos y páginas oficiales.",
        required_apis=["api_wikimedia_commons"],
        output_type="TEXT"
    ),
    "cap_stock_scraping_pexels_4k": Capability(
        id="cap_stock_scraping_pexels_4k",
        name="Scraping de Vídeo 4K en Movimiento",
        description="Descarga clips 4K de alta calidad con movimiento continuo.",
        required_apis=["api_pexels_stock"],
        output_type="VIDEO_CLIP"
    ),
    "cap_wikimedia_historical_archive": Capability(
        id="cap_wikimedia_historical_archive",
        name="Descarga de Fotografías y Planos de Archivo",
        description="Obtiene imágenes históricas de dominio público y alta resolución.",
        required_apis=["api_wikimedia_commons", "api_pexels_stock"],
        output_type="IMAGE"
    ),
    "cap_image_quality_filter": Capability(
        id="cap_image_quality_filter",
        name="Filtro Laplaciano & Contraste PIL",
        description="Verifica que las imágenes no estén borrosas y cumplan resolución mínima.",
        required_apis=[],
        output_type="IMAGE"
    ),
    # --- MOTION GRAPHICS & ENSAMBLAJE ---
    "cap_motion_remotion_react_hud": Capability(
        id="cap_motion_remotion_react_hud",
        name="Motor Motion Graphics Remotion 4.x (Local CLI)",
        description="Renderiza rótulos, telemetría, espectro FFT y capas táctiles en React.",
        required_apis=["local_remotion_cli"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_motion_remotion_lambda_cloud": Capability(
        id="cap_motion_remotion_lambda_cloud",
        name="Remotion 4.x Cloud Distributed (AWS Lambda 60 FPS)",
        description="Renderizado acelerado multi-hilo en la nube para proyectos de larga duración.",
        required_apis=["cloud_remotion_lambda"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_paper_texture_overlay": Capability(
        id="cap_paper_texture_overlay",
        name="Loop de Textura de Papel (27% Opacidad / 12 FPS)",
        description="Aplica la textura analógica del cuaderno de estilo Vox.",
        required_apis=[],
        output_type="MOTION_OVERLAY"
    ),
    "cap_audio_beat_transient_detector": Capability(
        id="cap_audio_beat_transient_detector",
        name="Detector de BPM y Transitorios de Audio",
        description="Analiza la pista WAV master para calcular los cortes y la energía espectral.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),
    "cap_audio_mixing_foley_ducking": Capability(
        id="cap_audio_mixing_foley_ducking",
        name="Mezclador EBU R128 con Ducking a -22 dB",
        description="Mezcla las capas de audio y atenúa la música en la voz en off.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),
    "cap_sfx_shutter_paper_typewriter": Capability(
        id="cap_sfx_shutter_paper_typewriter",
        name="Foley Físico Sincronizado",
        description="Inyecta sonidos de obturador, deslizamiento de papel y tecleo.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),
    "cap_contact_sheet_builder": Capability(
        id="cap_contact_sheet_builder",
        name="Generador de Tira de Fotogramas (Contact Sheet)",
        description="Compila mosaico visual para verificación y control de calidad.",
        required_apis=["local_ffmpeg_engine"],
        output_type="QA_REPORT"
    ),
    "cap_firebase_sync_engine": Capability(
        id="cap_firebase_sync_engine",
        name="Motor de Sincronización en la Nube",
        description="Persiste el estado, metadatos y catálogo en Firestore y R2.",
        required_apis=["firebase_firestore", "api_cloudflare_r2"],
        output_type="TEXT"
    )
}

# ============================================================================
# 3. CATÁLOGO DE NODOS DE PRODUCCIÓN (NIVEL 3)
# ============================================================================
SYSTEM_NODES: Dict[str, Node] = {
    "node_01_investigacion_y_narrativa": Node(
        id="node_01_investigacion_y_narrativa",
        number=1,
        name="Investigación Profunda & Storytelling",
        role_description="Construcción del arco narrativo unificado, dossier de fuentes y ficha de YouTube.",
        capabilities=[
            "cap_llm_story_director",
            "cap_llm_antigravity_agentic",
            "cap_web_search_scrappers",
            "cap_firebase_sync_engine"
        ]
    ),
    "node_02_audio_first_y_ritmo": Node(
        id="node_02_audio_first_y_ritmo",
        number=2,
        name="Audio-First & Sincronismo Temporal",
        role_description="Calibración de la línea de tiempo sobre la pista WAV master, locución y bandas sonoras.",
        capabilities=[
            "cap_audio_beat_transient_detector",
            "cap_vibevoice_serverless_free",
            "cap_vibevoice_local_vps",
            "cap_elevenlabs_voice_cloning",
            "cap_edgetts_fast_narration",
            "cap_flowmusic_browser_gen"
        ]
    ),
    "node_03_ingesta_multimedia_4k": Node(
        id="node_03_ingesta_multimedia_4k",
        number=3,
        name="Ingesta & Generación Multi-Activo 4K",
        role_description="Keyframes NanoBanana Pro (Bridge/API/Browser), FLUX.3 (ZeroGPU/Replicate/ComfyUI/RunPod), stock 4K y archivo histórico.",
        capabilities=[
            "cap_nanobanana_antigravity_bridge",
            "cap_nanobanana_google_api",
            "cap_nanobanana_flow_browser",
            "cap_flux3_serverless_free",
            "cap_flux3_replicate_cloud",
            "cap_flux3_comfyui_runpod",
            "cap_flux3_comfyui_local",
            "cap_stock_scraping_pexels_4k",
            "cap_wikimedia_historical_archive",
            "cap_image_quality_filter"
        ]
    ),
    "node_04_composicion_motion_graphics": Node(
        id="node_04_composicion_motion_graphics",
        number=4,
        name="Motion Graphics Remotion 4.x",
        role_description="Renderizado de rótulos táctiles, mapas y texturas de papel en React 18 (Local CLI o AWS Lambda Cloud).",
        capabilities=[
            "cap_motion_remotion_react_hud",
            "cap_motion_remotion_lambda_cloud",
            "cap_paper_texture_overlay"
        ]
    ),
    "node_05_masterizacion_audio_foley": Node(
        id="node_05_masterizacion_audio_foley",
        number=5,
        name="Mezcla Master & Foley Diegético",
        role_description="Integración de efectos físicos (obturador, papel) y masterización EBU R128.",
        capabilities=[
            "cap_audio_mixing_foley_ducking",
            "cap_sfx_shutter_paper_typewriter"
        ]
    ),
    "node_06_qa_evaluacion_y_sync": Node(
        id="node_06_qa_evaluacion_y_sync",
        number=6,
        name="QA Loop de Autoevaluación & Cloud Sync",
        role_description="Control anti-repetición de fotogramas, Contact Sheet y sincronización en Firebase y R2.",
        capabilities=[
            "cap_contact_sheet_builder",
            "cap_firebase_sync_engine"
        ]
    )
}

# ============================================================================
# 4. CATÁLOGO DE WORKFLOWS PARA CANALES DE YOUTUBE (NIVEL 4)
# ============================================================================
SYSTEM_WORKFLOWS: Dict[str, WorkflowPipeline] = {
    "workflow_vox_documentary_3min": WorkflowPipeline(
        id="workflow_vox_documentary_3min",
        name="Documental Explicativo Táctil (Estilo Vox / Johnny Harris)",
        description="Pipeline completo de 6 nodos con investigación profunda por capas, 4K b-roll, recortes 3D, mapas animados y foley de papel.",
        channel_target=YouTubeChannelTarget(
            channel_name="Ciudades Ocultas / Misterios Urbanos",
            niche="Documentales Explicativos y Periodismo Visual",
            format="16:9 4K 60FPS",
            visual_style="Vox Táctil (Fondo Crema #F4F1EA, Choppy Motion 12fps, Resaltador #FFC924, Foley Analógico)",
            target_audience="Audiencia interesada en historia, arquitectura secreta y misterios urbanos"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_narrativa",
            "node_02_audio_first_y_ritmo",
            "node_03_ingesta_multimedia_4k",
            "node_04_composicion_motion_graphics",
            "node_05_masterizacion_audio_foley",
            "node_06_qa_evaluacion_y_sync"
        ],
        estimated_duration_sec=177.64,
        output_specs={"resolution": "3840x2160", "fps": 60, "audio_lufs": -14.0}
    ),
    "workflow_fpv_chronodrift_travel": WorkflowPipeline(
        id="workflow_fpv_chronodrift_travel",
        name="Viajes Inmersivos FPV 6-DoF ChronoDrift",
        description="Pipeline con telemetría de vuelo, HUD cinemático y velocidad sincronizada a compases de 118 BPM.",
        channel_target=YouTubeChannelTarget(
            channel_name="ChronoDrift Expeditions",
            niche="Viajes FPV & Exploración Visual",
            format="16:9 4K 60FPS",
            visual_style="Cyber-HUD Minimalista con Físicas de Vuelo",
            target_audience="Entusiastas de drones FPV y viajes de alta fidelidad"
        ),
        ordered_nodes=[
            "node_02_audio_first_y_ritmo",
            "node_03_ingesta_multimedia_4k",
            "node_04_composicion_motion_graphics",
            "node_05_masterizacion_audio_foley",
            "node_06_qa_evaluacion_y_sync"
        ],
        estimated_duration_sec=180.0
    ),
    "workflow_shorts_viral_hook": WorkflowPipeline(
        id="workflow_shorts_viral_hook",
        name="Shorts & Reels de Máxima Retención",
        description="Montaje vertical de 60 segundos con subtítulos burned karaoke y cortes cada 1.5 segundos.",
        channel_target=YouTubeChannelTarget(
            channel_name="Curiosidades Flash 60s",
            niche="YouTube Shorts & Micro-documentales",
            format="9:16 Vertical 1080x1920",
            visual_style="Karaoke Subtitles Bold, Zoom In/Out cada 1.5s",
            target_audience="Consumidores de contenido corto en móvil"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_narrativa",
            "node_02_audio_first_y_ritmo",
            "node_03_ingesta_multimedia_4k",
            "node_04_composicion_motion_graphics",
            "node_06_qa_evaluacion_y_sync"
        ],
        estimated_duration_sec=60.0
    )
}


def sync_entire_ontology_to_firebase() -> bool:
    """Sincroniza la ontología completa de 4 niveles en Firebase Firestore."""
    token = firebase_sync._get_firebase_auth_token()
    project_id = config.app.get("firebase_project_id") or "ayuda-emilio-83261"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    ontology_payload = {
        "apis": {k: v.model_dump() for k, v in SYSTEM_APIS.items()},
        "capabilities": {k: v.model_dump() for k, v in SYSTEM_CAPABILITIES.items()},
        "nodes": {k: v.model_dump() for k, v in SYSTEM_NODES.items()},
        "workflows": {k: v.model_dump() for k, v in SYSTEM_WORKFLOWS.items()}
    }

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/architecture_ontology"
    fields = {
        "ontology_json": {"stringValue": json.dumps(ontology_payload, ensure_ascii=False)},
        "updated_at": {"stringValue": "2026-08-16T20:00:00"}
    }
    
    try:
        resp = requests.patch(url, headers=headers, json={"fields": fields}, timeout=10)
        return resp.status_code == 200
    except Exception as ex:
        print(f"Error sincronizando ontología en Firestore: {ex}")
        return False
