"""
Módulo de Gestión de Proyectos — VideoPro Studio (Modern DEV Architecture)
Single Source of Truth: Firebase Firestore & ProjectRepository.
Apertura instantánea en el Estudio, filtros dinámicos, trazabilidad y sincronización en la nube.
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from typing import List, Optional
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.services import firebase_sync
from app.core.services.project_repository import ProjectRepository
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG
from app.core.orchestration.repository import StudioRepository
from webui.views import view_studio_orchestrator


def invalidate_projects_cache():
    """Invalida la caché de proyectos en memoria para forzar un re-escaneo inmediato."""
    try:
        _get_cached_projects_summary.clear()
    except Exception:
        pass
    try:
        from app.core.services import project_repository
        project_repository._PROJECTS_SUMMARY_CACHE = []
        project_repository._PROJECTS_SUMMARY_LAST_FETCH = 0.0
    except Exception:
        pass


@st.cache_data(ttl=10, show_spinner=False)
def _get_cached_projects_summary() -> List[dict]:
    """Obtiene la lista indexada de proyectos desde disco con caché de alta velocidad."""
    repo = ProjectRepository()
    return repo.get_all_projects_summary()


def render_view():
    """Renderiza la galería y gestor de proyectos con estándar moderno DEV."""
    
    st.markdown("""
        <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="font-size: 24px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 10px;">
                        📁 Gestión de Proyectos
                        <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">LOCAL-FIRST</span>
                    </h2>
                    <p style="font-size: 13px; color: #94a3b8; margin: 2px 0 0 0;">
                        Biblioteca centralizada de producciones, guiones consolidados, trazabilidad de renderizado y sincronización en la nube.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Obtener proyectos
    projects = _get_cached_projects_summary()
    total_count = len(projects)
    completed_count = sum(1 for p in projects if p.get("has_video"))
    draft_count = total_count - completed_count
    cloud_synced_count = sum(1 for p in projects if p.get("cloud_synced") or p.get("cloud_url"))

    # 2. Barra de Métricas y Acciones Superiores
    m1, m2, m3, m4, m5 = st.columns([1.5, 1.5, 1.5, 1.5, 2.5], gap="small")
    with m1:
        st.metric("Total Proyectos", total_count)
    with m2:
        st.metric("Finalizados", f"🎬 {completed_count}")
    with m3:
        st.metric("En Guion / Borrador", f"📝 {draft_count}")
    with m4:
        st.metric("En Firestore / R2", f"☁️ {cloud_synced_count}")
    with m5:
        c_btn_new, c_btn_sync = st.columns([6, 4])
        with c_btn_new:
            if st.button("➕ Nuevo Proyecto", type="primary", use_container_width=True, help="Iniciar un nuevo proyecto con el Director Creativo"):
                st.session_state["active_view"] = "studio"
                st.session_state["director_messages"] = []
                st.session_state["current_project_id"] = None
                st.session_state["current_project_title"] = None
                st.session_state["current_archetype_plan"] = None
                st.session_state["director_spec"] = None
                st.session_state["flash_message"] = ("info", "Nuevo proyecto inicializado. ¡Comienza a co-crear!")
                st.rerun()
        with c_btn_sync:
            if st.button("🔄 Refrescar", use_container_width=True, help="Sincronizar proyectos"):
                invalidate_projects_cache()
                st.session_state["flash_message"] = ("info", "Catálogo de proyectos actualizado.")
                st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # 3. Buscador y Filtros
    c_search, c_filter_wf, c_filter_stat = st.columns([5, 3, 2], gap="medium")
    with c_search:
        search_query = st.text_input(
            "Buscar:",
            placeholder="🔍 Buscar por título, personajes, temática o ID...",
            label_visibility="collapsed",
            key="input_proj_search"
        )
    with c_filter_wf:
        wf_options = ["ALL"] + list(ARCHETYPES_CATALOG.keys())
        selected_wf_filter = st.selectbox(
            "Filtrar por Workflow:",
            options=wf_options,
            format_func=lambda x: "🌐 Todos los Workflows" if x == "ALL" else f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name}",
            label_visibility="collapsed",
            key="sel_proj_wf_filter"
        )
    with c_filter_stat:
        status_options = ["ALL", "COMPLETED", "DRAFT"]
        status_labels = {"ALL": "📊 Todos los Estados", "COMPLETED": "🎬 Finalizados", "DRAFT": "📝 En Edición"}
        selected_status_filter = st.selectbox(
            "Filtrar por Estado:",
            options=status_options,
            format_func=lambda x: status_labels.get(x, x),
            label_visibility="collapsed",
            key="sel_proj_status_filter"
        )

    # 4. Filtrar Proyectos
    filtered = list(projects)
    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [
            p for p in filtered
            if q in p.get("title", "").lower()
            or q in p.get("subject", "").lower()
            or q in p.get("project_id", "").lower()
            or q in json.dumps(p.get("director_spec", {})).lower()
        ]
    if selected_wf_filter != "ALL":
        filtered = [p for p in filtered if p.get("workflow_id") == selected_wf_filter]
    if selected_status_filter == "COMPLETED":
        filtered = [p for p in filtered if p.get("has_video")]
    elif selected_status_filter == "DRAFT":
        filtered = [p for p in filtered if not p.get("has_video")]

    # 5. Monitor de Jobs en Vivo y Lista de Proyectos
    tab_projects, tab_live_monitor = st.tabs([
        f"📋 Catálogo de Proyectos ({len(filtered)})",
        "⚡ Monitor de Render en Vivo"
    ])

    with tab_projects:
        if not filtered:
            st.info("💡 No se encontraron proyectos que coincidan con los filtros seleccionados.")
            return

        # Renderizado en Grid de 2 Columnas (Estilo DEV Moderno)
        col_left, col_right = st.columns(2, gap="medium")
        
        for idx, proj in enumerate(filtered):
            target_col = col_left if idx % 2 == 0 else col_right
            with target_col:
                _render_project_card(proj)

    with tab_live_monitor:
        _render_live_jobs_monitor()


