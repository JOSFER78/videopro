"""
Vista de Administración del Pipeline de Nodos — VideoPro Studio
Visualización y Reconfiguración Dinámica del Grafo basada en Peticiones de Investigación de Hermes.
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components

from app.config import config
from app.controllers.v1 import pipeline
from app.services import firebase_sync
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG, get_all_archetypes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "investigaciones", "capacidades", "workflow_designer_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "investigaciones", "capacidades", "comfy_pipeline_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "investigaciones", "capacidades", "workflow_designer_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "investigaciones", "capacidades", "comfy_pipeline_studio.html")


def render_comfy_pipeline_view():
    """Renderiza el Workflow Studio y el Administrador de Flujo de Nodos sincronizado."""
    
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                🏛️ Workflow Studio
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">WORKFLOWS & PIPELINES SYNC</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Visualización interactiva de nodos, módulos técnicos y sincronización 100% real de Pipelines por Arquetipo de Producción.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Asistente Agéntico de Investigación & Reconfiguración Dinámica
    with st.expander("🔬 Hermes Research Agent — Reconfiguración Dinámica del Pipeline", expanded=True):
        st.caption("Introduce cualquier tema o requisito de investigación para que Hermes ajuste los nodos, motores y parámetros del flujo en tiempo real.")
        c_p_in, c_p_btn = st.columns([8, 2], vertical_alignment="bottom")
        with c_p_in:
            agent_prompt = st.text_input(
                "Petición de Investigación o Modificación del Flujo:",
                placeholder="Ej: Documental histórico sobre la construcción del Golden Gate con fotos de hemerotecas y recreación 35mm...",
                key="pipeline_agent_prompt_input"
            )
        with c_p_btn:
            if st.button("⚡ Investigar & Reconfigurar", type="primary", use_container_width=True):
                if not agent_prompt.strip():
                    st.warning("Escribe primero una instrucción o tema de investigación.")
                else:
                    with st.spinner("Hermes está investigando y reconfigurando el pipeline de nodos..."):
                        agent_res = pipeline.agent_build_pipeline({
                            "prompt": agent_prompt,
                            "history": []
                        })
                        st.session_state["last_pipeline_agent_res"] = agent_res
                    st.success("✅ Pipeline reconfigurado dinámicamente y sincronizado con el Workflow real.")
                    st.rerun()

        if "last_pipeline_agent_res" in st.session_state:
            last_res = st.session_state["last_pipeline_agent_res"]
            st.markdown(f"**Respuesta del Agente:** {last_res.get('reply', '')}")
            if last_res.get("applied_changes"):
                st.markdown("**Cambios Aplicados:**")
                for ch in last_res.get("applied_changes", []):
                    st.markdown(f"• {ch}")

    # 2. Selector de Pipeline / Arquetipo & Modo de Visualización
    c_sel1, c_sel2 = st.columns([6, 4], vertical_alignment="center")
    with c_sel1:
        pipe_options = ["MASTER"] + list(ARCHETYPES_CATALOG.keys())
        selected_pipe = st.selectbox(
            "Seleccionar Pipeline a Visualizar / Modificar:",
            options=pipe_options,
            index=0,
            format_func=lambda x: "🎬 Grafo Maestro Activo (Sincronizado)" if x == "MASTER" else f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name}"
        )

    with c_sel2:
        pipe_view_mode = st.segmented_control(
            "Modo de Visualización:",
            options=["studio", "native"],
            default="native",
            format_func=lambda x: "🎛️ Lienzo Visual de Nodos (Canvas 60 FPS)" if x == "studio" else "🌲 Árbol Modular Dinámico",
            key="pipeline_view_mode_selector"
        ) if hasattr(st, "segmented_control") else st.radio(
            "Modo de Visualización:",
            options=["studio", "native"],
            index=1,
            format_func=lambda x: "🎛️ Lienzo Visual de Nodos (Canvas 60 FPS)" if x == "studio" else "🌲 Árbol Modular Dinámico",
            horizontal=True,
            key="pipeline_view_mode_selector"
        )

    # 3. Cargar estado del grafo según la selección
    if selected_pipe == "MASTER":
        graph_data = pipeline.load_pipeline_graph()
    else:
        arch_obj = ARCHETYPES_CATALOG.get(selected_pipe)
        graph_data = arch_obj.pipeline_graph if arch_obj else pipeline.load_pipeline_graph()

    nodes = graph_data.get("nodes", [])
    connections = graph_data.get("connections", [])
    active_nodes = sum(1 for n in nodes if n.get("enabled", True))
    loop_nodes = sum(1 for n in nodes if n.get("is_loop", False))

    # 4. Métricas del Pipeline Activo
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Nodos", f"{active_nodes}/{len(nodes)} Activos")
    with m2:
        st.metric("Conexiones Bezier", f"{len(connections)} Cables")
    with m3:
        st.metric("Bucles de Escena", f"{loop_nodes} Loops")
    with m4:
        st.metric("Topología", selected_pipe)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 5. Renderizado Dual-Mode (Studio Canvas / Árbol Modular Dinámico)
    canvas_rendered = False
    if pipe_view_mode == "studio" and os.path.isfile(STUDIO_HTML_PATH):
        try:
            with open(STUDIO_HTML_PATH, "r", encoding="utf-8") as f:
                html_content = f.read()

            from app.core.providers import registry as prov_reg
            current_registry = prov_reg.load_registry()

            injected_script = f"""<script>
                window.INJECTED_PIPELINE_DATA = {json.dumps(graph_data)};
                window.INJECTED_PROVIDERS_REGISTRY = {json.dumps(current_registry)};
            </script>"""
            
            # Inject at the very top of <head> so it runs BEFORE any other script in the HTML
            if "<head>" in html_content:
                html_content = html_content.replace("<head>", f"<head>\n{injected_script}\n")
            elif "<body>" in html_content:
                html_content = html_content.replace("<body>", f"<body>\n{injected_script}\n")
            else:
                html_content = f"{injected_script}\n{html_content}"

            components.html(html_content, height=860, scrolling=False)
            canvas_rendered = True
        except Exception as ex:
            st.warning(f"Aviso al cargar lienzo de nodos: {ex}. Conmutando a vista de árbol nativo.")

    if not canvas_rendered:
        _render_native_pipeline_tree(graph_data, selected_pipe)


def _render_native_pipeline_tree(graph_data: dict, selected_pipe: str = "MASTER"):
    """Renderiza la vista en árbol modular dinámico 100% editable y sin textos hardcodeados."""
    nodes = graph_data.get("nodes", [])
    connections = graph_data.get("connections", [])

    st.markdown(f"### 🌲 Topología Modular de Nodos ({graph_data.get('name', 'Pipeline')})")
    
    col_t1, col_t2 = st.columns([1, 1])
    for idx, node in enumerate(nodes):
        target_col = col_t1 if idx % 2 == 0 else col_t2
        with target_col:
            node_id = node.get("id", f"node_{idx}")
            title = node.get("title", node_id)
            color = node.get("color", "#38bdf8")
            enabled = node.get("enabled", True)
            is_loop = node.get("is_loop", False)
            params = node.get("parameters", [])

            badge_loop = " 🔁 Loop Escena" if is_loop else ""
            badge_status = "🟢 ACTIVO" if enabled else "⚪ DESACTIVADO"

            # Título limpio sin etiquetas HTML crudas
            with st.expander(f"{title} — {badge_status}{badge_loop}", expanded=True):
                st.markdown(f"<div style='border-left: 3px solid {color}; padding-left: 8px; margin-bottom: 6px; font-size: 11px; color: #94a3b8;'>ID: <code>{node_id}</code> | Categoría: <code>{node.get('category', 'general')}</code></div>", unsafe_allow_html=True)
                
                # Checkbox para activar/desactivar nodo en tiempo real
                is_node_active = st.checkbox("Nodo Habilitado en la Cadena", value=enabled, key=f"chk_act_{node_id}")
                node["enabled"] = is_node_active

                if params:
                    st.markdown("**Parámetros Dinámicos Configurables:**")
                    for p in params:
                        p_k = p.get("key", "param")
                        p_lbl = p.get("label", p_k)
                        p_val = p.get("value", "")
                        p_type = p.get("type", "text")
                        
                        if p_type == "select" and p.get("options") and len(p.get("options")) > 1:
                            opts = p.get("options", [p_val])
                            idx_opt = opts.index(p_val) if p_val in opts else 0
                            new_val = st.selectbox(p_lbl, options=opts, index=idx_opt, key=f"native_{node_id}_{p_k}")
                            p["value"] = new_val
                        elif p_type == "range" or p_type == "number":
                            new_val = st.number_input(p_lbl, value=int(p_val if str(p_val).lstrip('-').isdigit() else 0), key=f"native_{node_id}_{p_k}")
                            p["value"] = new_val
                        else:
                            new_val = st.text_input(p_lbl, value=str(p_val), key=f"native_{node_id}_{p_k}", help="Define libremente este parámetro según tu investigación o historia")
                            p["value"] = new_val

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("💾 Guardar y Aplicar Cambios al Workflow Activo", type="primary", use_container_width=True):
        if selected_pipe != "MASTER" and selected_pipe in ARCHETYPES_CATALOG:
            ARCHETYPES_CATALOG[selected_pipe].pipeline_graph = graph_data
            try:
                from app.core.orchestration.repository import StudioRepository
                wf_def = StudioRepository.load_workflow(selected_pipe)
                if wf_def:
                    wf_def.pipeline_graph = graph_data
                    StudioRepository.save_workflow(wf_def)
            except Exception:
                pass
        ok = pipeline.save_pipeline_graph(graph_data)
        if ok:
            st.success(f"✅ Cambios en el pipeline «{selected_pipe}» guardados y sincronizados con el Workflow de producción.")
            st.rerun()

    st.markdown("<hr style='margin: 12px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
    with st.expander("🔌 Ver Mapa de Conexiones Bezier de Datos (Sockets)", expanded=False):
        for conn in connections:
            st.markdown(f"• `[{conn.get('from_node')}]` ➔ <b>{conn.get('from_socket')}</b> ───► `[{conn.get('to_node')}]` ➔ <b>{conn.get('to_socket')}</b> (Tipo: <code>{conn.get('payload_type', 'any')}</code>)", unsafe_allow_html=True)
