import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="Cinema Master Player", page_icon="🎞️", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(59, 130, 246, 0.15)); border: 1px solid rgba(255, 255, 255, 0.12); padding: 20px 24px; border-radius: 16px; margin-bottom: 24px;">
    <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #f8fafc;">
        🎞️ Cinema Master Player & Auditor de Cortes
    </h1>
    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 14px;">
        Inspección de Másters Generados, Sincronización Acústico-Visual y Análisis de Bitrate
    </p>
</div>
""", unsafe_allow_html=True)

# Buscar vídeos en salidas
outputs_dirs = [
    Path("/home/ubuntu/serverless_hub/outputs"),
    Path("/home/ubuntu/MoneyPrinterTurbo/storage/tasks")
]

found_videos = []
for out_d in outputs_dirs:
    if out_d.exists():
        for f in out_d.glob("**/*.mp4"):
            found_videos.append(f)

if found_videos:
    selected_video = st.selectbox("Seleccionar Vídeo Generado", found_videos, format_func=lambda x: f"{x.parent.name} / {x.name}")
    if selected_video:
        st.video(str(selected_video))
        st.info(f"Ruta: {selected_video} | Tamaño: {selected_video.stat().st_size / (1024*1024):.2f} MB")
else:
    st.info("No se han encontrado archivos MP4 generados aún. Inicie una generación desde el Generador VideoPro o LTX-2.5 Studio.")
