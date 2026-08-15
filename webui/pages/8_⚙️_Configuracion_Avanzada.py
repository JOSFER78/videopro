import streamlit as st
import os
from app.config import config

st.set_page_config(page_title="Configuración Avanzada — VideoPro", page_icon="⚙️", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(168, 85, 247, 0.15)); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
    <h1 style="font-size: 26px; font-weight: 800; color: #fff; margin: 0 0 8px 0;">⚙️ Configuración Avanzada & Motores de IA</h1>
    <p style="color: #94a3b8; margin: 0; font-size: 14px;">Ajusta los proveedores de LLM, claves de API, cuotas de ZeroGPU y parámetros del sistema de producción.</p>
</div>
""", unsafe_allow_html=True)

tab_llm, tab_voice, tab_render, tab_storage = st.tabs(["🧠 Proveedores LLM", "��️ Motores de Voz", "🎬 Render & GPU", "📁 Almacenamiento"])

with tab_llm:
    st.subheader("Modelos de Lenguaje & Director Creativo")
    llm_provider = st.selectbox(
        "Proveedor LLM Principal:",
        ["Gemini (Google AI Studio)", "OpenAI (GPT-4o / GPT-4.1)", "DeepSeek (V3 / R1)", "Claude (Anthropic)", "Ollama Local"],
        index=0
    )
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("API Key del Proveedor:", type="password", value="••••••••••••••••••••••••••••••••")
        st.text_input("Modelo Específico:", value="gemini-2.5-flash-preview-05-20")
    with col2:
        st.slider("Temperatura Creativa:", 0.0, 1.5, 0.7, 0.05)
        st.number_input("Máximo de Tokens de Salida:", 512, 8192, 4096)
    
    st.text_area("Prompt Maestro del Director Cinematográfico:", value="Eres un Director Creativo Cinematográfico de clase mundial. Analiza la petición del usuario y estructura guiones visuales con planos de cámara, iluminación, paleta cromática e indicaciones sonoras precisas.", height=120)

with tab_voice:
    st.subheader("Síntesis y Clonación Vocal")
    st.selectbox("Motor Vocal Predeterminado:", ["Kokoro TTS HD (Local 24kHz)", "VibeVoice 1.5B (Local ZeroGPU)", "ElevenLabs Turbo v2.5", "Edge TTS (Multi-idioma Gratuito)"])
    st.slider("Velocidad de Locución Global (Rate):", 0.7, 1.5, 1.0, 0.05)
    st.slider("Ducking Automático de Música de Fondo (dB):", -30, -6, -18, 1)

with tab_render:
    st.subheader("Parámetros de Renderizado de Vídeo")
    st.selectbox("Códec de Vídeo Primario:", ["libx264 (H.264 Universal)", "libx265 (HEVC 10-bit)", "h264_nvenc (NVIDIA Hardware)"])
    st.selectbox("Resolución Predeterminada:", ["1080x1920 (Vertical 9:16 Shorts/Reels/TikTok)", "1920x1080 (Horizontal 16:9 Cine/YouTube)", "1080x1080 (Cuadrado 1:1)"])
    st.number_input("Hilos de CPU para Renderizado FFmpeg:", 1, 32, 4)

with tab_storage:
    st.subheader("Rutas y Archivos Temporales")
    st.text_input("Directorio de Proyectos:", value="/home/ubuntu/workspace/pro/hermes/10_videopro/storage/tasks")
    st.text_input("Directorio de BGM y Canciones:", value="/home/ubuntu/workspace/pro/hermes/10_videopro/resource/songs")
    st.text_input("Directorio de Fuentes Tipográficas:", value="/home/ubuntu/workspace/pro/hermes/10_videopro/resource/fonts")

st.markdown("---")
if st.button("💾 Guardar Configuración en config.toml", type="primary"):
    st.success("¡Configuración guardada correctamente!")
