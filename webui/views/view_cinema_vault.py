import os
import sys
import glob
from datetime import datetime
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.utils import utils

def render_view():
    tab_player, tab_vault = st.tabs([
        "Cinema Master Player",
        "Bóveda Multimedia"
    ])

    tasks_dir = utils.task_dir() if hasattr(utils, "task_dir") else os.path.join(BASE_DIR, "storage", "tasks")
    
    video_files = []
    if os.path.exists(tasks_dir):
        for ext in ("*.mp4", "*.mkv", "*.mov"):
            video_files.extend(glob.glob(os.path.join(tasks_dir, "**", ext), recursive=True))

    video_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    with tab_player:
        if not video_files:
            st.info("No se encontraron vídeos renderizados.")
        else:
            selected_video = st.selectbox(
                "Seleccionar Producción:",
                options=video_files,
                format_func=lambda x: f"{os.path.basename(os.path.dirname(x))} - {os.path.basename(x)}"
            )

            if selected_video and os.path.exists(selected_video):
                v_size_mb = round(os.path.getsize(selected_video) / (1024 * 1024), 2)
                st.video(selected_video)
                c_i1, c_i2 = st.columns([3, 1])
                with c_i1:
                    st.caption(f"Ruta: `{selected_video}` | Tamaño: **{v_size_mb} MB**")
                with c_i2:
                    with open(selected_video, "rb") as vf:
                        st.download_button("Descargar MP4", data=vf.read(), file_name=os.path.basename(selected_video), mime="video/mp4", use_container_width=True)

    with tab_vault:
        if not video_files:
            st.info("Bóveda vacía.")
        else:
            st.caption(f"Total producciones: {len(video_files)}")
            for vf in video_files:
                with st.container(border=True):
                    c_meta, c_btn = st.columns([3.5, 1.5])
                    with c_meta:
                        t_name = os.path.basename(os.path.dirname(vf))
                        f_name = os.path.basename(vf)
                        f_size = round(os.path.getsize(vf) / (1024 * 1024), 2)
                        st.markdown(f"**{t_name}** - `{f_name}` ({f_size} MB)")
                    with c_btn:
                        with open(vf, "rb") as f_data:
                            st.download_button("Descargar", data=f_data.read(), file_name=f_name, mime="video/mp4", key=f"vault_{t_name}_{f_name}", use_container_width=True)
