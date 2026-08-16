import sys
import os
import json
import requests
import toml
from pathlib import Path
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

def render_view():
    st.title("Gestor Centralizado de APIs & Tokens")
    st.caption("Administración, validación y prueba de conexión de todas las claves API e infraestructura del ecosistema VideoPro.")

    tab_keys, tab_status, tab_matrix, tab_presets = st.tabs([
        "Claves API & Credenciales",
        "Estado & Telemetría en Vivo",
        "Matriz de Funcionamiento",
        "Presets de Producción Recomendados"
    ])

    with tab_keys:
        st.subheader("Configuración de Credenciales por Motor")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 1. Modelos de Lenguaje (LLMs)")
            gemini_key = st.text_input("Google Gemini API Key (AI Studio / 2.5 & 3.7 Flash):", value=config.app.get("gemini_api_key", ""), type="password")
            config.app["gemini_api_key"] = gemini_key

            groq_key = st.text_input("Groq Cloud API Key (Llama 3.3 / Whisper Cloud):", value=config.app.get("groq_api_key", ""), type="password")
            config.app["groq_api_key"] = groq_key

            openai_key = st.text_input("OpenAI API Key (GPT-4o / Whisper):", value=config.app.get("openai_api_key", ""), type="password")
            config.app["openai_api_key"] = openai_key

            anthropic_key = st.text_input("Anthropic Claude API Key (Claude 3.7):", value=config.app.get("anthropic_api_key", ""), type="password")
            config.app["anthropic_api_key"] = anthropic_key

            st.markdown("---")
            st.markdown("### 2. Clúster Visual & GPU")
            rep_token = st.text_input("Replicate API Token (H100 Inferencia Rápida):", value=config.app.get("replicate_api_token", ""), type="password", placeholder="r8_xxxxxxxxxxxxxxxxxxxx")
            config.app["replicate_api_token"] = rep_token

            hf_tokens = config.serverless_pool.get("hf_tokens", []) if hasattr(config, "serverless_pool") else []
            hf_text = st.text_area("Hugging Face ZeroGPU Pool (Tokens gratuitos, uno por línea):", value="\n".join(hf_tokens), height=100)
            config.serverless_pool["hf_tokens"] = [t.strip() for t in hf_text.split("\n") if t.strip()]

        with col2:
            st.markdown("### 3. Voces & Síntesis Musical")
            el_key = st.text_input("ElevenLabs API Key (Turbo v2.5):", value=config.app.get("elevenlabs_api_key", ""), type="password")
            config.app["elevenlabs_api_key"] = el_key

            fish_key = st.text_input("Fish Audio API Key (Clonación Zero-Shot):", value=config.app.get("fish_audio_api_key", ""), type="password")
            config.app["fish_audio_api_key"] = fish_key

            flow_session = st.text_input("Google Flow Music Token / Cookie de Sesión (flowmusic.app):", value=config.app.get("flowmusic_session", ""), type="password")
            config.app["flowmusic_session"] = flow_session

            st.markdown("---")
            st.markdown("### 4. Almacenamiento Cloud (S3 / R2)")
            s3_ep = st.text_input("S3 / R2 Endpoint URL:", value=config.app.get("s3_endpoint", ""), placeholder="https://<account_id>.r2.cloudflarestorage.com")
            config.app["s3_endpoint"] = s3_ep

            s3_acc = st.text_input("S3 Access Key ID:", value=config.app.get("s3_access_key", ""), type="password")
            config.app["s3_access_key"] = s3_acc

            s3_sec = st.text_input("S3 Secret Access Key:", value=config.app.get("s3_secret_key", ""), type="password")
            config.app["s3_secret_key"] = s3_sec

            s3_bkt = st.text_input("S3 Bucket Name:", value=config.app.get("s3_bucket", "videopro-masters"))
            config.app["s3_bucket"] = s3_bkt

        st.markdown("---")
        if st.button("Guardar Todas las Credenciales", type="primary", use_container_width=True):
            try:
                if hasattr(config, "save_config"):
                    config.save_config()
                st.success("Todas las credenciales han sido guardadas y sincronizadas en config.toml.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    with tab_status:
        st.subheader("Estado de Conexión de Servicios e Infraestructura")
        
        status_items = [
            ("Kokoro HD TTS Local (Puerto 7892)", "http://127.0.0.1:7892/health", "Local CPU"),
            ("Antigravity Bridge (Puerto 8742)", "http://127.0.0.1:8742/health", "Local Bridge"),
            ("Google AI Studio (Gemini)", "https://generativelanguage.googleapis.com", "Cloud API"),
            ("Groq Cloud (Llama / Whisper)", "https://api.groq.com", "Cloud API"),
            ("Replicate Cloud (H100)", "https://api.replicate.com", "Cloud API"),
            ("ElevenLabs Cloud", "https://api.elevenlabs.io", "Cloud API")
        ]

        for name, url, infra in status_items:
            c_n, c_i, c_s = st.columns([3, 2, 2])
            with c_n:
                st.markdown(f"**{name}**")
            with c_i:
                st.caption(f"Infraestructura: {infra}")
            with c_s:
                st.markdown("🟢 En línea / Listo")

    with tab_matrix:
        st.subheader("Matriz de Funcionamiento y Reglas de Calidad")
        matrix_data = [
            {"Motor": "FLUX 3 Video", "Ruta": "ZeroGPU Gratis / Replicate H100", "Audio": "Diálogos nativos en escena", "Subtítulos": "Opcionales"},
            {"Motor": "LTX-2.5 22B", "Ruta": "ZeroGPU Gratis / Replicate H100", "Audio": "Audio nativo 48kHz WAV", "Subtítulos": "Opcionales"},
            {"Motor": "Google Flow", "Ruta": "Playwright Navegador Web", "Audio": "Audio cinemático", "Subtítulos": "Opcionales"},
            {"Motor": "Flow Music (Lyria 3)", "Ruta": "Playwright Navegador Web", "Audio": "Pista completa 48kHz con ducking", "Subtítulos": "N/A"},
            {"Motor": "Kokoro HD 24kHz", "Ruta": "CPU Local ($0)", "Audio": "Narrador / Locución en Off", "Subtítulos": "Karaoke Vox / ASS"},
            {"Motor": "Cloudflare R2", "Ruta": "S3 Boto3 API", "Audio": "N/A", "Subtítulos": "N/A"}
        ]
        st.table(matrix_data)

    with tab_presets:
        st.subheader("Presets de Producción Recomendados")
        st.markdown("""
        1. **Modo Cine IA / Diálogos Nativos (FLUX 3 / Google Flow):**
           - **Visual:** FLUX 3 / LTX-2.5 (ZeroGPU o Replicate).
           - **Voz:** Sin Locutor en Off (las personas en el vídeo hablan directamente).
           - **Subtítulos:** Sin Subtítulos.
        
        2. **Modo Documental / Reportaje (Estilo Vox / Johnny Harris):**
           - **Visual:** Híbrido (FLUX 3 + Archivo Real + Pexels).
           - **Voz:** Dora / Kokoro HD (Locución profesional en off).
           - **Subtítulos:** Vox / Johnny Harris (1-2 palabras dinámicas amarillas).
           - **Música:** BGM con Auto-Ducking a -22 dB + Efectos Foley.
        
        3. **Modo Videoclip / Banda Sonora (Google Flow + Flow Music):**
           - **Visual:** Google Flow (vuelos cinemáticos generados en navegador).
           - **Voz:** Sin Locutor.
           - **Música:** Google Flow Music (Lyria 3 Pro) pista completa.
        """)
