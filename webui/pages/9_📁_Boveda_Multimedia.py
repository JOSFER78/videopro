import streamlit as st
import os
import glob

st.set_page_config(page_title="Bóveda Multimedia — VideoPro", page_icon="📁", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(56, 189, 248, 0.15)); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
    <h1 style="font-size: 26px; font-weight: 800; color: #fff; margin: 0 0 8px 0;">📁 Bóveda Multimedia & Historial de Producción</h1>
    <p style="color: #94a3b8; margin: 0; font-size: 14px;">Explora, previsualiza y descarga los vídeos finales, pistas de audio, locuciones y escenas generadas.</p>
</div>
""", unsafe_allow_html=True)

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
