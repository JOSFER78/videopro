import os
import sys
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def render_view():
    tab_ltx, tab_flux = st.tabs([
        "LTX-2.5 22B Video Studio",
        "FLUX 3 Ultra Photoreal"
    ])

    with tab_ltx:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Parámetros de Cámara LTX-2.5**")
            optics = st.selectbox("Lente:", ["Cooke Anamorphic /i Full Frame Plus 40mm T2.3", "ARRI Master Prime 35mm T1.3", "Panavision C-Series 50mm Anamorphic", "Canon K35 Vintage 24mm T1.5"])
            cam_move = st.selectbox("Movimiento:", ["Slow Dolly-In with parallax", "Orbit 180° around subject", "High-angle crane descending", "FPV Dynamic Tracking"])
            ltx_prompt = st.text_area("Prompt Cinemático (4 capas):", value="Cinematic masterpiece, dramatic lighting, shot on 35mm film", height=70)
        with c2:
            st.markdown("**Ajustes de Render GPU**")
            steps = st.slider("Pasos de Difusión:", 20, 50, 30)
            guidance = st.slider("Guidance Scale:", 1.0, 10.0, 3.5, 0.5)
            fps = st.selectbox("FPS:", [24, 30, 60], index=0)
            if st.button("Generar Clip LTX-2.5", type="primary", use_container_width=True):
                st.info("Renderizando clip en clúster GPU...")

    with tab_flux:
        cf1, cf2 = st.columns(2)
        with cf1:
            st.markdown("**Prompt Fotográfico FLUX 3**")
            flux_prompt = st.text_area("Prompt FLUX 3:", value="Photorealistic portrait, 8k resolution, cinematic atmosphere", height=70)
            aspect = st.selectbox("Relación de Aspecto:", ["9:16 (Vertical)", "16:9 (Horizontal)", "1:1 (Cuadrado)"])
        with cf2:
            st.markdown("**Ajustes de Calidad**")
            cfg = st.slider("CFG Scale:", 1.0, 8.0, 3.5)
            flux_steps = st.slider("Pasos FLUX:", 20, 50, 28)
            if st.button("Generar Imagen FLUX 3", type="primary", use_container_width=True):
                st.info("Generando imagen fotográfica FLUX 3...")
