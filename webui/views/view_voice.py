import sys
import os
import requests
import json
from pathlib import Path
import streamlit as st

def render_view():
    st.title("Voice Studio")
    st.caption("Síntesis neural de voz y locución en alta fidelidad con control de prosodia.")

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
        st.subheader("Configuración del Locutor")
        
        lang_cat = st.radio("Idioma y Motor", list(VOICE_CATALOG.keys()))
        selected_voice_key = st.selectbox("Locutor", list(VOICE_CATALOG[lang_cat].keys()), format_func=lambda x: VOICE_CATALOG[lang_cat][x])
        
        script_text = st.text_area(
            "Texto a Sintetizar (con Humanizador Prosódico)",
            value="La inteligencia artificial transforma la producción audiovisual integrando síntesis neural de alta definición.",
            height=140
        )
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            tempo = st.slider("Cadencia / Tempo", 0.75, 1.25, 1.0, 0.05)
        with col_v2:
            micro_pauses = st.checkbox("Insertar micro-pausas de respiración (80ms)", value=True)
            
        synth_btn = st.button("Sintetizar Locución de Estudio", type="primary", use_container_width=True)

    with col_preview:
        st.subheader("Reproducción y Masterización")
        
        if synth_btn:
            st.info(f"Procesando locución con '{selected_voice_key}'...")
            try:
                kokoro_api = "http://127.0.0.1:7892/api/tts"
                payload = {
                    "text": script_text,
                    "voice": selected_voice_key,
                    "speed": tempo
                }
                r = requests.post(kokoro_api, json=payload, timeout=30)
                if r.status_code == 200:
                    audio_bytes = r.content
                    st.success("Audio sintetizado con calidad de estudio.")
                    st.audio(audio_bytes, format="audio/wav")
                    st.download_button(
                        "Descargar Master WAV 24kHz",
                        audio_bytes,
                        file_name=f"{selected_voice_key}_master.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                else:
                    st.warning(f"Respuesta del servicio: {r.status_code}.")
            except Exception as e:
                st.error(f"Error conectando con el servicio de voz: {e}")
