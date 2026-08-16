import os
from pathlib import Path
import streamlit as st

def render_view():
    st.title("Cinema Master Player")
    st.caption("Reproductor cinematográfico y verificador de pistas maestras con análisis técnico.")

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
        selected_video = st.selectbox("Seleccionar Vídeo Generado:", found_videos, format_func=lambda x: f"{x.parent.name} / {x.name}")
        if selected_video:
            st.video(str(selected_video))
            st.caption(f"Ruta: `{selected_video}` | Tamaño: {selected_video.stat().st_size / (1024*1024):.2f} MB")
            with open(selected_video, "rb") as vf:
                st.download_button(
                    "Descargar Vídeo MP4",
                    vf.read(),
                    file_name=selected_video.name,
                    mime="video/mp4",
                    use_container_width=True
                )
    else:
        st.info("No se han encontrado archivos MP4 generados aún. Inicia una producción desde el Generador Principal.")
