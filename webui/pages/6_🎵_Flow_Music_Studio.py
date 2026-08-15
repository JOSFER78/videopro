import streamlit as st
import os
import tempfile
from pathlib import Path
from app.services.audio.flowmusic_service import FlowMusicAutomationService

st.set_page_config(
    page_title="Flow Music Studio (Google Lyria 3 Pro)",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos Glassmorphism Premium
st.markdown("""
<style>
    .music-hero {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(49, 46, 129, 0.85));
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }
    .flow-badge {
        display: inline-block;
        background: rgba(139, 92, 246, 0.2);
        color: #a78bfa;
        border: 1px solid rgba(139, 92, 246, 0.4);
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .scene-card {
        background: rgba(15, 23, 42, 0.7);
        border-left: 4px solid #8b5cf6;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="music-hero">
    <div class="flow-badge">AUDIO-DRIVEN CINEMATIC PIPELINE</div>
    <h1 style="color:#ffffff; margin:0; font-size:32px; font-weight:900;">🎵 Flow Music Studio (Google Lyria 3 Pro)</h1>
    <p style="color:#cbd5e1; margin:6px 0 0 0; font-size:15px;">
        Generación de bandas sonoras multi-minuto, análisis de compases y troceado automatizado de audio sincronizado con <b>LTX-2.5 & FLUX 3</b>.
    </p>
</div>
""", unsafe_allow_html=True)

tab_prompt, tab_slice, tab_workflows, tab_docs = st.tabs([
    "🎹 1. Diseñador de Prompts Musicales",
    "✂️ 2. Troceador & Mapeador de Escenas (Audio Slicer)",
    "🔀 3. Flujos de Automatización (Music-First vs Script-First)",
    "📚 4. Documentación & Trucos SOTA"
])

service = FlowMusicAutomationService()

# =============================================================================
# TAB 1: PROMPT BUILDER
# =============================================================================
with tab_prompt:
    st.markdown("### 🎹 Constructor de Prompts para Google Flow Music")
    st.caption("Crea la estructura perfecta de instrumentación, tempo y progresiones para introducir en flowmusic.app.")

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

    st.markdown("#### 📋 Prompt Maestro Listo para Flow Music:")
    st.code(generated_prompt, language="text")

    st.markdown("""
    👉 **Paso siguiente:** Copia el prompt anterior y pégalo en la web oficial:  
    🔗 **[Abrir Google Flow Music (flowmusic.app)](https://flowmusic.app/)**
    """)

# =============================================================================
# TAB 2: AUDIO SLICER
# =============================================================================
with tab_slice:
    st.markdown("### ✂️ Troceador Inteligente & Mapeador de Escenas para Vídeo")
    st.caption("Sube la canción generada en Flow Music para dividirla automáticamente en compases y asociar cada fragmento a una toma de LTX-2.5 y FLUX 3.")

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
            btn_slice = st.button("✂️ Analizar y Trocear a Compás", type="primary")

        if btn_slice or "sliced_data" in st.session_state:
            if btn_slice:
                with st.spinner("Analizando espectro de audio, detectando compases y exportando cortes a 48kHz..."):
                    st.session_state["sliced_data"] = service.analyze_and_slice_audio(tmp_audio_path, target_fps=fps_val)
                    st.success("¡Pista analizada y troceada con éxito!")

            data = st.session_state.get("sliced_data", {})
            st.markdown(f"**Duración Total:** `{data.get('total_duration_s')}s` | **Total Frames:** `{data.get('total_frames')}` | **Total Planos:** `{data.get('total_scenes')}`")

            st.divider()
            st.markdown("#### 🎬 Escaleta de Producción Audiovisual Sincronizada:")

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
                        suggested_p = f"Cinematic master shot. {sc['shot_type']} with 6-DoF camera vector. High dynamic range, ARRI Alexa 65, Panavision 40mm, Mie volumetric scattering. [Audio 48kHz: Synced to {sc['phase']} energy, pristine mix]."
                        st.code(suggested_p, language="text")

# =============================================================================
# TAB 3: WORKFLOWS
# =============================================================================
with tab_workflows:
    st.markdown("### 🔀 Cuándo Usar Cada Flujo: Guía de Decisión")

    col_wf1, col_wf2 = st.columns(2)
    with col_wf1:
        with st.container(border=True):
            st.markdown("#### 🎵 Modo 1: Music-First Master Flow (Recomendado para Vídeos de Alto Impacto)")
            st.markdown("""
            **¿Cuándo usarlo?**  
            Para trailers, anuncios publicitarios, intros cinemáticas, clips musicales y vídeos de acción donde el ritmo visual DEBE bailar al compás de la música.

            **Paso a Paso:**
            1. Generar la canción en **Flow Music** (1 a 3 minutos).
            2. Subirla al *Audio Slicer* para extraer los trozos de compás ($SH_01, SH_02...$).
            3. Enviar peticiones de vídeo a **LTX-2.5 / FLUX 3** con la duración exacta en frames de cada trozo.
            4. Añadir la voz en off en los momentos de menor densidad instrumental (*Verse*).
            5. Ensamblar con **Sidechain Ducking (-14dB)**.
            """)

    with col_wf2:
        with st.container(border=True):
            st.markdown("#### 📜 Modo 2: Script-First Adaptive Flow (Recomendado para Documentales y Noticias)")
            st.markdown("""
            **¿Cuándo usarlo?**  
            Para documentales estilo Vox / Bloomberg, tutoriales, reportajes y vídeos educativos donde la locución es el elemento rector.

            **Paso a Paso:**
            1. Escribir el guion y generar la locución de voz (Kokoro HD en español o VibeVoice en inglés).
            2. Medir la duración exacta de la voz (ej. $38.5\\text{s}$).
            3. Pedir a Flow Music una base instrumental de esa duración exacta con tempo estable ($100-120\\text{ BPM}$).
            4. Asignar planos visuales LTX-2.5 que apoyen la narrativa del locutor.
            5. Aplicar compresión Sidechain para que la música se mantenga como cama de fondo (*bed audio*).
            """)

# =============================================================================
# TAB 4: DOCS & TRICKS
# =============================================================================
with tab_docs:
    st.markdown("### 📚 Trucos SOTA para Google Flow Music (Lyria 3 Pro)")
    st.markdown("""
    1. **Estructurar con Marcadores Temporales en el Prompt:**  
       Flow Music responde extremadamente bien a descripciones de línea temporal (ej: `[0:00-0:15 Soft Piano Intro], [0:15-0:45 Heavy Bass Buildup], [0:45-1:15 Explosive Drop]`).
    2. **Control de Frecuencias para Locución:**  
       Si vas a poner voz encima, añade siempre al prompt: `Mid-range notch for voiceover clarity, clean stereo sides, tight center sub-bass`. Esto deja espacio espectral natural para la voz de Kokoro/VibeVoice.
    3. **Troceado a 48kHz sin Pérdida:**  
       El motor de VideoPro exporta los fragmentos en formato WAV PCM 48kHz/16-bit para que LTX-2.5 no sufra artefactos de remuestreo ni desfases de fase.
    """)
