"""
videopro_system_registry.py
Registro Maestro del Sistema de 4 Niveles de VideoPro Studio & Hermes.
Mapea y sincroniza en Firebase Firestore:
1. APIs / Providers (Nivel 1: Infraestructura física y endpoints)
2. Capacidades (Capabilities / Nivel 2: Unidades atómicas ejecutables desacopladas)
3. Nodos (Nodes / Nivel 3: Etapas funcionales de la cadena de montaje)
4. Workflows / Pipelines (Nivel 4: Canales de YouTube y Arquetipos de producción)
"""

import json
from datetime import datetime
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
# 1. CATÁLOGO MAESTRO DE APIS Y PROVEEDORES DE INFRAESTRUCTURA (NIVEL 1)
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
    "api_ltx25_mmdit": ProviderAPI(
        id="api_ltx25_mmdit",
        name="LTX-Video 2.5 MMDiT 22B (Audio + Vídeo 24fps)",
        category=ProviderCategory.AI_VIDEO,
        base_url="https://api.replicate.com/v1",
        status="ACTIVE"
    ),
    "api_wan21_alibaba": ProviderAPI(
        id="api_wan21_alibaba",
        name="Wan 2.1 Video (Alibaba DiT 14B / 1.3B)",
        category=ProviderCategory.AI_VIDEO,
        status="ACTIVE"
    ),
    "api_minimax_h3": ProviderAPI(
        id="api_minimax_h3",
        name="MiniMax H3 / Hailuo-02 Video",
        category=ProviderCategory.AI_VIDEO,
        status="ACTIVE"
    ),
    "api_seedance": ProviderAPI(
        id="api_seedance",
        name="SeaDance 2.5 Coreografía Cinemática (ByteDance)",
        category=ProviderCategory.AI_VIDEO,
        status="ACTIVE"
    ),
    "api_pexels_stock": ProviderAPI(
        id="api_pexels_stock",
        name="Pexels Video & Photo API 4K",
        category=ProviderCategory.STOCK_MEDIA,
        base_url="https://api.pexels.com/v1",
        status="ACTIVE"
    ),
    "api_pixabay_media": ProviderAPI(
        id="api_pixabay_media",
        name="Pixabay Stock Media 4K/HD",
        category=ProviderCategory.STOCK_MEDIA,
        base_url="https://pixabay.com/api",
        status="ACTIVE"
    ),
    "api_wikimedia_commons": ProviderAPI(
        id="api_wikimedia_commons",
        name="Wikimedia Commons Historical Archive API",
        category=ProviderCategory.STOCK_MEDIA,
        base_url="https://commons.wikimedia.org/w/api.php",
        is_serverless_free=True,
        status="ACTIVE"
    ),

    # --- VOZ & AUDIO ---
    "serverless_vibevoice_tts": ProviderAPI(
        id="serverless_vibevoice_tts",
        name="VibeVoice 1.5B (Serverless Free TTS Space)",
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
    "api_fish_audio": ProviderAPI(
        id="api_fish_audio",
        name="Fish Audio API (Clonación S2.1 Pro)",
        category=ProviderCategory.AI_VOICE_TTS,
        status="ACTIVE"
    ),
    "api_minimax_speech": ProviderAPI(
        id="api_minimax_speech",
        name="MiniMax Speech 01 (Voz Expresiva T2S)",
        category=ProviderCategory.AI_VOICE_TTS,
        status="ACTIVE"
    ),

    # --- MÚSICA & BANDAS SONORAS ---
    "browser_playwright_flowmusic": ProviderAPI(
        id="browser_playwright_flowmusic",
        name="Google Flow Music Studio (Playwright Headless)",
        category=ProviderCategory.AI_MUSIC,
        status="ACTIVE"
    ),
    "api_suno_ai": ProviderAPI(
        id="api_suno_ai",
        name="Suno AI Music Generation API (v3/v4)",
        category=ProviderCategory.AI_MUSIC,
        status="ACTIVE"
    ),

    # --- DIRECTORES LLM & RAZONAMIENTO ---
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
    "api_openai_gpt": ProviderAPI(
        id="api_openai_gpt",
        name="OpenAI GPT-4o / GPT-5.5 API",
        category=ProviderCategory.AI_LLM,
        base_url="https://api.openai.com/v1",
        status="ACTIVE"
    ),
    "api_deepseek": ProviderAPI(
        id="api_deepseek",
        name="DeepSeek AI (V3 / R1 Oficial)",
        category=ProviderCategory.AI_LLM,
        base_url="https://api.deepseek.com",
        status="ACTIVE"
    ),
    "api_cloudflare_workers_ai": ProviderAPI(
        id="api_cloudflare_workers_ai",
        name="Cloudflare Workers AI (Serverless Edge)",
        category=ProviderCategory.AI_LLM,
        status="ACTIVE"
    ),
    "api_siliconflow": ProviderAPI(
        id="api_siliconflow",
        name="SiliconFlow & ModelScope Pasarela",
        category=ProviderCategory.AI_LLM,
        status="ACTIVE"
    ),

    # --- PROGRAMACIÓN, RENDER & SUBTÍTULOS ---
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
    "qgis_cartography_engine": ProviderAPI(
        id="qgis_cartography_engine",
        name="QGIS 4K Vector Cartography & DEM Elevation Map Engine",
        category=ProviderCategory.CODE_ENGINE,
        status="ACTIVE"
    ),
    "local_whisper_stt": ProviderAPI(
        id="local_whisper_stt",
        name="Whisper STT (Alineación Temporal & Word Timestamps)",
        category=ProviderCategory.CODE_ENGINE,
        status="ACTIVE"
    ),
    "local_hyperframes_engine": ProviderAPI(
        id="local_hyperframes_engine",
        name="HyperFrames WebGL & GLSL Shaders Engine",
        category=ProviderCategory.CODE_ENGINE,
        status="ACTIVE"
    ),

    # --- CLOUD, ALMACENAMIENTO & BD ---
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
        description="Generación de fotogramas 2K/4K y keyframes fotorrealistas sin coste vía puerto local 8742.",
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
        description="Captura de texturas y planos 3D interactivos en tiempo real vía automatización headless de navegador.",
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
        description="Inferencia directa vía API Replicate en GPU H100 para generación prioritaria y ultrarrápida.",
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

    # --- OTRAS CAPACIDADES VISUALES Y VÍDEO ---
    "cap_ltx25_lip_sync_24fps": Capability(
        id="cap_ltx25_lip_sync_24fps",
        name="LTX-2.5 Dual-Track Video + Lip-Sync 24fps",
        description="Generación de vídeo cinemático con sincronización labial y audio 48kHz integrado.",
        required_apis=["api_ltx25_mmdit"],
        output_type="VIDEO_CLIP"
    ),
    "cap_wan21_t2v_cinematic": Capability(
        id="cap_wan21_t2v_cinematic",
        name="Wan 2.1 Video DiT 14B High Dynamic Motion",
        description="Generación de planos fluidos con gran movimiento de cámara y coherencia temporal.",
        required_apis=["api_wan21_alibaba"],
        output_type="VIDEO_CLIP"
    ),
    "cap_minimax_h3_motion": Capability(
        id="cap_minimax_h3_motion",
        name="MiniMax Hailuo-02 Motion Video",
        description="Generación cinemática con dinámicas físicas realistas y acting de personajes.",
        required_apis=["api_minimax_h3"],
        output_type="VIDEO_CLIP"
    ),
    "cap_seedance_choreography": Capability(
        id="cap_seedance_choreography",
        name="SeaDance 2.5 Coreografía Cinemática",
        description="Movimientos de cámara complejos y coreografía de objetos en 3D.",
        required_apis=["api_seedance"],
        output_type="VIDEO_CLIP"
    ),
    "cap_stock_scraping_pexels_4k": Capability(
        id="cap_stock_scraping_pexels_4k",
        name="Scraping de Vídeo Stock Pexels 4K UHD",
        description="Búsqueda semántica y descarga de metraje 4K en movimiento continuo.",
        required_apis=["api_pexels_stock"],
        output_type="VIDEO_CLIP"
    ),
    "cap_pixabay_stock_media": Capability(
        id="cap_pixabay_stock_media",
        name="Stock Media Pixabay HD/4K",
        description="B-roll complementario y texturas fotográficas libres de derechos.",
        required_apis=["api_pixabay_media"],
        output_type="VIDEO_CLIP"
    ),
    "cap_wikimedia_historical_archive": Capability(
        id="cap_wikimedia_historical_archive",
        name="Descarga de Archivo Histórico & Planos Antiguos",
        description="Obtención de documentos, fotografías y grabados históricos de dominio público en alta resolución.",
        required_apis=["api_wikimedia_commons"],
        output_type="IMAGE"
    ),
    "cap_orbital_trajectories_4k": Capability(
        id="cap_orbital_trajectories_4k",
        name="Vuelos Orbitales 6-DoF en Google Flow",
        description="Trayectorias de cámara inmersiva y navegación orbital 3D.",
        required_apis=["browser_playwright_flow"],
        output_type="VIDEO_CLIP"
    ),
    "cap_image_quality_filter": Capability(
        id="cap_image_quality_filter",
        name="Filtro Laplaciano & Contraste PIL",
        description="Verifica que las imágenes no presenten borrosidad y cumplan con resolución 2K/4K.",
        required_apis=[],
        output_type="IMAGE"
    ),

    # --- CAPACIDADES VOZ & AUDIO ---
    "cap_vibevoice_serverless_free": Capability(
        id="cap_vibevoice_serverless_free",
        name="VibeVoice 1.5B via Serverless ZeroGPU ($0)",
        description="Generación de voz neural de alta expresividad y cadencia documental en espacios libres.",
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
    "cap_fish_audio_voice_cloning": Capability(
        id="cap_fish_audio_voice_cloning",
        name="Fish Audio Voice Cloning S2.1 Pro",
        description="Clonación rápida de voces expresivas con entonación dinámica.",
        required_apis=["api_fish_audio"],
        output_type="AUDIO_TRACK"
    ),
    "cap_minimax_speech_t2s": Capability(
        id="cap_minimax_speech_t2s",
        name="MiniMax Speech 01 Ultra-Realista",
        description="Síntesis de voz con respiraciones naturales y modulación emocional.",
        required_apis=["api_minimax_speech"],
        output_type="AUDIO_TRACK"
    ),

    # --- CAPACIDADES MÚSICA & FOLEY ---
    "cap_flowmusic_browser_gen": Capability(
        id="cap_flowmusic_browser_gen",
        name="Composición Musical via Google Flow Music (Browser)",
        description="Generación y descarga de bandas sonoras a compás exacto vía navegador automatizado.",
        required_apis=["browser_playwright_flowmusic"],
        output_type="AUDIO_TRACK"
    ),
    "cap_suno_song_generation": Capability(
        id="cap_suno_song_generation",
        name="Generación de Canciones y Temas Suno AI",
        description="Composición musical completa con arreglos instrumentales y armonías.",
        required_apis=["api_suno_ai"],
        output_type="AUDIO_TRACK"
    ),
    "cap_audio_beat_transient_detector": Capability(
        id="cap_audio_beat_transient_detector",
        name="Detector de BPM y Transitorios de Audio (FFmpeg)",
        description="Analiza la pista WAV master para calcular los cortes y la energía espectral a compás.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),
    "cap_audio_mixing_foley_ducking": Capability(
        id="cap_audio_mixing_foley_ducking",
        name="Mezclador EBU R128 con Ducking Dinámico (-22 dB)",
        description="Mezcla las capas de audio (voz, música, foley) y atenúa la música automáticamente bajo la voz.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),
    "cap_sfx_shutter_paper_typewriter": Capability(
        id="cap_sfx_shutter_paper_typewriter",
        name="Foley Físico Diegético Sincronizado",
        description="Inyecta sonidos de obturador de cámara, deslizamiento de papel y tecleo mecánico.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),

    # --- CAPACIDADES DIRECTORES LLM & STORYTELLING ---
    "cap_llm_story_director": Capability(
        id="cap_llm_story_director",
        name="Director Semántico & Storytelling (Gemini / OpenAI)",
        description="Genera el arco dramático por capas (descenso por niveles) y metadatos con fuentes oficiales.",
        required_apis=["api_google_gemini_llm", "api_openai_gpt"],
        output_type="TEXT"
    ),
    "cap_llm_antigravity_agentic": Capability(
        id="cap_llm_antigravity_agentic",
        name="Director Agentic Hermes (Antigravity CoT Bridge)",
        description="Planificación multicapa, subagentes especializados y verificación de coherencia global.",
        required_apis=["local_antigravity_agent_orchestrator"],
        output_type="TEXT"
    ),
    "cap_deepseek_reasoning_cot": Capability(
        id="cap_deepseek_reasoning_cot",
        name="Razonamiento Profundo DeepSeek R1 CoT",
        description="Estructuración dialéctica y deducción lógica rigurosa para ensayos complejos.",
        required_apis=["api_deepseek"],
        output_type="TEXT"
    ),
    "cap_web_search_scrappers": Capability(
        id="cap_web_search_scrappers",
        name="Scrappers de Investigación Profunda",
        description="Scrapea hemerotecas, fuentes oficiales, archivos de prensa y Reddit.",
        required_apis=["api_wikimedia_commons"],
        output_type="TEXT"
    ),

    # --- CAPACIDADES MOTION GRAPHICS & RENDER ---
    "cap_motion_remotion_react_hud": Capability(
        id="cap_motion_remotion_react_hud",
        name="Motion Graphics Remotion 4.x (Local CLI)",
        description="Renderiza rótulos táctiles estilo Vox, telemetría FPV, espectros FFT y tarjetas 3D en React 18.",
        required_apis=["local_remotion_cli"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_motion_remotion_lambda_cloud": Capability(
        id="cap_motion_remotion_lambda_cloud",
        name="Remotion 4.x Cloud Distributed (AWS Lambda 60 FPS)",
        description="Renderizado acelerado multi-hilo en la nube para producciones masivas.",
        required_apis=["cloud_remotion_lambda"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_paper_texture_overlay": Capability(
        id="cap_paper_texture_overlay",
        name="Loop de Textura de Papel Analógico (27% Opacidad / 12 FPS)",
        description="Aplica la textura táctil granulada característica del cuaderno documental Vox.",
        required_apis=[],
        output_type="MOTION_OVERLAY"
    ),
    "cap_whisper_word_level_timestamps": Capability(
        id="cap_whisper_word_level_timestamps",
        name="Subtítulos Vox Karaoke con Word-Level Timestamps",
        description="Alineación temporal fonética y renderizado de palabras resaltadas en tiempo real.",
        required_apis=["local_whisper_stt"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_hyperframes_webgl_shaders": Capability(
        id="cap_hyperframes_webgl_shaders",
        name="Shaders GLSL & WebGL Transitions (HyperFrames)",
        description="Transiciones ópticas procedurales, ruido Simplex y efectos de desenfoque de cámara.",
        required_apis=["local_hyperframes_engine"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_contact_sheet_builder": Capability(
        id="cap_contact_sheet_builder",
        name="Generador de Mosaico QA (Contact Sheet 4K)",
        description="Compila la tira de verificación fotograma a fotograma para control de calidad antes del render.",
        required_apis=["local_ffmpeg_engine"],
        output_type="QA_REPORT"
    ),
    # --- CAPACIDADES DE PRODUCCIÓN DOCUMENTAL ÉLITE & VOX MOTION GRAPHICS ---
    "cap_storyboard_shot_planner": Capability(
        id="cap_storyboard_shot_planner",
        name="Storyboard Studio & Desglose de Tipos de Plano (Tool Drop)",
        description="Clasifica cada segmento del guion en planos especializados: Cartografía QGIS, Prensa 3D Roughen, Blueprint DEM o Macro-Patente.",
        required_apis=["api_google_gemini_llm", "api_openai_gpt"],
        output_type="TEXT"
    ),
    "cap_qgis_vector_dash78": Capability(
        id="cap_qgis_vector_dash78",
        name="Cartografía Vectorial 4K QGIS con Dash=78 (Denys Zhylin)",
        description="Genera mapas 4K transparentes con textura de papel prensa (Multiply), trazado de rutas Dash=78, Trim Paths continuo y cámara Bezier.",
        required_apis=["qgis_cartography_engine", "local_ffmpeg_engine"],
        output_type="VIDEO_CLIP"
    ),
    "cap_newspaper_roughen_parallax": Capability(
        id="cap_newspaper_roughen_parallax",
        name="Prensa Histórica 3D con Roughen Edges & Resaltador Flúor (createdaley)",
        description="Periódicos de época en 3D con bordes rasgados procedimentales (Border 3.3px, Sharpness 4.58, Complexity 10), Tint de papel, rotulador flúor animado y sello oficial con rebote spring.",
        required_apis=["local_remotion_cli", "local_ffmpeg_engine"],
        output_type="VIDEO_CLIP"
    ),
    "cap_blueprint_dem_elevation": Capability(
        id="cap_blueprint_dem_elevation",
        name="Blueprint de Ingeniería & Relieve DEM -14M con Offset Z +0.001 (Wyspa Klatek)",
        description="Planos estructurales en corte transversal con cotas de nivel, relieve DEM de elevación, separación Z +0.001 anti Z-fighting y líneas guía de telemetría.",
        required_apis=["local_remotion_cli", "local_ffmpeg_engine"],
        output_type="VIDEO_CLIP"
    ),
    "cap_macro_horology_patent": Capability(
        id="cap_macro_horology_patent",
        name="Macro-Detalle de Patentes Históricas & Horología 1866 (Johnny Harris)",
        description="Esquemas de patentes con engranajes cinemáticos giratorios, péndulo de compensación oscilante y HUD de telemetría técnica monocromática.",
        required_apis=["local_ffmpeg_engine"],
        output_type="VIDEO_CLIP"
    ),
    "cap_foley_diegetic_soundscape": Capability(
        id="cap_foley_diegetic_soundscape",
        name="Paisaje Sonoro Foley Diegético Sincronizado",
        description="Síntesis e inyección de efectos sonoros físicos en sincronía milimétrica: Whooshes de corte, roces de papel, chirrido de rotulador, golpe de sello y tic-tac.",
        required_apis=["local_ffmpeg_engine"],
        output_type="AUDIO_TRACK"
    ),
    "cap_vox_paper_parallax_3d": Capability(
        id="cap_vox_paper_parallax_3d",
        name="Paralaje 3D Multicapa de Documentos & Prensa (Estilo Vox)",
        description="Textura de papel prensa analógica, desaturación con Tint, bordes irregulares con Roughen Edges, sombras suaves y movimiento de cámara en 3D.",
        required_apis=["local_remotion_cli", "local_ffmpeg_engine"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_vox_cinematic_map_3d": Capability(
        id="cap_vox_cinematic_map_3d",
        name="Cartografía Vectorial 3D Vox (QGIS 4K & Dash=78)",
        description="Mapas vectoriales 4K transparentes con rutas animadas de pluma (Dash=78 / Trim Paths), curvas Bezier y offset Z=+0.001 anti Z-fighting.",
        required_apis=["qgis_cartography_engine", "local_remotion_cli", "local_ffmpeg_engine"],
        output_type="VIDEO_CLIP"
    ),
    "cap_kinetic_word_subtitles": Capability(
        id="cap_kinetic_word_subtitles",
        name="Subtítulos Cinematográficos Dinámicos (Remotion / ASS)",
        description="Subtítulos palabra por palabra con resaltado activo sin recuadros opacos, tipografía Inter/Montserrat y animación elástica spring().",
        required_apis=["local_remotion_cli", "local_whisper_stt", "local_ffmpeg_engine"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_stagger_psicoacustico_motion": Capability(
        id="cap_stagger_psicoacustico_motion",
        name="Stagger Psicoacústico de Entrada (Desfase 3-5 Frames)",
        description="Desfase milimétrico en los fotogramas de entrada de elementos visuales (documento ➔ resaltador ➔ subtítulo) para retención >70%.",
        required_apis=["local_remotion_cli"],
        output_type="MOTION_OVERLAY"
    ),
    "cap_firebase_sync_engine": Capability(
        id="cap_firebase_sync_engine",
        name="Motor de Sincronización en la Nube (Firestore & R2)",
        description="Persiste el estado, metadatos, artefactos y catálogo en Firestore y Cloudflare R2 sin egress.",
        required_apis=["firebase_firestore", "api_cloudflare_r2"],
        output_type="TEXT"
    )
}

# ============================================================================
# 3. CATÁLOGO DE NODOS DE PRODUCCIÓN (NIVEL 3)
# ============================================================================
SYSTEM_NODES: Dict[str, Node] = {
    "node_01_investigacion_y_storyboard": Node(
        id="node_01_investigacion_y_storyboard",
        number=1,
        name="Investigación, Guion & Storyboard Studio",
        role_description="Construcción del arco narrativo unificado, dossier de fuentes y desglose escena a escena por tipo de plano documental.",
        capabilities=[
            "cap_llm_story_director",
            "cap_storyboard_shot_planner",
            "cap_deepseek_reasoning_cot",
            "cap_web_search_scrappers",
            "cap_firebase_sync_engine"
        ]
    ),
    "node_02_audio_first_y_foley": Node(
        id="node_02_audio_first_y_foley",
        number=2,
        name="Audio-First, Locución & Foley Diegético",
        role_description="Calibración milimétrica de la línea de tiempo sobre la pista WAV master, locución neural y efectos de foley físicos.",
        capabilities=[
            "cap_vibevoice_serverless_free",
            "cap_vibevoice_local_vps",
            "cap_elevenlabs_voice_cloning",
            "cap_edgetts_fast_narration",
            "cap_foley_diegetic_soundscape",
            "cap_whisper_word_level_timestamps",
            "cap_audio_beat_transient_detector"
        ]
    ),
    "node_03_generacion_activos_vox": Node(
        id="node_03_generacion_activos_vox",
        number=3,
        name="Generación de Activos Auténticos VOX 4K",
        role_description="Creación procedimental de mapas vectoriales QGIS (Dash=78), periódicos 1919 con Roughen Edges, blueprints DEM -14M y patentes macro.",
        capabilities=[
            "cap_qgis_vector_dash78",
            "cap_newspaper_roughen_parallax",
            "cap_blueprint_dem_elevation",
            "cap_macro_horology_patent",
            "cap_wikimedia_historical_archive",
            "cap_nanobanana_antigravity_bridge",
            "cap_flux3_serverless_free",
            "cap_flux3_comfyui_runpod",
            "cap_image_quality_filter"
        ]
    ),
    "node_04_composicion_3d_parallax": Node(
        id="node_04_composicion_3d_parallax",
        number=4,
        name="Composición 3D Parallax & Video-as-Code",
        role_description="Montaje espacial en perspectiva 3D con físicas spring(), trazado continuo de rutas, offset Z +0.001 y stagger temporal de 3-5 frames.",
        capabilities=[
            "cap_vox_paper_parallax_3d",
            "cap_vox_cinematic_map_3d",
            "cap_stagger_psicoacustico_motion",
            "cap_motion_remotion_react_hud",
            "cap_paper_texture_overlay",
            "cap_hyperframes_webgl_shaders"
        ]
    ),
    "node_05_subtitulos_y_hud": Node(
        id="node_05_subtitulos_y_hud",
        number=5,
        name="Subtítulos Cinematográficos & Telemetría HUD",
        role_description="Subtítulos en píldora translúcida con resaltado de palabras activo, etiquetas de expediente y mirillas de tracking sobre detalles.",
        capabilities=[
            "cap_kinetic_word_subtitles",
            "cap_whisper_word_level_timestamps",
            "cap_motion_remotion_react_hud"
        ]
    ),
    "node_06_masterizacion_ebu_r128": Node(
        id="node_06_masterizacion_ebu_r128",
        number=6,
        name="Masterización Acústica EBU R128 & Compresión",
        role_description="Compresión y ensamblado final multicapa en FFmpeg con sidechain ducking (-18 dB) y normalización a -14 LUFS.",
        capabilities=[
            "cap_audio_mixing_foley_ducking",
            "cap_sfx_shutter_paper_typewriter",
            "cap_foley_diegetic_soundscape"
        ]
    ),
    "node_07_qa_contact_sheet_sync": Node(
        id="node_07_qa_contact_sheet_sync",
        number=7,
        name="QA Loop, Mosaico de Contactos 4K & Cloud Sync",
        role_description="Generación del mosaico QA fotograma a fotograma para control de calidad y sincronización en Firebase Firestore y Cloudflare R2.",
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
    "workflow_vox_investigative_doc": WorkflowPipeline(
        id="workflow_vox_investigative_doc",
        name="Documental de Investigación VOX (Johnny Harris & createdaley Style)",
        description="Workflow insignia de periodismo visual documental: Storyboard Studio, mapas vectoriales QGIS con rutas Dash=78, recortes de prensa 3D con Roughen Edges (border=3.3px, sharpness=4.58), rotulador flúor animado, blueprints DEM con separación Z +0.001 y masterización EBU R128 con Foley diegético.",
        channel_target=YouTubeChannelTarget(
            channel_name="Hermes Investigative / Vox Visual Docs",
            niche="Periodismo de Investigación, Geopolítica & Ensayos Visuales",
            format="16:9 4K 60FPS",
            visual_style="Vox Cinematic Parallax (Papel Prensa Texturizado, Mapas 3D QGIS Dash=78, Roughen Edges, Subtítulos Cinematográficos sin Cajas, Stagger Psicoacústico)",
            target_audience="Audiencias de YouTube interesadas en documentales de alta retención, análisis geopolítico e historia visual profunda"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=180.0,
        output_specs={"resolution": "3840x2160", "fps": 60, "audio_lufs": -14.0}
    ),
    "workflow_geopolitical_historical_maps": WorkflowPipeline(
        id="workflow_geopolitical_historical_maps",
        name="Geopolítica & Cartografía Histórica 3D (Johnny Harris Style)",
        description="Workflow especializado en geopolítica, evolución de fronteras e historia de conflictos con sobrevuelos de cámara en 3D (DEM QGIS), trazado de rutas bélicas/comerciales y documentos desclasificados.",
        channel_target=YouTubeChannelTarget(
            channel_name="Atlas de Geopolítica & Mapas 3D",
            niche="Conflictos Geopolíticos, Rutas Comerciales e Historia de Fronteras",
            format="16:9 4K 60FPS",
            visual_style="Cartografía Satelital 3D en Relieve (DEM QGIS, Rutas Dash=78, Soft Glow, Viñeteado de Estudio)",
            target_audience="Estudiantes de relaciones internacionales, historia bélica y geografía estratégica"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=240.0,
        output_specs={"resolution": "3840x2160", "fps": 60, "audio_lufs": -14.0}
    ),
    "workflow_madrid_curiosities_3min": WorkflowPipeline(
        id="workflow_madrid_curiosities_3min",
        name="Madrid Secreto 4K: Curiosidades Reales & Beat-Sync (3 min)",
        description="Workflow maestro conducido al 100% por la pista de audio (177.64s). 6 capítulos de misterios bajo el asfalto (Cibeles, Chamberí, Posición Jaca, Reloj Sol, Pasadizo Encarnación, Tumba Goya), paneles glassmorphism 3D, mapas vectoriales QGIS Dash=78 y patentes históricas.",
        channel_target=YouTubeChannelTarget(
            channel_name="Madrid Secreto & Rutas Históricas 4K",
            niche="Documentales Urbanos, Curiosidades y Misterios Ocultos",
            format="16:9 4K 60FPS",
            visual_style="Hollywood Master Montage (Paneles 3D Glassmorphism, B-Roll Real 4K, Fuentes Oficiales en Pantalla)",
            target_audience="Entusiastas de la historia urbana, arquitectura secreta y turismo cultural profundo"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=177.64,
        output_specs={"resolution": "3840x2160", "fps": 60, "audio_lufs": -14.0}
    ),
    "workflow_chronodrift_tritemporal": WorkflowPipeline(
        id="workflow_chronodrift_tritemporal",
        name="CHRONODRIFT: Urban Time Travel 4K (1626 ➔ 2026 ➔ 2226)",
        description="Pipeline tritemporal con transición de eras: archivo histórico de 1626, planos reales 4K de 2026 y reconstrucción ciberpunk 2226 con NanoBanana Pro y FLUX.3.",
        channel_target=YouTubeChannelTarget(
            channel_name="ChronoDrift Expeditions",
            niche="Evolución Urbana y Viajes Temporales",
            format="16:9 4K 60FPS",
            visual_style="Transición Tritemporal (Sepia Grabado ➔ 4K Dron ➔ Cyberpunk Neón)",
            target_audience="Amantes del urbanismo, historia comparada y ciencia ficción arquitectónica"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=180.0,
        output_specs={"resolution": "3840x2160", "fps": 60}
    ),
    "workflow_pixar_3d_animation": WorkflowPipeline(
        id="workflow_pixar_3d_animation",
        name="Cuentos & Animación 3D (Pixar Style)",
        description="Pipeline de narración emotiva con diseño de personajes, LoRAs 3D en FLUX/NanoBanana, iluminación de hora dorada y orquestación sinfónica.",
        channel_target=YouTubeChannelTarget(
            channel_name="Living Canvas / Cuentos Vivos",
            niche="Animación 3D Emotiva & Cuentacuentos",
            format="16:9 4K 24FPS",
            visual_style="Pixar 3D Cinematic (Subsurface Scattering, Bokeh T1.8, Volumetric Light)",
            target_audience="Familias y amantes del cine de animación de alta calidad"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=210.0
    ),
    "workflow_historical_scraping": WorkflowPipeline(
        id="workflow_historical_scraping",
        name="Documental Histórico & Archivo Real",
        description="Pipeline de periodismo de archivo con scraping en hemerotecas, recortes de fotografías de época, mapas animados y voz sobria.",
        channel_target=YouTubeChannelTarget(
            channel_name="Archivos Desclasificados",
            niche="Historia Documental & Desclasificados",
            format="16:9 4K 60FPS",
            visual_style="Estilo Vox Documental (Papel envejecido, sellos de tinta, fotos restauradas)",
            target_audience="Audiencia interesada en historia rigurosa, enigmas y documentación oficial"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=240.0
    ),
    "workflow_deep_explainer_essay": WorkflowPipeline(
        id="workflow_deep_explainer_essay",
        name="Deep Explainer & Videoensayo Dialéctico",
        description="Videoensayos de alta complejidad con razonamiento en 3 actos, gráficos cinéticos en Remotion y montaje dialéctico.",
        channel_target=YouTubeChannelTarget(
            channel_name="TerraMorph / Deep Essays",
            niche="Videoensayos de Filosofía, Geopolítica y Futuro",
            format="16:9 4K 60FPS",
            visual_style="Minimalismo Cinemático & Gráficos Editoriales Suizos",
            target_audience="Estudiantes, investigadores y profesionales del análisis profundo"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=300.0
    ),
    "workflow_viral_shorts_hook": WorkflowPipeline(
        id="workflow_viral_shorts_hook",
        name="Viral Shorts & Retención Extrema (TikTok / Reels 60s)",
        description="Montaje vertical de 60 segundos con subtítulos burned karaoke, cortes cada 1.5s, zoom in/out y transiciones aceleradas.",
        channel_target=YouTubeChannelTarget(
            channel_name="Curiosidades Flash 60s",
            niche="YouTube Shorts & Micro-documentales",
            format="9:16 Vertical 1080x1920",
            visual_style="Karaoke Subtitles Bold, Zoom In/Out cada 1.5s",
            target_audience="Consumidores de contenido corto en móvil"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=60.0
    ),
    "workflow_city_routes_beats": WorkflowPipeline(
        id="workflow_city_routes_beats",
        name="Rutas Urbanas & Vídeos Musicales (City Beats 118-128 BPM)",
        description="Tomas continuas de ciudades sincronizadas con música electrónica lo-fi o synthwave con cortes en los golpes de caja.",
        channel_target=YouTubeChannelTarget(
            channel_name="City Beats Soundtracks",
            niche="Vídeos Musicales Urbanos & Paisajes Sonoros",
            format="16:9 4K 60FPS",
            visual_style="Cine Nocturno Neón, Tomas en Movimiento Rápido",
            target_audience="Amantes de la música electrónica y paseos urbanos nocturnos"
        ),
        ordered_nodes=[
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ],
        estimated_duration_sec=180.0
    ),
    "workflow_fpv_urban_real_flow": WorkflowPipeline(
        id="workflow_fpv_urban_real_flow",
        name="Tours Urbanos Flow Real 4K & Beat-Sync",
        description="Planos aéreos continuos, vuelos orbitales en Google Flow 3D y telemetría cinemática.",
        channel_target=YouTubeChannelTarget(
            channel_name="Urban Flow Expeditions",
            niche="Tours Aéreos y Recorridos FPV Urbanos",
            format="16:9 4K 60FPS",
            visual_style="HUD FPV Dinámico con Velocímetro y Altitud",
            target_audience="Aficionados a los viajes visuales de alta inmersión"
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
    "workflow_fpv_urban_storytelling": WorkflowPipeline(
        id="workflow_fpv_urban_storytelling",
        name="Tours FPV y Storytelling Urbano 4K",
        description="Fusión de vuelo FPV con narrativa histórica explicativa y paradas en puntos de interés.",
        channel_target=YouTubeChannelTarget(
            channel_name="AstroDrift / FPV Stories",
            niche="Exploración Narrada de Megaciudades",
            format="16:9 4K 60FPS",
            visual_style="Vuelo Cinemático Guiado con Anotaciones en Pantalla",
            target_audience="Viajeros y curiosos del diseño arquitectónico"
        ),
        ordered_nodes=[
            "node_01_investigacion_y_narrativa",
            "node_02_audio_first_y_ritmo",
            "node_03_ingesta_multimedia_4k",
            "node_04_composicion_motion_graphics",
            "node_05_masterizacion_audio_foley",
            "node_06_qa_evaluacion_y_sync"
        ],
        estimated_duration_sec=200.0
    )
}


def sync_entire_ontology_to_firebase() -> bool:
    """Sincroniza la ontología completa de 4 niveles y la memoria de aprendizaje en Firebase Firestore."""
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
        "updated_at": {"stringValue": datetime.now().isoformat()}
    }
    
    try:
        resp = requests.patch(url, headers=headers, json={"fields": fields}, timeout=10)
        # Sincronizar también la memoria de aprendizaje
        from app.services.learning_memory_engine import learning_engine
        learning_engine.sync_to_firebase_async()
        return resp.status_code in (200, 201)
    except Exception as ex:
        print(f"Error sincronizando ontología en Firestore: {ex}")
        return False

