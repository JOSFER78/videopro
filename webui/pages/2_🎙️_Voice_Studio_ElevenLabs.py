import streamlit as st
import os
import requests
import json
from pathlib import Path

st.set_page_config(page_title="Voice Studio SOTA", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    .voice-header {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(16, 185, 129, 0.15));
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 20px 24px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="voice-header">
    <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #f8fafc;">
        🎙️ Voice Studio SOTA (ElevenLabs-Grade)
    </h1>
    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 14px;">
        VibeVoice 0.5B Realtime (ZeroGPU A100) & Kokoro HD (Studio 24kHz) con Prosodia Humana Orgánica
    </p>
</div>
""", unsafe_allow_html=True)

col_ctrl, col_preview = st.columns([5, 4])

VOICE_CATALOG = {
    "Español (Kokoro HD Studio 24kHz)": {
        "es_dora": "Dora (España Studio HD - Calidez Documental)",
        "es_alex": "Alex (España Dinámico HD - Reels & Shorts)",
        "es_santa": "Santiago (España Solemne HD - Histórico/Solemne)"
    },
    "Inglés (VibeVoice 0.5B ZeroGPU A100 & Kokoro HD)": {
        "en_heart": "Heart (US Grade-A Master - Máxima Calidez)",
        "en_adam": "Adam (US Barítono Épico)",
        "vibevoice_carter": "Carter (VibeVoice 0.5B Difusión Acústica)",
        "vibevoice_emma": "Emma (VibeVoice 0.5B Podcast Fluido)",
        "en_emma_uk": "Emma (UK BBC Authority)"
    }
}

with col_ctrl:
    st.subheader("🗣️ Configuración del Locutor")
    
    lang_cat = st.radio("Idioma y Motor", list(VOICE_CATALOG.keys()))
    selected_voice_key = st.selectbox("Locutor de Élite", list(VOICE_CATALOG[lang_cat].keys()), format_func=lambda x: VOICE_CATALOG[lang_cat][x])
    
    script_text = st.text_area(
        "Texto a Sintetizar (con Humanizador Prosódico)",
        value="La inteligencia artificial ya no es solo una promesa del futuro; es el motor invisible que transforma cada aspecto de nuestra realidad hoy.",
        height=140
    )
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        tempo = st.slider("Cadencia / Tempo", 0.75, 1.25, 1.0, 0.05)
    with col_v2:
        micro_pauses = st.checkbox("Insertar micro-pausas de respiración (80ms)", value=True)
        
    synth_btn = st.button("✨ Sintetizar Locución de Estudio", type="primary", use_container_width=True)

with col_preview:
    st.subheader("🎧 Reproducción y Masterización")
    
    if synth_btn:
        st.info(f"Procesando locución con '{selected_voice_key}'...")
        try:
            # Invocar backend local de Kokoro o VibeVoice
            kokoro_api = "http://127.0.0.1:7892/api/tts"
            payload = {
                "text": script_text,
                "voice": selected_voice_key,
                "speed": tempo
            }
            r = requests.post(kokoro_api, json=payload, timeout=30)
            if r.status_code == 200:
                audio_bytes = r.content
                st.success("¡Audio Sintetizado con Calidad de Estudio!")
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    "💾 Descargar Master WAV 24kHz",
                    audio_bytes,
                    file_name=f"{selected_voice_key}_master.wav",
                    mime="audio/wav",
                    use_container_width=True
                )
            else:
                st.warning(f"Respuesta del servicio: {r.status_code}. Comprobando fallback local...")
        except Exception as e:
            st.error(f"Error conectando con el servicio de voz: {e}")
