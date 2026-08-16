"""
Módulo de Gestión de Proyectos Organizados por Año / Mes / Día / Nombre — VideoPro Studio
Jerarquía cronológica estricta en disco: storage/tasks/YYYY/MM/DD/YYYY-MM-DD_nombre/
y sincronización Cloud Storage (Cloudflare R2 / S3 / Firestore).
"""

import os
import sys
import json
import time
import shutil
import glob
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.utils import utils
from app.services.storage.factory import StorageFactory
from app.services.storage.r2 import CloudflareR2StorageService
from app.models import const
from app.services import state as sm
from app.services import task as tm


MONTH_NAMES = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}


def _get_tasks_dir():
    if hasattr(utils, "task_dir"):
        return os.path.abspath(utils.task_dir())
    return os.path.abspath(os.path.join(BASE_DIR, "storage", "tasks"))


def _is_cloud_storage_configured():
    s3_ep = config.app.get("s3_endpoint", "")
    s3_acc = config.app.get("s3_access_key", "")
    s3_sec = config.app.get("s3_secret_key", "")
    s3_bkt = config.app.get("s3_bucket", "")
    return bool(s3_ep and s3_acc and s3_sec and s3_bkt)


def _scan_project_folder(task_path, tasks_root):
    """Analiza una carpeta de proyecto individual y extrae año, mes, día, nombre y metadatos."""
    if not os.path.isdir(task_path):
        return None

    folder_name = os.path.basename(task_path)
    rel_path = os.path.relpath(task_path, tasks_root)
    mtime = os.path.getmtime(task_path)

    # Buscar si tiene script.json
    script_file = os.path.join(task_path, "script.json")
    script_data = {}
    if os.path.isfile(script_file):
        try:
            with open(script_file, "r", encoding="utf-8") as f:
                script_data = json.load(f)
            mtime = max(mtime, os.path.getmtime(script_file))
        except Exception:
            pass

    # Cargar estado desde sm.state si existe
    task_state_record = {}
    try:
        task_state_record = sm.state.get_task(folder_name) or sm.state.get_task(rel_path) or {}
    except Exception:
        task_state_record = {}

    state_code = task_state_record.get("state", const.TASK_STATE_COMPLETE)
    progress = int(task_state_record.get("progress", 100 if state_code == const.TASK_STATE_COMPLETE else 0))

    params = script_data.get("params", {})
    subject = (
        params.get("video_subject")
        or task_state_record.get("subject")
        or script_data.get("script", "")[:50]
        or folder_name
    )
    script_text = script_data.get("script", "")

    # Buscar vídeos finales
    video_files = []
    for ext in ("*.mp4", "*.mkv", "*.mov", "*.webm"):
        video_files.extend(glob.glob(os.path.join(task_path, ext)))
        video_files.extend(glob.glob(os.path.join(task_path, "final-*", ext)))
    
    final_video = ""
    if video_files:
        video_files.sort(key=lambda x: os.path.getsize(x) if os.path.isfile(x) else 0, reverse=True)
        final_video = video_files[0]
        mtime = max(mtime, os.path.getmtime(final_video))

    has_video = bool(final_video and os.path.isfile(final_video) and os.path.getsize(final_video) > 1024)

    if has_video and state_code != const.TASK_STATE_FAILED:
        state_code = const.TASK_STATE_COMPLETE
        progress = 100

    r2_marker_file = os.path.join(task_path, ".r2_synced.json")
    cloud_info = {}
    if os.path.isfile(r2_marker_file):
        try:
            with open(r2_marker_file, "r", encoding="utf-8") as f:
                cloud_info = json.load(f)
        except Exception:
            cloud_info = {}

    # Desglosar fecha Año / Mes / Día
    dt = datetime.fromtimestamp(mtime)
    
    # Intentar parsear fecha desde la ruta si está estructurada como YYYY/MM/DD
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) >= 4 and len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
        year = parts[0]
        month = parts[1]
        day = parts[2]
    else:
        year = dt.strftime("%Y")
        month = dt.strftime("%m")
        day = dt.strftime("%d")

    month_label = MONTH_NAMES.get(month, month)
    date_formatted = f"{day}/{month}/{year}"

    return {
        "task_id": folder_name,
        "rel_path": rel_path,
        "task_path": task_path,
        "subject": subject,
        "script": script_text,
        "params": params,
        "final_video": final_video,
        "has_video": has_video,
        "mtime": mtime,
        "datetime": dt,
        "year": year,
        "month": month,
        "month_label": month_label,
        "day": day,
        "date_formatted": date_formatted,
        "state": state_code,
        "progress": progress,
        "cloud_synced": bool(cloud_info.get("synced")),
        "cloud_key": cloud_info.get("remote_key", ""),
        "cloud_url": cloud_info.get("presigned_url", "")
    }


