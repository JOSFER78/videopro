"""
Vista de Administración del Pipeline de Nodos & Catálogo de Workflows — VideoPro Studio
Organización integral de Workflows por Arquetipo, Visualización en Lienzo de Nodos y Sincronización con Producción.
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components

from app.config import config
from app.controllers.v1 import pipeline
from app.services import firebase_sync
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG, get_all_archetypes, get_archetype
from app.core.orchestration.videopro_system_registry import SYSTEM_WORKFLOWS, SYSTEM_NODES, SYSTEM_CAPABILITIES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "dashboards_y_estudios_web", "comfy_pipeline_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "dashboards_y_estudios_web", "workflow_designer_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "investigaciones", "capacidades", "workflow_designer_studio.html")
if not os.path.isfile(STUDIO_HTML_PATH):
    STUDIO_HTML_PATH = os.path.join(BASE_DIR, "docs", "investigaciones", "capacidades", "comfy_pipeline_studio.html")


@st.cache_data(show_spinner=False)
def _load_cached_studio_html(path: str) -> str:
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def render_comfy_canvas_component(graph_data: dict, height: int = 940) -> bool:
    """Renderiza el lienzo interactivo estilo ComfyUI con inyección del grafo y proveedores en tiempo real."""
    if not os.path.isfile(STUDIO_HTML_PATH):
        return False
    try:
        html_content = _load_cached_studio_html(STUDIO_HTML_PATH)
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

        components.html(html_content, height=height, scrolling=False)
        return True
    except Exception as ex:
        st.warning(f"Aviso al cargar lienzo de nodos: {ex}. Conmutando a vista de árbol nativo.")
        return False


def render_comfy_pipeline_view():
    """Renderiza la vista completa de Workflows: Catálogo Organizado, Lienzo de Nodos, Topología y Matriz."""
    
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                🏛️ Workflow Studio & Catálogo de Pipelines
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">WORKFLOWS & PIPELINES SYNC</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Organización de Workflows por Arquetipo, Explicación Modular de Nodos, Lienzo Interactivo y Sincronización en Producción.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Tabs de navegación interna de Workflows
    tab_catalog, tab_canvas, tab_topology, tab_matrix, tab_learning = st.tabs([
        "🗂️ Catálogo & Organización de Workflows",
        "🏛️ Lienzo de Nodos Interactivo (Canvas)",
        "🌲 Topología Modular de Nodos",
        "📊 Matriz Comparativa de Capacidades",
        "🧠 Motor de Aprendizaje & Memoria de Experiencia"
    ])

    # =========================================================================
    # TAB 1: CATÁLOGO Y ORGANIZACIÓN DE WORKFLOWS
    # =========================================================================
    with tab_catalog:
        _render_workflows_catalog()

    # =========================================================================
    # TAB 2: LIENZO DE NODOS INTERACTIVO (CANVAS)
    # =========================================================================
    with tab_canvas:
        _render_interactive_canvas_tab()

    # =========================================================================
    # TAB 3: TOPOLOGÍA MODULAR DE NODOS
    # =========================================================================
    with tab_topology:
        _render_topology_tab()

    # =========================================================================
    # TAB 4: MATRIZ COMPARATIVA DE CAPACIDADES
    # =========================================================================
    with tab_matrix:
        _render_matrix_tab()

    # =========================================================================
    # TAB 5: MOTOR DE APRENDIZAJE & MEMORIA DE EXPERIENCIA
    # =========================================================================
    with tab_learning:
        _render_learning_memory_tab()



def _render_workflows_catalog():
    """Renderiza el catálogo organizado de todos los workflows con tarjetas explicativas ricas."""
    
    # 1. Franja de KPIs del Sistema de Producción
    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    with c_k1:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #1e293b; border-radius: 8px; padding: 8px 12px; border-left: 3px solid #38bdf8;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">WORKFLOWS MAESTROS</div>
                <div style="font-size: 17px; font-weight: 800; color: #f8fafc;">8 Arquetipos</div>
            </div>
        """, unsafe_allow_html=True)
    with c_k2:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #1e293b; border-radius: 8px; padding: 8px 12px; border-left: 3px solid #c084fc;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">NODOS DISPONIBLES</div>
                <div style="font-size: 17px; font-weight: 800; color: #f8fafc;">48 Módulos</div>
            </div>
        """, unsafe_allow_html=True)
    with c_k3:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #1e293b; border-radius: 8px; padding: 8px 12px; border-left: 3px solid #34d399;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">MOTORES GENERATIVOS</div>
                <div style="font-size: 17px; font-weight: 800; color: #f8fafc;">14 Capacidades</div>
            </div>
        """, unsafe_allow_html=True)
    with c_k4:
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #1e293b; border-radius: 8px; padding: 8px 12px; border-left: 3px solid #fbbf24;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">SINCRONIZACIÓN</div>
                <div style="font-size: 17px; font-weight: 800; color: #f8fafc;">100% Producción</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. Barra de Filtro y Búsqueda
    c_f1, c_f2, c_f3 = st.columns([5, 4, 3], vertical_alignment="center")
    with c_f1:
        cat_filter = st.selectbox(
            "Filtrar por Categoría / Nicho:",
            options=["TODAS", "travel_fpv_action", "documentary", "storytelling", "educational", "social_media", "music_travel"],
            format_func=lambda x: {
                "TODAS": "🌐 Todas las Categorías (8 Workflows)",
                "travel_fpv_action": "🛰️ ChronoDrift & Tours Urbanos FPV",
                "documentary": "📜 Documental & Archivo Histórico",
                "storytelling": "🧸 Cuentos & Animación 3D",
                "educational": "📊 Videoensayos & Divulgación (Vox)",
                "social_media": "⚡ Viral Shorts & Retención",
                "music_travel": "🏙️ Rutas Musicales (City Beats)"
            }.get(x, x),
            key="cat_filter_selector"
        )
    with c_f2:
        aspect_filter = st.selectbox(
            "Filtrar por Formato / Aspect Ratio:",
            options=["TODOS", "16:9", "9:16"],
            format_func=lambda x: "📐 Todos los Formatos" if x == "TODOS" else f"📐 Formato {x} ({'Panorámico YouTube' if x == '16:9' else 'Vertical Shorts/TikTok'})",
            key="aspect_filter_selector"
        )
    with c_f3:
        search_query = st.text_input("🔍 Buscar Workflow...", placeholder="Ej: FPV, Pixar, 4K, Vox...", key="search_wf_input")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 3. Listado Organizado de Tarjetas de Workflows
    archetypes = get_all_archetypes()
    filtered = []
    for arch in archetypes:
        if cat_filter != "TODAS" and arch.category != cat_filter:
            continue
        if aspect_filter != "TODOS" and arch.default_aspect_ratio != aspect_filter:
            continue
        if search_query.strip():
            q = search_query.lower()
            match = (
                q in arch.name.lower() or
                q in arch.description.lower() or
                q in arch.tag.lower() or
                q in arch.category.lower() or
                q in arch.target_audience.lower()
            )
            if not match:
                continue
        filtered.append(arch)

    if not filtered:
        st.info("No se encontraron workflows con los filtros seleccionados.")
        return

    # Renderizar cada tarjeta de Workflow con estética premium
    for arch in filtered:
        nodes = arch.pipeline_graph.get("nodes", [])
        node_titles = [n.get("title", n.get("id", "Nodo")) for n in nodes]
        
        with st.container(border=True):
            # Encabezado de la Tarjeta
            c_h1, c_h2 = st.columns([8, 4], vertical_alignment="center")
            with c_h1:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                        <span style="font-size: 24px;">{arch.icon}</span>
                        <div>
                            <span style="font-size: 16px; font-weight: 700; color: #f8fafc;">{arch.name}</span>
                            <span style="font-size: 10.5px; font-weight: 600; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">
                                {arch.tag}
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with c_h2:
                strat_label = getattr(arch.visual_strategy, "value", str(arch.visual_strategy)).upper()
                st.markdown(f"""
                    <div style="text-align: right; font-size: 11px; color: #94a3b8;">
                        <span style="background: #1e293b; padding: 3px 8px; border-radius: 4px; border: 1px solid #334155;">📐 {arch.default_aspect_ratio}</span>
                        <span style="background: #1e293b; padding: 3px 8px; border-radius: 4px; border: 1px solid #334155; margin-left: 4px;">🎬 {strat_label}</span>
                    </div>
                """, unsafe_allow_html=True)

            # Descripción y Público Objetivo
            st.markdown(f"""
                <p style="font-size: 12.5px; color: #cbd5e1; margin: 4px 0 8px 0; line-height: 1.45;">
                    {arch.description}
                </p>
                <div style="font-size: 11.5px; color: #94a3b8; margin-bottom: 8px;">
                    🎯 <b>Público Objetivo / Canal:</b> {arch.target_audience}
                </div>
            """, unsafe_allow_html=True)

            # Cadena de Nodos (Diagrama de Pasos)
            if node_titles:
                st.markdown("**🔗 Secuencia de Nodos del Pipeline:**")
                badges_html = " ".join([
                    f"<span style='display:inline-block; background: #0f172a; border: 1px solid #334155; color: #38bdf8; font-size: 11px; font-weight: 500; padding: 3px 7px; border-radius: 5px; margin: 2px 2px;'>{idx+1}. {t}</span>" +
                    (" <span style='color: #64748b; font-size: 10px;'>➔</span>" if idx < len(node_titles) - 1 else "")
                    for idx, t in enumerate(node_titles)
                ])
                st.markdown(f"<div style='margin-bottom: 10px; line-height: 1.9;'>{badges_html}</div>", unsafe_allow_html=True)

            # Fila de Parámetros Clave
            c_p1, c_p2, c_p3, c_p4 = st.columns(4)
            with c_p1:
                st.caption(f"🎙️ **Locución:** `{arch.default_voice_engine}` ({arch.default_voice_id})")
            with c_p2:
                st.caption(f"🎵 **BGM:** `{arch.default_music_genre}`")
            with c_p3:
                st.caption(f"🧱 **Módulos:** `{len(nodes)} Nodos Activos`")
            with c_p4:
                st.caption(f"⚙️ **Preguntas CoT:** `{len(arch.interview_schema)} Pasos`")

            # Botones de Acción
            c_b1, c_b2, c_b3 = st.columns([4, 4, 4])
            with c_b1:
                if st.button(f"👁️ Cargar en Lienzo de Nodos", key=f"btn_load_canvas_{arch.id}", use_container_width=True):
                    st.session_state["pipeline_selected_archetype"] = arch.id
                    st.toast(f"Cargado «{arch.name}» en el Lienzo de Nodos.")
                    st.rerun()
            with c_b2:
                if st.button(f"🚀 Usar en Co-Creación", type="primary", key=f"btn_cocreate_{arch.id}", use_container_width=True):
                    try:
                        from webui.views.view_studio_orchestrator import _init_director_session
                        _init_director_session(arch.id)
                    except Exception:
                        st.session_state["director_arch_id"] = arch.id
                    st.session_state["active_view"] = "studio"
                    st.rerun()
            with c_b3:
                with st.popover("📋 Ver Esquema & Preguntas", use_container_width=True):
                    st.markdown(f"#### 📋 Esquema de Producción: {arch.name}")
                    st.markdown(f"**Categoría:** `{arch.category}` | **Versión:** `{arch.version}`")
                    st.markdown("**Preguntas de la Entrevista Narrativa:**")
                    for q_idx, q in enumerate(arch.interview_schema, 1):
                        st.markdown(f"**{q_idx}. {q.question}**")
                        st.caption(f"• Tipo: `{q.question_type}` | Valor por defecto: `{q.default_value}`")
                        if q.options:
                            st.caption(f"• Opciones: {', '.join(q.options)}")


