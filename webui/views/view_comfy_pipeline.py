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

    # 2. Métricas del Pipeline
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Nodos", f"{active_nodes}/{len(nodes)} Activos")
    with m2:
        st.metric("Conexiones Bezier", f"{len(connections)} Cables")
    with m3:
        st.metric("Bucles de Escena", f"{loop_nodes} Loops")
    with m4:
        st.metric("Persistencia", "🟢 Firestore Sync")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 3. Leer y renderizar el HTML interactivo de ComfyUI
    if os.path.isfile(STUDIO_HTML_PATH):
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
    else:
        st.error("No se encontró el archivo de interfaz comfy_pipeline_studio.html.")
