import streamlit as st

def render_step_3_audio(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>🎙️ PASO 3:</span> Voces Neorales, Foley Acústico 48kHz & Música
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Configura la locución en off (Kokoro HD $0 / VibeVoice), los efectos de sonido y la mezcla musical con Sidechain Ducking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("##### 🎙️ Motor y Voz de Locución")
        voice_options = {
            "kokoro_dora": "Kokoro HD (Español): Dora — Tono Cálido Documental ($0)",
            "kokoro_alex": "Kokoro HD (Español): Alex — Tono Dinámico / Noticias ($0)",
            "kokoro_santiago": "Kokoro HD (Español): Santiago — Narrador Épico ($0)",
            "vibevoice_es": "VibeVoice Pro: Expresiva con Prosodia Natural",
            "none": "🚫 Sin Locutor (Vídeo Cinemático Puro con Sonido Ambiental)"
        }
        cur_voice = st.selectbox(
            "Seleccionar Voz:",
            options=list(voice_options.keys()),
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
        
        bgm_options = [
            "Google Flow Music (Lyria 3 Pro a compás)",
            "Música Épica Cinemática (WAV 48kHz)",
            "Lo-Fi Periodístico Investigativo",
            "🚫 Sin Música de Fondo"
        ]
        cur_bgm = st.selectbox("Banda Sonora (BGM):", bgm_options, key="w_step3_bgm")
        params.bgm_type = cur_bgm
