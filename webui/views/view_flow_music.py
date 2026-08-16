import sys
import os
import tempfile
from pathlib import Path
import streamlit as st
from app.services.audio.flowmusic_service import FlowMusicAutomationService

def render_view():
    st.title("Flow Music Studio")
    st.caption("Composición y generación de pistas musicales estructuradas con Google Lyria 3 Pro.")

    tab_prompt, tab_slice, tab_workflows, tab_docs = st.tabs([
        "Diseñador de Prompts Musicales",
        "Troceador & Mapeador de Escenas (Audio Slicer)",
        "Flujos de Automatización",
        "Documentación Técnica"
    ])

    service = FlowMusicAutomationService()

    with tab_prompt:
        st.subheader("Constructor de Prompts para Google Flow Music")
        st.caption("Crea la estructura de instrumentación, tempo y progresiones para flowmusic.app.")

        c1, c2, c3 = st.columns(3)
        with c1:
            genre = st.selectbox(
                "Género Musical",
                [
                    "Cinematic Hybrid Orchestral (Hans Zimmer / Nolan Style)",
                    "Cyberpunk Synthwave & Dark Electro (Blade Runner 2049)",
                    "Minimalist Ambient & Neo-Classical (Olafur Arnalds)",
                    "Deep Tech & Atmospheric Electronica (Max Cooper)",
                    "Institutional Wall Street Pulse (Bloomberg / Succession Style)",
                    "Epic Trailer Orchestral & Heavy Brass Hits",
                    "Chillstep / Lo-Fi Focus Flow"
                ]
            )
            mood = st.selectbox(
                "Emoción / Mood",
                ["Tensión Creciente & Anticipación", "Épico & Triunfante", "Furtivo & Suspenso", "Melancólico & Reflexivo", "Futurista & Alta Velocidad", "Inspiracional & Majestuoso"]
            )

        with c2:
            bpm = st.slider("Tempo Maestro (BPM)", min_value=60, max_value=160, value=120, step=5)
            is_inst = st.checkbox("Solo Instrumental (Sin voces)", value=True)
            structure = st.selectbox(
                "Estructura de la Pista",
                [
                    "Intro (0-15s) -> Buildup (15-35s) -> Drop (35-55s) -> Outro (55-60s)",
                    "Establishing Ambient (0-20s) -> Heavy Bass Drop (20-60s)",
                    "Continuous Slow Crescendo (0-90s) -> Abrupt Cut",
                    "Full Song: Intro -> Verse 1 -> Chorus -> Verse 2 -> Final Drop -> Outro (3 mins)"
                ]
            )

        with c3:
            st.markdown("**Instrumentos Clave:**")
            inst_opts = st.multiselect(
                "Seleccionar Instrumentos",
                ["Analog Moog Sub-bass", "Crisp 808 Snares & Hi-Hats", "Staccato Cellos & Violins", "French Horns & Low Brass", "Granular Glitch Pads", "Acoustic Felt Piano", "Electric Guitar Reverb Swells"],
                default=["Analog Moog Sub-bass", "Crisp 808 Snares & Hi-Hats", "Staccato Cellos & Violins"]
            )

        generated_prompt = service.build_flowmusic_prompt(
            genre=genre,
            mood=mood,
            bpm=bpm,
            instruments=inst_opts,
            structure=structure,
            is_instrumental=is_inst
        )

        st.markdown("#### Prompt Maestro Listo para Flow Music:")
        st.code(generated_prompt, language="text")

        st.markdown("""
        👉 **Paso siguiente:** Copia el prompt anterior y pégalo en la web oficial:  
        🔗 **[Abrir Google Flow Music (flowmusic.app)](https://flowmusic.app/)**
        """)

    with tab_slice:
        st.subheader("Troceador Inteligente & Mapeador de Escenas para Vídeo")
        st.caption("Sube la canción generada en Flow Music para dividirla en compases y asociar cada fragmento a una toma de LTX-2.5 y FLUX 3.")

        uploaded_audio = st.file_uploader("Subir Pista Maestra de Flow Music (MP3 / WAV)", type=["mp3", "wav", "m4a", "ogg"])

        if uploaded_audio is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_audio.name)[1]) as tmp_file:
                tmp_file.write(uploaded_audio.read())
                tmp_audio_path = tmp_file.name

            st.audio(tmp_audio_path)

            col_sl1, col_sl2 = st.columns([2, 1])
            with col_sl1:
                fps_val = st.selectbox("FPS de Producción", [24, 25, 30, 60], index=0)
            with col_sl2:
                st.write("")
                btn_slice = st.button("Analizar y Trocear a Compás", type="primary")

            if btn_slice or "sliced_data" in st.session_state:
                if btn_slice:
                    with st.spinner("Analizando espectro de audio, detectando compases y exportando cortes a 48kHz..."):
                        st.session_state["sliced_data"] = service.analyze_and_slice_audio(tmp_audio_path, target_fps=fps_val)
                        st.success("Pista analizada y troceada con éxito.")

                data = st.session_state.get("sliced_data", {})
                st.markdown(f"**Duración Total:** `{data.get('total_duration_s')}s` | **Total Frames:** `{data.get('total_frames')}` | **Total Planos:** `{data.get('total_scenes')}`")

                st.divider()
                st.markdown("#### Escaleta de Producción Audiovisual Sincronizada:")

                for sc in data.get("scenes", []):
                    with st.container(border=True):
                        c_s1, c_s2, c_s3 = st.columns([1, 2, 2])
                        with c_s1:
                            st.markdown(f"### {sc['shot_id']}")
                            st.markdown(f"**Fase:** `{sc['phase']}`")
                            st.caption(f"⏱️ {sc['start_s']}s -> {sc['end_s']}s ({sc['frames_count']} frames)")
                        with c_s2:
                            st.markdown(f"**Tipo de Toma DoP:** {sc['shot_type']}")
                            st.markdown(f"**Nivel de Energía:** `{sc['energy_level']}`")
                            if os.path.exists(sc.get("slice_path", "")):
                                st.audio(sc["slice_path"])
                        with c_s3:
                            st.markdown("**Prompt DoP Recomendado:**")
                            suggested_p = f"Cinematic master shot. {sc['shot_type']} with 6-DoF camera vector. High dynamic range, ARRI Alexa 65, Panavision 40mm. [Audio 48kHz: Synced to {sc['phase']} energy]."
                            st.code(suggested_p, language="text")

    with tab_workflows:
        st.subheader("Flujos de Trabajo")
        col_wf1, col_wf2 = st.columns(2)
        with col_wf1:
            with st.container(border=True):
                st.markdown("#### Modo 1: Music-First Master Flow")
                st.markdown("""
                **¿Cuándo usarlo?**  
                Para trailers, anuncios publicitarios, intros cinemáticas y clips musicales donde el ritmo visual baila al compás de la música.

                **Paso a Paso:**
                1. Generar la canción en **Flow Music** (1 a 3 minutos).
                2. Subirla al *Audio Slicer* para extraer los trozos de compás ($SH_01, SH_02...$).
                3. Enviar peticiones de vídeo a **LTX-2.5 / FLUX 3** con la duración exacta en frames.
                4. Añadir la voz en off en los momentos de menor densidad instrumental.
                5. Ensamblar con **Sidechain Ducking (-14dB)**.
                """)

        with col_wf2:
            with st.container(border=True):
                st.markdown("#### Modo 2: Script-First Adaptive Flow")
                st.markdown("""
                **¿Cuándo usarlo?**  
                Para documentales estilo Vox / Bloomberg, reportajes y tutoriales donde la locución es el elemento rector.

                **Paso a Paso:**
                1. Escribir el guion y generar la locución (Kokoro HD / VibeVoice).
                2. Medir la duración exacta de la voz.
                3. Pedir a Flow Music una base instrumental de esa duración exacta.
                4. Asignar planos visuales LTX-2.5 que apoyen la narrativa.
                5. Aplicar compresión Sidechain para mantener la música de fondo.
                """)

    with tab_docs:
        st.subheader("Documentación Técnica")
        st.markdown("""
        1. **Marcadores Temporales en el Prompt:**  
           Flow Music responde a descripciones de línea temporal (ej: `[0:00-0:15 Soft Piano Intro], [0:15-0:45 Heavy Bass Buildup]`).
        2. **Control de Frecuencias para Locución:**  
           Añade siempre al prompt: `Mid-range notch for voiceover clarity, clean stereo sides, tight center sub-bass` para dejar espacio a la voz.
        3. **Troceado a 48kHz sin Pérdida:**  
           El motor de VideoPro exporta fragmentos en WAV PCM 48kHz/16-bit.
        """)