@st.dialog("🗑️ Confirmar Eliminación")
def _show_delete_modal(project_id: str, title: str):
    """Modal nativo centrado para confirmar el borrado sin deformar la interfaz."""
    st.markdown(f"¿Estás seguro de que deseas eliminar permanentemente este proyecto?")
    st.markdown(f"🎬 **{title}** (`{project_id}`)")
    st.caption("Esta acción eliminará todos los archivos locales en la VPS y metadatos.")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        if st.button("❌ Cancelar", use_container_width=True, key=f"btn_cancel_del_{project_id}"):
            st.rerun()
    with c2:
        if st.button("🗑️ Sí, Eliminar", type="primary", use_container_width=True, key=f"btn_do_del_{project_id}"):
            repo = ProjectRepository()
            repo.delete_project(project_id)
            invalidate_projects_cache()
            st.session_state["flash_message"] = ("success", f"Proyecto '{title}' eliminado correctamente.")
            st.rerun()


@st.dialog("🎬 Previsualización de Vídeo")
def _show_video_modal(title: str, local_vid: str, cloud_url: str):
    """Modal nativo para previsualizar vídeos terminados."""
    st.markdown(f"#### 🎥 {title}")
    if local_vid and os.path.exists(local_vid):
        st.video(local_vid)
    elif cloud_url:
        st.video(cloud_url)
    else:
        st.warning("No se encontró el archivo de vídeo.")


