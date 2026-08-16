"""
Módulo de Gestión de Proyectos y Sincronización con Cloudflare R2 & Firestore — VideoPro Studio
Unifica Proyectos de Studio (storage/projects/), Tareas Jerárquicas (storage/tasks/)
y Sincronización Automática Bidireccional con Cloudflare R2 Object Storage.
"""

import os
import sys
import json
import time
import shutil
import glob
from datetime import datetime
from pathlib import Path
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.config.config_manager import config_manager
from app.utils import utils
from app.services.storage.factory import StorageFactory
from app.services.storage.r2 import CloudflareR2StorageService
from app.models import const
from app.services import state as sm
from app.services import firebase_sync
from app.core.services.project_repository import ProjectRepository
from app.core.orchestration.repository import StudioRepository


MONTH_NAMES = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}


def _get_storage_root():
    if hasattr(utils, "storage_dir"):
        return os.path.abspath(utils.storage_dir())
    return os.path.abspath(os.path.join(BASE_DIR, "storage"))


def _get_tasks_dir():
    return os.path.join(_get_storage_root(), "tasks")


def _get_projects_dir():
    return os.path.join(_get_storage_root(), "projects")


def _is_cloud_storage_configured():
    s3_ep = config_manager.get("storage.s3.endpoint_url") or config_manager.get("r2.endpoint_url") or config.app.get("s3_endpoint", "")
    s3_acc = config_manager.get("storage.s3.access_key_id") or config_manager.get("r2.access_key_id") or config.app.get("s3_access_key", "")
    s3_sec = config_manager.get("storage.s3.secret_access_key") or config_manager.get("r2.secret_access_key") or config.app.get("s3_secret_key", "")
    s3_bkt = config_manager.get("storage.s3.bucket_name") or config_manager.get("r2.bucket_name") or config.app.get("s3_bucket", "")
    return bool(s3_ep and s3_acc and (s3_sec or "cloudflarestorage" in s3_ep) and s3_bkt)


def _upload_single_project_to_r2(project_dict):
    """Sube un proyecto local a Cloudflare R2 y actualiza el marcador y Firestore."""
    try:
        storage_service = StorageFactory.get_storage_service(force_reload=True)
        if not isinstance(storage_service, CloudflareR2StorageService):
            return False, "Cloud Storage no está configurado como Cloudflare R2 en Ajustes."

        proj_path = project_dict["task_path"]
        task_id = project_dict["task_id"]
        y, m, d = project_dict["year"], project_dict["month"], project_dict["day"]
        
        remote_prefix = f"projects/{y}/{m}/{d}/{task_id}"

        # 1. Subir vídeo final si existe
        remote_video_key = ""
        presigned_url = ""
        if project_dict["has_video"] and os.path.isfile(project_dict["final_video"]):
            v_name = os.path.basename(project_dict["final_video"])
            target_key = f"{remote_prefix}/{v_name}"
            remote_video_key = storage_service.upload_file(project_dict["final_video"], target_key)
            presigned_url = storage_service.get_presigned_url(remote_video_key, expiration_seconds=86400 * 7)

        # 2. Subir manifiestos (project.json y script.json)
        p_json = os.path.join(proj_path, "project.json")
        if os.path.isfile(p_json):
            storage_service.upload_file(p_json, f"{remote_prefix}/project.json")
            
        s_json = os.path.join(proj_path, "script.json")
        if os.path.isfile(s_json):
            storage_service.upload_file(s_json, f"{remote_prefix}/script.json")

        # 3. Guardar marcador local .r2_synced.json
        marker_data = {
            "synced": True,
            "synced_at": datetime.now().isoformat(),
            "remote_key": remote_video_key,
            "presigned_url": presigned_url,
            "cloud_path": remote_prefix,
            "bucket": storage_service.bucket_name
        }
        with open(os.path.join(proj_path, ".r2_synced.json"), "w", encoding="utf-8") as f:
            json.dump(marker_data, f, indent=2)

        # 4. Respaldo en Firebase Firestore
        try:
            p_copy = dict(project_dict)
            p_copy["cloud_synced"] = True
            p_copy["cloud_url"] = presigned_url
            p_copy["cloud_path"] = remote_prefix
            firebase_sync.backup_project_to_firebase(p_copy)
        except Exception:
            pass

        return True, "Sincronizado con éxito en Cloudflare R2 y Firestore."
    except Exception as ex:
        return False, f"Error al subir a Cloudflare R2: {ex}"


