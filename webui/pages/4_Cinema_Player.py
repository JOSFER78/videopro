import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from webui.nav import render_top_navigation
import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="Cinema Master Player — VideoPro", layout="wide")

# Barra de navegacion superior
render_top_navigation()

col_back, col_title = st.columns([1.5, 8.5], vertical_alignment="center")
with col_back:
    st.page_link("Main.py", label="← Volver al Inicio")
with col_title:
    st.title("Cinema Master Player")
st.caption("Reproductor cinematografico y verificador de pistas maestras.")




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
