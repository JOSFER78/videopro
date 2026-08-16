import os
import glob
import streamlit as st

def render_view():
    st.title("Bóveda Multimedia")
    st.caption("Explorador y descarga de producciones audiovisuales renderizadas.")

    task_dir = "/home/ubuntu/workspace/pro/hermes/10_videopro/storage/tasks"
    os.makedirs(task_dir, exist_ok=True)

    final_videos = glob.glob(f"{task_dir}/**/final-*.mp4", recursive=True)

    if not final_videos:
        st.info("Aún no se han renderizado vídeos en este estudio. Genera tu primer vídeo en el Generador Principal.")
    else:
        st.subheader(f"Vídeos Renderizados ({len(final_videos)})")
        cols = st.columns(3)
        for idx, vid_path in enumerate(final_videos):
            with cols[idx % 3]:
                st.video(vid_path)
                st.caption(f"`{os.path.basename(vid_path)}`")
                with open(vid_path, "rb") as f:
                    st.download_button(
                        label="Descargar MP4",
                        data=f,
                        file_name=os.path.basename(vid_path),
                        mime="video/mp4",
                        key=f"download_{idx}"
                    )
