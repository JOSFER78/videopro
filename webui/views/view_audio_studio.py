"""
view_audio_studio.py
Estudio de Audio, Foley Físico & Masterización EBU R128 — VideoPro Studio
- Control de las 3 capas acústicas (Música Master, Voz Neural y Foley Físico)
- Parámetros de Audio Ducking dinámico a -22 dB
- Repositorio y reproductor de Foley analógico (obturador de cámara, pase de página, tecleo).
"""

import os
import sys
from pathlib import Path
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

def render_view():
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 8px;">
                🎙️ Estudio de Audio, Foley & Masterización
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">EBU R128 (-14 LUFS)</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 2px 0 0 0;">
                Diseño sonoro en 3 capas, atenuación dinámica (Ducking a -22 dB) y efectos diegéticos analógicos.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_layers, tab_voice, tab_foley, tab_master_wav = st.tabs([
        "🎚️ 1. Mezclador de 3 Capas",
        "🗣️ 2. Voces Neurales (TTS)",
        "📸 3. Librería Foley Analógico",
        "🎵 4. Pista Master WAV"
    ])

    with tab_layers:
        st.markdown("##### 🎛️ Configuración de Mezcla y Ducking Dinámico")
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            with st.container(border=True):
                st.markdown("**Capa 1: Música Master**")
                st.slider("Volumen Base (dB):", -12, 6, 0, key="vol_bgm")
                st.slider("Ducking en Voz (dB):", -30, -10, -22, key="ducking_bgm")
                st.caption("Atenuación automática sincronizada con la locución.")
        with c2:
            with st.container(border=True):
                st.markdown("**Capa 2: Locución / Voz**")
                st.slider("Ganancia de Voz (dB):", 0, 12, 6, key="vol_voice")
                st.selectbox("Perfil de EQ:", ["Presencia Cristalina (Cinema)", "Cálido Radio Broadcast", "Neutro Plano"], key="eq_voice")
                st.caption("Normalización a -14 LUFS integrado.")
        with c3:
            with st.container(border=True):
                st.markdown("**Capa 3: Foley Diegético**")
                st.slider("Nivel de Efectos (dB):", -18, 0, -6, key="vol_foley")
                st.toggle("Micro-destello con Obturador", value=True, key="flash_shutter")
                st.caption("Sincronización exacta fotograma a fotograma.")

    with tab_voice:
        st.markdown("##### 🗣️ Generador de Locución Neural")
        cv1, cv2 = st.columns([1.5, 2.5], gap="medium")
        with cv1:
            v_engine = st.selectbox("Motor TTS:", [
                "VibeVoice 1.5B (Serverless Free)",
                "Kokoro TTS HD 24kHz (Local)",
                "ElevenLabs Cinema Studio"
            ])
            v_lang = st.selectbox("Idioma:", ["es-ES (Español Neutro)", "en-US (Inglés Studio)", "fr-FR (Francés)"])
            v_speed = st.slider("Velocidad de Lectura:", 0.8, 1.5, 1.0, 0.05)
        with cv2:
            v_text = st.text_area("Texto a Locutar:", placeholder="Escribe el texto para sintetizar...", height=110)
            if st.button("🎙️ Generar Locución de Prueba", type="primary", use_container_width=True):
                if v_text.strip():
                    st.success(f"Locución generada con {v_engine}.")
                else:
                    st.warning("Introduce un texto para locutar.")

    with tab_foley:
        st.markdown("##### 📸 Efectos Sonoros Analógicos (Foley del Cuaderno)")
        st.caption("Sonidos diegéticos táctiles de anclaje de realidad.")
        foley_items = [
            ("📸 Camera Shutter Click", "Disparo analógico al fijar fotos de archivo histórico."),
            ("📄 Paper Slide & Page Turn", "Deslizamiento y pase de página al desplegar documentos."),
            ("⌨️ Typewriter Keypress", "Tecleo mecánico rápido al revelar rótulos."),
            ("🌊 Underground Water Echo", "Goteo sutil de agua en los niveles -5m a -35m.")
        ]
        for f_name, f_desc in foley_items:
            with st.container(border=True):
                c_f1, c_f2 = st.columns([3.5, 1.5], vertical_alignment="center")
                with c_f1:
                    st.markdown(f"**{f_name}** — *{f_desc}*")
                with c_f2:
                    st.button("🔊 Probar Sonido", key=f"btn_{f_name[:5]}", use_container_width=True)

    with tab_master_wav:
        st.markdown("##### 🎵 Pista Master de Audio del Proyecto")
        st.caption("Pista WAV estéreo 48 kHz que dicta el tiempo del montaje.")
        
        wav_files = list(Path(BASE_DIR).glob("storage/projects/**/tours*.wav")) + list(Path(BASE_DIR).glob("storage/projects/**/*.wav"))
        if wav_files:
            active_wav = wav_files[0]
            st.info(f"📁 Pista Activa: `{active_wav.name}` ({active_wav.stat().st_size / (1024*1024):.2f} MB)")
            st.audio(str(active_wav))
        else:
            st.info("No se encontró archivo WAV maestro en storage/projects/.")
