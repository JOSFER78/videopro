"""
Ajustes y Configuración Integral — VideoPro Studio
Gestor Dinámico de Credenciales de APIs, Modelos, Enlaces Funcionales y Ayuda Técnica
100% sincronizado con la Matriz Maestra y los selectores del Generador.
"""

import os
import sys
import json
import logging
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.services import firebase_sync
from app.core.providers import health_checker, registry

logger = logging.getLogger("videopro.settings")

# Soporte para diálogos nativos limpios de Streamlit
dialog_fn = getattr(st, "dialog", getattr(st, "experimental_dialog", None))


def _badge_html(badge_str: str) -> str:
    """Convierte el string de badge de health_checker en una etiqueta HTML con estilo."""
    if "ONLINE" in badge_str or "🟢" in badge_str:
        return f"<span style='background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.35); color:#34d399; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"
    elif "OFFLINE" in badge_str or "🔴" in badge_str:
        return f"<span style='background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.35); color:#f87171; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"
    elif "🟡" in badge_str:
        return f"<span style='background:rgba(234,179,8,0.15); border:1px solid rgba(234,179,8,0.35); color:#facc15; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"
    else:
        return f"<span style='background:rgba(148,163,184,0.1); border:1px solid rgba(148,163,184,0.25); color:#94a3b8; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"


def _get_badge(matrix: dict, key: str, default: str = "⚪ Sin configurar") -> str:
    """Helper seguro para obtener el badge HTML de un proveedor."""
    entry = matrix.get(key, {})
    if isinstance(entry, dict):
        return _badge_html(entry.get("badge", default))
    return _badge_html(default)


def _render_category_api_manager(reg: dict, matrix: dict, category_code: str, help_title: str):
    """Renderiza dinámicamente las fichas de configuración de APIs basándose estrictamente en los motores ACTIVOS en la Matriz."""
    cat_providers = [
        (p_id, p_info) for p_id, p_info in reg.items()
        if p_info.get("category") == category_code and p_info.get("enabled", True)
    ]
    
    if not cat_providers:
        st.info(f"💡 No hay motores de {help_title} activos. Activa el interruptor 'USAR' en la pestaña Matriz Maestra para configurar sus credenciales y modelos.")
        return

    col_1, col_2 = st.columns(2, gap="medium")
    for idx, (p_id, p_info) in enumerate(cat_providers):
        target_col = col_1 if idx % 2 == 0 else col_2
        with target_col:
            p_name = p_info.get("name", p_id)
            p_desc = p_info.get("description", "")
            doc_link = p_info.get("doc_link", "")
            doc_link_text = p_info.get("doc_link_text", "Obtener clave / Consola ↗")
            link_html = f" · <a href='{doc_link}' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>{doc_link_text}</a>" if doc_link else ""
            
            badge_html = _get_badge(matrix, p_id)
            st.markdown(f"**{p_name}** {badge_html}{link_html}", unsafe_allow_html=True)
            if p_desc:
                st.caption(p_desc)

            # Input de clave API si aplica
            api_field = p_info.get("api_key_field")
            if api_field:
                cur_k = config.app.get(api_field, "")
                if api_field == "hf_token":
                    new_k = st.text_area("Tokens Hugging Face (uno por línea):", value=cur_k, height=70, key=f"dyn_k_{p_id}", placeholder="hf_token1\nhf_token2")
                else:
                    new_k = st.text_input(f"Clave API ({p_name}):", value=cur_k, type="password", key=f"dyn_k_{p_id}", placeholder=f"Introduce la clave para {p_name}...")
                if new_k != cur_k:
                    config.app[api_field] = new_k

            # Input de Endpoint si aplica
            ep_field = p_info.get("endpoint_field")
            if ep_field:
                cur_ep = config.app.get(ep_field, p_info.get("endpoint_default", ""))
                new_ep = st.text_input(f"Endpoint URL ({p_name}):", value=cur_ep, key=f"dyn_ep_{p_id}", placeholder="http://...")
                if new_ep != cur_ep:
                    config.app[ep_field] = new_ep

            # Selector de Modelo si aplica
            md_field = p_info.get("model_field")
            if md_field:
                cur_md = config.app.get(md_field, p_info.get("model_default", ""))
                md_opts = p_info.get("model_options")
                if md_opts and isinstance(md_opts, list):
                    sel_idx = md_opts.index(cur_md) if cur_md in md_opts else 0
                    new_md = st.selectbox(f"Modelo ({p_name}):", options=md_opts, index=sel_idx, key=f"dyn_md_{p_id}")
                else:
                    new_md = st.text_input(f"Modelo ({p_name}):", value=cur_md, key=f"dyn_md_{p_id}")
                if new_md != cur_md:
                    config.app[md_field] = new_md

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


