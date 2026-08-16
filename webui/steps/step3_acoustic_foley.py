import streamlit as st
from app.core.providers import registry, health_checker


def render_step_3_audio(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>🎙️ PASO 3:</span> Voces Neuronales, Foley Acústico 48kHz & Música
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Configura la locución (Local VPS $0, Serverless ZeroGPU o Cloud API), foley y mezcla musical con Sidechain Ducking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    # Construir opciones de voz filtradas estrictamente por la Matriz de Proveedores
    voice_options = {}

    if registry.is_provider_enabled("kokoro_local"):
        voice_options["kokoro_dora"] = "Kokoro HD (Español): Dora — Tono Cálido Documental [🟢 $0 Local CPU]"
        voice_options["kokoro_alex"] = "Kokoro HD (Español): Alex — Tono Dinámico / Noticias [🟢 $0 Local CPU]"
        voice_options["kokoro_santiago"] = "Kokoro HD (Español): Santiago — Narrador Épico [🟢 $0 Local CPU]"

    if registry.is_provider_enabled("vibevoice_local"):
        voice_options["vibevoice:es-emilio-Male"] = "🎙️ VibeVoice 1.5B Local (VPS /es-emilio) [🟢 $0 Local VPS]"
        voice_options["vibevoice:en-Carter-Male"] = "🎙️ VibeVoice 1.5B Local (VPS /en-Carter) [🟢 $0 Local VPS]"
        voice_options["vibevoice:en-Alice-Female"] = "🎙️ VibeVoice 1.5B Local (VPS /en-Alice) [🟢 $0 Local VPS]"

    if registry.is_provider_enabled("vibevoice_serverless"):
        voice_options["vibevoice_serverless:es-emilio-Male"] = "☁️ VibeVoice 1.5B Serverless (ZeroGPU Pool) [🟢 $0 ZeroGPU Cloud]"
        voice_options["vibevoice_serverless:en-Carter-Male"] = "☁️ VibeVoice 1.5B Serverless (ZeroGPU Pool) [🟢 $0 ZeroGPU Cloud]"

    if registry.is_provider_enabled("edge_tts"):
        voice_options["es-ES-AlvaroNeural"] = "Edge-TTS Neural: Álvaro (Español Neutro) [🟢 $0 Cloud]"
        voice_options["es-ES-ElviraNeural"] = "Edge-TTS Neural: Elvira (Español Natural) [🟢 $0 Cloud]"
        voice_options["en-US-GuyNeural"] = "Edge-TTS Neural: Guy (English US) [🟢 $0 Cloud]"

    if registry.is_provider_enabled("elevenlabs"):
        voice_options["elevenlabs_adam"] = "ElevenLabs Cinema: Adam (Narrador Profundo) [Cloud API]"
        voice_options["elevenlabs_rachel"] = "ElevenLabs Cinema: Rachel (Calidad Estudio) [Cloud API]"

    voice_options["none"] = "🚫 Sin Locutor (Vídeo Cinemático Puro con Sonido Ambiental)"

    with col1:
        st.markdown("##### 🎙️ Motor y Voz de Locución")
        v_keys = list(voice_options.keys())
        prev_v = getattr(params, "voice_name", v_keys[0])
        p_v_idx = v_keys.index(prev_v) if prev_v in v_keys else 0

        cur_voice = st.selectbox(
            "Seleccionar Voz:",
            options=v_keys,
            index=p_v_idx,
            format_func=lambda x: voice_options[x],
            key="w_step3_voice"
        )
        params.voice_name = cur_voice

        voice_rate = st.slider("Velocidad de Lectura:", 0.8, 1.4, 1.0, 0.05, key="w_step3_rate")
        params.voice_rate = voice_rate

    with col2:
        st.markdown("##### 🎵 Banda Sonora & Efectos Foley 48kHz")
        st.checkbox("✨ Efectos Foley Acústicos Automáticos (Clicks, Papel, Engranajes)", value=True, key="w_step3_foley")
        st.checkbox("✨ Sidechain Ducking Automático (-22 dB durante la locución)", value=True, key="w_step3_ducking")
        
        bgm_options = []
        if registry.is_provider_enabled("flowmusic"):
            bgm_options.append("Google Flow Music (Lyria 3 Pro a compás)")
        if registry.is_provider_enabled("suno"):
            bgm_options.append("Suno AI (Composición Sonora Completa)")

        bgm_options.extend([
            "Música Épica Cinemática (WAV 48kHz)",
            "Lo-Fi Periodístico Investigativo",
            "🚫 Sin Música de Fondo"
        ])

        cur_bgm = st.selectbox("Banda Sonora (BGM):", bgm_options, key="w_step3_bgm")
        params.bgm_type = cur_bgm