def _render_interactive_canvas_tab():
    """Renderiza el lienzo visual ComfyUI con selector de workflow y asistente agéntico Hermes."""
    
    # 1. Asistente Agéntico de Investigación & Reconfiguración Dinámica
    with st.expander("🔬 Hermes Research Agent — Reconfiguración Dinámica del Pipeline", expanded=False):
        st.caption("Introduce cualquier tema o requisito de investigación para que Hermes ajuste los nodos, motores y parámetros del flujo en tiempo real.")
        c_p_in, c_p_btn = st.columns([8, 2], vertical_alignment="bottom")
        with c_p_in:
            agent_prompt = st.text_input(
                "Petición de Investigación o Modificación del Flujo:",
                placeholder="Ej: Documental histórico sobre la construcción del Golden Gate con fotos de hemerotecas y recreación 35mm...",
                key="pipeline_agent_prompt_input_canvas"
            )
        with c_p_btn:
            if st.button("⚡ Investigar & Reconfigurar", type="primary", use_container_width=True, key="btn_agent_investigate_canvas"):
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

    # 2. Selector de Pipeline / Arquetipo de Vídeo
    c_sel1, c_sel2, c_sel3 = st.columns([6, 3, 3], vertical_alignment="center")
    
    pipe_options = ["MASTER"] + list(ARCHETYPES_CATALOG.keys())
    cur_selected = st.session_state.get("pipeline_selected_archetype", "MASTER")
    default_idx = pipe_options.index(cur_selected) if cur_selected in pipe_options else 0

    with c_sel1:
        selected_pipe = st.selectbox(
            "Seleccionar Pipeline a Visualizar / Modificar:",
            options=pipe_options,
            index=default_idx,
            format_func=lambda x: "🎬 Grafo Maestro Activo (Sincronizado con Producción)" if x == "MASTER" else f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name} ({ARCHETYPES_CATALOG[x].category.upper()})",
            key="main_pipeline_selector_canvas"
        )
        if selected_pipe != st.session_state.get("pipeline_selected_archetype"):
            st.session_state["pipeline_selected_archetype"] = selected_pipe

    with c_sel2:
        if st.button("🔄 Restablecer Canónico", use_container_width=True, help="Restaura la configuración canónica de los nodos", key="btn_reset_canonical"):
            pipeline.reset_pipeline_graph_to_canonical()
            st.success("Grafo restablecido a valores canónicos.")
            st.rerun()

    with c_sel3:
        if selected_pipe != "MASTER" and selected_pipe in ARCHETYPES_CATALOG:
            if st.button("🚀 Rodar este Workflow", type="primary", use_container_width=True, key="btn_canvas_goto_director"):
                try:
                    from webui.views.view_studio_orchestrator import _init_director_session
                    _init_director_session(selected_pipe)
                except Exception:
                    st.session_state["director_arch_id"] = selected_pipe
                st.session_state["active_view"] = "studio"
                st.rerun()

    # 3. Cargar estado del grafo según la selección
    if selected_pipe == "MASTER":
        graph_data = pipeline.load_pipeline_graph()
    else:
        arch_obj = ARCHETYPES_CATALOG.get(selected_pipe)
        graph_data = arch_obj.pipeline_graph if arch_obj else pipeline.load_pipeline_graph()

    # 4. Renderizado Principal del Lienzo Visual ComfyUI (Full Hero Canvas)
    canvas_ok = render_comfy_canvas_component(graph_data, height=940)
    
    if not canvas_ok:
        st.warning("Aviso: cargando vista de respaldo...")
        _render_native_pipeline_tree(graph_data, selected_pipe)


