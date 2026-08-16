"""
Registro Maestro de Proveedores, Infraestructura y Configuración Activa — VideoPro Studio
Fuente de Verdad Única del Ecosistema: gestiona motores, infraestructuras (Local, Serverless, Cloud),
credenciales de API, enlaces funcionales, modelos, opciones atómicas y persistencia estricta.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

REGISTRY_PATH = os.path.join(BASE_DIR, "storage", "providers_registry.json")

logger = logging.getLogger("videopro.registry")

# Catálogo maestro con enlaces a consolas, credenciales asociadas y modelos
DEFAULT_PROVIDERS = {
    # --- 1. VISUAL & VÍDEO ---
    "nanobanana": {
        "id": "nanobanana",
        "name": "NanoBanana Pro 2 (Gemini Imagen 3 — Local Bridge 8742)",
        "category": "visual",
        "infra_type": "local",
        "enabled": True,
        "label": "🍌 NanoBanana Pro 2 (Local Bridge Puerto 8742 — 2K/4K)",
        "source_engine": "nanobanana",
        "description": "Generación de fotogramas clave en 2K/4K y texturas fotorrealistas vía Antigravity Bridge ($0).",
        "endpoint_field": "antigravity_endpoint",
        "endpoint_default": "http://127.0.0.1:8742/v1",
        "model_field": "nanobanana_model",
        "model_default": "gemini-3.1-flash-image",
        "model_options": ["gemini-3.1-flash-image", "gemini-3.7-flash-image", "imagen-3.0-generate-002"],
        "doc_link": "https://aistudio.google.com/",
        "doc_link_text": "Google AI Studio ↗",
        "categories": [
            {"text": "Generación de Keyframes 2K/4K (Imagen 3)", "checked": True},
            {"text": "Texturas Fotorrealistas 35mm sin Artefactos", "checked": True},
            {"text": "Inferencia Directa $0 vía Antigravity Bridge", "checked": True}
        ],
        "infrastructure": [
            {"text": "CPU/GPU Local Servidor (Puerto 8742 $0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Generar siempre en 2K (2048x2048 / 2048x1152)", "checked": True},
            {"text": "✨ Preferencia: Grano de película cinemático sutil", "checked": True},
            {"text": "🚫 Descartar NanoBanana Lite / Modelos Fast (<1024px)", "checked": True}
        ],
        "behaviors": [
            {"text": "Renderiza fotogramas de alta coherencia para la pista de vídeo", "checked": True}
        ],
        "notes": "Motor principal de generación de imágenes fotorrealistas a coste $0."
    },
    "flux_zerogpu": {
        "id": "flux_zerogpu",
        "name": "FLUX 3 Video (Serverless ZeroGPU Cloud Pool)",
        "category": "visual",
        "infra_type": "serverless",
        "enabled": True,
        "label": "FLUX 3 Video (Serverless ZeroGPU Pool $0)",
        "source_engine": "flux",
        "description": "Inferencia serverless distribuida en espacios Hugging Face ZeroGPU con rotación de tokens.",
        "api_key_field": "hf_token",
        "doc_link": "https://huggingface.co/settings/tokens",
        "doc_link_text": "Crear token HuggingFace ↗",
        "categories": [
            {"text": "Text-to-Video Cinemático 4K (Flow Matching)", "checked": True},
            {"text": "Diálogos Nativos de Personajes 4K", "checked": True},
            {"text": "Generación de Stills / Keyframes 4K", "checked": True}
        ],
        "infrastructure": [
            {"text": "GPU Gratis (ZeroGPU Hugging Face Pool con rotación de tokens)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Generar siempre en 1080p nativo", "checked": True},
            {"text": "✨ Preferencia: Tasa de 24fps Cinemática", "checked": True},
            {"text": "🚫 Descartar 480p", "checked": True},
            {"text": "🚫 Descartar 720p de bajo bitrate", "checked": True}
        ],
        "behaviors": [
            {"text": "Genera diálogos nativos de los personajes en el propio vídeo", "checked": True},
            {"text": "NO poner locutor narrador encima (evitar solapamiento)", "checked": True}
        ],
        "notes": "Difusión de vídeo serverless sin consumo de CPU del servidor VPS."
    },
    "flux_replicate": {
        "id": "flux_replicate",
        "name": "FLUX 3 Video (Replicate H100 Dedicated GPU)",
        "category": "visual",
        "infra_type": "cloud",
        "enabled": True,
        "label": "FLUX 3 Video (Replicate Clúster H100)",
        "source_engine": "flux",
        "description": "GPU H100 dedicada de alta velocidad bajo demanda para render prioritario.",
        "api_key_field": "replicate_api_token",
        "doc_link": "https://replicate.com/account/api-tokens",
        "doc_link_text": "Consola Replicate ↗",
        "categories": [
            {"text": "Inferencia Dedicada en Clúster NVIDIA H100", "checked": True},
            {"text": "FLUX 1.1 Pro Ultra-HD", "checked": True}
        ],
        "infrastructure": [
            {"text": "GPU Pago (Replicate H100 Dedicado)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Render 1080p / 4K UHD", "checked": True}
        ],
        "behaviors": [
            {"text": "Render acelerado con cola prioritaria", "checked": True}
        ],
        "notes": "Vía de alta velocidad cuando hay congestión en ZeroGPU."
    },
    "ltx25": {
        "id": "ltx25",
        "name": "LTX-2.5 MMDiT 22B (Audio + Vídeo 24fps)",
        "category": "visual",
        "infra_type": "cloud",
        "enabled": True,
        "label": "LTX-2.5 MMDiT 22B (Audio + Vídeo 24fps)",
        "source_engine": "ltx25",
        "description": "Vídeo nativo a 24fps con audio sincronizado y síntesis de diálogos.",
        "api_key_field": "replicate_api_token",
        "doc_link": "https://replicate.com/lightricks/ltx-video",
        "doc_link_text": "Documentación LTX ↗",
        "categories": [
            {"text": "22B MMDiT Dual-Track Audio-Visual Synthesis", "checked": True},
            {"text": "Audio Nativo 48kHz Directo", "checked": True},
            {"text": "Sincronización Labial Lip-Sync a 24fps", "checked": True}
        ],
        "infrastructure": [
            {"text": "GPU Pago (Replicate H100) / ZeroGPU", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Audio master 48kHz WAV", "checked": True},
            {"text": "✨ Preferencia: Lip-sync sincronizado a 24fps", "checked": True},
            {"text": "🚫 Descartar audio 16kHz", "checked": True}
        ],
        "behaviors": [
            {"text": "Sintetiza voces directas de los personajes sin locutor externo", "checked": True},
            {"text": "Audio ambiental y foley acústico nativo en la pista", "checked": True}
        ],
        "notes": "Modelo de 22B parámetros con audio integrado a 48kHz."
    },
    "fal_ai": {
        "id": "fal_ai",
        "name": "Fal.ai (FLUX Schnell / FLUX Pro)",
        "category": "visual",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Fal.ai FLUX Schnell & Pro",
        "source_engine": "fal",
        "description": "Inferencia de baja latencia para generación de escenas fotográficas y vídeo.",
        "api_key_field": "fal_api_key",
        "doc_link": "https://fal.ai/dashboard/keys",
        "doc_link_text": "Consola Fal.ai ↗",
        "categories": [
            {"text": "FLUX Schnell Generación Instantánea", "checked": True}
        ],
        "infrastructure": [
            {"text": "Fal.ai Serverless Cloud GPU", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Generación a 1080p", "checked": True}
        ],
        "behaviors": [
            {"text": "Procesamiento acelerado", "checked": True}
        ],
        "notes": "Pasarela de inferencia ultra-rápida de modelos FLUX."
    },
    "pexels": {
        "id": "pexels",
        "name": "Pexels Video Stock 4K",
        "category": "visual",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Pexels Video Stock HD ($0)",
        "source_engine": "pexels",
        "description": "Material de archivo stock 4K/1080p libre de royalties para documentales.",
        "api_key_field": "pexels_api_key",
        "doc_link": "https://www.pexels.com/api/",
        "doc_link_text": "Obtener clave Pexels ↗",
        "categories": [
            {"text": "Búsqueda Semántica de Stock 4K/1080p", "checked": True},
            {"text": "Licencia Comercial Libre $0", "checked": True}
        ],
        "infrastructure": [
            {"text": "Cloud API (Pexels / Pixabay)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Vídeo en 1080p o superior", "checked": True}
        ],
        "behaviors": [
            {"text": "Corte y reencuadre dinámico 9:16 o 16:9", "checked": True}
        ],
        "notes": "Recurso complementario de stock para planos documentales."
    },
    "pixabay": {
        "id": "pixabay",
        "name": "Pixabay Video & Foto Stock HD",
        "category": "visual",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Pixabay Stock HD ($0)",
        "source_engine": "pixabay",
        "description": "Clips de vídeo y fotografías complementarias de uso libre sin coste.",
        "api_key_field": "pixabay_api_key",
        "doc_link": "https://pixabay.com/api/docs/",
        "doc_link_text": "Obtener clave Pixabay ↗",
        "categories": [
            {"text": "Stock de Apoyo Documental", "checked": True}
        ],
        "infrastructure": [
            {"text": "Pixabay Cloud API", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Clips Full HD", "checked": True}
        ],
        "behaviors": [
            {"text": "Ajuste dinámico a timeline", "checked": True}
        ],
        "notes": "Colección de stock libre complementaria."
    },
    "google_flow": {
        "id": "google_flow",
        "name": "Google Flow (Playwright Navegador Web 4K)",
        "category": "visual",
        "infra_type": "local_headless",
        "enabled": True,
        "label": "Google Flow (Playwright Navegador Web 4K)",
        "source_engine": "google_flow",
        "description": "Automatización de vídeo cinemático 4K y trayectoria orbital 3D vía navegador Chrome Playwright ($0).",
        "doc_link": "https://flow.google.com/",
        "doc_link_text": "Web Google Flow ↗",
        "model_field": "google_flow_model",
        "model_default": "flow-cinematic-4k",
        "model_options": ["flow-cinematic-4k", "flow-freeze-frame-3d", "flow-omni-flash"],
        "endpoint_field": "google_flow_session",
        "categories": [
            {"text": "3D Freeze-Frame Orbital Trajectory", "checked": True},
            {"text": "Storyboard Studio Multiclip", "checked": True}
        ],
        "infrastructure": [
            {"text": "Navegador Web (Playwright en flow.google.com)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Vídeo cinemático 1080p", "checked": True}
        ],
        "behaviors": [
            {"text": "Vídeo cinemático puro sin narrador ciego", "checked": True}
        ],
        "notes": "Automatización en navegador Chromium desatendido."
    },
    "real_news": {
        "id": "real_news",
        "name": "DuckDuckGo & Wikimedia Real News",
        "category": "visual",
        "infra_type": "serverless",
        "enabled": True,
        "label": "DuckDuckGo & Wikimedia Images ($0)",
        "source_engine": "real_news",
        "description": "Fotoperiodismo e imágenes fácticas reales en alta resolución sin token ($0).",
        "doc_link": "https://commons.wikimedia.org/",
        "doc_link_text": "Wikimedia Commons ↗",
        "model_field": "real_news_resolution",
        "model_default": "Filtro HD / 4K Fáctico",
        "model_options": ["Filtro HD / 4K Fáctico", "Fotoperiodismo de Alta Resolución", "Imágenes Históricas Documentales"],
        "categories": [
            {"text": "Fotoperiodismo Real Documental", "checked": True}
        ],
        "infrastructure": [
            {"text": "Ingestion Web Directa ($0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Imágenes de alta resolución", "checked": True}
        ],
        "behaviors": [
            {"text": "Efecto Ken Burns sutil (Paneo y Zoom 2.5D)", "checked": True}
        ],
        "notes": "Imágenes fácticas reales para noticias e historia."
    },

    # --- 2. DIRECTORES LLM ---
    "gemini": {
        "id": "gemini",
        "name": "Google Gemini (AI Studio Cloud)",
        "category": "llm",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Gemini 2.5 Flash / Gemini 3.7 Flash",
        "description": "Director principal en la nube: guiones multimodales de alta coherencia a coste $0 en tier gratuito.",
        "api_key_field": "gemini_api_key",
        "model_field": "gemini_model_name",
        "model_default": "gemini-2.5-flash",
        "model_options": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.7-flash", "gemini-1.5-pro"],
        "doc_link": "https://aistudio.google.com/app/apikey",
        "doc_link_text": "Obtener clave Google AI Studio ↗",
        "categories": [
            {"text": "Gemini 2.5 / 3.7 Multimodal", "checked": True},
            {"text": "Análisis Contextual Amplio (1M tokens)", "checked": True}
        ],
        "infrastructure": [
            {"text": "Google AI Studio Cloud Direct", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Modo Flash para alta velocidad", "checked": True}
        ],
        "behaviors": [
            {"text": "Estructuración de guiones de 3 a 5 párrafos", "checked": True}
        ],
        "notes": "Director en la nube oficial de Google AI Studio."
    },
    "groq": {
        "id": "groq",
        "name": "Groq Cloud (Llama 3.3 70B Fast)",
        "category": "llm",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Groq Llama 3.3 70B Versatile",
        "description": "Inferencia ultra-rápida a +300 tokens/s en chips LPU y transcripción Whisper sin latencia.",
        "api_key_field": "groq_api_key",
        "model_field": "groq_model_name",
        "model_default": "llama-3.3-70b-versatile",
        "model_options": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        "doc_link": "https://console.groq.com/keys",
        "doc_link_text": "Obtener clave Groq ↗",
        "categories": [
            {"text": "Inferencia LPU Ultra-Rápida (+300 tokens/s)", "checked": True},
            {"text": "Llama 3.3 70B Versatile", "checked": True}
        ],
        "infrastructure": [
            {"text": "Groq Cloud LPU", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Latencia mínima en streaming", "checked": True}
        ],
        "behaviors": [
            {"text": "Generación de escaleta instantánea", "checked": True}
        ],
        "notes": "Inferencia acelerada para redacción en tiempo real."
    },
    "antigravity": {
        "id": "antigravity",
        "name": "Antigravity Bridge & OpenAI (Gemini 3.7 / GPT-4o)",
        "category": "llm",
        "infra_type": "local",
        "enabled": True,
        "label": "🍌 Antigravity Bridge (Gemini 3.7 Flash High / Puerto 8742)",
        "description": "Director principal local en puerto 8742 sin consumo de tokens ($0) o puente OpenAI GPT-4o.",
        "api_key_field": "openai_api_key",
        "endpoint_field": "openai_base_url",
        "endpoint_default": "http://127.0.0.1:8742/v1",
        "model_field": "openai_model_name",
        "model_default": "gemini-3.7-flash-high",
        "doc_link": "https://platform.openai.com/api-keys",
        "doc_link_text": "Consola OpenAI ↗",
        "categories": [
            {"text": "Director Cinematográfico 5D", "checked": True},
            {"text": "Razonamiento y Guiones con Streaming Nativo", "checked": True},
            {"text": "Sin Consumo de Tokens de Pago ($0)", "checked": True}
        ],
        "infrastructure": [
            {"text": "Antigravity Bridge (Puerto 8742 Local)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Gemini 3.7 Flash High con streaming", "checked": True}
        ],
        "behaviors": [
            {"text": "Interpreta lenguaje natural y genera especificaciones por escena", "checked": True}
        ],
        "notes": "Director de IA principal predeterminado de VideoPro Studio."
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic Claude (Claude 3.5 Sonnet)",
        "category": "llm",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Claude 3.5 Sonnet",
        "description": "Dramaturgia de autor y narrativa cinematográfica con máxima calidad literaria.",
        "api_key_field": "anthropic_api_key",
        "doc_link": "https://console.anthropic.com/settings/keys",
        "doc_link_text": "Obtener clave Anthropic ↗",
        "categories": [
            {"text": "Claude 3.5 Sonnet Dramaturgia", "checked": True}
        ],
        "infrastructure": [
            {"text": "Anthropic Cloud API", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Estilo narrativo de autor", "checked": True}
        ],
        "behaviors": [
            {"text": "Diálogos cinematográficos envolventes", "checked": True}
        ],
        "notes": "Modelo para guiones de alta factura narrativa."
    },
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek Oficial (DeepSeek-V3 / R1)",
        "category": "llm",
        "infra_type": "cloud",
        "enabled": True,
        "label": "DeepSeek R1 / V3",
        "description": "Análisis documental exhaustivo y razonamiento profundo con cadena de pensamiento.",
        "api_key_field": "deepseek_api_key",
        "doc_link": "https://platform.deepseek.com/api_keys",
        "doc_link_text": "Consola DeepSeek ↗",
        "categories": [
            {"text": "DeepSeek R1 Cadena de Pensamiento", "checked": True}
        ],
        "infrastructure": [
            {"text": "DeepSeek Cloud API", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Verificación factual profunda", "checked": True}
        ],
        "behaviors": [
            {"text": "Validación lógica paso a paso", "checked": True}
        ],
        "notes": "Especialista en investigación documental y precisión."
    },
    "cloudflare_ai": {
        "id": "cloudflare_ai",
        "name": "Cloudflare Workers AI (Serverless Edge)",
        "category": "llm",
        "infra_type": "serverless",
        "enabled": True,
        "label": "Cloudflare Llama 3.3 & FLUX Schnell",
        "description": "Inferencia global en la red Edge de Cloudflare sin servidores para Llama 3.3 y FLUX Schnell.",
        "api_key_field": "cloudflare_api_key",
        "endpoint_field": "cloudflare_account_id",
        "doc_link": "https://dash.cloudflare.com/",
        "doc_link_text": "Cloudflare Dashboard ↗",
        "categories": [
            {"text": "Inferencia Serverless Global en el Borde", "checked": True}
        ],
        "infrastructure": [
            {"text": "Cloudflare Workers AI Edge", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Distribución global de baja latencia", "checked": True}
        ],
        "behaviors": [
            {"text": "Ejecución distribuida sin servidor", "checked": True}
        ],
        "notes": "Inferencia en la red edge de Cloudflare."
    },
    "siliconflow": {
        "id": "siliconflow",
        "name": "SiliconFlow & ModelScope Pasarela",
        "category": "llm",
        "infra_type": "cloud",
        "enabled": True,
        "label": "SiliconFlow DeepSeek / Qwen",
        "description": "Despliegue serverless de alta disponibilidad para DeepSeek-V3 y Qwen 2.5 72B.",
        "api_key_field": "siliconflow_api_key",
        "doc_link": "https://cloud.siliconflow.cn/account/ak",
        "doc_link_text": "Consola SiliconFlow ↗",
        "categories": [
            {"text": "Inferencia Serverless Reducida", "checked": True}
        ],
        "infrastructure": [
            {"text": "SiliconFlow Cloud GPU", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Coste ultra-reducido", "checked": True}
        ],
        "behaviors": [
            {"text": "Ejecución continua", "checked": True}
        ],
        "notes": "Pasarela serverless de alta disponibilidad."
    },

    # --- 3. VOCES & LOCUCIÓN ---
    "kokoro_local": {
        "id": "kokoro_local",
        "name": "Kokoro TTS HD (Local CPU Puerto 7892)",
        "category": "voice",
        "infra_type": "local",
        "enabled": True,
        "label": "Kokoro TTS HD ($0 Local CPU Puerto 7892)",
        "description": "Voz local en español de alta fidelidad 24kHz ejecutada 100% en el servidor local ($0).",
        "categories": [
            {"text": "Kokoro-82M ONNX High-Fidelity 24kHz Text-to-Speech", "checked": True},
            {"text": "Locución en Off / Narrador", "checked": True},
            {"text": "Voz Documental (Dora / Santiago / Alex)", "checked": True}
        ],
        "infrastructure": [
            {"text": "CPU Local Servidor ($0 Sin Coste en puerto 7892)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Voces en Español (Dora / Santiago / Alex)", "checked": True},
            {"text": "✨ Preferencia: Síntesis en 24kHz High-Fidelity", "checked": True},
            {"text": "🚫 Descartar voces sintéticas robotizadas (8kHz/16kHz)", "checked": True}
        ],
        "behaviors": [
            {"text": "Solo se sintetiza si el usuario elige expresamente un locutor", "checked": True},
            {"text": "Atenúa la música de fondo automáticamente a -22 dB", "checked": True}
        ],
        "notes": "Totalmente gratuito sin consumo de API ni conexión externa."
    },
    "vibevoice_local": {
        "id": "vibevoice_local",
        "name": "VibeVoice 1.5B (Local VPS Engine)",
        "category": "voice",
        "infra_type": "local",
        "enabled": True,
        "label": "VibeVoice 1.5B (Local VPS Python /home/ubuntu/vibevoice-venv)",
        "description": "Inferencia local directa en la VPS sin dependencias externas ni consumo de red.",
        "categories": [
            {"text": "VibeVoice 1.5B Continuous-Prosody Neural TTS", "checked": True},
            {"text": "Clonación de Voz Emocional Zero-Shot", "checked": True},
            {"text": "Locución Documental Expresiva (es-emilio)", "checked": True}
        ],
        "infrastructure": [
            {"text": "VPS Local Python (/home/ubuntu/vibevoice-venv)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Modelo local en disco", "checked": True},
            {"text": "✨ Preferencia: Master Audio 24kHz / 48kHz WAV", "checked": True}
        ],
        "behaviors": [
            {"text": "Inferencia directa en CPU/GPU local", "checked": True},
            {"text": "Atenúa la música de fondo automáticamente a -22 dB", "checked": True}
        ],
        "notes": "Inferencia 100% offline y soberana en el propio servidor VPS."
    },
    "vibevoice_serverless": {
        "id": "vibevoice_serverless",
        "name": "VibeVoice 1.5B (Serverless ZeroGPU Cloud Pool)",
        "category": "voice",
        "infra_type": "serverless",
        "enabled": True,
        "label": "VibeVoice 1.5B (Serverless ZeroGPU Cloud Pool $0)",
        "description": "Inferencia serverless en clúster Hugging Face ZeroGPU con rotación de tokens $0.",
        "api_key_field": "hf_token",
        "doc_link": "https://huggingface.co/settings/tokens",
        "doc_link_text": "Tokens HuggingFace ↗",
        "categories": [
            {"text": "VibeVoice 1.5B Continuous-Prosody Neural TTS", "checked": True},
            {"text": "Clonación de Voz Emocional Zero-Shot", "checked": True},
            {"text": "Locución Documental Expresiva (es-emilio)", "checked": True}
        ],
        "infrastructure": [
            {"text": "GPU Gratis (ZeroGPU Hugging Face Pool)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Voz Emilio (es-emilio-Male)", "checked": True},
            {"text": "✨ Preferencia: Master Audio 24kHz / 48kHz", "checked": True}
        ],
        "behaviors": [
            {"text": "Auto-ducking a -22 dB en banda musical durante la locución", "checked": True}
        ],
        "notes": "Inferencia serverless distribuida en la nube sin carga en la CPU del VPS."
    },
    "edge_tts": {
        "id": "edge_tts",
        "name": "Edge-TTS Neural (Microsoft Cloud Serverless)",
        "category": "voice",
        "infra_type": "serverless",
        "enabled": True,
        "label": "Edge-TTS Neural ($0 Cloud Serverless)",
        "description": "Locución neural fluida multilingüe en la nube de Microsoft sin coste.",
        "categories": [
            {"text": "Locución Neural Microsoft $0", "checked": True},
            {"text": "Voces Castellano & Latino Natural", "checked": True}
        ],
        "infrastructure": [
            {"text": "Cloud Serverless Ingestion ($0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Voces Álvaro y Elvira", "checked": True}
        ],
        "behaviors": [
            {"text": "Síntesis inmediata sin latencia", "checked": True}
        ],
        "notes": "Locución fluida en la nube sin coste."
    },
    "elevenlabs": {
        "id": "elevenlabs",
        "name": "ElevenLabs Cinema Voices (Cloud API)",
        "category": "voice",
        "infra_type": "cloud",
        "enabled": True,
        "label": "ElevenLabs Cinema & Clonación",
        "description": "Calidad cinematográfica hiperrealista y clonación de voz profesional.",
        "api_key_field": "elevenlabs_api_key",
        "doc_link": "https://elevenlabs.io/",
        "doc_link_text": "Consola ElevenLabs ↗",
        "categories": [
            {"text": "Voces Hiperrealistas de Cine", "checked": True},
            {"text": "Clonación Instantánea de Voz", "checked": True}
        ],
        "infrastructure": [
            {"text": "ElevenLabs Cloud Dedicated", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Voces Adam y Rachel a 44.1kHz", "checked": True}
        ],
        "behaviors": [
            {"text": "Modulación emocional profunda por frase", "checked": True}
        ],
        "notes": "Calidad de producción para trailers y cortometrajes."
    },
    "fish_audio": {
        "id": "fish_audio",
        "name": "Fish Audio API (Clonación de Voz)",
        "category": "voice",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Fish Audio Neural",
        "description": "Modelos neurales expresivos de baja latencia con clonación ultra-rápida.",
        "api_key_field": "fish_audio_api_key",
        "doc_link": "https://fish.audio/",
        "doc_link_text": "Consola Fish Audio ↗",
        "categories": [
            {"text": "Clonación Neural de Ultra-Baja Latencia", "checked": True}
        ],
        "infrastructure": [
            {"text": "Fish Audio Cloud API", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Síntesis fluida 44.1kHz", "checked": True}
        ],
        "behaviors": [
            {"text": "Entonación adaptativa", "checked": True}
        ],
        "notes": "Motor de síntesis vocal rápida."
    },
    "minimax": {
        "id": "minimax",
        "name": "MiniMax Speech 01 (Voz Expresiva)",
        "category": "voice",
        "infra_type": "cloud",
        "enabled": True,
        "label": "MiniMax Speech 01",
        "description": "Inflexión dramática y entonación adaptativa para narraciones cinematográficas.",
        "api_key_field": "minimax_api_key",
        "doc_link": "https://www.minimax.io/",
        "doc_link_text": "Consola MiniMax ↗",
        "categories": [
            {"text": "Entonación Dramática MiniMax", "checked": True}
        ],
        "infrastructure": [
            {"text": "MiniMax Cloud API", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Narración inmersiva", "checked": True}
        ],
        "behaviors": [
            {"text": "Atenuación musical automática", "checked": True}
        ],
        "notes": "Locución con modulación dramática profunda."
    },

    # --- 4. MÚSICA & FOLEY ---
    "flowmusic": {
        "id": "flowmusic",
        "name": "Google Flow Music (Lyria 3)",
        "category": "music",
        "infra_type": "local_headless",
        "enabled": True,
        "label": "Google Flow Music (Lyria 3)",
        "description": "Bandas sonoras cinemáticas y foley dinámico adaptado por escena.",
        "api_key_field": "flowmusic_session",
        "categories": [
            {"text": "Composición Orquestal Lyria 3", "checked": True},
            {"text": "Foley Acústico Dinámico", "checked": True}
        ],
        "infrastructure": [
            {"text": "Playwright Headless Navegador", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Audio WAV 48kHz", "checked": True}
        ],
        "behaviors": [
            {"text": "Sincronización a compás de las transiciones", "checked": True}
        ],
        "notes": "Música adaptativa según la tensión dramática del guion."
    },
    "suno": {
        "id": "suno",
        "name": "Suno AI API (v3 / v4)",
        "category": "music",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Suno AI (v3 / v4)",
        "description": "Composición musical con arreglos modernos instrumentales o con lírica.",
        "api_key_field": "suno_api_key",
        "doc_link": "https://suno.com/",
        "doc_link_text": "Consola Suno ↗",
        "categories": [
            {"text": "Composición Canciones Completas v3/v4", "checked": True}
        ],
        "infrastructure": [
            {"text": "Suno AI Cloud API", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Versión Instrumental", "checked": True}
        ],
        "behaviors": [
            {"text": "Atenuación automática bajo voz", "checked": True}
        ],
        "notes": "Composición musical con arreglos modernos."
    },
    "r2_storage": {
        "id": "r2_storage",
        "name": "Cloudflare R2 Object Storage (Zero Egress)",
        "category": "cloud",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Cloudflare R2 (S3 Zero Egress)",
        "description": "Almacenamiento y CDN global de vídeos máster sin coste por descarga.",
        "endpoint_field": "s3_endpoint",
        "api_key_field": "s3_access_key",
        "doc_link": "https://dash.cloudflare.com/",
        "doc_link_text": "Consola Cloudflare R2 ↗",
        "categories": [
            {"text": "Almacenamiento Global S3 Compatible", "checked": True},
            {"text": "Zero Egress (Descargas Gratuitas)", "checked": True}
        ],
        "infrastructure": [
            {"text": "Cloudflare Global Edge R2", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Presigned URLs de 24h", "checked": True}
        ],
        "behaviors": [
            {"text": "Respaldo automático de másters de vídeo", "checked": True}
        ],
        "notes": "Almacenamiento seguro para exportación y visualización remota."
    },
    "firebase_db": {
        "id": "firebase_db",
        "name": "Firebase Firestore & Hosting",
        "category": "cloud",
        "infra_type": "cloud",
        "enabled": True,
        "label": "Firebase Firestore (Base de Datos)",
        "description": "Persistencia en la nube de configuraciones, claves y proyectos.",
        "endpoint_field": "firebase_project_id",
        "doc_link": "https://console.firebase.google.com/",
        "doc_link_text": "Consola Firebase ↗",
        "categories": [
            {"text": "Persistencia de Ajustes en la Nube", "checked": True},
            {"text": "Hosting Web de Producción", "checked": True}
        ],
        "infrastructure": [
            {"text": "Google Cloud Firestore", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Sincronización asíncrona", "checked": True}
        ],
        "behaviors": [
            {"text": "Sincronización en segundo plano de proyectos y claves", "checked": True}
        ],
        "notes": "Base de datos maestra en la nube para sincronización multi-dispositivo."
    },

    # --- 5. PROGRAMACIÓN, SUBTÍTULOS & ENSAMBLAJE (HABILIDADES DEL SISTEMA) ---
    "vox_subtitles": {
        "id": "vox_subtitles",
        "name": "Subtítulos Dinámicos Vox Style (Karaoke & Highlight)",
        "category": "programacion",
        "infra_type": "local",
        "enabled": True,
        "label": "Subtítulos Vox Dynamic Highlight (Amarillo/Blanco)",
        "description": "Generación y estilizado de subtítulos animados cinemáticos con palabra activa resaltada.",
        "categories": [
            {"text": "Subtítulos Vox Dynamic Highlight (Amarillo/Blanco)", "checked": True},
            {"text": "Karaoke Word-by-Word Animation", "checked": True},
            {"text": "Segmentación Inteligente (1-3 palabras por pantalla)", "checked": True}
        ],
        "infrastructure": [
            {"text": "Motor Interno ASS / FFmpeg Sub Station ($0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Estilo Vox Highlight (Amarillo Dinámico)", "checked": True},
            {"text": "✨ Preferencia: Máximo 2 palabras simultáneas", "checked": True},
            {"text": "✨ Preferencia: Posición inferior central (Bottom Margin 60px)", "checked": True},
            {"text": "🚫 Descartar subtítulos estáticos en bloque largo", "checked": True}
        ],
        "behaviors": [
            {"text": "Sincroniza el resaltado exacto con los timestamps de Whisper STT", "checked": True},
            {"text": "Quema subtítulos en el render final o exporta archivo .SRT/.ASS", "checked": True}
        ],
        "notes": "Renderizado programático de subtítulos dinámicos de alto impacto visual."
    },
    "whisper_stt": {
        "id": "whisper_stt",
        "name": "Whisper STT (Alineación Temporal & Transcripción)",
        "category": "programacion",
        "infra_type": "local",
        "enabled": True,
        "label": "Whisper STT Word Timestamps",
        "description": "Transcripción fonética y alineación milimétrica palabra por palabra para subtítulos.",
        "categories": [
            {"text": "Whisper Base/Small Local Multilingüe", "checked": True},
            {"text": "Alineación Fonética Milimétrica (Word Timestamps)", "checked": True},
            {"text": "Detección Automática de Idioma y Puntuación", "checked": True}
        ],
        "infrastructure": [
            {"text": "Inferencia CPU Local / Faster-Whisper ($0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Modelo Whisper Base en español", "checked": True},
            {"text": "✨ Preferencia: Timestamps exactos por palabra", "checked": True},
            {"text": "🚫 Descartar transcripción sin marcas temporales", "checked": True}
        ],
        "behaviors": [
            {"text": "Genera la pista temporal para el motor de subtítulos Vox", "checked": True}
        ],
        "notes": "Motor de reconocimiento y segmentación acústica de voz."
    },
    "ffmpeg_core": {
        "id": "ffmpeg_core",
        "name": "Motor de Ensamblaje FFmpeg + MoviePy",
        "category": "programacion",
        "infra_type": "local",
        "enabled": True,
        "label": "FFmpeg Engine & Ducking Acústico",
        "description": "Pipeline multicapa de vídeo, transiciones, audio máster y ducking a -22dB.",
        "categories": [
            {"text": "Pipeline Multicapa Vídeo + Audio + Subtítulos", "checked": True},
            {"text": "Auto-Ducking Acústico (-22 dB bajo voz)", "checked": True},
            {"text": "Codificación Hardware x264 / NVENC / ProRes", "checked": True}
        ],
        "infrastructure": [
            {"text": "Binario FFmpeg 6.x Local VPS ($0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Render nativo 1080x1920 (9:16) o 1920x1080 (16:9)", "checked": True},
            {"text": "✨ Preferencia: 24fps cinemáticos con CRF 19", "checked": True},
            {"text": "✨ Preferencia: Audio master 48kHz Stereo AAC/WAV", "checked": True}
        ],
        "behaviors": [
            {"text": "Atenúa automáticamente la música cuando entra la voz del locutor", "checked": True},
            {"text": "Aplica transiciones cruzadas y efecto Ken Burns a las imágenes", "checked": True}
        ],
        "notes": "Motor central de renderizado y producción final de vídeo."
    },
    "remotion_engine": {
        "id": "remotion_engine",
        "name": "Remotion (React Video-as-Code & Spring Vox)",
        "category": "programacion",
        "infra_type": "local",
        "enabled": True,
        "label": "Remotion (React 4.x / TSX Video-as-Code)",
        "description": "Renderizado programático de composiciones React (.tsx), animaciones Spring estilo Vox y tarjetas cinéticas.",
        "doc_link": "https://www.remotion.dev/docs",
        "doc_link_text": "Documentación Remotion ↗",
        "categories": [
            {"text": "React Video Compositions (.tsx / useCurrentFrame)", "checked": True},
            {"text": "Vox Spring Animations (Snappy / Bouncy / Smooth)", "checked": True},
            {"text": "Picture-in-Picture & Animated Data Cards", "checked": True}
        ],
        "infrastructure": [
            {"text": "Node.js Remotion CLI (npx remotion render $0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Composición 1080x1920 a 30fps con choppy text 12fps", "checked": True},
            {"text": "✨ Preferencia: Concurrencia de 4 hilos en render local", "checked": True},
            {"text": "🚫 Descartar frames con saltos de interpolación", "checked": True}
        ],
        "behaviors": [
            {"text": "Compila escenas desde scenes.json a componentes React estructurados", "checked": True},
            {"text": "Exporta máster en MP4 con multiplexado de audio nativo", "checked": True}
        ],
        "notes": "Framework React para creación de vídeo programático de alta fidelidad."
    },
    "hyperframes_engine": {
        "id": "hyperframes_engine",
        "name": "HyperFrames (HTML-as-Code & WebGL Shaders)",
        "category": "programacion",
        "infra_type": "local",
        "enabled": True,
        "label": "HyperFrames (Declarative HTML5 + GSAP)",
        "description": "Renderizado declarativo de timelines web (.html) con animaciones GSAP y shaders WebGL en tiempo real.",
        "doc_link": "https://hyperframes.org/",
        "doc_link_text": "Documentación HyperFrames ↗",
        "categories": [
            {"text": "Declarative Timeline HTML5 & CSS3", "checked": True},
            {"text": "GSAP Timelines Pausadas & Keyframing", "checked": True},
            {"text": "HyperShader WebGL Visual Effects", "checked": True}
        ],
        "infrastructure": [
            {"text": "Node.js HyperFrames CLI (npx hyperframes render $0)", "checked": True}
        ],
        "preferences": [
            {"text": "✨ Preferencia: Render acelerado por GPU Chromium Headless", "checked": True},
            {"text": "✨ Preferencia: Texturas de papel orgánico (#F4F1EA)", "checked": True},
            {"text": "🚫 Descartar shaders sin fallback CSS", "checked": True}
        ],
        "behaviors": [
            {"text": "Genera timelines HTML declarativos a partir de especificaciones de guion", "checked": True}
        ],
        "notes": "Motor de renderizado de vídeo basado en estándares web puros y GSAP."
    }
}

DELETED_PROVIDERS_PATH = os.path.join(BASE_DIR, "storage", "deleted_providers.json")


def load_deleted_providers() -> set:
    """Retorna el conjunto de IDs de proveedores eliminados permanentemente (tombstones)."""
    if os.path.isfile(DELETED_PROVIDERS_PATH):
        try:
            with open(DELETED_PROVIDERS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
        except Exception:
            pass
    return set()


def save_deleted_provider(provider_id: str):
    """Registra un ID de proveedor en el fichero de borrados permanentes (tombstones)."""
    tombstones = load_deleted_providers()
    tombstones.add(provider_id)
    try:
        os.makedirs(os.path.dirname(DELETED_PROVIDERS_PATH), exist_ok=True)
        with open(DELETED_PROVIDERS_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted(list(tombstones)), f, indent=2)
    except Exception as ex:
        logger.error(f"Error al guardar tombstone de proveedor: {ex}")


def load_registry() -> Dict[str, Any]:
    """Carga el registro de proveedores desde disco. Respeta estrictamente los borrados y tombstones."""
    tombstones = load_deleted_providers()
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    if os.path.isfile(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                import copy
                # Purga inmediata de cualquier proveedor borrado
                for dead_id in list(tombstones):
                    if dead_id in saved:
                        del saved[dead_id]
                
                # Merge de metadatos SOLO para proveedores existentes no borrados
                for k, v in list(saved.items()):
                    if k in tombstones:
                        del saved[k]
                        continue
                    if k in DEFAULT_PROVIDERS:
                        def_info = DEFAULT_PROVIDERS[k]
                        for m_field in ("doc_link", "doc_link_text", "api_key_field", "endpoint_field", "model_field", "model_options", "source_engine", "label", "description"):
                            if m_field in def_info and (m_field not in v or not v[m_field]):
                                v[m_field] = def_info[m_field]
                        for list_field in ("categories", "infrastructure", "preferences", "behaviors"):
                            if (list_field not in v or not v[list_field]) and list_field in def_info:
                                v[list_field] = copy.deepcopy(def_info[list_field])
                        if not v.get("notes") and def_info.get("notes"):
                            v["notes"] = def_info["notes"]
                save_registry(saved)
                return saved
        except Exception as ex:
            logger.error(f"Error al cargar registro de proveedores: {ex}")
    
    # Inicializar con defaults excluyendo permanentemente los borrados
    initial = {k: v for k, v in DEFAULT_PROVIDERS.items() if k not in tombstones}
    save_registry(initial)
    return initial


def save_registry(registry_data: Dict[str, Any]):
    """Guarda el estado activo del registro de proveedores en disco, purgando cualquier tombstone."""
    tombstones = load_deleted_providers()
    cleaned = {k: v for k, v in registry_data.items() if k not in tombstones}
    try:
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)
        
        # Sincronizar lista de proveedores activos en memoria
        active_ids = [k for k, v in cleaned.items() if v.get("enabled", True)]
        config.app["enabled_providers"] = active_ids
    except Exception as ex:
        logger.error(f"Error al guardar registro de proveedores: {ex}")


def is_provider_enabled(provider_id: str) -> bool:
    """Verifica si un proveedor específico está habilitado para su uso en el generador."""
    reg = load_registry()
    aliases = {
        "kokoro": "kokoro_local",
        "vibevoice": "vibevoice_serverless" if reg.get("vibevoice_serverless", {}).get("enabled", True) else "vibevoice_local",
        "flux": "flux_zerogpu" if reg.get("flux_zerogpu", {}).get("enabled", True) else "flux_replicate"
    }
    target_id = aliases.get(provider_id, provider_id)
    prov = reg.get(target_id)
    if prov is not None:
        return bool(prov.get("enabled", True))
    return True


def delete_provider(provider_id: str) -> bool:
    """Elimina permanentemente un proveedor del registro y lo bloquea con tombstone."""
    save_deleted_provider(provider_id)
    aliases = {
        "kokoro": "kokoro_local",
        "vibevoice": "vibevoice_serverless",
        "flux": "flux_zerogpu"
    }
    target_id = aliases.get(provider_id, provider_id)
    save_deleted_provider(target_id)
    
    reg = load_registry()
    if target_id in reg:
        del reg[target_id]
        save_registry(reg)
    
    try:
        from app.services import firebase_sync
        firebase_sync.save_settings_to_firebase_async()
    except Exception:
        pass
    return True


def set_provider_enabled(provider_id: str, enabled: bool):
    """Habilita o deshabilita un proveedor en el sistema."""
    reg = load_registry()
    aliases = {
        "kokoro": "kokoro_local",
        "vibevoice": "vibevoice_serverless",
        "flux": "flux_zerogpu"
    }
    target_id = aliases.get(provider_id, provider_id)
    if target_id in reg:
        reg[target_id]["enabled"] = enabled
        save_registry(reg)


def get_active_visual_engines() -> Dict[str, str]:
    """Retorna el diccionario de motores visuales habilitados para el Paso 2 del Generador."""
    reg = load_registry()
    active_engines = {}
    for p_id, p_info in reg.items():
        if p_info.get("category") == "visual" and p_info.get("enabled", True):
            source_key = p_info.get("source_engine", p_id)
            active_engines[source_key] = p_info.get("label", p_info.get("name", p_id))
    return active_engines


def get_active_llm_directors() -> Dict[str, str]:
    """Retorna los directores LLM habilitados para el Paso 1 del Generador."""
    reg = load_registry()
    active_llms = {}
    for p_id, p_info in reg.items():
        if p_info.get("category") == "llm" and p_info.get("enabled", True):
            active_llms[p_id] = p_info.get("label", p_info.get("name", p_id))
    return active_llms


def get_active_voice_engines() -> Dict[str, str]:
    """Retorna los motores de voz habilitados para el Generador."""
    reg = load_registry()
    active_voices = {}
    for p_id, p_info in reg.items():
        if p_info.get("category") == "voice" and p_info.get("enabled", True):
            active_voices[p_id] = p_info.get("label", p_info.get("name", p_id))
    return active_voices


def get_matrix_table_data() -> List[Dict[str, Any]]:
    """Exporta el registro en el formato estructurado para la tabla interactiva proveedores_excel.html."""
    from app.core.providers import health_checker
    matrix_live = health_checker.get_all_providers_matrix()
    reg = load_registry()
    
    items = []
    for p_id, p_info in reg.items():
        live_entry = matrix_live.get(p_id, {})
        live_status = live_entry.get("badge", "🟢 Operativo" if p_info.get("enabled", True) else "⚪ Inactivo")
        
        item = {
            "id": p_id,
            "enabled": bool(p_info.get("enabled", True)),
            "name": p_info.get("name", p_id),
            "category": p_info.get("category", ""),
            "infra_type": p_info.get("infra_type", "cloud"),
            "liveStatus": live_status,
            "categories": p_info.get("categories", []),
            "infrastructure": p_info.get("infrastructure", []),
            "preferences": p_info.get("preferences", []),
            "behaviors": p_info.get("behaviors", []),
            "notes": p_info.get("notes", p_info.get("description", ""))
        }
        items.append(item)
    return items


def sync_from_matrix_table(items_list: List[Dict[str, Any]]):
    """Sincroniza los cambios enviados desde la tabla interactiva (toggles, opciones, borrados) con el registro maestro."""
    reg = load_registry()
    incoming_ids = set()
    
    for it in items_list:
        p_id = it.get("id")
        if not p_id:
            name = it.get("name", "")
            for k, v in reg.items():
                if v.get("name") == name:
                    p_id = k
                    break
            if not p_id:
                p_id = "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")[:30]
        
        incoming_ids.add(p_id)
        if p_id in reg:
            reg[p_id]["enabled"] = bool(it.get("enabled", True))
            reg[p_id]["name"] = it.get("name", reg[p_id]["name"])
            if "categories" in it: reg[p_id]["categories"] = it["categories"]
            if "infrastructure" in it: reg[p_id]["infrastructure"] = it["infrastructure"]
            if "preferences" in it: reg[p_id]["preferences"] = it["preferences"]
            if "behaviors" in it: reg[p_id]["behaviors"] = it["behaviors"]
            if "notes" in it: reg[p_id]["notes"] = it["notes"]
        else:
            reg[p_id] = {
                "id": p_id,
                "name": it.get("name", p_id),
                "category": it.get("category", "visual"),
                "infra_type": it.get("infra_type", "cloud"),
                "enabled": bool(it.get("enabled", True)),
                "label": it.get("name", p_id),
                "description": it.get("notes", "Creado en Matriz Maestra"),
                "categories": it.get("categories", []),
                "infrastructure": it.get("infrastructure", []),
                "preferences": it.get("preferences", []),
                "behaviors": it.get("behaviors", []),
                "notes": it.get("notes", "")
            }
            
    # Eliminar del registro cualquier elemento que haya sido borrado en la tabla
    keys_to_remove = [k for k in list(reg.keys()) if k not in incoming_ids and len(incoming_ids) > 0]
    for k in keys_to_remove:
        del reg[k]
        
    save_registry(reg)
    from app.services import firebase_sync
    firebase_sync.save_settings_to_firebase_async()
    return True