def _collect_all_projects():
    """Escanea el árbol completo de storage/tasks en busca de proyectos (Año/Mes/Día/Nombre)."""
    tasks_root = _get_tasks_dir()
    os.makedirs(tasks_root, exist_ok=True)
    projects = []
    seen_paths = set()

    for root, dirs, files in os.walk(tasks_root):
        # Evitar carpetas de sistema o temporales
        if os.path.basename(root).startswith("."):
            continue

        is_project_dir = "script.json" in files or any(f.endswith((".mp4", ".mov", ".mkv")) for f in files)
        is_leaf_task = bool(dirs == [] and root != tasks_root)

        if is_project_dir or is_leaf_task:
            if root not in seen_paths and root != tasks_root:
                proj = _scan_project_folder(root, tasks_root)
                if proj:
                    projects.append(proj)
                    seen_paths.add(root)

    projects.sort(key=lambda p: p["mtime"], reverse=True)
    return projects


def _upload_project_to_cloud(project):
    """Sube el render y metadata del proyecto a Cloudflare R2 / S3 respetando la jerarquía Año/Mes/Día/Nombre."""
    try:
        storage_service = StorageFactory.get_storage_service(force_reload=True)
        if not isinstance(storage_service, CloudflareR2StorageService):
            return False, "Cloud Storage no está configurado como R2/S3. Ajusta las claves en Ajustes."

        # Jerarquía remota: projects/YYYY/MM/DD/nombre_proyecto/
        remote_prefix = f"projects/{project['year']}/{project['month']}/{project['day']}/{project['task_id']}"

        remote_video_key = ""
        if project["has_video"]:
            video_name = os.path.basename(project["final_video"])
            target_key = f"{remote_prefix}/{video_name}"
            remote_video_key = storage_service.upload_file(project["final_video"], target_key)

        script_file = os.path.join(project["task_path"], "script.json")
        if os.path.isfile(script_file):
            storage_service.upload_file(script_file, f"{remote_prefix}/script.json")

        presigned_url = ""
        if remote_video_key:
            presigned_url = storage_service.get_presigned_url(remote_video_key, expiration_seconds=86400 * 7)

        # Guardar marcador local
        r2_marker = {
            "synced": True,
            "synced_at": datetime.now().isoformat(),
            "remote_key": remote_video_key,
            "presigned_url": presigned_url,
            "cloud_path": remote_prefix
        }
        with open(os.path.join(project["task_path"], ".r2_synced.json"), "w", encoding="utf-8") as f:
            json.dump(r2_marker, f)

        # Sincronizar con Firebase Firestore
        try:
            from app.services import firebase_sync
            project_copy = dict(project)
            project_copy["cloud_synced"] = True
            project_copy["cloud_url"] = presigned_url
            project_copy["cloud_path"] = remote_prefix
            firebase_sync.backup_project_to_firebase(project_copy)
        except Exception:
            pass

        return True, "Subido a Cloud Storage y respaldado en Firebase Firestore."
    except Exception as ex:
        return False, f"Error al subir a Cloud Storage: {ex}"


