import sys
import os
import json
import requests
import toml
from pathlib import Path
import streamlit as st

CONFIG_PATH = Path("/home/ubuntu/MoneyPrinterTurbo/config.toml")
HUB_API = "http://127.0.0.1:7899"

def render_view():
    st.title("Gestor de APIs & Tokens")
    st.caption("Gestión y validación de tokens para Hugging Face ZeroGPU, Replicate y LLMs.")

    tab_keys, tab_matrix, tab_presets = st.tabs([
        "Claves API y Servidores",
        "Matriz de Funcionamiento",
        "Presets de Producción Recomendados"
    ])

    with tab_keys:
        cfg = {}
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = toml.load(f)
            except Exception:
                pass

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

        if st.button("Guardar Configuración", type="primary", use_container_width=True):
            if "app" not in cfg:
                cfg["app"] = {}
            if "serverless_pool" not in cfg:
                cfg["serverless_pool"] = {}
            
            cfg["app"]["replicate_api_token"] = rep_token.strip()
            cfg["app"]["gemini_api_key"] = gemini_k.strip()
            cfg["app"]["groq_api_key"] = groq_k.strip()
            cfg["app"]["elevenlabs_api_key"] = eleven_k.strip()
            cfg["serverless_pool"]["hf_tokens"] = [t.strip() for t in hf_pool.split("\n") if t.strip()]

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                toml.dump(cfg, f)
            st.success("Configuración guardada correctamente en config.toml.")

    with tab_matrix:
        st.subheader("Matriz de Funcionamiento de VideoPro")
        matrix_data = [
            {
                "Motor / Herramienta": "FLUX 3 Video",
                "Tipo de Generación": "Vídeo Cinemático / Escenas IA",
                "Ruta de Ejecución": "ZeroGPU Gratis (HF) o Replicate H100 (Pago)",
                "Comportamiento de Audio": "Diálogos integrados. Sin locutor en off por defecto.",
                "Subtítulos": "Desactivados por defecto (opcional)",
                "Música": "Sin música salvo activación de Flow Music"
            },
            {
                "Motor / Herramienta": "LTX-2.5 (22B MMDiT)",
                "Tipo de Generación": "Vídeo AI Fotorealista",
                "Ruta de Ejecución": "ZeroGPU Gratis (HF) o Replicate H100 (Pago)",
                "Comportamiento de Audio": "Diálogos y audio ambiental nativo a 48kHz.",
                "Subtítulos": "Desactivados por defecto (opcional)",
                "Música": "Sin música salvo activación de Flow Music"
            },
            {
                "Motor / Herramienta": "Google Flow",
                "Tipo de Generación": "Storyboard & Vuelos Cinemáticos 4K",
                "Ruta de Ejecución": "Navegador Web Automático (Playwright)",
                "Comportamiento de Audio": "Vídeo puro / Audio de escena.",
                "Subtítulos": "Desactivados por defecto (opcional)",
                "Música": "Ideal con Google Flow Music"
            },
            {
                "Motor / Herramienta": "Google Flow Music (Lyria 3 Pro)",
                "Tipo de Generación": "Pistas Musicales IA Multiminuto",
                "Ruta de Ejecución": "Navegador Web Automático (Playwright)",
                "Comportamiento de Audio": "Banda sonora máster con ducking a -22 dB si hay voz.",
                "Subtítulos": "N/A",
                "Música": "Pista completa generada"
            },
            {
                "Motor / Herramienta": "Kokoro HD 24kHz",
                "Tipo de Generación": "Locución en Off (Español / Inglés)",
                "Ruta de Ejecución": "CPU Local Servidor ($0 Sin Coste)",
                "Comportamiento de Audio": "Narrador / Voz en Off dedicada.",
                "Subtítulos": "Compatible con Karaoke Vox / TikTok",
                "Música": "Aplica ducking a la música"
            }
        ]
        st.table(matrix_data)

    with tab_presets:
        st.markdown("""
        ### Presets de Producción Recomendados
        
        1. **Modo Cine IA / Diálogos Nativos (FLUX 3 / Google Flow):**
           - **Visual:** FLUX 3 (ZeroGPU gratis o Replicate H100).
           - **Voz:** Sin Locutor en Off (las personas en el vídeo hablan directamente).
           - **Subtítulos:** Sin Subtítulos (imagen limpia).
           - **Música:** Opcional.
        
        2. **Modo Documental / Reportaje (Estilo Vox / Johnny Harris):**
           - **Visual:** Híbrido (FLUX 3 + Archivo Real + Pexels).
           - **Voz:** Dora / Kokoro HD (Locución profesional en off).
           - **Subtítulos:** Vox / Johnny Harris (1-2 palabras dinámicas amarillas).
           - **Música:** BGM con Auto-Ducking a -22 dB + Efectos Foley.
        
        3. **Modo Videoclip / Banda Sonora (Google Flow + Flow Music):**
           - **Visual:** Google Flow (vuelos cinemáticos generados en navegador).
           - **Voz:** Sin Locutor.
           - **Subtítulos:** Sin Subtítulos.
           - **Música:** Google Flow Music (Lyria 3 Pro) pista completa.
        """)
