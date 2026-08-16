"""
view_cinema_vault.py
Bóveda Multimedia & Master Cinema Player — VideoPro Studio
- Indexa vídeos máster 4K renderizados en storage/projects/
- Organiza los 72 activos descargados por Hermes (vídeos 4K e imágenes de archivo por cotas)
- Muestra tiras de fotogramas y mosaicos de control de calidad (Contact Sheets).
"""

import os
import sys
import glob
from pathlib import Path
from datetime import datetime
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.services import firebase_sync

def render_view():
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 8px;">
                🎞️ Bóveda Multimedia & Master Cinema Player
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">72 ACTIVOS CLASIFICADOS</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 2px 0 0 0;">
                Catálogo de metraje 4K, fotografías de archivo histórico por cotas de profundidad y reproductores máster.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_player, tab_media_by_depth, tab_qa_contact_sheets = st.tabs([
        "🎬 Reproductor Master 4K",
        "📂 Activos por Cotas de Profundidad (Hermes)",
        "📸 Mosaicos QA & Contact Sheets"
    ])

    projects_base = Path(BASE_DIR) / "storage" / "projects"
    master_videos = sorted(list(projects_base.glob("**/renders/*.mp4")) + list(projects_base.glob("**/*.mp4")), key=lambda p: p.stat().st_mtime, reverse=True)

    with tab_player:
        if not master_videos:
            st.info("No se encontraron vídeos máster renderizados en `storage/projects/`.")
        else:
            selected_video = st.selectbox(
                "Seleccionar Producción Máster:",
                options=[str(v) for v in master_videos],
                format_func=lambda x: f"🎬 {Path(x).parent.parent.name} / {Path(x).name} ({Path(x).stat().st_size / (1024*1024):.1f} MB)"
            )

            if selected_video and os.path.exists(selected_video):
                v_path = Path(selected_video)
                v_size_mb = round(v_path.stat().st_size / (1024 * 1024), 2)
                st.video(str(v_path))
                
                c_i1, c_i2 = st.columns([3, 1])
                with c_i1:
                    st.caption(f"📁 Ruta: `{v_path.relative_to(Path(BASE_DIR))}` | Tamaño: **{v_size_mb} MB**")
                with c_i2:
                    with open(str(v_path), "rb") as vf:
                        st.download_button("⬇️ Descargar Master 4K", data=vf.read(), file_name=v_path.name, mime="video/mp4", use_container_width=True)

    with tab_media_by_depth:
        st.markdown("##### 🏛️ Activos Clasificados por Cota de Descenso Subterráneo")
        st.caption("Metraje real 4K y fotos de archivo histórico organizadas por el agente Hermes.")

        depth_levels = [
            ("0m", "0m: Superficie (Gran Vía y Cibeles)"),
            ("neg5m", "-5m: Qanats Musulmanes de Mayrit (854)"),
            ("neg10m", "-10m: Pasadizo Secreto de Felipe III (1611)"),
            ("neg15m", "-15m: Metro Chamberí 1919 & Cripta"),
            ("neg20m", "-20m: Búnker Militar Posición Jaca (1937)"),
            ("neg35m", "-35m: Cámara Acorazada del Oro (Cibeles)")
        ]

        # Buscar proyecto estructurado más reciente con media/
        media_dirs = list(projects_base.glob("**/media"))
        if media_dirs:
            active_media_dir = media_dirs[0]
            for d_key, d_title in depth_levels:
                lvl_dir = active_media_dir / d_key
                vids = list((lvl_dir / "videos").glob("*.mp4")) if lvl_dir.exists() else []
                imgs = list((lvl_dir / "images").glob("*.jpg")) if lvl_dir.exists() else []
                
                with st.expander(f"🧱 Cota **{d_title}** — ({len(vids)} vídeos 4K, {len(imgs)} fotos)", expanded=(d_key == "0m")):
                    c_v, c_p = st.columns(2, gap="medium")
                    with c_v:
                        st.markdown("**📹 Vídeos 4K en Movimiento:**")
                        for v in vids:
                            st.caption(f"• `{v.name}` ({v.stat().st_size / (1024*1024):.2f} MB)")
                    with c_p:
                        st.markdown("**📸 Fotografías & Planos de Archivo:**")
                        for im in imgs:
                            st.caption(f"• `{im.name}` ({im.stat().st_size / 1024:.1f} KB)")
        else:
            st.info("No se han encontrado carpetas de medios clasificados aún.")

    with tab_qa_contact_sheets:
        st.markdown("##### 📸 Tiras de Fotogramas de Control de Calidad (Contact Sheets)")
        st.caption("Verificación visual de no-repetición y balance de color.")
        
        contact_sheets = list(projects_base.glob("**/*contact_sheet*.jpg")) + list(Path("/home/ubuntu/.gemini/antigravity-ide/brain/753522d0-fb23-452a-befd-d7a33b3b3415").glob("*mosaic*.jpg"))
        if contact_sheets:
            for cs in contact_sheets:
                with st.container(border=True):
                    st.markdown(f"**Tira de Fotogramas:** `{cs.name}`")
                    st.image(str(cs), use_column_width=True)
        else:
            st.info("No hay mosaicos de control de calidad generados.")
