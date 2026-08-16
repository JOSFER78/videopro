import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from webui.nav import render_top_navigation
import streamlit as st
import os
import glob

st.set_page_config(page_title="Boveda Multimedia — VideoPro", layout="wide")

# Barra de navegacion superior
render_top_navigation()

col_back, col_title = st.columns([1.5, 8.5], vertical_alignment="center")
with col_back:
    st.page_link("Main.py", label="← Volver al Inicio")
with col_title:
    st.title("Boveda Multimedia")
st.caption("Explorador y descarga de producciones renderizadas.")




task_dir = "/home/ubuntu/workspace/pro/hermes/10_videopro/storage/tasks"
os.makedirs(task_dir, exist_ok=True)

final_videos = glob.glob(f"{task_dir}/**/final-*.mp4", recursive=True)

if not final_videos:
    st.info("💡 Aún no se han renderizado vídeos en este estudio. Genera tu primer vídeo en el Generador Principal.")
else:
    st.subheader(f"🎬 Vídeos Renderizados ({len(final_videos)})")
    cols = st.columns(3)
    for idx, vid_path in enumerate(final_videos):
        with cols[idx % 3]:
            st.video(vid_path)
            st.caption(f"�� {os.path.basename(vid_path)}")
            with open(vid_path, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar MP4",
                    data=f,
                    file_name=os.path.basename(vid_path),
                    mime="video/mp4",
                    key=f"download_{idx}"
                )