def _render_topology_tab():
    """Renderiza el desglose nodo a nodo con parámetros configurables y sockets."""
    pipe_options = ["MASTER"] + list(ARCHETYPES_CATALOG.keys())
    cur_selected = st.session_state.get("pipeline_selected_archetype", "MASTER")
    default_idx = pipe_options.index(cur_selected) if cur_selected in pipe_options else 0

    c_s1, c_s2 = st.columns([8, 4], vertical_alignment="center")
    with c_s1:
        sel_pipe_top = st.selectbox(
            "Seleccionar Pipeline para Configurar Nodos:",
            options=pipe_options,
            index=default_idx,
            format_func=lambda x: "🎬 Grafo Maestro Activo" if x == "MASTER" else f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name}",
            key="topology_pipeline_selector"
        )
    with c_s2:
        st.caption("Ajusta parámetros, activa o desactiva nodos y guarda en el motor de ejecución.")

    if sel_pipe_top == "MASTER":
        graph_data = pipeline.load_pipeline_graph()
    else:
        arch_obj = ARCHETYPES_CATALOG.get(sel_pipe_top)
        graph_data = arch_obj.pipeline_graph if arch_obj else pipeline.load_pipeline_graph()

    _render_native_pipeline_tree(graph_data, sel_pipe_top)


