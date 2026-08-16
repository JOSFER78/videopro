import streamlit as st
from app.core.providers import health_checker
from app.core.providers import registry


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

    # Consultar estado en vivo de proveedores
    matrix = health_checker.get_all_providers_matrix()
    nb_badge = "🟢 Listo" if matrix.get("nanobanana", {}).get("status") == "ok" else "🔴 Inactivo"
    rep_badge = "🟢 H100" if matrix.get("replicate", {}).get("status") == "ok" else "⚪ ZeroGPU $0"
    pex_badge = "🟢 4K" if matrix.get("pexels", {}).get("status") == "ok" else "⚪ Sin clave"

    # Motores disponibles filtrados estrictamente por la Matriz de Proveedores
    candidate_engines = {
        "nanobanana": ("nanobanana", f"🍌 NanoBanana Pro 2 (Gemini Imagen 3 — 2K/4K) [{nb_badge}]"),
        "flux": ("flux", f"FLUX 3 Video / Keyframes [{rep_badge}]"),
        "ltx25": ("ltx25", f"LTX-2.5 MMDiT 22B (Audio + Vídeo 24fps) [{rep_badge}]"),
        "google_flow": ("google_flow", "Google Flow (Playwright Navegador Web 4K) [🟢 Headless]"),
        "pexels": ("pexels", f"Pexels & Pixabay Video Stock HD ($0) [{pex_badge}]"),
        "real_news": ("real_news", "DuckDuckGo & Wikimedia Real News Images ($0) [🟢 Libre]")
    }

    engine_options = {}
    for eng_id, (prov_key, label) in candidate_engines.items():
        if registry.is_provider_enabled(prov_key):
            engine_options[eng_id] = label

    # Fallback seguro si el usuario desactivara todo
    if not engine_options:
        engine_options["nanobanana"] = "🍌 NanoBanana Pro 2 (Gemini Imagen 3 — 2K/4K)"

    with col1:
        st.markdown("##### 🛸 Motor de Generación Visual")
        cur_keys = list(engine_options.keys())
        prev_idx = 0
        if getattr(params, "video_source", None) in cur_keys:
            prev_idx = cur_keys.index(params.video_source)

        cur_engine = st.selectbox(
            "Seleccionar Motor Principal:",
            options=cur_keys,
            index=prev_idx,
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
