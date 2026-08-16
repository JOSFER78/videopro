"""
Vista de Administración del Pipeline de Nodos (ComfyUI Style) — VideoPro Studio
Permite visualizar, editar y conmutar entre los Pipelines ComfyUI especializados por Arquetipo.
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
STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "investigaciones", "capacidades", "comfy_pipeline_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "investigaciones", "capacidades", "comfy_pipeline_studio.html")


def render_comfy_pipeline_view():
    """Renderiza el Administrador de Flujo de Nodos estilo ComfyUI dentro de VideoPro."""
    
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                🎛️ Pipeline ComfyUI & Arquitectura de Nodos
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">SPECIALIZED WORKFLOWS</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Conmuta y edita la topología de nodos ComfyUI específica para cada tipo de contenido: Animación 3D, Documental Histórico con Scraping, Rutas Urbanas o Shorts Virales.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Selector de Pipeline / Arquetipo
    c_sel1, c_sel2 = st.columns([6, 4], vertical_alignment="center")
    with c_sel1:
        pipe_options = ["MASTER"] + list(ARCHETYPES_CATALOG.keys())
        selected_pipe = st.selectbox(
            "Seleccionar Pipeline ComfyUI a Visualizar / Editar:",
            options=pipe_options,
            index=0,
            format_func=lambda x: "🎬 Grafo Maestro de Producción (10 Nodos)" if x == "MASTER" else f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name}"
        )

    with c_sel2:
        pipe_view_mode = st.segmented_control(
            "Modo de Visualización:",
            options=["studio", "native"],
            default="studio",
            format_func=lambda x: "🎛️ Lienzo ComfyUI (Canvas 60 FPS)" if x == "studio" else "🌲 Árbol Modular (Python)",
            key="pipeline_view_mode_selector"
        ) if hasattr(st, "segmented_control") else st.radio(
            "Modo de Visualización:",
            options=["studio", "native"],
            index=0,
            format_func=lambda x: "🎛️ Lienzo ComfyUI (Canvas 60 FPS)" if x == "studio" else "🌲 Árbol Modular (Python)",
            horizontal=True,
            key="pipeline_view_mode_selector"
        )

    # 2. Cargar estado del grafo según la selección
    if selected_pipe == "MASTER":
        graph_data = pipeline.load_pipeline_graph()
    else:
        arch_obj = ARCHETYPES_CATALOG.get(selected_pipe)
        graph_data = arch_obj.pipeline_graph if arch_obj else pipeline.load_pipeline_graph()

    nodes = graph_data.get("nodes", [])
    connections = graph_data.get("connections", [])
    active_nodes = sum(1 for n in nodes if n.get("enabled", True))
    loop_nodes = sum(1 for n in nodes if n.get("is_loop", False))

    # 3. Métricas del Pipeline Activo
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

    # 4. Renderizado Dual-Mode (Studio Canvas / Árbol Nativo)
    canvas_rendered = False
    if pipe_view_mode == "studio" and os.path.isfile(STUDIO_HTML_PATH):
        try:
            with open(STUDIO_HTML_PATH, "r", encoding="utf-8") as f:
                html_content = f.read()

            from app.core.providers import registry as prov_reg
            current_registry = prov_reg.load_registry()

            # Inyectar el estado del grafo y la base de datos viva de proveedores en tiempo de renderizado
            injected_script = f"""<script>
                window.INJECTED_PIPELINE_DATA = {json.dumps(graph_data)};
                window.INJECTED_PROVIDERS_REGISTRY = {json.dumps(current_registry)};
            </script>"""
            if "</body>" in html_content:
                html_content = html_content.replace("</body>", f"{injected_script}</body>")
            else:
                html_content += injected_script

            components.html(html_content, height=860, scrolling=False)
            canvas_rendered = True
        except Exception as ex:
            st.warning(f"Aviso al cargar lienzo ComfyUI: {ex}. Conmutando a vista de árbol nativo.")

    # Fallback o vista nativa directa 100% Python
    if not canvas_rendered:
        _render_native_pipeline_tree(graph_data)


def _render_native_pipeline_tree(graph_data: dict):
    """Renderiza una vista nativa en árbol 100% Python/Streamlit del pipeline."""
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

            badge_loop = " 🔁 <i>Loop Escena</i>" if is_loop else ""
            badge_status = "🟢 <b>ACTIVO</b>" if enabled else "⚪ <i>DESACTIVADO</i>"

            with st.expander(f"{title} — {badge_status}", expanded=True):
                st.markdown(f"<div style='border-left: 3px solid {color}; padding-left: 8px; margin-bottom: 6px; font-size: 11px; color: #94a3b8;'>ID: <code>{node_id}</code> | Categoría: <code>{node.get('category', 'general')}</code>{badge_loop}</div>", unsafe_allow_html=True)
                
                if params:
                    st.markdown("**Parámetros Configurables:**")
                    for p in params:
                        p_k = p.get("key", "param")
                        p_lbl = p.get("label", p_k)
                        p_val = p.get("value", "")
                        p_type = p.get("type", "text")
                        
                        if p_type == "select":
                            st.selectbox(p_lbl, options=p.get("options", [p_val]), index=0, key=f"native_{node_id}_{p_k}")
                        elif p_type == "number":
                            st.number_input(p_lbl, value=int(p_val if str(p_val).isdigit() else 0), key=f"native_{node_id}_{p_k}")
                        else:
                            st.text_input(p_lbl, value=str(p_val), key=f"native_{node_id}_{p_k}")

    st.markdown("<hr style='margin: 12px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
    with st.expander("🔌 Ver Mapa de Conexiones Bezier de Datos (Sockets)", expanded=False):
        for conn in connections:
            st.markdown(f"• `[{conn.get('from_node')}]` ➔ <b>{conn.get('from_socket')}</b> ───► `[{conn.get('to_node')}]` ➔ <b>{conn.get('to_socket')}</b> (Tipo: <code>{conn.get('payload_type', 'any')}</code>)", unsafe_allow_html=True)
