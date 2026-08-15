import streamlit as st
import os
import json
import requests
import toml
from pathlib import Path

st.set_page_config(page_title="Gestor de APIs & Matriz de Infraestructura", page_icon="🔑", layout="wide")

CONFIG_PATH = Path("/home/ubuntu/MoneyPrinterTurbo/config.toml")
HUB_API = "http://127.0.0.1:7899"

# CSS Glassmorphism
st.markdown("""
<style>
    .hub-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 24px 28px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .table-container {
        background: rgba(18, 24, 38, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 24px;
    }
    .pill-free {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-browser {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-paid {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hub-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #f8fafc;">📋 Matriz de Motores, Infraestructura y Rutas de Ejecución</h1>
            <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 14px;">Define claramente qué infraestructura utiliza cada motor, qué genera y cómo interactúan las voces, la música y los subtítulos.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 1. TABLA MAESTRA EXPLICATIVA
st.subheader("📊 Matriz de Funcionamiento de VideoPro")
st.markdown("""
Esta tabla resume con total transparencia el origen de procesamiento de cada herramienta para evitar confusiones de audio, música o subtítulos:
""")

matrix_data = [
    {
        "Motor / Herramienta": "🎥 **FLUX 3 Video**",
        "Tipo de Generación": "Vídeo Cinemático / Escenas IA",
        "Ruta de Ejecución": "🟢 ZeroGPU Gratis (HF) o ⚡ Replicate H100 (Pago)",
        "Comportamiento de Audio / Voces": "🗣️ **Diálogos de personajes integrados**. NO añade locutor en off por defecto.",
        "Subtítulos": "🚫 Desactivados por defecto (opcional)",
        "Música": "🚫 Sin música salvo que se active Flow Music"
    },
    {
        "Motor / Herramienta": "🛸 **LTX-2.5 (22B MMDiT)**",
        "Tipo de Generación": "Vídeo AI Fotorealista",
        "Ruta de Ejecución": "🟢 ZeroGPU Gratis (HF) o ⚡ Replicate H100 (Pago)",
        "Comportamiento de Audio / Voces": "🗣️ **Diálogos y audio ambiental nativo**. Sin locutor en off a ciegas.",
        "Subtítulos": "🚫 Desactivados por defecto (opcional)",
        "Música": "🚫 Sin música salvo que se active Flow Music"
    },
    {
        "Motor / Herramienta": "🌐 **Google Flow**",
        "Tipo de Generación": "Storyboard & Vuelos Cinemáticos 4K",
        "Ruta de Ejecución": "🌐 **Navegador Web Automático (Playwright)**",
        "Comportamiento de Audio / Voces": "🎬 **Vídeo puro / Audio de escena**. No mete locutor a menos que se elija.",
        "Subtítulos": "🚫 Desactivados por defecto (opcional)",
        "Música": "🎵 Ideal con Google Flow Music"
    },
    {
        "Motor / Herramienta": "🎵 **Google Flow Music (Lyria 3 Pro)**",
        "Tipo de Generación": "Pistas Musicales IA Multiminuto",
        "Ruta de Ejecución": "🌐 **Navegador Web Automático (Playwright)**",
        "Comportamiento de Audio / Voces": "🎶 **Banda sonora máster**. Si hay locución, aplica auto-ducking a -22 dB.",
        "Subtítulos": "N/A",
        "Música": "✅ Pista completa generada"
    },
    {
        "Motor / Herramienta": "🎙️ **Kokoro HD 24kHz**",
        "Tipo de Generación": "Locución en Off (Español / Inglés)",
        "Ruta de Ejecución": "💻 **CPU Local Servidor ($0 Sin Coste)**",
        "Comportamiento de Audio / Voces": "🎙️ **Narrador / Voz en Off**. Solo se genera si el usuario elige expresamente un locutor.",
        "Subtítulos": "🟡 Compatible con Karaoke Vox / TikTok",
        "Música": "Aplica ducking a la música"
    },
    {
        "Motor / Herramienta": "🎙️ **VibeVoice 0.5B / ElevenLabs**",
        "Tipo de Generación": "Locución Podcast / Voz Ultra-Real",
        "Ruta de Ejecución": "🟢 ZeroGPU A100 (VibeVoice) / ⚡ API Key (ElevenLabs)",
        "Comportamiento de Audio / Voces": "🎙️ **Narrador / Voz en Off**. Solo si se activa.",
        "Subtítulos": "🟡 Sincronización palabra por palabra",
        "Música": "Aplica ducking a la música"
    },
    {
        "Motor / Herramienta": "📝 **Subtítulos Dinámicos ASS**",
        "Tipo de Generación": "Subtítulos Karaoke (Vox, TikTok, Steampunk)",
        "Ruta de Ejecución": "💻 **CPU Local Servidor ($0 Sin Coste)**",
        "Comportamiento de Audio / Voces": "Resalta palabras al ritmo de la voz.",
        "Subtítulos": "🚫 Se pueden apagar completamente con 'Sin Subtítulos'",
        "Música": "N/A"
    }
]

st.table(matrix_data)

st.divider()

# 2. CONFIGURACIÓN Y CREDENCIALES
st.subheader("🔑 Configuración de Claves & Servidores")

tab_keys, tab_presets = st.tabs(["🔐 Claves API y Servidores", "🎬 Presets de Producción Recomendados"])

with tab_keys:
    # Load config
    cfg = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = toml.load(f)
        except Exception: pass

    c_k1, c_k2 = st.columns(2)
    with c_k1:
        st.markdown("### 1. Clúster Visual & GPU")
        rep_token = st.text_input("Replicate API Token (H100 de Pago)", value=cfg.get("app", {}).get("replicate_api_token", ""), type="password", placeholder="r8_...")
        hf_pool = st.text_area("Hugging Face ZeroGPU Pool (Tokens Gratis separados por línea)", value="\n".join(cfg.get("serverless_pool", {}).get("hf_tokens", [])), height=100)
    
    with c_k2:
        st.markdown("### 2. Audio & LLMs")
        gemini_k = st.text_input("Google AI Studio (Gemini Direct)", value=cfg.get("app", {}).get("gemini_api_key", ""), type="password", placeholder="AIzaSy...")
        groq_k = st.text_input("Groq Cloud API Key", value=cfg.get("app", {}).get("groq_api_key", ""), type="password", placeholder="gsk_...")
        eleven_k = st.text_input("ElevenLabs API Key", value=cfg.get("app", {}).get("elevenlabs_api_key", ""), type="password", placeholder="sk_...")

    if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
        if "app" not in cfg: cfg["app"] = {}
        if "serverless_pool" not in cfg: cfg["serverless_pool"] = {}
        
        cfg["app"]["replicate_api_token"] = rep_token.strip()
        cfg["app"]["gemini_api_key"] = gemini_k.strip()
        cfg["app"]["groq_api_key"] = groq_k.strip()
        cfg["app"]["elevenlabs_api_key"] = eleven_k.strip()
        cfg["serverless_pool"]["hf_tokens"] = [t.strip() for t in hf_pool.split("\n") if t.strip()]

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            toml.dump(cfg, f)
        st.success("¡Configuración guardada correctamente en config.toml!")

with tab_presets:
    st.markdown("""
    ### 🎯 ¿Qué modo elegir según tu proyecto?
    
    1. **🎬 Modo Cine IA / Diálogos Nativos (FLUX 3 / Google Flow):**
       - **Visual:** FLUX 3 (ZeroGPU gratis o Replicate H100).
       - **Voz:** **🚫 Sin Locutor en Off** (las personas en el vídeo hablan directamente).
       - **Subtítulos:** **🚫 Sin Subtítulos** (imagen limpia).
       - **Música:** Opcional (solo si quieres banda sonora ambiente detrás de los diálogos).
    
    2. **🎙️ Modo Documental / Reportaje (Estilo Vox / Johnny Harris):**
       - **Visual:** Híbrido (FLUX 3 + Archivo Real + Pexels).
       - **Voz:** **🇪🇸 Dora / Kokoro HD** (Locución profesional en off).
       - **Subtítulos:** **🟡 Vox / Johnny Harris** (1-2 palabras dinámicas amarillas).
       - **Música:** BGM con Auto-Ducking a -22 dB + Efectos Foley (shutter, typewriter, paper slide).
    
    3. **🎵 Modo Videoclip / Banda Sonora (Google Flow + Flow Music):**
       - **Visual:** Google Flow (vuelos cinemáticos generados en navegador).
       - **Voz:** **🚫 Sin Locutor**.
       - **Subtítulos:** **🚫 Sin Subtítulos**.
       - **Música:** **Google Flow Music (Lyria 3 Pro)** pista completa.
    """)