def render_view():
    st.markdown("""
    <div style='display:flex; justify-content:space-between; align-items:center; padding: 4px 0 8px 0; border-bottom: 1px solid #1e293b; margin-bottom: 12px;'>
        <div>
            <span style='font-size: 15px; font-weight: 700; color: #f1f5f9;'>Proyectos y Tareas (Año / Mes / Día / Nombre)</span>
            <span style='font-size: 12px; color: #64748b; margin-left: 10px;'>Organización jerárquica estricta con respaldo en la nube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tasks_dir = _get_tasks_dir()
    all_projects = _collect_all_projects()

    is_cloud_on = _is_cloud_storage_configured()
    bucket_name = config.app.get("s3_bucket", "videopro-masters")

    c_stat1, c_stat2, c_stat3, c_stat4 = st.columns([2.0, 2.0, 2.2, 3.8], gap="medium")
    with c_stat1:
        st.metric("Total Proyectos", len(all_projects))
    with c_stat2:
        processing_count = sum(1 for p in all_projects if p["state"] == const.TASK_STATE_PROCESSING)
        st.metric("En Generación", processing_count)
    with c_stat3:
        complete_count = sum(1 for p in all_projects if p["has_video"])
        st.metric("Vídeos Listos", complete_count)
    with c_stat4:
        if is_cloud_on:
            st.markdown(f"""
            <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:6px; padding:6px 10px; margin-top:2px;'>
                <div style='font-size:11px; font-weight:600; color:#34d399;'>🟢 Cloud Storage Conectado</div>
                <div style='font-size:10.5px; color:#94a3b8;'>Estructura: <code>projects/YYYY/MM/DD/nombre/</code></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:rgba(234,179,8,0.1); border:1px solid rgba(234,179,8,0.3); border-radius:6px; padding:6px 10px; margin-top:2px;'>
                <div style='font-size:11px; font-weight:600; color:#facc15;'>💾 Disco Local (Año / Mes / Día)</div>
                <div style='font-size:10.5px; color:#94a3b8;'>Ruta: <code>storage/tasks/YYYY/MM/DD/nombre/</code></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    # Barra superior de filtros, buscador y acceso directo al Generador
    c_srch, c_sort, c_goto_gen = st.columns([5.5, 2.5, 2.0], gap="medium")
    with c_srch:
        search_query = st.text_input(
            "Buscar Proyecto:",
            placeholder="Filtrar por nombre, año, mes o fecha (ej: 2026/08/16)...",
            label_visibility="collapsed",
            key="proj_search_input"
        )
    with c_sort:
        sort_order = st.selectbox(
            "Orden:",
            ["Más recientes primero", "Más antiguos primero", "Por nombre (A-Z)"],
            label_visibility="collapsed",
            key="proj_sort_select"
        )
    with c_goto_gen:
        if st.button("🎬 Ir al Generador", type="primary", use_container_width=True, help="Crear nuevos proyectos en el Generador de Vídeo"):
            st.session_state["active_view"] = "main"
            st.rerun()

    # Tabs de Filtrado por Estado
    tab_all, tab_processing, tab_complete, tab_failed = st.tabs([
        f"Todos ({len(all_projects)})",
        f"⚡ En Generación ({processing_count})",
        f"✅ Completados ({complete_count})",
        f"⚠️ Fallidos / Otros ({len(all_projects) - complete_count - processing_count})"
    ])

    def _render_project_list(projects_subset, tab_key):
        filtered = list(projects_subset)
        if search_query.strip():
            q = search_query.strip().lower()
            filtered = [
                p for p in filtered 
                if q in p["subject"].lower() or q in p["rel_path"].lower() or q in p["date_formatted"]
            ]

        if not filtered:
            st.info("No hay proyectos en esta categoría.")
            return

        if sort_order == "Más antiguos primero":
            filtered.sort(key=lambda p: p["mtime"], reverse=False)
        elif sort_order == "Por nombre (A-Z)":
            filtered.sort(key=lambda p: p["subject"].lower())
        else:
            filtered.sort(key=lambda p: p["mtime"], reverse=True)

        # Agrupar jerárquicamente por Año / Mes / Día
        # Estructura: groups[Year][Month][Day] = [projects]
        tree = {}
        for p in filtered:
            y = p["year"]
            m = f"{p['month']} ({p['month_label']})"
            d = p["day"]
            tree.setdefault(y, {}).setdefault(m, {}).setdefault(d, []).append(p)

        for y_key, months_dict in tree.items():
            for m_key, days_dict in months_dict.items():
                for d_key, projs_in_day in days_dict.items():
                    st.markdown(f"""
                    <div style='background:#0f172a; border-left:3px solid #38bdf8; padding:5px 12px; margin: 12px 0 6px 0; border-radius: 0 4px 4px 0;'>
                        <span style='font-size:12.5px; font-weight:700; color:#38bdf8;'>📅 {y_key} ➔ {m_key} ➔ Día {d_key}</span>
                        <span style='font-size:11px; color:#64748b; margin-left:10px;'>({len(projs_in_day)} proyecto{'s' if len(projs_in_day) > 1 else ''})</span>
                    </div>
                    """, unsafe_allow_html=True)

                    for p in projs_in_day:
                        task_id = p["task_id"]
                        with st.container(border=True):
                            c_head, c_actions = st.columns([5.5, 4.5], vertical_alignment="center")
                            
                            with c_head:
                                f_time = p["datetime"].strftime("%H:%M")
                                
                                # Badge de estado
                                if p["state"] == const.TASK_STATE_PROCESSING:
                                    status_badge = "<span style='background:#1e3a8a; color:#93c5fd; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600;'>⚡ RENDERIZANDO</span>"
                                elif p["has_video"]:
                                    status_badge = "<span style='background:#064e3b; color:#6ee7b7; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600;'>✅ VÍDEO LISTO</span>"
                                elif p["state"] == const.TASK_STATE_FAILED:
                                    status_badge = "<span style='background:#7f1d1d; color:#fca5a5; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600;'>❌ FALLIDO</span>"
                                else:
                                    status_badge = "<span style='background:#334155; color:#cbd5e1; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600;'>📝 BORRADOR</span>"

                                cloud_badge = ""
                                if p["cloud_synced"]:
                                    cloud_badge = "<span style='background:#047857; color:#a7f3d0; padding:2px 5px; border-radius:4px; font-size:9.5px; margin-left:5px;'>☁️ R2</span>"

                                st.markdown(f"<div style='font-size:13.5px; font-weight:600; color:#f1f5f9; margin-bottom:2px;'>{p['subject']} {status_badge}{cloud_badge}</div><div style='font-size:11px; color:#64748b;'>📁 <code>{p['rel_path']}</code> · ⏰ {f_time}</div>", unsafe_allow_html=True)
                                
                                if p["state"] == const.TASK_STATE_PROCESSING:
                                    st.progress(p["progress"] / 100.0, text=f"Progreso: {p['progress']}%")

                            with c_actions:
                                b1, b2, b3, b4, b5 = st.columns(5, gap="small")
                                
                                with b1:
                                    if st.button("Cargar", key=f"load_{tab_key}_{p['rel_path']}", use_container_width=True, help="Cargar en el Generador"):
                                        st.session_state["task_restore_candidate_id"] = p["rel_path"]
                                        st.session_state["active_view"] = "main"
                                        st.rerun()

                                with b2:
                                    if p["has_video"]:
                                        is_showing = st.session_state.get(f"show_vid_{p['rel_path']}", False)
                                        btn_label = "Cerrar" if is_showing else "Ver"
                                        if st.button(btn_label, key=f"view_{tab_key}_{p['rel_path']}", use_container_width=True, help="Previsualizar vídeo"):
                                            st.session_state[f"show_vid_{p['rel_path']}"] = not is_showing
                                            st.rerun()
                                    else:
                                        st.button("-", key=f"novid_{tab_key}_{p['rel_path']}", disabled=True, use_container_width=True)

                                with b3:
                                    if is_cloud_on and p["has_video"]:
                                        btn_cloud_label = "☁️ Link" if p["cloud_synced"] else "☁️ Subir"
                                        if st.button(btn_cloud_label, key=f"cloud_{tab_key}_{p['rel_path']}", use_container_width=True, help="Subir a Cloud Storage"):
                                            if not p["cloud_synced"]:
                                                with st.spinner("Subiendo a Cloud Storage (R2)..."):
                                                    ok, msg = _upload_project_to_cloud(p)
                                                    if ok:
                                                        st.toast("Proyecto sincronizado en Cloud Storage.")
                                                        st.rerun()
                                                    else:
                                                        st.error(msg)
                                            else:
                                                st.session_state[f"show_cloud_link_{p['rel_path']}"] = not st.session_state.get(f"show_cloud_link_{p['rel_path']}", False)
                                                st.rerun()
                                    else:
                                        st.button("☁️", key=f"cloud_off_{tab_key}_{p['rel_path']}", disabled=True, use_container_width=True, help="Configura Cloud Storage en Ajustes")

                                with b4:
                                    if st.button("Clonar", key=f"clone_{tab_key}_{p['rel_path']}", use_container_width=True, help="Duplicar proyecto"):
                                        dest = f"{p['task_path']}_copia_{int(time.time()) % 1000}"
                                        try:
                                            shutil.copytree(p["task_path"], dest)
                                            st.toast("Proyecto duplicado con éxito.")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Error al clonar: {ex}")

                                with b5:
                                    if st.button("Borrar", key=f"del_{tab_key}_{p['rel_path']}", use_container_width=True, help="Eliminar permanentemente"):
                                        try:
                                            if hasattr(sm.state, "delete_task"):
                                                sm.state.delete_task(task_id)
                                            shutil.rmtree(p["task_path"])
                                            st.toast("Proyecto eliminado.")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Error al eliminar: {ex}")

                            # Reproductor de vídeo desplegable
                            if st.session_state.get(f"show_vid_{p['rel_path']}", False) and p["has_video"]:
                                st.markdown("---")
                                vcol1, vcol2 = st.columns([7, 3])
                                with vcol1:
                                    st.video(p["final_video"])
                                with vcol2:
                                    v_size_mb = os.path.getsize(p["final_video"]) / (1024 * 1024)
                                    st.caption(f"**Archivo:** `{os.path.basename(p['final_video'])}`")
                                    st.caption(f"**Tamaño:** {v_size_mb:.2f} MB")
                                    st.caption(f"**Ubicación:** `{p['rel_path']}`")
                                    with open(p["final_video"], "rb") as f_vid:
                                        st.download_button(
                                            "📥 Descargar MP4",
                                            data=f_vid.read(),
                                            file_name=os.path.basename(p["final_video"]),
                                            mime="video/mp4",
                                            use_container_width=True,
                                            key=f"dl_btn_{tab_key}_{p['rel_path']}"
                                        )

                            # Enlace Cloud Storage desplegable
                            if st.session_state.get(f"show_cloud_link_{p['rel_path']}", False) and p["cloud_synced"]:
                                st.markdown("---")
                                st.success(f"Enlace CDN R2: `{p.get('cloud_url', '')}`")
                                st.caption(f"Ruta remota: `projects/{p['year']}/{p['month']}/{p['day']}/{task_id}/` en `{bucket_name}`")

    with tab_all:
        _render_project_list(all_projects, "all")

    with tab_processing:
        processing_tasks = [p for p in all_projects if p["state"] == const.TASK_STATE_PROCESSING]
        _render_project_list(processing_tasks, "proc")

    with tab_complete:
        complete_tasks = [p for p in all_projects if p["has_video"]]
        _render_project_list(complete_tasks, "comp")

    with tab_failed:
        failed_tasks = [p for p in all_projects if not p["has_video"] and p["state"] != const.TASK_STATE_PROCESSING]
        _render_project_list(failed_tasks, "fail")