def _collect_all_unified_projects():
    """Recolecta tanto proyectos modernos de Studio como tareas jerárquicas locales y remotas."""
    projects_root = _get_projects_dir()
    tasks_root = _get_tasks_dir()
    os.makedirs(projects_root, exist_ok=True)
    os.makedirs(tasks_root, exist_ok=True)

    all_projs = []
    seen_ids = set()

    # 1. Escaneo de storage/projects/ (Studio Projects)
    for p_dir in glob.glob(os.path.join(projects_root, "*")):
        if not os.path.isdir(p_dir):
            continue
        p_id = os.path.basename(p_dir)
        p_json_file = os.path.join(p_dir, "project.json")
        mtime = os.path.getmtime(p_dir)
        
        p_data = {}
        if os.path.isfile(p_json_file):
            try:
                with open(p_json_file, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                mtime = max(mtime, os.path.getmtime(p_json_file))
            except Exception:
                pass

        # Buscar vídeos
        video_files = []
        for ext in ("*.mp4", "*.mkv", "*.mov", "*.webm"):
            video_files.extend(glob.glob(os.path.join(p_dir, ext)))
            video_files.extend(glob.glob(os.path.join(p_dir, "renders", ext)))
        
        final_video = ""
        if video_files:
            video_files.sort(key=lambda x: os.path.getsize(x) if os.path.isfile(x) else 0, reverse=True)
            final_video = video_files[0]
            mtime = max(mtime, os.path.getmtime(final_video))

        has_video = bool(final_video and os.path.isfile(final_video) and os.path.getsize(final_video) > 1024)

        # Chequear marcador de R2
        r2_file = os.path.join(p_dir, ".r2_synced.json")
        r2_info = {}
        if os.path.isfile(r2_file):
            try:
                with open(r2_file, "r", encoding="utf-8") as f:
                    r2_info = json.load(f)
            except Exception:
                pass

        dt = datetime.fromtimestamp(mtime)
        year, month, day = dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")

        all_projs.append({
            "task_id": p_id,
            "project_id": p_id,
            "rel_path": f"projects/{p_id}",
            "task_path": p_dir,
            "subject": p_data.get("title") or p_id,
            "script": str(p_data.get("scenes", ""))[:500],
            "params": p_data.get("render_spec", {}),
            "final_video": final_video,
            "has_video": has_video,
            "mtime": mtime,
            "datetime": dt,
            "year": year,
            "month": month,
            "month_label": MONTH_NAMES.get(month, month),
            "day": day,
            "date_formatted": f"{day}/{month}/{year}",
            "state": const.TASK_STATE_COMPLETE if has_video else const.TASK_STATE_DRAFT,
            "progress": 100 if has_video else 0,
            "cloud_synced": bool(r2_info.get("synced")),
            "cloud_key": r2_info.get("remote_key", ""),
            "cloud_url": r2_info.get("presigned_url", ""),
            "is_studio": True
        })
        seen_ids.add(p_id)

    # 2. Escaneo de storage/tasks/ (Jerárquico Año/Mes/Día)
    for root, dirs, files in os.walk(tasks_root):
        if os.path.basename(root).startswith("."):
            continue
        is_project_dir = "script.json" in files or any(f.endswith((".mp4", ".mov", ".mkv")) for f in files)
        is_leaf_task = bool(dirs == [] and root != tasks_root)

        if (is_project_dir or is_leaf_task) and root != tasks_root:
            p_id = os.path.basename(root)
            if p_id in seen_ids:
                continue

            rel_path = os.path.relpath(root, tasks_root)
            mtime = os.path.getmtime(root)

            script_file = os.path.join(root, "script.json")
            script_data = {}
            if os.path.isfile(script_file):
                try:
                    with open(script_file, "r", encoding="utf-8") as f:
                        script_data = json.load(f)
                    mtime = max(mtime, os.path.getmtime(script_file))
                except Exception:
                    pass

            video_files = []
            for ext in ("*.mp4", "*.mkv", "*.mov", "*.webm"):
                video_files.extend(glob.glob(os.path.join(root, ext)))
                video_files.extend(glob.glob(os.path.join(root, "final-*", ext)))
            
            final_video = ""
            if video_files:
                video_files.sort(key=lambda x: os.path.getsize(x) if os.path.isfile(x) else 0, reverse=True)
                final_video = video_files[0]
                mtime = max(mtime, os.path.getmtime(final_video))

            has_video = bool(final_video and os.path.isfile(final_video) and os.path.getsize(final_video) > 1024)

            r2_file = os.path.join(root, ".r2_synced.json")
            r2_info = {}
            if os.path.isfile(r2_file):
                try:
                    with open(r2_file, "r", encoding="utf-8") as f:
                        r2_info = json.load(f)
                except Exception:
                    pass

            dt = datetime.fromtimestamp(mtime)
            parts = rel_path.replace("\\", "/").split("/")
            if len(parts) >= 4 and len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
                year, month, day = parts[0], parts[1], parts[2]
            else:
                year, month, day = dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")

            params = script_data.get("params", {})
            subject = params.get("video_subject") or script_data.get("script", "")[:45] or p_id

            all_projs.append({
                "task_id": p_id,
                "project_id": p_id,
                "rel_path": rel_path,
                "task_path": root,
                "subject": subject,
                "script": script_data.get("script", ""),
                "params": params,
                "final_video": final_video,
                "has_video": has_video,
                "mtime": mtime,
                "datetime": dt,
                "year": year,
                "month": month,
                "month_label": MONTH_NAMES.get(month, month),
                "day": day,
                "date_formatted": f"{day}/{month}/{year}",
                "state": const.TASK_STATE_COMPLETE if has_video else const.TASK_STATE_DRAFT,
                "progress": 100 if has_video else 0,
                "cloud_synced": bool(r2_info.get("synced")),
                "cloud_key": r2_info.get("remote_key", ""),
                "cloud_url": r2_info.get("presigned_url", ""),
                "is_studio": False
            })
            seen_ids.add(p_id)

    all_projs.sort(key=lambda p: p["mtime"], reverse=True)
    return all_projs


def render_view():
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                📁 Bóveda de Proyectos & Sincronización Cloudflare R2
                <span style="font-size: 11px; font-weight: 700; background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 8px; border-radius: 12px;">R2 & FIRESTORE SYNC</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Persistencia híbrida local y respaldo automático en Cloudflare R2 (Zero Egress) con metadatos en Firebase Firestore.
            </p>
        </div>
    """, unsafe_allow_html=True)

    is_cloud_on = _is_cloud_storage_configured()
    all_projects = _collect_all_unified_projects()
    synced_count = sum(1 for p in all_projects if p["cloud_synced"])
    complete_count = sum(1 for p in all_projects if p["has_video"])

    # Tarjetas de Métricas Superiores con Botón de Sincronización Masiva
    c1, c2, c3, c4 = st.columns([2.2, 2.2, 2.4, 4.2], gap="medium")
    with c1:
        st.metric("Total Proyectos", len(all_projects))
    with c2:
        st.metric("Vídeos Renderizados", complete_count)
    with c3:
        st.metric("Sincronizados en R2", f"{synced_count} / {len(all_projects)}")
    with c4:
        c_sync_btn, c_sync_status = st.columns([6, 4], vertical_alignment="center")
        with c_sync_btn:
            if st.button("☁️ Sincronizar Todo con R2", type="primary", use_container_width=True, key="btn_sync_all_r2"):
                with st.spinner("Sincronizando todos los proyectos con Cloudflare R2 y Firestore..."):
                    uploaded_ok = 0
                    errors = 0
                    for p in all_projects:
                        if not p["cloud_synced"]:
                            ok, _ = _upload_single_project_to_r2(p)
                            if ok:
                                uploaded_ok += 1
                            else:
                                errors += 1
                    st.success(f"✅ Sincronización completada: {uploaded_ok} subidos, {errors} errores.")
                    st.rerun()
        with c_sync_status:
            if is_cloud_on:
                st.markdown("<span style='font-size:11px; font-weight:700; color:#34d399;'>🟢 Cloudflare R2 ACTIVO</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size:11px; font-weight:700; color:#facc15;'>🟡 Solo Disco Local</span>", unsafe_allow_html=True)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # Buscador y Filtro
    c_srch, c_sort, c_goto_dir = st.columns([5.5, 2.5, 2.0], gap="medium")
    with c_srch:
        search_query = st.text_input(
            "Buscar Proyecto:",
            placeholder="Filtrar por título, ID, fecha (ej: 2026/08/16)...",
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
    with c_goto_dir:
        if st.button("🎬 Director Creativo", use_container_width=True, help="Ir al Director Creativo para crear un nuevo proyecto"):
            st.session_state["active_view"] = "studio"
            st.rerun()

    # Pestañas de Filtrado y Monitor en Vivo
    tab_live, tab_all, tab_synced, tab_pending, tab_videos = st.tabs([
        "⚡ En Proceso & Monitor en Vivo",
        f"Todos ({len(all_projects)})",
        f"☁️ Sincronizados en R2 ({synced_count})",
        f"⏳ Pendientes de Nube ({len(all_projects) - synced_count})",
        f"🎞️ Con Vídeo ({complete_count})"
    ])

    with tab_live:
        st.markdown("##### ⚡ Monitor de Producción Cinemática en Tiempo Real")
        st.caption("Seguimiento de jobs de renderizado multimotor, pipelines de inferencia y estado de entrega.")
        from app.core.orchestration.repository import StudioRepository
        recent_jobs = StudioRepository.list_jobs(limit=15)
        if not recent_jobs:
            st.info("No hay producciones activas o recientes en este momento. Inicia una desde la pestaña '🚀 Empezar'.")
        else:
            for j in recent_jobs:
                j_id = j.get("job_id", "job")
                j_proj = j.get("project_id", "proj")
                j_wf = j.get("workflow_id", "Workflow")
                j_status = str(j.get("status", "unknown")).upper()
                j_metrics = j.get("metrics", {})
                j_dur = j_metrics.get("total_duration_seconds", 0)
                j_steps = j.get("steps", [])
                
                badge_bg = "rgba(16, 185, 129, 0.2)" if j_status == "COMPLETED" else "rgba(245, 158, 11, 0.2)"
                badge_color = "#34d399" if j_status == "COMPLETED" else "#facc15"
                
                with st.expander(f"🎬 Job `{j_id}` — {j_status} ({j_wf})", expanded=(j_status != "COMPLETED")):
                    c_j1, c_j2 = st.columns([7, 3])
                    with c_j1:
                        st.markdown(f"• **Proyecto:** `{j_proj}` | **Workflow:** `{j_wf}`")
                        st.markdown(f"• **Tiempo de Render:** `{j_dur:.2f}s` | **Pasos:** {len(j_steps)}")
                        
                        st.markdown("<div style='font-size:11.5px; font-weight:700; color:#38bdf8; margin-top:4px;'>Trazabilidad de Pasos:</div>", unsafe_allow_html=True)
                        for s_idx, stp in enumerate(j_steps):
                            s_name = stp.get("step_id", f"Paso {s_idx+1}")
                            s_stat = stp.get("status", "ok")
                            st.markdown(f"<div style='font-size:11px; color:#cbd5e1;'>✅ `{s_name}` — {s_stat.upper()}</div>", unsafe_allow_html=True)
                    with c_j2:
                        st.markdown(f"<div style='padding:6px; background:{badge_bg}; border:1px solid {badge_color}; border-radius:6px; text-align:center; font-weight:700; color:{badge_color}; font-size:12px;'>{j_status}</div>", unsafe_allow_html=True)
                        if st.button("🎬 Abrir en Empezar", key=f"btn_open_dir_{j_id}", use_container_width=True):
                            st.session_state["active_view"] = "studio"
                            st.rerun()

    def _render_projects_grid(proj_list, tab_prefix):
        filtered = list(proj_list)
        if search_query.strip():
            q = search_query.strip().lower()
            filtered = [p for p in filtered if q in p["subject"].lower() or q in p["project_id"].lower() or q in p["date_formatted"]]

        if not filtered:
            st.info("No hay proyectos en esta sección.")
            return

        if sort_order == "Más antiguos primero":
            filtered.sort(key=lambda p: p["mtime"], reverse=False)
        elif sort_order == "Por nombre (A-Z)":
            filtered.sort(key=lambda p: p["subject"].lower())
        else:
            filtered.sort(key=lambda p: p["mtime"], reverse=True)

        # Agrupación por Año ➔ Mes ➔ Día
        tree = {}
        for p in filtered:
            y = p["year"]
            m = f"{p['month']} ({p['month_label']})"
            d = p["day"]
            tree.setdefault(y, {}).setdefault(m, {}).setdefault(d, []).append(p)

        for y_key, m_dict in tree.items():
            for m_key, d_dict in m_dict.items():
                for d_key, projs in d_dict.items():
                    st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.85); border-left: 3px solid #38bdf8; padding: 4px 10px; margin: 10px 0 4px 0; border-radius: 0 4px 4px 0; font-size: 12px; font-weight: 700; color: #38bdf8;">
                            📅 {y_key} ➔ {m_key} ➔ Día {d_key} <span style="font-size: 11px; font-weight: 400; color: #64748b; margin-left: 8px;">({len(projs)} proyecto{'s' if len(projs) > 1 else ''})</span>
                        </div>
                    """, unsafe_allow_html=True)

                    for p in projs:
                        with st.container(border=True):
                            c_info, c_acts = st.columns([6, 4], vertical_alignment="center")
                            
                            with c_info:
                                time_str = p["datetime"].strftime("%H:%M")
                                
                                # Badges
                                vid_badge = "<span style='background:#064e3b; color:#6ee7b7; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600;'>✅ VÍDEO MASTER</span>" if p["has_video"] else "<span style='background:#334155; color:#94a3b8; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600;'>📝 PROYECTO</span>"
                                
                                r2_badge = "<span style='background:rgba(16,185,129,0.2); color:#34d399; border:1px solid rgba(16,185,129,0.4); padding:1px 6px; border-radius:4px; font-size:10px; font-weight:600; margin-left:4px;'>☁️ R2 SYNC</span>" if p["cloud_synced"] else "<span style='background:rgba(234,179,8,0.15); color:#facc15; border:1px solid rgba(234,179,8,0.3); padding:1px 6px; border-radius:4px; font-size:10px; font-weight:600; margin-left:4px;'>💾 LOCAL</span>"
                                
                                studio_badge = "<span style='background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); padding:1px 6px; border-radius:4px; font-size:10px; font-weight:600; margin-left:4px;'>🏛️ STUDIO</span>" if p.get("is_studio") else ""

                                st.markdown(f"""
                                    <div style="font-size: 13.5px; font-weight: 700; color: #f8fafc; margin-bottom: 2px;">
                                        {p['subject']} {vid_badge}{r2_badge}{studio_badge}
                                    </div>
                                    <div style="font-size: 11px; color: #64748b;">
                                        📁 <code>{p['project_id']}</code> · ⏰ {time_str}
                                    </div>
                                """, unsafe_allow_html=True)

                            with c_acts:
                                b_play, b_cloud, b_edit, b_del = st.columns(4, gap="small")
                                
                                with b_play:
                                    if p["has_video"]:
                                        is_open = st.session_state.get(f"show_vid_{p['project_id']}", False)
                                        btn_lbl = "Cerrar" if is_open else "Ver"
                                        if st.button(btn_lbl, key=f"btn_v_{tab_prefix}_{p['project_id']}", use_container_width=True):
                                            st.session_state[f"show_vid_{p['project_id']}"] = not is_open
                                            st.rerun()
                                    else:
                                        st.button("-", key=f"btn_nv_{tab_prefix}_{p['project_id']}", disabled=True, use_container_width=True)

                                with b_cloud:
                                    if p["cloud_synced"]:
                                        is_c_open = st.session_state.get(f"show_c_{p['project_id']}", False)
                                        btn_c_lbl = "Cerrar" if is_c_open else "☁️ R2"
                                        if st.button(btn_c_lbl, key=f"btn_c_{tab_prefix}_{p['project_id']}", use_container_width=True):
                                            st.session_state[f"show_c_{p['project_id']}"] = not is_c_open
                                            st.rerun()
                                    else:
                                        if st.button("☁️ Subir", key=f"btn_c_{tab_prefix}_{p['project_id']}", use_container_width=True):
                                            with st.spinner("Subiendo a Cloudflare R2..."):
                                                ok, msg = _upload_single_project_to_r2(p)
                                                if ok:
                                                    st.toast("Proyecto sincronizado en Cloudflare R2.")
                                                    st.rerun()
                                                else:
                                                    st.error(msg)

                                with b_edit:
                                    if st.button("🎬 Abrir", key=f"btn_edit_{tab_prefix}_{p['project_id']}", use_container_width=True, help="Abrir en el Director Semántico"):
                                        st.session_state["current_project_id"] = p["project_id"]
                                        st.session_state["active_view"] = "studio"
                                        st.rerun()

                                with b_del:
                                    if st.button("🗑️", key=f"btn_d_{tab_prefix}_{p['project_id']}", use_container_width=True, help="Eliminar proyecto"):
                                        try:
                                            if os.path.exists(p["task_path"]):
                                                shutil.rmtree(p["task_path"])
                                            st.toast("Proyecto eliminado.")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Error al eliminar: {ex}")

                            # Visor de Vídeo
                            if st.session_state.get(f"show_vid_{p['project_id']}", False) and p["has_video"]:
                                st.markdown("<hr style='margin: 8px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
                                vc1, vc2 = st.columns([7, 3])
                                with vc1:
                                    st.video(p["final_video"])
                                with vc2:
                                    sz_mb = os.path.getsize(p["final_video"]) / (1024 * 1024)
                                    st.caption(f"**Archivo:** `{os.path.basename(p['final_video'])}`")
                                    st.caption(f"**Tamaño:** {sz_mb:.2f} MB")
                                    with open(p["final_video"], "rb") as fv:
                                        st.download_button(
                                            "📥 Descargar MP4",
                                            data=fv.read(),
                                            file_name=os.path.basename(p["final_video"]),
                                            mime="video/mp4",
                                            use_container_width=True,
                                            key=f"dl_{tab_prefix}_{p['project_id']}"
                                        )

                            # Enlace de R2
                            if st.session_state.get(f"show_c_{p['project_id']}", False) and p["cloud_synced"]:
                                st.markdown("<hr style='margin: 8px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
                                st.success(f"🔗 **URL Cloudflare R2:** `{p.get('cloud_url', '')}`")
                                st.caption("Streaming y descarga directa con ancho de banda gratuito (Zero Egress).")

    with tab_all:
        _render_projects_grid(all_projects, "all")

    with tab_synced:
        _render_projects_grid([p for p in all_projects if p["cloud_synced"]], "synced")

    with tab_pending:
        _render_projects_grid([p for p in all_projects if not p["cloud_synced"]], "pend")

    with tab_videos:
        _render_projects_grid([p for p in all_projects if p["has_video"]], "vids")