def _render_project_card(proj: dict):
    """Renderiza una tarjeta de proyecto moderna con acciones y estado relacional."""
    p_id = proj.get("project_id", "proj_unknown")
    title = proj.get("title") or proj.get("subject", p_id)
    wf_id = proj.get("workflow_id", "PIXAR_3D_ANIMATION")
    arch = ARCHETYPES_CATALOG.get(wf_id)
    wf_name = arch.name if arch else proj.get("workflow_name", "Producción Cinemática")
    wf_icon = arch.icon if arch else proj.get("workflow_icon", "🎬")
    
    has_video = proj.get("has_video", False)
    local_vid = proj.get("local_video_path", "")
    cloud_url = proj.get("cloud_url", "")
    scenes_cnt = proj.get("scenes_count", len(proj.get("scenes", [])))
    aspect = proj.get("aspect_ratio", "16:9")
    voice_id = proj.get("voice_id", "vibevoice")
    
    # Formatear fecha
    upd_raw = proj.get("updated_at")
    upd_str = "Reciente"
    if isinstance(upd_raw, (int, float)):
        upd_str = datetime.fromtimestamp(upd_raw).strftime("%d/%m/%Y %H:%M")
    elif isinstance(upd_raw, str) and len(upd_raw) >= 10:
        try:
            upd_str = datetime.fromisoformat(upd_raw.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
        except Exception:
            upd_str = upd_raw[:16]

    spec = proj.get("director_spec", {})
    premise = spec.get("subject", proj.get("subject", ""))
    chars = spec.get("characters", "")

    status_badge = "🟢 FINALIZADO" if has_video else ("🟡 LISTO PARA RODAR" if scenes_cnt > 0 else "⚪ EN DEFINICIÓN")
    status_color = "#34d399" if has_video else ("#38bdf8" if scenes_cnt > 0 else "#94a3b8")

    with st.container(border=True):
        # Cabecera de la Tarjeta
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                <div style="font-size:11px; font-weight:700; color:#38bdf8; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.25); padding:2px 8px; border-radius:12px;">
                    {wf_icon} {wf_name}
                </div>
                <div style="font-size:11px; font-weight:700; color:{status_color};">
                    {status_badge}
                </div>
            </div>
            <div style="font-size:15px; font-weight:800; color:#f8fafc; margin-bottom:4px; line-height:1.3;">
                {title}
            </div>
            <div style="font-size:11px; font-family:monospace; color:#38bdf8; background:rgba(15,23,42,0.8); padding:2px 6px; border-radius:4px; margin-bottom:6px; display:inline-block; border:1px solid #1e293b;">
                📁 {proj.get('rel_path', p_id)}
            </div>
        """, unsafe_allow_html=True)

        if premise and premise != title:
            st.caption(f"📌 **Premisa:** {premise[:75]}...")
        if chars:
            st.caption(f"🧸 **Personajes:** {chars[:65]}...")

        # Metadatos Técnicos
        st.markdown(f"""
            <div style="display:flex; gap:12px; font-size:11.5px; color:#94a3b8; background:rgba(15,23,42,0.6); padding:6px 10px; border-radius:6px; border:1px solid #334155; margin:6px 0 10px 0;">
                <div>🎬 <b>{scenes_cnt}</b> tomas</div>
                <div>📐 <b>{aspect}</b></div>
                <div>🎙️ <b>{voice_id}</b></div>
                <div>🕒 <b>{upd_str}</b></div>
            </div>
        """, unsafe_allow_html=True)

        # Botones de Acción
        c_act1, c_act2, c_act3 = st.columns([5, 3, 2], gap="small")
        with c_act1:
            if st.button("📂 Abrir en Estudio", key=f"btn_open_studio_{p_id}", type="primary", use_container_width=True, help="Abrir proyecto en el Director Creativo"):
                with st.spinner("Cargando proyecto y restaurando sesión..."):
                    ok = view_studio_orchestrator.load_project_into_session(p_id)
                    if ok:
                        st.session_state["flash_message"] = ("info", f"Proyecto '{title}' cargado en el Estudio.")
                        st.session_state["active_view"] = "studio"
                        st.rerun()
                    else:
                        st.error(f"No se pudo cargar el proyecto {p_id}")
        with c_act2:
            if has_video:
                b_vid, b_r2 = st.columns(2, gap="small")
                with b_vid:
                    if st.button("🎬 Ver", key=f"btn_view_vid_{p_id}", use_container_width=True, help="Reproducir vídeo renderizado"):
                        _show_video_modal(title, local_vid, cloud_url)
                with b_r2:
                    if not proj.get("cloud_synced"):
                        if st.button("☁️ R2", key=f"btn_r2_{p_id}", use_container_width=True, help="Subir a Cloudflare R2"):
                            with st.spinner("Subiendo vídeo a Cloudflare R2..."):
                                try:
                                    from app.services.storage.factory import StorageFactory
                                    srv = StorageFactory.get_storage_service()
                                    if srv and local_vid and os.path.isfile(local_vid):
                                        key = f"projects/{p_id}/{os.path.basename(local_vid)}"
                                        remote_key = srv.upload_file(local_vid, key)
                                        url = srv.get_presigned_url(remote_key)
                                        proj["cloud_synced"] = True
                                        proj["cloud_url"] = url
                                        r2_marker = os.path.join(os.path.dirname(local_vid), ".r2_synced.json")
                                        with open(r2_marker, "w") as f:
                                            json.dump({"synced": True, "remote_key": remote_key, "presigned_url": url}, f)
                                        firebase_sync.backup_project_to_firebase_async(proj)
                                        invalidate_projects_cache()
                                        st.session_state["flash_message"] = ("success", f"Vídeo de '{title}' subido con éxito a Cloudflare R2.")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
            else:
                if st.button("📋 Duplicar", key=f"btn_dup_{p_id}", use_container_width=True, help="Duplicar proyecto (Fork)"):
                    new_pid = f"{p_id}_copia_{int(time.time())}"
                    new_title = f"{title} (Copia)"
                    repo = ProjectRepository()
                    proj_copy = dict(proj)
                    proj_copy["project_id"] = new_pid
                    proj_copy["task_id"] = new_pid
                    proj_copy["title"] = new_title
                    
                    # Guardar copia en disco local
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    target_dir = os.path.join(base_dir, "storage", "projects", new_pid)
                    os.makedirs(target_dir, exist_ok=True)
                    with open(os.path.join(target_dir, "project.json"), "w", encoding="utf-8") as f:
                        json.dump(proj_copy, f, indent=2, ensure_ascii=False)
                    
                    firebase_sync.backup_project_to_firebase_async(proj_copy)
                    invalidate_projects_cache()
                    st.session_state["flash_message"] = ("success", f"Proyecto duplicado como: {new_title}")
                    st.rerun()
        with c_act3:
            if st.button("🗑️", key=f"btn_del_trigger_{p_id}", use_container_width=True, help="Eliminar este proyecto"):
                _show_delete_modal(p_id, title)


def _render_live_jobs_monitor():
    """Renderiza el monitor de trazabilidad de jobs de renderizado en vivo."""
    st.markdown("##### ⚡ Monitor de Producción Cinemática en Tiempo Real")
    st.caption("Seguimiento detallado de jobs de renderizado, fase semántica actual, trazabilidad y carpetas del proyecto.")
    
    studio_repo = StudioRepository()
    try:
        active_jobs = studio_repo.list_active_jobs()
    except Exception:
        try:
            active_jobs = studio_repo.list_jobs(limit=10)
        except Exception:
            active_jobs = []
    
    if not active_jobs:
        st.info("💡 No hay ningún job de renderizado ejecutándose en este momento.")
        return

    for j in active_jobs:
        j_id = j.get("job_id", "job_unknown")
        j_proj = j.get("project_id", "")
        j_status = j.get("status", "pending")
        j_dur = j.get("duration_seconds", 0.0)
        j_steps = j.get("steps", [])

        with st.container(border=True):
            st.markdown(f"**Job ID:** `{j_id}` | **Proyecto:** `{j_proj}` | **Estado:** `{j_status}` | **Duración:** `{j_dur:.2f}s`")
            for stp in j_steps:
                st.markdown(f"• ✅ **{stp.get('step_id')}** — `{stp.get('status', 'ok')}` ({stp.get('duration_seconds', 0):.2f}s)")
