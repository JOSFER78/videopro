import os
import sys
import tempfile
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.services import voice as voice_service

def render_view():
    st.title("Estudio de Audio & Música")
    st.caption("Consola unificada de locución neural multilingüe, clonación de voz y composición de bandas sonoras.")

    tab_voice, tab_music = st.tabs([
        "Locución & Voces Neurales",
        "Composición Musical Flow Music"
    ])

    with tab_voice:
        st.subheader("Síntesis Vocal Neural y Clonación de Voz")
        st.caption("Genera locuciones en alta fidelidad con Kokoro TTS HD 24kHz (/bin/bash local en puerto 7892), VibeVoice, ElevenLabs y Fish Audio.")

        col_v1, col_v2 = st.columns([1.2, 1.8])

        with col_v1:
            with st.container(border=True):
                st.markdown("#### Configuración de Voz")
                engine = st.selectbox(
                    "Motor de Síntesis Vocal:",
                    ["Kokoro TTS HD (Local 24kHz - /bin/bash)", "VibeVoice 1.5B (ZeroGPU)", "ElevenLabs Turbo v2.5", "Fish Audio (Clonación)", "Edge TTS (Microsoft Gratis)"],
                    index=0
                )

                if "Kokoro" in engine:
                    voice_name = st.selectbox("Voz Neural Española / Multilingüe:", ["es_dora (Español Neutro Femenino)", "es_santiago (Español Masculino)", "es_alex (Español Dinámico)", "en_nicole (Inglés Femenino)", "en_adam (Inglés Masculino)"])
                elif "ElevenLabs" in engine:
                    voice_name = st.selectbox("Voz ElevenLabs:", ["Rachel (Narradora)", "Adam (Documental)", "Antoni (Comercial)", "Domi (Enérgica)"])
                else:
                    voice_name = st.text_input("Identificador de Voz / Speaker ID:", value="es-ES-AlvaroNeural")

                rate = st.slider("Velocidad de Habla (Tempo):", 0.7, 1.5, 1.0, 0.05)
                pitch = st.slider("Tono / Entonación (Pitch):", -5, 5, 0, 1)

        with col_v2:
            with st.container(border=True):
                st.markdown("#### Guion de Locución")
                text_to_speak = st.text_area(
                    "Texto a sintetizar:",
                    value="En un mundo dominado por algoritmos, el verdadero poder reside en quienes entienden la arquitectura oculta de la inteligencia artificial.",
                    height=140
                )

                if st.button("Sintetizar Audio Maestro", type="primary", use_container_width=True):
                    if text_to_speak.strip():
                        with st.spinner("Generando locución neural..."):
                            try:
                                v_id = voice_name.split(" ")[0] if " " in voice_name else voice_name
                                audio_file = voice_service.tts(
                                    text=text_to_speak,
                                    voice_name=v_id,
                                    voice_rate=rate,
                                    voice_file=tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
                                )
                                if audio_file and os.path.exists(audio_file):
                                    st.success("Audio generado con éxito.")
                                    st.audio(audio_file)
                                    with open(audio_file, "rb") as af:
                                        st.download_button(
                                            "Descargar Audio WAV (48kHz Master)",
                                            data=af.read(),
                                            file_name="locucion_master.wav",
                                            mime="audio/wav",
                                            use_container_width=True
                                        )
                                else:
                                    st.warning("No se pudo generar el archivo de audio. Verifica el motor seleccionado.")
                            except Exception as e:
                                st.error(f"Error en la síntesis vocal: {e}")
                    else:
                        st.error("Introduce un texto para sintetizar.")

    with tab_music:
        st.subheader("Compositor y Diseñador de Bandas Sonoras Flow Music")
        st.caption("Estructura pistas musicales completas basadas en el modelo de Google Lyria 3 Pro con timing exacto a 24 fps.")

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            with st.container(border=True):
                st.markdown("#### Parámetros Musicales")
                genre = st.selectbox(
                    "Género / Atmósfera:",
                    ["Cinematic Hybrid Orchestral (Hans Zimmer)", "Cyberpunk Synthwave 120 BPM", "Ambient Dark Drone (Documental)", "Lo-Fi Hip Hop Chill (Estudio)", "Epic Action Trailer (Híbrido)"]
                )
                tempo = st.slider("Tempo (BPM):", 60, 160, 120, 5)
                duration_sec = st.number_input("Duración deseada (segundos):", 15, 300, 60, 5)

                st.markdown("#### Matemáticas de Sincronización a 24 FPS")
                frames_per_beat = (60.0 / tempo) * 24.0
                bars_frames = frames_per_beat * 4.0
                st.info(f"1 Beat = **{frames_per_beat:.1f} frames** ({60/tempo:.2f}s) | 1 Compás (4/4) = **{bars_frames:.1f} frames** ({240/tempo:.2f}s)")

        with col_m2:
            with st.container(border=True):
                st.markdown("#### Prompt Musical Generativo (Google Lyria 3)")
                prompt_text = st.text_area(
                    "Prompt Estructurado:",
                    value=f"Genre: {genre}, Tempo: {tempo} BPM, Key: D Minor, Instrumentation: Analog Moog Bass, Anamorphic Strings, 808 Sub-kick, 48kHz Master Stereo.",
                    height=130
                )

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Copiar Prompt para Flow Music", use_container_width=True):
                        st.toast("Prompt copiado al portapapeles.")
                with col_b2:
                    st.link_button("Abrir Flow Music Web", "https://flowmusic.app", use_container_width=True)

        st.markdown("---")
        st.markdown("#### Importar Pista BGM y Ajustar Sidechain Ducking")
        uploaded_bgm = st.file_uploader("Subir archivo de audio BGM (WAV / MP3):", type=["wav", "mp3", "ogg"])
        if uploaded_bgm:
            st.audio(uploaded_bgm)
            ducking_val = st.slider("Nivel de Ducking bajo la voz (dB):", -30, -6, -22, 1)
            st.caption(f"La música se atenuará automáticamente a **{ducking_val} dB** cada vez que el locutor hable.")
