import streamlit as st
import os
import json
import time
import requests
from pathlib import Path

st.set_page_config(page_title="LTX-2.5 & FLUX 3 Studio", page_icon="🛸", layout="wide")

st.markdown("""
<style>
    .studio-header {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.15), rgba(168, 85, 247, 0.15));
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 20px 24px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    .badge-ltx {
        background: linear-gradient(135deg, #00f2fe, #4facfe);
        color: #050b14;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
    }
    .badge-flux {
        background: linear-gradient(135deg, #a855f7, #ec4899);
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="studio-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #f8fafc;">
                🛸 LTX-2.5 & FLUX 3 Cinematic Studio
            </h1>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 14px;">
                Generación Exclusiva de Vídeo Multimodal con Audio Nativo 48kHz y Control Óptico Hollywood/Netflix
            </p>
        </div>
        <div>
            <span class="badge-ltx">LTX-2.5 MMDiT 22B</span>
            <span class="badge-flux" style="margin-left: 6px;">FLUX 3 Video</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

HUB_API = "http://127.0.0.1:7899"

col_left, col_right = st.columns([5, 4])

with col_left:
    st.subheader("🎥 Configuración de Escena y Óptica")
    
    engine = st.selectbox(
        "Motor Generativo",
        ["LTX-2.5 (Lightricks 22B Dual MMDiT + Audio Nativo 48kHz)", "FLUX 3 (Black Forest Labs 6-DoF Cinema)"]
    )
    
    col_dop1, col_dop2 = st.columns(2)
    with col_dop1:
        dop_preset = st.selectbox(
            "Cámara y Lente (Perfil DoP)",
            [
                "ARRI Alexa 65 + Panavision Anamorphic 35mm f/2.8",
                "Hasselblad X2D 100C + 24mm f/2.8 Ultra-Sharp",
                "Cooke Anamorphic /i 2.39:1 Cinemascope",
                "Custom Manual Parameters"
            ]
        )
    with col_dop2:
        cam_motion = st.selectbox(
            "Cinemática 6-DoF",
            [
                "Inception Low Glide -> Dynamic Parabolic Arc -> Horizon Lock",
                "Street Level Low-Altitude Parallax 1.8 m/s",
                "Freeze 3D 180° Orbit (@M_Dobrodziej)",
                "FPV High-Speed Dive & Atmospheric Settle"
            ]
        )

    st.markdown("### 🧩 Las 4 Capas de Prompting Multimodal")
    c1 = st.text_area(
        "Capa 1: Sujeto Visual & Escena (Luz, Texturas, Color)",
        value="Cinematic master shot of an autonomous carbon-fiber VTOL aero-vehicle gliding through a hyper-dense Neo-Tokyo skyline during blue twilight. Ultra-detailed volumetric fog, wet asphalt reflections, luminescent cyan and amber neon signs, ARRI Alexa 65 look.",
        height=75
    )
    
    c2 = st.text_area(
        "Capa 2: Dinámica de Cámara (Óptica y Vector 3D)",
        value=f"Smooth optical motion: {cam_motion}. Kodak Vision3 500T 35mm film grain, anamorphic horizontal flare.",
        height=60
    )
    
    c3 = st.text_area(
        "Capa 3: Foley Acústico Diegético (Sincronizado a 48kHz)",
        value="Whirring composite turbine blades with electromagnetic hum, aerodynamic air friction, distant rain on canopy, 48kHz binaural spatial audio.",
        height=60
    )
    
    c4 = st.text_area(
        "Capa 4: Score Atmosférico y Música",
        value="Deep 40Hz sub-bass analog synth drone, evolving atmospheric granular pads, rising cinematic tension.",
        height=60
    )
    
    uploaded_frame = st.file_uploader("🖼️ Fotograma Maestro Inicial ($t=0$) (Image-to-Video)", type=["jpg", "png", "webp"])

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        duration_s = st.slider("Duración (Segundos)", min_value=2.0, max_value=10.0, value=5.0, step=0.5)
    with col_p2:
        fps_val = st.selectbox("Frame Rate", [24, 25, 30, 60], index=1)
    with col_p3:
        aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "2.39:1", "1:1"])

    generate_btn = st.button("🚀 Iniciar Renderizado Multimodal SOTA", type="primary", use_container_width=True)

with col_right:
    st.subheader("📺 Monitor de Render & Reproductor 48kHz")
    
    if generate_btn:
        st.info(f"Enviando petición a {engine} mediante el pool rotativo de tokens ZeroGPU...")
        full_prompt = f"""{c1}
[CAMERA]: {c2}
[FOLEY_48KHZ]: {c3}
[SCORE]: {c4}"""
        
        payload = {
            "prompt": full_prompt,
            "engine": "ltx-2.5" if "LTX" in engine else "flux-3",
            "duration_s": duration_s,
            "fps": fps_val,
            "aspect_ratio": aspect_ratio
        }
        
        try:
            res = requests.post(f"{HUB_API}/api/generate", json=payload, timeout=120)
            if res.status_code == 200:
                data = res.json()
                st.success("¡Vídeo con Audio Nativo Co-Generado con Éxito!")
                video_url = data.get("video_url")
                if video_url:
                    st.video(f"{HUB_API}{video_url}" if video_url.startswith("/") else video_url)
                st.json(data)
            else:
                st.error(f"Error en Hub: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Error conectando al Serverless Hub: {e}")

    # Mostrar galería de fotogramas maestros existentes
    st.markdown("#### 🎞️ Fotogramas Maestros de Referencia DoP")
    master_dir = Path("/home/ubuntu/serverless_hub/outputs/master_dop")
    if master_dir.exists():
        imgs = list(master_dir.glob("*.jpg")) + list(master_dir.glob("*.png"))
        if imgs:
            for img_p in imgs[:3]:
                st.image(str(img_p), caption=img_p.name, use_container_width=True)
