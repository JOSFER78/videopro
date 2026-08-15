import streamlit as st

def render_step_2_visuals(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>🎨 PASO 2:</span> Motor Visual, Resoluciones (2K/4K) & Formato
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Configura el motor de renderizado de vídeo e imágenes, la relación de aspecto y las reglas de descarte.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("##### 🛸 Motor de Generación Visual")
        engine_options = {
            "flux": "FLUX 3 Video / Keyframes (Replicate H100 / ZeroGPU)",
            "ltx25": "LTX-2.5 MMDiT 22B (Audio + Vídeo 24fps)",
            "google_flow": "Google Flow (Playwright Navegador Web 4K)",
            "pexels": "Pexels & Pixabay Video Stock HD ($0)",
            "real_news": "DuckDuckGo & Wikimedia Real News Images ($0)"
        }
        cur_engine = st.selectbox(
            "Seleccionar Motor Principal:",
            options=list(engine_options.keys()),
            format_func=lambda x: engine_options[x],
            key="w_step2_engine"
        )
        params.video_source = cur_engine

        st.markdown("##### 📐 Formato de Pantalla & Plataforma")
        ar_options = {
            "9:16": "9:16 Vertical (TikTok / Reels / Shorts)",
            "16:9": "16:9 Panorámico (YouTube / Cine)",
            "1:1": "1:1 Cuadrado (Instagram Feed)"
        }
        cur_ar = st.radio(
            "Relación de Aspecto:",
            options=list(ar_options.keys()),
            format_func=lambda x: ar_options[x],
            horizontal=True,
            key="w_step2_aspect"
        )
        params.video_aspect = cur_ar

    with col2:
        st.markdown("##### ✨ Preferencias Granulares de Calidad")
        st.checkbox("✨ Generar Stills en 2K (2048x2048 / 2048x1152)", value=True, key="w_step2_pref_2k")
        st.checkbox("✨ Renderizado de Vídeo en 1080p Nativo a 24fps", value=True, key="w_step2_pref_1080p")
        st.checkbox("✨ Control de Movimiento de Cámara 35mm Cinemático", value=True, key="w_step2_pref_cam")

        st.markdown("##### 🚫 Reglas de Descarte Automático")
        st.checkbox("🚫 Descartar resoluciones bajas (480p / 720p)", value=True, key="w_step2_disc_lowres")
        st.checkbox("🚫 Descartar imágenes con marcas de agua o <400x300", value=True, key="w_step2_disc_wm")
        st.checkbox("🚫 Descartar NanoBanana Lite / Modelos Fast", value=True, key="w_step2_disc_lite")