def render_view():
    # Notificación de borrado previo si existe
    if "deleted_provider_toast" in st.session_state:
        st.toast(st.session_state.pop("deleted_provider_toast"))

    # Modal nativo de confirmación de borrado seguro (elimina el bug de saltar al siguiente)
    if "confirm_delete_provider" in st.session_state and st.session_state["confirm_delete_provider"]:
        del_id, del_name = st.session_state["confirm_delete_provider"]
        if dialog_fn:
            @dialog_fn("⚠️ Confirmar Eliminación de Motor")
            def _show_delete_modal(id_to_del, name_to_del):
                st.markdown(f"¿Estás seguro de que deseas eliminar permanentemente a **«{name_to_del}»** de la Matriz y del Generador?")
                st.caption("Esta acción es irreversible y eliminará el motor del catálogo activo.")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    if st.button("❌ Cancelar", use_container_width=True, key="dlg_btn_cancel"):
                        st.session_state["confirm_delete_provider"] = None
                        st.rerun()
                with c_d2:
                    if st.button("🗑️ Sí, Eliminar", type="primary", use_container_width=True, key="dlg_btn_confirm_del"):
                        registry.delete_provider(id_to_del)
                        firebase_sync.save_settings_to_firebase_async()
                        st.session_state["confirm_delete_provider"] = None
                        st.session_state["deleted_provider_toast"] = f"✅ «{name_to_del}» borrado OK, todo listo."
                        st.rerun()
            _show_delete_modal(del_id, del_name)
        else:
            # Fallback si dialog no está disponible
            st.warning(f"⚠️ ¿Eliminar **«{del_name}»**?")
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                if st.button("❌ Cancelar", key="fb_canc_btn"):
                    st.session_state["confirm_delete_provider"] = None
                    st.rerun()
            with c_d2:
                if st.button("🗑️ Confirmar Eliminación", type="primary", key="fb_conf_btn"):
                    registry.delete_provider(del_id)
                    firebase_sync.save_settings_to_firebase_async()
                    st.session_state["confirm_delete_provider"] = None
                    st.session_state["deleted_provider_toast"] = f"✅ «{del_name}» borrado OK, todo listo."
                    st.rerun()

    st.markdown("""
    <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;'>
        <div>
            <h2 style='margin:0; font-size:24px; font-weight:800; color:#f8fafc;'>⚙️ Ajustes & Ecosistema de VideoPro</h2>
            <div style='font-size:13px; color:#94a3b8; margin-top:2px;'>
                Gestión integral de claves de APIs, infraestructura ($0 Local VPS, Serverless Pool, Cloud), directores y reglas de producción.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    force_check = st.session_state.get("force_health_refresh", False)
    if force_check:
        st.session_state["force_health_refresh"] = False

    matrix = health_checker.get_all_providers_matrix(force=force_check)
    reg = registry.load_registry()

    # Métricas de resumen rápido del estado
    total_services = len(matrix)
    active_services = sum(1 for v in matrix.values() if isinstance(v, dict) and "🟢" in v.get("badge", ""))
    error_items = [(k, v) for k, v in matrix.items() if isinstance(v, dict) and "🔴" in v.get("badge", "")]

    c_m1, c_m2, c_m3, c_m4 = st.columns([1.2, 1.2, 1.3, 1.1])
    with c_m1:
        st.markdown(f"""
        <div style='background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:6px; padding:6px 12px;'>
            <div style='font-size:11px; color:#94a3b8; font-weight:600;'>Estado General</div>
            <div style='font-size:14px; font-weight:800; color:#38bdf8;'>{active_services}/{total_services} APIs Conectadas</div>
        </div>
        """, unsafe_allow_html=True)
    with c_m2:
        st.markdown(f"""
        <div style='background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:6px; padding:6px 12px;'>
            <div style='font-size:11px; color:#34d399; font-weight:600;'>🟢 Listos Producción</div>
            <div style='font-size:14px; font-weight:800; color:#10b981;'>{active_services} Motores Activos</div>
        </div>
        """, unsafe_allow_html=True)
    with c_m3:
        if error_items:
            with st.popover(f"🔴 {len(error_items)} Requieren Atención", use_container_width=True):
                st.markdown(f"**⚠️ Diagnóstico de Servicios con Errores ({len(error_items)})**")
                st.caption("Detalle de servicios:")
                for e_k, e_v in error_items:
                    st.markdown(f"• **{e_v.get('name', e_k)}**: `{e_v.get('message', 'Desconectado')}`")
                    st.caption(f"Estado: {e_v.get('badge', '🔴 Error')}")
                st.markdown("---")
                if st.button("⚡ Reintentar Diagnóstico", key="pop_retry_diag", use_container_width=True):
                    st.session_state["force_health_refresh"] = True
                    st.rerun()
        else:
            st.markdown(f"""
            <div style='background:rgba(148,163,184,0.06); border:1px solid rgba(148,163,184,0.2); border-radius:6px; padding:6px 12px;'>
                <div style='font-size:11px; color:#94a3b8; font-weight:600;'>⚪ Diagnóstico</div>
                <div style='font-size:14px; font-weight:800; color:#cbd5e1;'>100% Estable</div>
            </div>
            """, unsafe_allow_html=True)
    with c_m4:
        if st.button("⚡ Diagnosticar Todo", use_container_width=True, help="Comprobar en vivo el estado real de todas las conexiones"):
            st.session_state["force_health_refresh"] = True
            st.toast("Comprobando conexiones de todos los proveedores...")
            st.rerun()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    tab_apis, tab_matrix, tab_storage, tab_firebase, tab_system, tab_lang = st.tabs([
        "🔑 Gestor de APIs & Credenciales",
        "📊 Matriz Maestra de Proveedores",
        "☁️ Cloud Storage (Cloudflare R2)",
        "🔥 Firebase Firestore & Hosting",
        "⚙️ Sistema y Render FFmpeg",
        "🌐 Idioma de la Interfaz"
    ])

    # =========================================================
    # TAB 1: GESTOR DINÁMICO DE APIS & CREDENCIALES (100% SINCRONIZADO)
    # =========================================================
    with tab_apis:
        subtab_llm, subtab_video, subtab_voice, subtab_music = st.tabs([
            "1. LLMs & Directores de Guion",
            "2. Vídeo, Visual e Imágenes",
            "3. Voz, Locución & Foley",
            "4. Música y Bandas Sonoras"
        ])

        with subtab_llm:
            _render_category_api_manager(reg, matrix, "llm", "Directores de Guion / LLM")

        with subtab_video:
            _render_category_api_manager(reg, matrix, "visual", "Vídeo e Imágenes")

        with subtab_voice:
            _render_category_api_manager(reg, matrix, "voice", "Voces y Locución")

        with subtab_music:
            _render_category_api_manager(reg, matrix, "music", "Música y Foley")

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Guardar y Persistir Credenciales en Firestore", type="primary", use_container_width=True, key="btn_save_creds_dyn"):
            firebase_sync.save_settings_to_firebase_async()
            st.toast("✅ Credenciales guardadas y sincronizadas con éxito.")

    # =========================================================
    # TAB 2: MATRIZ MAESTRA DE PROVEEDORES & REGLAS
    # =========================================================
    with tab_matrix:
        total_p = len(reg)
        enabled_p = sum(1 for v in reg.values() if v.get("enabled", True))
        local_p = sum(1 for v in reg.values() if v.get("infra_type") in ("local", "local_headless") and v.get("enabled", True))
        serverless_p = sum(1 for v in reg.values() if v.get("infra_type") == "serverless" and v.get("enabled", True))
        cloud_p = sum(1 for v in reg.values() if v.get("infra_type") == "cloud" and v.get("enabled", True))

        cm_1, cm_2, cm_3, cm_4 = st.columns(4)
        with cm_1:
            st.metric("Total Motores", f"{enabled_p}/{total_p} Activos")
        with cm_2:
            st.metric("🖥️ Local VPS ($0)", f"{local_p} Motores")
        with cm_3:
            st.metric("☁️ Serverless Pool ($0)", f"{serverless_p} Espacios")
        with cm_4:
            st.metric("🚀 Cloud Dedicada", f"{cloud_p} APIs")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        with st.expander("⚡ Gestor Rápido de Activación & Parámetros", expanded=False):
            col_hdr1, col_hdr2 = st.columns([7, 3], vertical_alignment="center")
            with col_hdr1:
                st.markdown("**Control de Activación del Generador de Vídeo**")
            with col_hdr2:
                with st.popover("➕ Añadir Motor Personalizado"):
                    st.markdown("**Registrar Nuevo Proveedor**")
                    new_p_id = st.text_input("ID único:", key="add_p_id_exp").strip().lower().replace(" ", "_")
                    new_p_name = st.text_input("Nombre:", key="add_p_name_exp")
                    new_p_cat = st.selectbox("Categoría:", ["visual", "llm", "voice", "music", "cloud"], key="add_p_cat_exp")
                    new_p_infra = st.selectbox("Infraestructura:", ["local", "serverless", "cloud"], key="add_p_infra_exp")
                    new_p_desc = st.text_input("Descripción técnica:", key="add_p_desc_exp")
                    if st.button("Guardar Motor", type="primary", use_container_width=True, key="btn_save_exp_motor"):
                        if new_p_id and new_p_name:
                            reg[new_p_id] = {
                                "id": new_p_id,
                                "name": new_p_name,
                                "category": new_p_cat,
                                "infra_type": new_p_infra,
                                "enabled": True,
                                "label": f"{new_p_name} ({new_p_infra.upper()})",
                                "description": new_p_desc or "Motor personalizado",
                                "categories": [{"text": "Inferencia Activa", "checked": True}],
                                "infrastructure": [{"text": f"Modo {new_p_infra.upper()}", "checked": True}],
                                "preferences": [{"text": "Preferencia activa", "checked": True}],
                                "behaviors": [{"text": "Regla de procesamiento", "checked": True}],
                                "notes": new_p_desc or "Personalizado"
                            }
                            registry.save_registry(reg)
                            firebase_sync.save_settings_to_firebase_async()
                            st.toast(f"✅ {new_p_name} añadido.")
                            st.rerun()

            # Filtro por categoría en el Gestor Rápido
            cat_filter_opts = [
                ("all", f"🌐 Todos ({len(reg)})"),
                ("visual", f"🎬 Vídeo ({sum(1 for v in reg.values() if v.get('category') == 'visual')})"),
                ("llm", f"🧠 LLMs ({sum(1 for v in reg.values() if v.get('category') == 'llm')})"),
                ("voice", f"🎙️ Voz ({sum(1 for v in reg.values() if v.get('category') == 'voice')})"),
                ("music", f"🎵 Música ({sum(1 for v in reg.values() if v.get('category') == 'music')})"),
                ("programacion", f"⚙️ Programación ({sum(1 for v in reg.values() if v.get('category') == 'programacion')})"),
                ("cloud", f"☁️ Cloud ({sum(1 for v in reg.values() if v.get('category') == 'cloud')})"),
            ]
            sel_fast_cat = st.segmented_control(
                "Filtrar por Categoría:",
                options=[k for k, _ in cat_filter_opts],
                default="all",
                format_func=lambda x: dict(cat_filter_opts).get(x, x),
                key="fast_mgr_cat_pills"
            ) if hasattr(st, "segmented_control") else st.radio(
                "Filtrar por Categoría:",
                options=[k for k, _ in cat_filter_opts],
                index=0,
                format_func=lambda x: dict(cat_filter_opts).get(x, x),
                horizontal=True,
                key="fast_mgr_cat_radio"
            )

            filtered_items = [
                (p_id, p_info) for p_id, p_info in reg.items()
                if sel_fast_cat in ("all", None) or p_info.get("category") == sel_fast_cat
            ]

            for p_id, p_info in filtered_items:
                p_name = p_info.get("name", p_id)
                p_enabled = bool(p_info.get("enabled", True))
                p_infra = p_info.get("infra_type", "cloud")
                p_desc = p_info.get("description", "")
                p_label = p_info.get("label", p_name)

                live_entry = matrix.get(p_id, {})
                badge_str = live_entry.get("badge", "🟢 Configurado" if p_enabled else "⚪ Inactivo")
                badge_tag = _badge_html(badge_str)

                c_c1, c_c2, c_c3, c_c4 = st.columns([5.5, 2.0, 1.3, 1.2], vertical_alignment="center")
                with c_c1:
                    st.markdown(f"<div style='font-size:13px; font-weight:700; color:#f1f5f9;'>{p_name} {badge_tag}</div>", unsafe_allow_html=True)
                    st.caption(p_desc)
                with c_c2:
                    n_st = st.toggle("USAR", value=p_enabled, key=f"mat_sw_tg_{p_id}")
                    if n_st != p_enabled:
                        registry.set_provider_enabled(p_id, n_st)
                        firebase_sync.save_settings_to_firebase_async()
                        st.toast(f"{p_name} {'habilitado' if n_st else 'deshabilitado'}.")
                        st.rerun()
                with c_c3:
                    with st.popover("✏️"):
                        e_name = st.text_input("Nombre:", value=p_name, key=f"e_nm_{p_id}")
                        e_label = st.text_input("Etiqueta:", value=p_label, key=f"e_lbl_{p_id}")
                        e_infra = st.selectbox("Infraestructura:", ["local", "serverless", "cloud"], index=["local", "serverless", "cloud"].index(p_infra) if p_infra in ["local", "serverless", "cloud"] else 0, key=f"e_inf_{p_id}")
                        if st.button("Guardar", type="primary", key=f"btn_sv_{p_id}"):
                            reg[p_id]["name"] = e_name
                            reg[p_id]["label"] = e_label
                            reg[p_id]["infra_type"] = e_infra
                            registry.save_registry(reg)
                            firebase_sync.save_settings_to_firebase_async()
                            st.toast(f"✅ {p_name} actualizado.")
                            st.rerun()
                with c_c4:
                    if st.button("🗑️", key=f"req_del_btn_{p_id}", help=f"Eliminar {p_name}"):
                        st.session_state["confirm_delete_provider"] = (p_id, p_name)
                        st.rerun()
                st.markdown("<hr style='margin: 4px 0 8px 0; border-color: #1e293b;'>", unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # TABLA MAESTRA VISUAL COMPLETA (EXCEL INTERACTIVO + IA)
        # ---------------------------------------------------------
        st.markdown("#### 📋 Matriz Visual Granular (Opciones Atómicas, Asistente IA, Preferencias & Comportamientos)")
        st.caption("Controla capacidades técnicas, modelos de inferencia, reglas de descarte estricto y comportamientos acústicos en tiempo real.")

        matrix_file = os.path.join(BASE_DIR, "investigaciones", "capacidades", "proveedores_excel.html")
        if os.path.exists(matrix_file):
            try:
                with open(matrix_file, "r", encoding="utf-8") as f:
                    matrix_html = f.read()

                # Inyectar datos vivos de Python para sincronización inmediata y exacta
                table_items = registry.get_matrix_table_data()
                table_items_json = json.dumps(table_items, ensure_ascii=False)
                injection_tag = f"<script>window.INJECTED_MATRIX_DATA = {table_items_json};</script>"
                if "</head>" in matrix_html:
                    matrix_html = matrix_html.replace("</head>", f"{injection_tag}</head>")
                else:
                    matrix_html = injection_tag + matrix_html

                components.html(matrix_html, height=780, scrolling=True)
            except Exception as e:
                st.error(f"Error al cargar la matriz visual: {e}")
        else:
            st.error("Archivo de matriz visual no encontrado.")

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        c_act1, c_act2 = st.columns(2)
        with c_act1:
            if st.button("⚡ Diagnosticar Todas las Conexiones", use_container_width=True, key="mat_btn_diag_bot_2"):
                st.session_state["force_health_refresh"] = True
                st.toast("Comprobando conexiones de todos los proveedores...")
                st.rerun()
        with c_act2:
            if st.button("🔄 Guardar y Sincronizar Estado en Firestore", type="primary", use_container_width=True, key="mat_btn_sync_bot_2"):
                try:
                    registry.save_registry(reg)
                    firebase_sync.save_settings_to_firebase_async()
                    st.toast("✅ Matriz y estado de proveedores guardados con éxito.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # =========================================================
    # TAB 3: CLOUD STORAGE & CDN (CLOUDFLARE R2)
    # =========================================================
    with tab_storage:
        b_r2 = _get_badge(matrix, "r2")
        st.markdown(f"#### ☁️ Cloudflare R2 Object Storage (S3 API Compatible) {b_r2}")
        st.caption("Almacenamiento en la nube de coste cero por descarga (Zero Egress) para hospedar vídeos máster, previsualizaciones y escenas.")

        col_r1, col_r2 = st.columns(2, gap="medium")
        with col_r1:
            r2_enable = st.toggle("Habilitar Sincronización Automática con Cloudflare R2", value=config.app.get("s3_enabled", False), key="s_r2_en")
            config.app["s3_enabled"] = r2_enable

            r2_endpoint = st.text_input("S3 / R2 Endpoint URL:", value=config.app.get("s3_endpoint", ""), key="s_r2_ep", placeholder="https://<ACCOUNT_ID>.r2.cloudflarestorage.com")
            config.app["s3_endpoint"] = r2_endpoint

            r2_bucket = st.text_input("Nombre del Bucket R2:", value=config.app.get("s3_bucket", "videopro-masters"), key="s_r2_bk")
            config.app["s3_bucket"] = r2_bucket

        with col_r2:
            r2_ak = st.text_input("Access Key ID:", value=config.app.get("s3_access_key", ""), key="s_r2_ak")
            config.app["s3_access_key"] = r2_ak

            r2_sk = st.text_input("Secret Access Key:", value=config.app.get("s3_secret_key", ""), type="password", key="s_r2_sk")
            config.app["s3_secret_key"] = r2_sk

            r2_cdn = st.text_input("Dominio Público / CDN Custom URL (Opcional):", value=config.app.get("s3_public_url", ""), key="s_r2_cdn", placeholder="https://media.videopro.studio")
            config.app["s3_public_url"] = r2_cdn

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        col_test_r2, col_info_r2 = st.columns([1, 2])
        with col_test_r2:
            if st.button("🧪 Probar Subida Multipart a R2", key="btn_test_r2_upload", use_container_width=True):
                from app.services import r2_storage
                with st.spinner("Probando transferencia a Cloudflare R2..."):
                    res = r2_storage.test_r2_upload_diagnostic()
                    if res.get("success"):
                        st.success(res.get("message"))
                    else:
                        st.error(res.get("message"))
                        if res.get("hint"):
                            st.info(f"💡 **Recomendación:** {res.get('hint')}")

        with col_info_r2:
            st.caption("""
            ℹ️ **Credenciales S3 de Cloudflare R2:**
            En *Cloudflare Dashboard > R2 > Manage R2 API Tokens*, crea un token con permisos de administración (Read & Write). Cloudflare generará un **Access Key ID** (32 caracteres) y un **Secret Access Key** (64 caracteres).
            """)

    # =========================================================
    # TAB 4: FIREBASE FIRESTORE & HOSTING
    # =========================================================
    with tab_firebase:
        b_fb = _get_badge(matrix, "firebase")
        st.markdown(f"#### 🔥 Firebase Firestore & Hosting {b_fb}")
        st.caption("Persistencia y sincronización en la nube de proyectos, metadatos y preferencias.")

        col_fb1, col_fb2 = st.columns(2, gap="medium")
        with col_fb1:
            fb_pid = st.text_input("Firebase Project ID:", value=config.app.get("firebase_project_id", "ayuda-emilio-83261"), key="s_fb_pid")
            config.app["firebase_project_id"] = fb_pid
            
            fb_url = st.text_input("URL de Hosting Público:", value=config.app.get("firebase_hosting_url", "https://videopro-studio.web.app"), key="s_fb_hurl")
            config.app["firebase_hosting_url"] = fb_url

        with col_fb2:
            st.markdown("**Acciones de Sincronización con Firestore:**")
            if st.button("📤 Guardar Configuración en Firestore Ahora", use_container_width=True, key="btn_fb_save_now"):
                ok, msg = firebase_sync.save_settings_to_firebase()
                if ok: st.success(msg)
                else: st.error(msg)

            if st.button("📥 Restaurar Configuración desde Firestore", use_container_width=True, key="btn_fb_load_now"):
                ok, msg = firebase_sync.load_settings_from_firebase()
                if ok:
                    st.success(msg)
                    st.rerun()
                else: st.error(msg)

    # =========================================================
    # TAB 5: AJUSTES DEL SISTEMA & RENDER FFMPEG
    # =========================================================
    with tab_system:
        st.markdown("#### ⚙️ Parámetros del Motor de Render & Concurrencia")
        col_sys1, col_sys2 = st.columns(2, gap="medium")
        with col_sys1:
            max_conc = st.slider("Concurrencia Máxima de Generación de Escenas:", min_value=1, max_value=8, value=int(config.app.get("max_concurrent_scenes", 3)), key="s_sys_conc")
            config.app["max_concurrent_scenes"] = max_conc

            crf_val = st.slider("Calidad de Codificación FFmpeg (CRF - Menor es mayor calidad):", min_value=14, max_value=28, value=int(config.app.get("ffmpeg_crf", 19)), key="s_sys_crf")
            config.app["ffmpeg_crf"] = crf_val

        with col_sys2:
            preset_val = st.selectbox("Preset de Codificación x264/NVENC:", ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"], index=2, key="s_sys_preset")
            config.app["ffmpeg_preset"] = preset_val

            keep_temp = st.toggle("Conservar fotogramas temporales y WAVs intermedios", value=config.app.get("keep_temp_files", False), key="s_sys_temp")
            config.app["keep_temp_files"] = keep_temp

    # =========================================================
    # TAB 6: IDIOMA DE LA INTERFAZ
    # =========================================================
    with tab_lang:
        st.markdown("#### 🌐 Idioma y Localización de la Interfaz")
        col_l1, col_l2 = st.columns([1, 1])
        with col_l1:
            cur_lang = config.ui.get("language", "es")
            lang_opts = ["es", "en", "zh-CN", "zh-TW", "ja", "ko", "ru", "fr", "de"]
            lang_labels = {
                "es": "🇪🇸 Español (Castellano)",
                "en": "🇬🇧 English (International)",
                "zh-CN": "🇨🇳 简体中文 (Simplified Chinese)",
                "zh-TW": "🇹🇼 繁體中文 (Traditional Chinese)",
                "ja": "🇯🇵 日本語 (Japanese)",
                "ko": "🇰🇷 한국어 (Korean)",
                "ru": "🇷🇺 Русский (Russian)",
                "fr": "🇫🇷 Français (French)",
                "de": "🇩🇪 Deutsch (German)"
            }
            sel_lang = st.selectbox(
                "Seleccionar Idioma de VideoPro:",
                options=lang_opts,
                index=lang_opts.index(cur_lang) if cur_lang in lang_opts else 0,
                format_func=lambda x: lang_labels.get(x, x),
                key="s_lang_sel"
            )
            if sel_lang != cur_lang:
                config.ui["language"] = sel_lang
                st.toast(f"Idioma cambiado a {lang_labels.get(sel_lang, sel_lang)}")
                st.rerun()
