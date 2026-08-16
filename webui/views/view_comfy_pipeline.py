"""
Vista de Administración del Pipeline de Nodos (ComfyUI Style) — VideoPro Studio
Permite visualizar, editar y ejecutar el grafo de flujo interactivo del generador de vídeo.
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components

from app.config import config
from app.controllers.v1 import pipeline
from app.services import firebase_sync

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
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">ENGINEERING STUDIO</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Representación visual interactiva 100% real del flujo del generador: guion, síntesis de voz, alineación fonética, generación visual, ducking y renderizado máster.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Cargar estado actual del grafo
    graph_data = pipeline.load_pipeline_graph()
    nodes = graph_data.get("nodes", [])
    connections = graph_data.get("connections", [])

    active_nodes = sum(1 for n in nodes if n.get("enabled", True))
    loop_nodes = sum(1 for n in nodes if n.get("is_loop", False))

    # 2. Métricas del Pipeline & Selector de Modo
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Nodos", f"{active_nodes}/{len(nodes)} Activos")
    with m2:
        st.metric("Conexiones Bezier", f"{len(connections)} Cables")
    with m3:
        st.metric("Bucles de Escena", f"{loop_nodes} Loops")
    with m4:
        st.metric("Persistencia", "🟢 Firestore Sync")

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    col_pipe_hdr, col_pipe_mode = st.columns([6, 4], vertical_alignment="center")
    with col_pipe_hdr:
        st.caption("Arquitectura modular y cableado de datos del generador de vídeo.")
    with col_pipe_mode:
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

    # 3. Renderizado Dual-Mode (Studio Canvas / Árbol Nativo)
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

    st.markdown("### 🌲 Topología Modular de Nodos")
    
    col_t1, col_t2 = st.columns([1, 1])
    for idx, node in enumerate(nodes):
        target_col = col_t1 if idx % 2 == 0 else col_t2
        with target_col:
            node_id = node.get("id", f"node_{idx}")
            title = node.get("title", node_id)
            color = node.get("color", "#38bdf8")
            enabled = node.get("enabled", True)
            is_loop = node.get("is_loop", False)
            category = node.get("category", "general")

            with st.expander(f"{title} ({'🟢 ACTIVO' if enabled else '⚪ DESACTIVADO'})", expanded=enabled):
                c_n1, c_n2 = st.columns([7, 3])
                with c_n1:
                    st.markdown(f"<div style='font-size:12px; color:#94a3b8;'>ID: <code>{node_id}</code> · Categoría: <b>{category.upper()}</b></div>", unsafe_allow_html=True)
                with c_n2:
                    new_en = st.toggle("Activo", value=enabled, key=f"nat_pipe_tog_{node_id}")
                    if new_en != enabled:
                        node["enabled"] = new_en
                        pipeline.save_pipeline_graph(graph_data)
                        st.toast(f"Nodo {title} actualizado.")
                        st.rerun()

                # Parámetros del nodo
                params = node.get("parameters", [])
                if params:
                    st.markdown("<div style='font-size:11px; font-weight:700; color:#38bdf8; margin-top:4px;'>⚙️ Parámetros:</div>", unsafe_allow_html=True)
                    for p in params:
                        k = p.get("key", "")
                        lbl = p.get("label", k)
                        v = p.get("value", "")
                        st.markdown(f"<div style='font-size:11.5px; color:#cbd5e1;'>• <b>{lbl}:</b> <code>{v}</code></div>", unsafe_allow_html=True)

                # Conexiones entrantes y salientes
                in_cables = [c for c in connections if c.get("to_node") == node_id]
                out_cables = [c for c in connections if c.get("from_node") == node_id]

                if in_cables:
                    st.markdown("<div style='font-size:11px; font-weight:700; color:#34d399; margin-top:6px;'>📥 Entradas:</div>", unsafe_allow_html=True)
                    for ic in in_cables:
                        st.markdown(f"<div style='font-size:11px; color:#94a3b8;'>← Desde <code>{ic.get('from_node')}</code> [{ic.get('from_socket')}] ➔ [{ic.get('to_socket')}]</div>", unsafe_allow_html=True)

                if out_cables:
                    st.markdown("<div style='font-size:11px; font-weight:700; color:#facc15; margin-top:6px;'>📤 Salidas:</div>", unsafe_allow_html=True)
                    for oc in out_cables:
                        st.markdown(f"<div style='font-size:11px; color:#94a3b8;'>→ Hacia <code>{oc.get('to_node')}</code> [{oc.get('from_socket')}] ➔ [{oc.get('to_socket')}]</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("⚡ Trazar y Probar Flujo", use_container_width=True, key="btn_nat_trace_pipe"):
            res = pipeline.trace_pipeline_execution({"project_id": "test_trace"})
            st.success(f"Flujo trazado con éxito: {len(res.get('execution_trace', []))} pasos evaluados.")
    with c_btn2:
        if st.button("💾 Guardar y Sincronizar Pipeline en Firestore", type="primary", use_container_width=True, key="btn_nat_save_pipe"):
            pipeline.save_pipeline_graph(graph_data)
            st.toast("✅ Grafo de pipeline persistido en Firestore.")