def _render_matrix_tab():
    """Renderiza la matriz comparativa de los 8 Arquetipos y sus capacidades técnicas."""
    st.markdown("### 📊 Matriz Comparativa de Workflows & Capacidades")
    st.caption("Comparación técnica de relaciones de aspecto, estrategias de vídeo, motores de voz, géneros BGM y número de etapas.")

    archetypes = get_all_archetypes()
    
    matrix_data = []
    for arch in archetypes:
        nodes = arch.pipeline_graph.get("nodes", [])
        matrix_data.append({
            "Workflow": f"{arch.icon} {arch.name}",
            "ID": arch.id,
            "Categoría": arch.category,
            "Formato": arch.default_aspect_ratio,
            "Estrategia Visual": getattr(arch.visual_strategy, "value", str(arch.visual_strategy)),
            "Motor Voz": arch.default_voice_engine,
            "Género BGM": arch.default_music_genre,
            "Nodos": len(nodes),
            "Público Objetivo": arch.target_audience
        })

    import pandas as pd
    df = pd.DataFrame(matrix_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 🏛️ Arquitectura de Producción de 4 Niveles")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown("""
            - **Nivel 1 (APIs Base):** Replicate, VibeVoice Serverless, Pexels, Wikimedia Commons, Remotion React, Cloudflare R2, Firebase.
            - **Nivel 2 (Capacidades):** Ingesta 4K, Audio-First Beat Sync, Scraping de Archivos, Generación de Keyframes, Motion HUD.
        """)
    with c_m2:
        st.markdown("""
            - **Nivel 3 (Nodos):** Módulos coordinados de Investigación, Audio, Ingesta, Motion Graphics, Masterización y QA.
            - **Nivel 4 (Workflows):** Pipelines completos para canales de YouTube optimizados por nicho y estilo audiovisual.
        """)


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
    if st.button("💾 Guardar y Aplicar Cambios al Workflow Activo", type="primary", use_container_width=True, key="btn_save_topology_changes"):
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


def _render_learning_memory_tab():
    """Renderiza el Tab 5: Motor de Aprendizaje & Memoria de Experiencia Continua."""
    from app.services.learning_memory_engine import learning_engine
    from app.models.learning_experience import (
        LearnedLesson, ProjectCritiqueFeedback,
        LessonCategory, LessonSeverity, ProviderExecutionMetric, ProviderExecutionMode
    )

    all_lessons = learning_engine.get_all_lessons()
    all_critiques = learning_engine.get_all_critiques()
    all_metrics = learning_engine.get_provider_metrics()
    critical_rules_count = sum(1 for l in all_lessons if l.severity == LessonSeverity.CRITICAL)

    # Encabezado y Badges
    st.markdown("""
        <div style="background: radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.15) 0%, rgba(15, 23, 42, 0.8) 90%); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0; font-size: 18px; font-weight: 800; color: #f1f5f9; display: flex; align-items: center; gap: 8px;">
                        🧠 Motor de Aprendizaje & Memoria de Experiencia
                        <span style="font-size: 11px; background: rgba(139, 92, 246, 0.25); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.4); padding: 2px 8px; border-radius: 10px; font-weight: 700;">SELF-LEARNING LOOP</span>
                    </h3>
                    <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8;">
                        Captura continua de experiencia de producción, auditoría de errores pasados (anti-patrones), estándares dorados inmutables y optimización multi-proveedor sincronizada en Firebase Firestore.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Métricas Globales en 4 Columnas
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Lecciones & Reglas", f"{len(all_lessons)}", help="Reglas aprendidas activas aplicadas antes de cada rodaje")
    with m_col2:
        st.metric("Reglas Críticas", f"{critical_rules_count}", delta="Inmutables", help="Reglas estrictas no negociables (ej. ritmo visual 3s, tipografía limpia)")
    with m_col3:
        st.metric("Críticas Post-Rodaje", f"{len(all_critiques)}", help="Evaluaciones de calidad registradas para proyectos finalizados")
    with m_col4:
        st.metric("Rutas Multi-Proveedor", f"{len(all_metrics)}", help="Proveedores calibrados (Free ZeroGPU vs Replicate vs RunPod vs Local)")

    # Barra de acciones de sincronización con Firestore
    sync_c1, sync_c2 = st.columns([1, 1])
    with sync_c1:
        if st.button("☁️ Sincronizar Memoria Completa en Firebase Firestore", type="primary", use_container_width=True, key="btn_sync_learning_fb"):
            with st.spinner("Sincronizando lecciones, críticas y métricas en Firestore..."):
                ok, msg = learning_engine.sync_to_firebase()
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ Error al sincronizar: {msg}")
    with sync_c2:
        if st.button("📥 Descargar Memoria desde Firebase Firestore", use_container_width=True, key="btn_load_learning_fb"):
            with st.spinner("Descargando memoria de aprendizaje de Firestore..."):
                ok, msg = learning_engine.load_from_firebase()
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.warning(f"⚠️ {msg}")

    st.markdown("<hr style='margin: 16px 0; border-color: #1e293b;'>", unsafe_allow_html=True)

    # Sub-tabs del Motor de Aprendizaje
    subtab_lessons, subtab_critiques, subtab_providers, subtab_new_lesson = st.tabs([
        "📜 Estándares Dorados & Anti-Patrones",
        "📝 Historial de Críticas & Evaluaciones",
        "⚡ Despacho Multi-Proveedor (FLUX.3 / APIs)",
        "➕ Registrar Nueva Lección"
    ])

    # =========================================================================
    # SUBTAB 1: ESTÁNDARES DORADOS & ANTI-PATRONES
    # =========================================================================
    with subtab_lessons:
        st.markdown("##### 📚 Catálogo de Reglas y Directrices Extraídas de la Experiencia")
        
        # Filtros
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
        with f_col1:
            cat_options = ["TODAS"] + [c.value for c in LessonCategory]
            sel_category = st.selectbox("Filtrar por Categoría:", cat_options, key="sel_lesson_cat")
        with f_col2:
            sev_options = ["TODAS"] + [s.value for s in LessonSeverity]
            sel_severity = st.selectbox("Filtrar por Severidad:", sev_options, key="sel_lesson_sev")
        with f_col3:
            all_nodes_in_lessons = sorted(list(set(n for l in all_lessons for n in l.applicable_nodes)))
            node_options = ["TODOS"] + all_nodes_in_lessons
            sel_node = st.selectbox("Filtrar por Nodo:", node_options, key="sel_lesson_node")

        filtered_lessons = all_lessons
        if sel_category != "TODAS":
            filtered_lessons = [l for l in filtered_lessons if l.category.value == sel_category]
        if sel_severity != "TODAS":
            filtered_lessons = [l for l in filtered_lessons if l.severity.value == sel_severity]
        if sel_node != "TODOS":
            filtered_lessons = [l for l in filtered_lessons if sel_node in l.applicable_nodes]

        st.caption(f"Mostrando **{len(filtered_lessons)}** de **{len(all_lessons)}** lecciones aprendidas.")

        for idx, lesson in enumerate(filtered_lessons):
            sev_color = "#ef4444" if lesson.severity == LessonSeverity.CRITICAL else ("#f59e0b" if lesson.severity == LessonSeverity.STRICT else "#3b82f6")
            sev_bg = "rgba(239, 68, 68, 0.15)" if lesson.severity == LessonSeverity.CRITICAL else ("rgba(245, 158, 11, 0.15)" if lesson.severity == LessonSeverity.STRICT else "rgba(59, 130, 246, 0.15)")
            
            with st.expander(f"🔹 [{lesson.category.value}] {lesson.title} ({lesson.severity.value})", expanded=(idx == 0)):
                st.markdown(f"""
                    <div style="display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;">
                        <span style="font-size: 11px; background: {sev_bg}; color: {sev_color}; border: 1px solid {sev_color}; padding: 2px 8px; border-radius: 8px; font-weight: 700;">
                            {lesson.severity.value}
                        </span>
                        <span style="font-size: 11px; background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 8px;">
                            ID: <code>{lesson.id}</code>
                        </span>
                        <span style="font-size: 11px; background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 8px; border-radius: 8px;">
                            ⭐ Éxito: {int(lesson.success_rating * 100)}% ({lesson.applied_count} ejecuciones)
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                anti_c, golden_c = st.columns(2)
                with anti_c:
                    st.markdown(f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 10px; border-radius: 0 6px 6px 0; margin-bottom: 8px;">
                            <strong style="color: #f87171;">❌ Anti-Patrón (Causa de Fallo Previa):</strong>
                            <p style="font-size: 12px; color: #cbd5e1; margin: 4px 0 0 0;">{lesson.what_failed}</p>
                        </div>
                    """, unsafe_allow_html=True)
                with golden_c:
                    st.markdown(f"""
                        <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10b981; padding: 10px; border-radius: 0 6px 6px 0; margin-bottom: 8px;">
                            <strong style="color: #4ade80;">✨ Regla Áurea Obligatoria:</strong>
                            <p style="font-size: 12px; color: #cbd5e1; margin: 4px 0 0 0;">{lesson.golden_rule}</p>
                        </div>
                    """, unsafe_allow_html=True)

                nodes_str = ", ".join([f"`{n}`" for n in lesson.applicable_nodes]) if lesson.applicable_nodes else "`TODOS`"
                wf_str = ", ".join([f"`{w}`" for w in lesson.applicable_workflows]) if lesson.applicable_workflows else "`ALL`"
                st.markdown(f"**Nodos Afectados:** {nodes_str}")
                st.markdown(f"**Workflows Vinculados:** {wf_str}")

    # =========================================================================
    # SUBTAB 2: HISTORIAL DE CRÍTICAS & EVALUACIONES
    # =========================================================================
    with subtab_critiques:
        st.markdown("##### 🎙️ Historial de Feedback, Evaluaciones y Críticas de Producción")
        if not all_critiques:
            st.info("No hay evaluaciones registradas aún. Puedes añadir una evaluación manual abajo o desde la pestaña de Proyectos.")
        else:
            for crit in reversed(all_critiques):
                score_color = "#10b981" if crit.overall_score >= 80 else ("#f59e0b" if crit.overall_score >= 60 else "#ef4444")
                with st.expander(f"📋 Feedback Proyecto `{crit.project_id}` — Puntuación: {crit.overall_score}/100 ({crit.timestamp[:10]})", expanded=True):
                    c_h1, c_h2 = st.columns([2, 1])
                    with c_h1:
                        st.markdown(f"""
                            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Transcripción Verbatim del Feedback / Crítica:</div>
                                <div style="font-size: 13px; color: #e2e8f0; font-style: italic;">«{crit.user_feedback_raw}»</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c_h2:
                        st.markdown(f"""
                            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 8px; padding: 12px; text-align: center;">
                                <div style="font-size: 11px; color: #94a3b8;">Calificación Global</div>
                                <div style="font-size: 26px; font-weight: 800; color: {score_color};">{crit.overall_score} / 100</div>
                            </div>
                        """, unsafe_allow_html=True)

                    if crit.critique_breakdown:
                        st.markdown("**Desglose Dimensional:**")
                        bd_cols = st.columns(len(crit.critique_breakdown))
                        for b_idx, (dim, val) in enumerate(crit.critique_breakdown.items()):
                            with bd_cols[b_idx]:
                                st.metric(dim.replace("_", " ").title(), f"{val}/100")

                    if crit.lessons_extracted:
                        st.markdown(f"**Lecciones y Reglas Extraídas:** {', '.join([f'`{r}`' for r in crit.lessons_extracted])}")

    # =========================================================================
    # SUBTAB 3: DESPACHO MULTI-PROVEEDOR (FLUX.3 & APIS)
    # =========================================================================
    with subtab_providers:
        st.markdown("##### ⚡ Matriz de Despacho y Rendimiento Multi-Proveedor")
        st.markdown("Desacoplamiento canónico de capacidades y pasarelas de ejecución (Serverless Free vs APIs vs Dedicated GPU):")

        for metric in all_metrics:
            mode_badge = "🆓 SERVERLESS FREE" if metric.mode == ProviderExecutionMode.FREE_SERVERLESS else ("⚡ DEDICATED GPU" if metric.mode == ProviderExecutionMode.RUNPOD_GPU else ("🌐 REPLICATE API" if metric.mode == ProviderExecutionMode.REPLICATE_API else "🖥️ LOCAL VPS"))

            with st.expander(f"⚙️ {metric.capability_id} ➔ {metric.provider_name} ({mode_badge})", expanded=True):
                p_c1, p_c2, p_c3, p_c4 = st.columns(4)
                with p_c1:
                    st.metric("Modo", mode_badge)
                with p_c2:
                    st.metric("Latencia Media", f"{metric.latency_avg_sec}s")
                with p_c3:
                    st.metric("Tasa de Éxito", f"{int(metric.success_rate * 100)}%")
                with p_c4:
                    st.metric("Coste por Render", f"${metric.cost_per_generation}")

                if metric.notes:
                    st.info(f"💡 **Observaciones:** {metric.notes}")

    # =========================================================================
    # SUBTAB 4: REGISTRAR NUEVA LECCIÓN
    # =========================================================================
    with subtab_new_lesson:
        st.markdown("##### ➕ Registrar Nuevo Estándar Dorado / Regla de Experiencia")
        with st.form("form_new_lesson"):
            nl_id = st.text_input("ID de la Regla (snake_case):", value="rule_new_cinematic_principle")
            nl_title = st.text_input("Título de la Lección:", value="Nuevo Estándar de Calidad")
            nl_cat = st.selectbox("Categoría:", [c.value for c in LessonCategory], index=0)
            nl_sev = st.selectbox("Severidad:", [s.value for s in LessonSeverity], index=1)
            
            col_ap, col_gs = st.columns(2)
            with col_ap:
                nl_ap = st.text_area("Anti-Patrón (Lo que falló en el pasado):", value="Ejemplo del fallo visual o técnico observado.")
            with col_gs:
                nl_gs = st.text_area("Estándar Dorado (Lo que el sistema debe hacer ahora):", value="Directriz de ejecución exacta y no negociable.")

            all_avail_nodes = list(SYSTEM_NODES.keys())
            nl_nodes = st.multiselect("Nodos Aplicables:", options=all_avail_nodes, default=[all_avail_nodes[0]] if all_avail_nodes else [])
            
            all_avail_wf = list(SYSTEM_WORKFLOWS.keys())
            nl_wf = st.multiselect("Workflows Aplicables:", options=all_avail_wf, default=all_avail_wf)

            btn_submit_lesson = st.form_submit_button("💾 Guardar Lección y Sincronizar en Memoria", type="primary")
            if btn_submit_lesson:
                new_lesson_obj = LearnedLesson(
                    id=nl_id.strip(),
                    category=LessonCategory(nl_cat),
                    severity=LessonSeverity(nl_sev),
                    title=nl_title.strip(),
                    what_failed=nl_ap.strip(),
                    golden_rule=nl_gs.strip(),
                    applicable_nodes=nl_nodes,
                    applicable_workflows=nl_wf,
                    success_rating=1.0,
                    applied_count=1
                )
                ok = learning_engine.register_lesson(new_lesson_obj)
                if ok:
                    learning_engine.sync_to_firebase_async()
                    st.success(f"✅ Lección «{nl_title}» guardada y sincronizada.")
                    st.rerun()
                else:
                    st.error("Error al guardar la lección.")

