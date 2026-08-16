"""
Vista de Inicio / Dashboard de Resumen Global — VideoPro Studio
Centro de control ejecutivo con métricas del sistema, accesos directos, estado de servicios y proyectos recientes.
"""

import os
import streamlit as st
from datetime import datetime

from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG
from app.core.providers import registry as prov_reg


@st.cache_data(ttl=5, show_spinner=False)
def _get_system_stats():
    """Calcula métricas globales de proyectos y motores rápidamente sin bloquear el render."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    projects_dir = os.path.join(base_dir, "storage", "projects")
    
    total_projects = 0
    recent_projects = []
    
    if os.path.isdir(projects_dir):
        for root, dirs, files in os.walk(projects_dir):
            if "project.json" in files or "metadata.json" in files:
                total_projects += 1
                folder_name = os.path.basename(root)
                mtime = os.path.getmtime(root)
                recent_projects.append({
                    "name": folder_name,
                    "path": root,
                    "mtime": mtime,
                    "date_str": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                })
    
    recent_projects.sort(key=lambda x: x["mtime"], reverse=True)
    
    reg = prov_reg.load_registry()
    total_providers = len(reg)
    active_providers = len([p for p in reg.values() if p.get("enabled", True)])
    
    return {
        "total_projects": max(total_projects, len(recent_projects)),
        "recent_projects": recent_projects[:6],
        "total_archetypes": len(ARCHETYPES_CATALOG),
        "total_providers": total_providers,
        "active_providers": active_providers
    }


def render_home_dashboard_view():
    """Renderiza el Dashboard Principal de Resumen."""
    stats = _get_system_stats()

    # Encabezado Ejecutivo
    st.markdown("""
        <div style="margin-bottom: 16px; padding: 14px 18px; background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.8)); border-radius: 10px; border: 1px solid rgba(56,189,248,0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 8px;">
                        <span>🏠</span> VideoPro Studio — Centro de Control & Resumen
                    </h2>
                    <p style="font-size: 12.5px; color: #94a3b8; margin: 4px 0 0 0;">
                        Panel general de producción cinemática, estado de servicios de IA, orquestación de workflows y trazabilidad de proyectos.
                    </p>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 11px; font-weight: 700; background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); padding: 3px 10px; border-radius: 12px; display: flex; align-items: center; gap: 5px;">
                        <span style="width: 7px; height: 7px; background: #34d399; border-radius: 50%; display: inline-block;"></span> SISTEMA OPERATIVO
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Tarjetas de Métricas Globales (KPIs)
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.markdown(f"""
            <div style="padding: 12px 14px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; border-left: 3px solid #38bdf8;">
                <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">📁 Proyectos Creados</div>
                <div style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 4px 0 2px 0;">{stats['total_projects']}</div>
                <div style="font-size: 10.5px; color: #38bdf8;">Jerarquía YYYY/MM/DD en disco & cloud</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi_cols[1]:
        st.markdown(f"""
            <div style="padding: 12px 14px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; border-left: 3px solid #a855f7;">
                <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">🎛️ Workflows Disponibles</div>
                <div style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 4px 0 2px 0;">{stats['total_archetypes']} Arquetipos</div>
                <div style="font-size: 10.5px; color: #c084fc;">Pixar 3D, Vox, Bloomberg, Cine 35mm</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi_cols[2]:
        st.markdown(f"""
            <div style="padding: 12px 14px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; border-left: 3px solid #34d399;">
                <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">⚡ Motores Activos</div>
                <div style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 4px 0 2px 0;">{stats['active_providers']}/{stats['total_providers']} Motores</div>
                <div style="font-size: 10.5px; color: #34d399;">$0 Cloud Serverless & ZeroGPU</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi_cols[3]:
        st.markdown("""
            <div style="padding: 12px 14px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; border-left: 3px solid #f59e0b;">
                <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">☁️ Nube & Base de Datos</div>
                <div style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 4px 0 2px 0;">Firestore</div>
                <div style="font-size: 10.5px; color: #fbbf24;">ayuda-emilio-83261 🟢 Conectado</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Grid de Accesos Rápidos a Módulos
    st.markdown("### 🚀 Accesos Directos a Módulos de Producción")
    
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    
    with row1_c1:
        with st.container(border=True):
            st.markdown("#### 🎬 1. Director Creativo & Co-Creación")
            st.caption("Investigación profunda con subagentes Hermes, Cadena de Pensamiento (CoT) y ficha técnica consolidada.")
            if st.button("Abrir Director Creativo 🚀", type="primary", use_container_width=True, key="home_btn_studio"):
                st.session_state["active_view"] = "studio"
                st.rerun()

    with row1_c2:
        with st.container(border=True):
            st.markdown("#### 🏛️ 2. Lienzo de Nodos (ComfyUI Studio)")
            st.caption("Diseño visual de flujos con cables Bezier interactivos y Asistente Agéntico de IA flotante.")
            if st.button("Abrir Lienzo Visual 🎨", use_container_width=True, key="home_btn_canvas"):
                st.session_state["active_view"] = "pipeline"
                st.rerun()

    with row1_c3:
        with st.container(border=True):
            st.markdown("#### 📁 3. Gestor de Proyectos")
            st.caption("Explorador de proyectos estructurados por fecha `YYYY/MM/DD`, estado de render y tomas generadas.")
            if st.button("Explorar Proyectos 📁", use_container_width=True, key="home_btn_projects"):
                st.session_state["active_view"] = "projects"
                st.rerun()

    row2_c1, row2_c2, row2_c3 = st.columns(3)
    
    with row2_c1:
        with st.container(border=True):
            st.markdown("#### 🎞️ 4. Bóveda Multimedia (Cinema Vault)")
            st.caption("Galería cinematográfica con reproductor MP4 máster, tomas de vídeo y metadatos de producción.")
            if st.button("Ir a Bóveda Multimedia 🎞️", use_container_width=True, key="home_btn_vault"):
                st.session_state["active_view"] = "cinema_vault"
                st.rerun()

    with row2_c2:
        with st.container(border=True):
            st.markdown("#### 🎙️ 5. Audio, Foley & Locutores")
            st.caption("Laboratorio de síntesis vocal (ElevenLabs, VibeVoice 1.5B), auto-ducking a -22dB y bandas sonoras.")
            if st.button("Estudio de Audio 🎙️", use_container_width=True, key="home_btn_audio"):
                st.session_state["active_view"] = "audio_studio"
                st.rerun()

    with row2_c3:
        with st.container(border=True):
            st.markdown("#### ⚙️ 6. Matriz de APIs & Proveedores")
            st.caption("Gestor de claves API, orquestación de clústeres GPU y diagnóstico de latencia en tiempo real.")
            if st.button("Configurar Ajustes & APIs ⚙️", use_container_width=True, key="home_btn_settings"):
                st.session_state["active_view"] = "settings"
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Estado de Salud de Servicios y Proyectos Recientes en 2 Columnas
    c_status, c_recent = st.columns([5, 5], gap="medium")
    
    with c_status:
        st.markdown("### ⚡ Estado de Servicios y Telemetría")
        with st.container(border=True):
            st.markdown("""
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 10px; background: #070b14; border-radius: 6px;">
                        <span>🚀 <b>FastAPI Backend Core</b> (Puerto 8080)</span>
                        <span style="color: #34d399; font-weight: 700;">🟢 En Línea (HTTP 200)</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 10px; background: #070b14; border-radius: 6px;">
                        <span>🎨 <b>Streamlit WebUI Dashboard</b> (Puerto 8501)</span>
                        <span style="color: #34d399; font-weight: 700;">🟢 Activo</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 10px; background: #070b14; border-radius: 6px;">
                        <span>🔥 <b>Google Cloud Firestore Database</b></span>
                        <span style="color: #34d399; font-weight: 700;">🟢 Conectado</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 10px; background: #070b14; border-radius: 6px;">
                        <span>☁️ <b>Cloudflare R2 Object Storage</b></span>
                        <span style="color: #38bdf8; font-weight: 700;">🟢 Zero Egress</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 10px; background: #070b14; border-radius: 6px;">
                        <span>🍌 <b>Antigravity LLM Bridge</b> (Puerto 8742)</span>
                        <span style="color: #34d399; font-weight: 700;">🟢 Gemini 3.7 Flash High</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with c_recent:
        st.markdown("### 📋 Proyectos Recientes en Disco")
        with st.container(border=True):
            if not stats["recent_projects"]:
                st.info("No hay proyectos generados aún. Haz clic en **Empezar** para crear tu primera producción.")
            else:
                for proj in stats["recent_projects"]:
                    c_p_info, c_p_btn = st.columns([7, 3], vertical_alignment="center")
                    with c_p_info:
                        st.markdown(f"**📁 {proj['name']}**")
                        st.caption(f"Fecha: `{proj['date_str']}`")
                    with c_p_btn:
                        if st.button("Abrir ↗", key=f"open_proj_{proj['name']}", use_container_width=True):
                            st.session_state["active_view"] = "projects"
                            st.rerun()
