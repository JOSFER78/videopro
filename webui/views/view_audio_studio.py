import os
import sys
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

def render_view():
    tab_voice, tab_music = st.tabs([
        "Locución & Voces Neurales",
        "Composición Musical Flow Music"
    ])

    with tab_voice:
        c1, c2 = st.columns([1.5, 2.5])
        with c1:
            st.markdown("**Motores de Síntesis Vocal**")
            v_engine = st.selectbox("Motor:", [
                "Kokoro TTS HD 24kHz (Local Port 7892 - $0/h)",
                "VibeVoice 1.5B (Edge-TTS Fast)",
                "ElevenLabs Cinema Studio",
                "Fish Audio Multilingual 48kHz"
            ])
            v_lang = st.selectbox("Idioma:", ["es (Español Neutro)", "en (Inglés Studio)", "fr (Francés)", "de (Alemán)"])
            v_speed = st.slider("Velocidad:", 0.5, 2.0, 1.0, 0.05)
            
        with c2:
            st.markdown("**Texto a Sintetizar**")
            v_text = st.text_area("Texto / Narración:", placeholder="Escribe el guion para sintetizar...", height=90)
            if st.button("Sintetizar Audio de Prueba", type="primary", use_container_width=True):
                if v_text.strip():
                    st.info("Sintetizando locución con " + v_engine + "...")
                else:
                    st.warning("Introduce un texto para locutar.")

    with tab_music:
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.markdown("**Parámetros de Composición**")
            genre = st.selectbox("Género / Mood:", ["Cinematic Dramatic", "Cyberpunk Synthwave", "Epic Hollywood Trailer", "Ambient Lo-Fi Chill", "Corporate Tech Modern"])
            tempo = st.slider("BPM (Tempo):", 60, 180, 110)
            ducking = st.slider("Atenuación Sidechain con Voz (dB):", -30, -6, -18)

        with c_m2:
            st.markdown("**Generador de Prompt Musical Lyria 3**")
            m_prompt = st.text_area("Instrucciones musicales:", value=f"{genre}, tempo {tempo} BPM, cinematic orchestra with brass and hybrid sub-bass", height=90)
            if st.button("Componer Banda Sonora (Flow Music)", type="primary", use_container_width=True):
                st.success("Composición musical iniciada con Google Lyria 3 Pro.")
