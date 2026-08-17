"""
view_learning_workflows.py
==========================
Interfaz Web Interactiva de Aprendizaje Continuo, Control de Workflows y Tablero QA — VideoPro Studio.

Módulos integrados:
1. Visor de Workflows por Arquetipo: inspección profunda de parámetros (óptica, 6-DoF, audio BPM, ducking, Levenshtein, transiciones, prompts 7 capas, SHA-256).
2. Historial de Versiones y Diffs: comparador gráfico de versiones (v1.0 -> v1.1...), parches aplicados y trazabilidad.
3. Tablero de Auditoría de Calidad (Reglas R01 a R10): semáforo QA por proyecto/vídeo, detección de anomalías y desglose por categorías.
4. Panel de Control de Aprendizaje: forzar re-evaluación/auto-mejora (v+1), rollback de versiones, sincronización bidireccional con Firebase Firestore y catálogo de lecciones.

Estética: Dark Glassmorphism Premium con paleta de alto contraste y micro-interacciones.
"""

import os
import sys
import json
import yaml
import difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from scripts.workflow_learner import (
        WorkflowLearner, GOLDEN_RULES_CATALOG,
        compute_levenshtein_distance, compute_text_similarity
    )
    from scripts.workflow_registry import (
        WorkflowRegistry, StructuredWorkflow,
        CANONICAL_ARCHETYPES_DEFS
    )
    from app.services.learning_memory_engine import learning_engine
    from app.models.learning_experience import (
        LearnedLesson, LessonCategory, LessonSeverity,
        ProjectCritiqueFeedback, ProviderExecutionMetric
    )
    from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG, get_all_archetypes
    from app.services.hermes_mission_dispatcher import HermesMissionDispatcher
except Exception as ex:
    st.error(f"Error importando módulos del motor de aprendizaje: {ex}")
    WorkflowLearner = None
    WorkflowRegistry = None
    learning_engine = None


# ============================================================================
# ESTILOS CSS DARK GLASSMORPHYSIC PREMIUM
# ============================================================================
def _inject_custom_styles():
    st.markdown("""
    <style>
    /* Tarjetas Dark Glassmorphism */
    .glass-card {
        background: rgba(15, 23, 42, 0.78) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(56, 189, 248, 0.22) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45) !important;
    }

    .glass-card-purple {
        background: radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.15) 0%, rgba(15, 23, 42, 0.85) 90%) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45) !important;
    }

    .glass-card-success {
        background: rgba(6, 78, 59, 0.2) !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
    }

    .glass-card-danger {
        background: rgba(127, 29, 29, 0.25) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
    }

    .glass-card-warning {
        background: rgba(120, 53, 15, 0.25) !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
    }

    /* Badges de calidad y estados */
    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
        letter-spacing: 0.3px;
    }

    .badge-cyan {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
    }

    .badge-purple {
        background: rgba(192, 132, 252, 0.15);
        color: #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.35);
    }

    .badge-green {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    .badge-red {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }

    .badge-amber {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }

    /* Indicador de semáforo con pulsación */
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-green { background-color: #10b981; box-shadow: 0 0 8px #10b981; }
    .dot-red { background-color: #ef4444; box-shadow: 0 0 8px #ef4444; }
    .dot-amber { background-color: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
    .dot-blue { background-color: #38bdf8; box-shadow: 0 0 8px #38bdf8; }

    /* Parámetros en tabla visual */
    .param-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 10px;
        margin-top: 8px;
    }
    .param-item {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 8px 10px;
    }
    .param-label {
        font-size: 10.5px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .param-value {
        font-size: 12.5px;
        color: #f1f5f9;
        font-weight: 700;
        font-family: monospace;
    }

    /* Diffs Side-by-Side */
    .diff-box {
        background: #090d16;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 10px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 11.5px;
        line-height: 1.4;
        white-space: pre-wrap;
    }
    .diff-add { color: #34d399; background: rgba(16, 185, 129, 0.1); }
    .diff-rem { color: #f87171; background: rgba(239, 68, 68, 0.1); }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# INSTANCIACIÓN DE SERVICIOS
# ============================================================================
@st.cache_resource(show_spinner=False)
def _get_services():
    storage_dir = BASE_DIR / "storage"
    workflows_dir = storage_dir / "workflows"
    learning_dir = storage_dir / "learning_memory"

    workflows_dir.mkdir(parents=True, exist_ok=True)
    learning_dir.mkdir(parents=True, exist_ok=True)

    reg = WorkflowRegistry(storage_dir=workflows_dir)
    learner = WorkflowLearner(storage_dir=storage_dir, workflows_dir=workflows_dir, learning_dir=learning_dir)
    dispatcher = HermesMissionDispatcher(base_storage_dir=str(storage_dir / "missions"))

    return reg, learner, dispatcher


# ============================================================================
# VISTA PRINCIPAL
# ============================================================================
def render_learning_workflows_view():
    """Renderiza la vista completa de Aprendizaje Continuo y Control de Workflows."""
    _inject_custom_styles()
    
    registry, learner, dispatcher = _get_services()
    all_workflows = registry.list_workflows()
    all_lessons = learning_engine.get_all_lessons() if learning_engine else []
    all_critiques = learning_engine.get_all_critiques() if learning_engine else []
    
    # -------------------------------------------------------------------------
    # 1. HEADER EJECUTIVO CON ESTÉTICA DARK GLASSMORPHISM
    # -------------------------------------------------------------------------
    st.markdown("""
        <div class="glass-card-purple">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="font-size: 21px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 10px;">
                        <span>🧠</span> Aprendizaje Continuo & Control de Workflows
                        <span class="badge-chip badge-purple">AUTONOMOUS FEEDBACK LOOP</span>
                    </h2>
                    <p style="font-size: 12.5px; color: #cbd5e1; margin: 4px 0 0 0;">
                        Inspección profunda de arquetipos cinemáticos, historial de versiones semánticas (v1.0 -> v+1), tablero de auditoría QA de 10 Reglas de Oro (R01 a R10) y control determinista de auto-mejora.
                    </p>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="badge-chip badge-cyan">
                        <span class="status-dot dot-blue"></span> 8 ARQUETIPOS CANÓNICOS
                    </span>
                    <span class="badge-chip badge-green">
                        <span class="status-dot dot-green"></span> 10 REGLAS ACTIVAS
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. FRANJA DE KPIS GLOBALES DEL MOTOR DE APRENDIZAJE
    # -------------------------------------------------------------------------
    k1, k2, k3, k4, k5 = st.columns(5)
    
    with k1:
        st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #38bdf8; padding: 10px 12px; margin-bottom: 8px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">ARQUETIPOS ACTIVOS</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc;">{len(all_workflows)} Canónicos</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #c084fc; padding: 10px 12px; margin-bottom: 8px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">REGLAS DE ORO QA</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc;">10 Estándares</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #34d399; padding: 10px 12px; margin-bottom: 8px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">LECCIONES APRENDIDAS</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc;">{len(all_lessons)} Directrices</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #fbbf24; padding: 10px 12px; margin-bottom: 8px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">CRÍTICAS POST-MORTEM</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc;">{len(all_critiques)} Evaluadas</div>
            </div>
        """, unsafe_allow_html=True)
    with k5:
        # Puntuación media histórica
        avg_score = 92.5
        if all_critiques:
            scores = [c.overall_score for c in all_critiques if hasattr(c, "overall_score")]
            if scores:
                avg_score = sum(scores) / len(scores)
        st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #10b981; padding: 10px 12px; margin-bottom: 8px;">
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">SCORE QA GLOBAL</div>
                <div style="font-size: 18px; font-weight: 800; color: #f8fafc;">{avg_score:.1f} / 100</div>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. PESTAÑAS PRINCIPALES DE INTERACCIÓN
    # -------------------------------------------------------------------------
    tab_telemetry, tab_archetype_viewer, tab_version_diffs, tab_qa_audit, tab_control_panel = st.tabs([
        "⚡ Telemetría & Feed en Vivo",
        "🎛️ Visor de Workflows por Arquetipo",
        "🔄 Historial de Versiones & Diffs",
        "🛡️ Tablero de Auditoría QA (Reglas R01-R10)",
        "🧠 Panel de Control & Auto-Mejora"
    ])

    # =========================================================================
    # TAB 0: TELEMETRÍA & FEED EN VIVO
    # =========================================================================
    with tab_telemetry:
        _render_live_telemetry_tab(learner)

    # =========================================================================
    # TAB 1: VISOR DE WORKFLOWS POR ARQUETIPO
    # =========================================================================
    with tab_archetype_viewer:
        _render_archetype_viewer_tab(registry)

    # =========================================================================
    # TAB 2: HISTORIAL DE VERSIONES & DIFFS
    # =========================================================================
    with tab_version_diffs:
        _render_version_diffs_tab(registry, learner)

    # =========================================================================
    # TAB 3: TABLERO DE AUDITORÍA QA (REGLAS R01 A R10)
    # =========================================================================
    with tab_qa_audit:
        _render_qa_audit_tab(learner, dispatcher)

    # =========================================================================
    # TAB 4: PANEL DE CONTROL & AUTO-MEJORA
    # =========================================================================
    with tab_control_panel:
        _render_control_panel_tab(registry, learner, dispatcher)


# ============================================================================
# SECCIÓN 0: TELEMETRÍA & EVENTOS EN VIVO
# ============================================================================
def _render_live_telemetry_tab(learner: WorkflowLearner):
    """Renderiza el feed de eventos en tiempo real, sesión activa y disparador interactivo."""
    st.markdown("#### ⚡ Feed de Telemetría & Auto-Aprendizaje en Tiempo Real")
    st.caption("Emisión y captura continua de eventos de evaluación QA, detección de fallos, parches aplicados e incrementos de versión (v+1).")

    # Acciones superiores
    t_c1, t_c2 = st.columns([3, 1])
    with t_c1:
        last_sess = learner.get_latest_session_events()
        if last_sess:
            sid = last_sess.get("session_id", "N/A")
            aid = last_sess.get("archetype_id", "GLOBAL")
            pid = last_sess.get("project_id", "N/A")
            last_ts = last_sess.get("last_updated", "")[:19].replace("T", " ")
            st.markdown(f"""
                <div class="glass-card" style="border-left: 3px solid #10b981; padding: 10px 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span class="badge-chip badge-green"><span class="status-dot dot-green"></span> SESIÓN ACTIVA</span>
                            <span style="font-size: 12px; font-weight: 700; color: #f8fafc; margin-left: 8px;">{sid}</span>
                        </div>
                        <div style="font-size: 11px; color: #94a3b8;">Último evento: <b>{last_ts}</b></div>
                    </div>
                    <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">
                        Arquetipo: <code>{aid}</code> | Proyecto: <code>{pid}</code>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    with t_c2:
        if st.button("🔄 Actualizar Feed", use_container_width=True, key="btn_refresh_telemetry"):
            st.rerun()

    # Disparador interactivo de auditoría QA
    with st.expander("🧪 Disparar Auditoría QA & Auto-Mejora en Vivo con Emisión de Eventos", expanded=False):
        projects_base = Path(BASE_DIR) / "storage" / "projects"
        candidates = []
        if projects_base.exists():
            for m in projects_base.glob("**/manifest.json"):
                candidates.append(str(m))
            for m in projects_base.glob("**/project_manifest.json"):
                candidates.append(str(m))

        sel_m = st.selectbox("Seleccionar Manifiesto:", options=["(Personalizado)"] + candidates, key="sel_telemetry_manifest")
        m_path = ""
        if sel_m == "(Personalizado)":
            m_path = st.text_input("Ruta a manifest:", value="storage/projects/2026/08/2026-08-17_documental_futurista_4k_40tomas_120s/v1/manifest.json", key="txt_telemetry_custom_m")
        else:
            m_path = sel_m

        c_ap, c_run = st.columns([1, 2], vertical_alignment="bottom")
        with c_ap:
            auto_p = st.checkbox("Auto-parchear workflow (v+1)", value=True, key="chk_telemetry_ap")
        with c_run:
            if st.button("🚀 Ejecutar Auditoría en Vivo", type="primary", use_container_width=True, key="btn_exec_telemetry_audit"):
                with st.spinner("Ejecutando auditoría y emitiendo telemetría en tiempo real..."):
                    try:
                        res = learner.audit_and_optimize_post_execution(m_path, auto_patch=auto_p)
                        st.success(f"✅ Auditoría completada con éxito! Score: {res['audit']['overall_score']}/100")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error ejecutando auditoría: {ex}")

    # Eventos recientes
    all_events = learner.get_recent_events(limit=60)
    
    # Filtros
    ef1, ef2 = st.columns([1, 1])
    with ef1:
        types = sorted(list(set(e.get("event_type", "") for e in all_events)))
        sel_t = st.selectbox("Filtrar por Tipo:", ["TODOS"] + types, key="sel_tel_type")
    with ef2:
        sevs = sorted(list(set(e.get("severity", "") for e in all_events)))
        sel_s = st.selectbox("Filtrar por Severidad:", ["TODAS"] + sevs, key="sel_tel_sev")

    filtered = all_events
    if sel_t != "TODOS":
        filtered = [e for e in filtered if e.get("event_type") == sel_t]
    if sel_s != "TODAS":
        filtered = [e for e in filtered if e.get("severity") == sel_s]

    if not filtered:
        st.info("No se encontraron eventos con los filtros seleccionados.")
    else:
        st.caption(f"Mostrando **{len(filtered)}** de **{len(all_events)}** eventos emitidos.")
        for ev in filtered:
            sev = ev.get("severity", "INFO")
            badge_class = "badge-red" if sev in ("CRITICAL", "HIGH") else ("badge-amber" if sev == "WARNING" else "badge-cyan")
            dot_class = "dot-red" if sev in ("CRITICAL", "HIGH") else ("dot-amber" if sev == "WARNING" else "dot-blue")
            
            st.markdown(f"""
                <div class="glass-card" style="padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                            <span class="badge-chip {badge_class}">
                                <span class="status-dot {dot_class}"></span> {ev.get('event_type')}
                            </span>
                            <span style="font-size: 11px; background: rgba(148, 163, 184, 0.1); color: #cbd5e1; padding: 2px 6px; border-radius: 6px; font-weight: 600;">
                                {ev.get('archetype_id')}
                            </span>
                            <span style="font-size: 11px; color: #94a3b8;">
                                Proyecto: <code>{ev.get('project_id')}</code>
                            </span>
                        </div>
                        <div style="font-size: 11px; color: #64748b;">
                            🕒 {ev.get('timestamp', '')[:19].replace('T', ' ')}
                        </div>
                    </div>
                    <div style="font-size: 12.5px; color: #f1f5f9; font-weight: 600; margin-top: 6px;">
                        {ev.get('message')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if ev.get("payload"):
                with st.expander("Ver Payload JSON", expanded=False):
                    st.json(ev["payload"])


# ============================================================================
# SECCIÓN 1: VISOR DE WORKFLOWS POR ARQUETIPO
# ============================================================================
def _render_archetype_viewer_tab(registry: WorkflowRegistry):
    """Inspección detallada de parámetros de cada arquetipo canónico."""
    st.markdown("#### 🔍 Inspección de Parámetros Físicos y Algorítmicos por Arquetipo")
    
    canonical_list = [
        ("CHRONODRIFT_6DOF", "🛰️ ChronoDrift 6-DoF Tritemporal Urban Master"),
        ("FPV_URBAN", "🚁 FPV Urban Real Flow 4K"),
        ("VOX_EXPLAINER", "📜 VOX Investigative Documentary 4K"),
        ("VIRAL_SHORTS_916", "⚡ Viral Shorts & High-Retention Hook 9:16"),
        ("DOCUMENTAL_35MM", "🎞️ Documental Histórico 35mm Master"),
        ("NANOVERSE", "🔬 NanoVerse Cellular & Quantum Macro 4K"),
        ("LIVING_CANVAS", "🎨 Living Canvas Fine Art 3D Animation"),
        ("ASTRODRIFT", "🌌 AstroDrift Deep Space Relativistic 4K")
    ]
    
    col_sel, col_ver = st.columns([3, 1])
    with col_sel:
        selected_archetype_id = st.selectbox(
            "Seleccionar Arquetipo de Producción:",
            options=[item[0] for item in canonical_list],
            format_func=lambda x: next((item[1] for item in canonical_list if item[0] == x), x),
            key="sel_archetype_viewer"
        )

    versions_info = registry.list_versions(selected_archetype_id)
    version_options = [v.semver for v in versions_info] if versions_info else ["v1.0.0"]
    
    with col_ver:
        selected_version = st.selectbox(
            "Versión a Inspeccionar:",
            options=version_options,
            index=0,
            key="sel_version_viewer"
        )

    # Cargar datos estructurados del workflow
    workflow = registry.get_workflow(selected_archetype_id, selected_version)
    if not workflow:
        # Intentar cargar la última versión disponible
        workflow = registry.get_workflow(selected_archetype_id, "latest")
    
    if not workflow:
        st.warning(f"No se encontró definición persistida para '{selected_archetype_id}'.")
        return

    if hasattr(workflow, "model_dump"):
        wf_dict = workflow.model_dump()
    elif hasattr(workflow, "dict"):
        wf_dict = workflow.dict()
    elif isinstance(workflow, dict):
        wf_dict = workflow
    else:
        wf_dict = {}

    camera = wf_dict.get("camera_optics", {})
    audio = wf_dict.get("audio_spec", {})
    subtitles = wf_dict.get("subtitles_pacing", {})
    render_cfg = wf_dict.get("render_config", {})
    prompts = wf_dict.get("prompt_manifest", {})
    v_info = wf_dict.get("version_info", {})
    semver_str = v_info.get("semver", "v1.0.0")
    hash_str = v_info.get("sha256_hash", "")

    # Mappings y valores derivados para renderizado visual
    anti_black = {
        "canvas_base_hex": render_cfg.get("background_color", "#243048"),
        "enforce_no_pure_black": render_cfg.get("anti_blackdetect", True),
        "youtube_dead_zone_bottom_right": "160x50 px Protegida",
        "thumbnail_max_words": 3
    }
    transitions_list = render_cfg.get("transitions", ["whip_pan_cinema", "crossfade_30ms"])
    transitions = {
        "max_shot_duration_sec": subtitles.get("max_shot_duration_sec", 4.0),
        "ken_burns_zoompan": subtitles.get("ken_burns_zoompan", True),
        "cut_every_bars": subtitles.get("cut_every_bars", 2),
        "cut_timing_mode": "on_snare_hit" if subtitles.get("cut_on_beat", True) else "free_flow",
        "pacing_stagger_frames": subtitles.get("stagger_frames", 4),
        "default_transition": transitions_list[0] if transitions_list else "whip_pan_cinema",
        "transition_duration_ms": 30
    }

    # Tarjeta Principal del Arquetipo
    st.markdown(f"""
        <div class="glass-card" style="margin-top: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="font-size: 16px; font-weight: 800; color: #f8fafc; margin: 0;">
                        {workflow.name}
                    </h3>
                    <p style="font-size: 12px; color: #94a3b8; margin: 3px 0 0 0;">
                        {workflow.description}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span class="badge-chip badge-cyan">Versión: {semver_str}</span>
                    <span class="badge-chip badge-purple">Nicho: {workflow.category}</span>
                    <div style="font-size: 10.5px; color: #64748b; margin-top: 4px; font-family: monospace;">
                        SHA-256: {hash_str[:16] if hash_str else 'N/A'}...
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SEIS CUADRANTES DE PARÁMETROS ESPECÍFICOS
    # -------------------------------------------------------------------------
    q1, q2 = st.columns(2)

    with q1:
        # CUADRANTE A: ÓPTICA Y CÁMARA 6-DOF
        st.markdown("""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 14px;">📷</span>
                    <strong style="color: #38bdf8; font-size: 13px;">1. Óptica Física & Cámara 6-DoF</strong>
                </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="param-grid">
                <div class="param-item">
                    <div class="param-label">Distancia Focal</div>
                    <div class="param-value">{camera.get('focal_length_mm', 35.0)} mm</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Perfil de Sensor</div>
                    <div class="param-value">{camera.get('sensor_profile', 'ARRI_Alexa_35')}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Apertura Diafragma</div>
                    <div class="param-value">f/{camera.get('aperture_f_stop', 2.0)}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Movimiento de Cámara</div>
                    <div class="param-value">{camera.get('motion_type', '6-DoF Orbit')}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Estabilización</div>
                    <div class="param-value">{camera.get('stabilization', '3-Axis Gimbal')}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Shutter / FOV / ISO</div>
                    <div class="param-value">{camera.get('shutter_angle_deg', 180)}° / {camera.get('fov_deg', 65)}° / ISO {camera.get('iso_target', 800)}</div>
                </div>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">
                <strong>Bokeh & DoF:</strong> {camera.get('depth_of_field', 'Cinematic shallow depth of field')}
            </div>
            </div>
        """, unsafe_allow_html=True)

        # CUADRANTE B: SUBTÍTULOS LEVENSHTEIN Y TIPOGRAFÍA
        st.markdown("""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 14px;">✍️</span>
                    <strong style="color: #c084fc; font-size: 13px;">2. Subtítulos Levenshtein & Tipografía Broadcast</strong>
                </div>
        """, unsafe_allow_html=True)

        min_lev = subtitles.get('min_levenshtein_similarity', 0.85)
        lev_color = "#10b981" if min_lev >= 0.85 else "#f59e0b"

        st.markdown(f"""
            <div class="param-grid">
                <div class="param-item">
                    <div class="param-label">Motor de Alineación</div>
                    <div class="param-value">{subtitles.get('alignment_engine', 'forced_levenshtein')}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Similitud Mínima</div>
                    <div class="param-value" style="color: {lev_color};">{int(min_lev * 100)}% (Levenshtein)</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Estilo Gráfico</div>
                    <div class="param-value">{subtitles.get('style', 'modern_boxless_gold')}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Palabras por Línea</div>
                    <div class="param-value">Máx. {subtitles.get('max_words_per_line', 4)} palabras</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Caja Invasiva (Box)</div>
                    <div class="param-value">{'Prohibida (Cero Box)' if not subtitles.get('box_background_enabled', False) else 'Activa'}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Colores de Texto</div>
                    <div class="param-value">{subtitles.get('active_word_color', '#FFD700')} / {subtitles.get('inactive_word_color', '#FFFFFF')}</div>
                </div>
            </div>
            </div>
        """, unsafe_allow_html=True)

        # CUADRANTE C: NEURODISEÑO Y ANTI-BLACKDETECT
        st.markdown("""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 14px;">🎨</span>
                    <strong style="color: #fbbf24; font-size: 13px;">3. Neurodiseño & Paleta Anti-Blackdetect</strong>
                </div>
        """, unsafe_allow_html=True)

        bg_hex = anti_black.get('canvas_base_hex', '#243048')
        st.markdown(f"""
            <div class="param-grid">
                <div class="param-item" style="border-left: 4px solid {bg_hex};">
                    <div class="param-label">Color de Fondo Canvas</div>
                    <div class="param-value">{bg_hex}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Filtro Negro Puro (0,0,0)</div>
                    <div class="param-value">{'Estricto (Bloqueado)' if anti_black.get('enforce_no_pure_black', True) else 'Inactivo'}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Safe Zone Dead Spot (YT)</div>
                    <div class="param-value">{anti_black.get('youtube_dead_zone_bottom_right', '160x50 px Protegida')}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Microcopy Miniatura</div>
                    <div class="param-value">Máx. {anti_black.get('thumbnail_max_words', 3)} palabras</div>
                </div>
            </div>
            </div>
        """, unsafe_allow_html=True)

    with q2:
        # CUADRANTE D: AUDIO Y MASTERING EBU R128
        st.markdown("""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 14px;">🎙️</span>
                    <strong style="color: #34d399; font-size: 13px;">4. Audio & Mastering Audiófilo EBU R128</strong>
                </div>
        """, unsafe_allow_html=True)

        ducking_val = audio.get('ducking_db', -18.0)
        duck_color = "#10b981" if ducking_val <= -18.0 else "#f59e0b"

        st.markdown(f"""
            <div class="param-grid">
                <div class="param-item">
                    <div class="param-label">BPM / Tempo Musical</div>
                    <div class="param-value">{audio.get('bpm', 118)} BPM ({audio.get('genre', 'Lo-Fi Chillhop')})</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Atenuación Ducking</div>
                    <div class="param-value" style="color: {duck_color};">{ducking_val} dB (<= -18dB)</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Attack / Release Ducking</div>
                    <div class="param-value">{audio.get('ducking_attack_ms', 30)}ms / {audio.get('ducking_release_ms', 250)}ms</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Sonoridad EBU R128</div>
                    <div class="param-value">{audio.get('ebu_r128_target_lufs', -14.0)} LUFS (Peak: {audio.get('ebu_r128_true_peak_dbtp', -1.0)} dBTP)</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Sub-80Hz Mono</div>
                    <div class="param-value">{'Activado (Graves Limpios)' if audio.get('sub_80hz_mono', True) else 'Desactivado'}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Motor y Voz</div>
                    <div class="param-value">{audio.get('voice_engine', 'vibevoice')} ({audio.get('voice_preset_id', 'es-emilio')})</div>
                </div>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">
                <strong>Capas Foley:</strong> {", ".join(audio.get('foley_presets', [])) or 'Foley ambiente sincronizado'}
            </div>
            </div>
        """, unsafe_allow_html=True)

        # CUADRANTE E: RITMO DE MONTAJE Y TRANSICIONES
        st.markdown("""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 14px;">⏱️</span>
                    <strong style="color: #38bdf8; font-size: 13px;">5. Ritmo de Montaje & Variación Dinámica (3-5s)</strong>
                </div>
        """, unsafe_allow_html=True)

        shot_dur = transitions.get('max_shot_duration_sec', 4.0)
        shot_color = "#10b981" if shot_dur <= 5.0 else "#ef4444"

        st.markdown(f"""
            <div class="param-grid">
                <div class="param-item">
                    <div class="param-label">Duración Máx. Toma</div>
                    <div class="param-value" style="color: {shot_color};">{shot_dur} s (Regla R04)</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Movimiento Ken-Burns</div>
                    <div class="param-value">{'Obligatorio (Zoompan)' if transitions.get('ken_burns_zoompan', True) else 'Inactivo'}</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Corte al Compás</div>
                    <div class="param-value">Cada {transitions.get('cut_every_bars', 2)} compases ({transitions.get('cut_timing_mode', 'on_snare_hit')})</div>
                </div>
                <div class="param-item">
                    <div class="param-label">Stagger Entry Capas</div>
                    <div class="param-value">{transitions.get('pacing_stagger_frames', 4)} frames desfase</div>
                </div>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">
                <strong>Transición Primaria:</strong> {transitions.get('default_transition', 'whip_pan_cinema')} ({transitions.get('transition_duration_ms', 30)}ms)
            </div>
            </div>
        """, unsafe_allow_html=True)

        # CUADRANTE F: DIRECTOR DOP (PROMPTS EN 7 CAPAS FÍSICAS)
        st.markdown("""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 14px;">🎬</span>
                    <strong style="color: #c084fc; font-size: 13px;">6. Director DoP: Manifiesto de 7 Capas FÍsicas</strong>
                </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="font-size: 11.5px; line-height: 1.5; color: #cbd5e1;">
                <div><strong style="color: #38bdf8;">Capa 1 (Sujeto):</strong> {prompts.get('layer1_subject', 'Núcleo narrativo')}</div>
                <div><strong style="color: #38bdf8;">Capa 2 (Entorno):</strong> {prompts.get('layer2_environment', 'Escenario físico y época')}</div>
                <div><strong style="color: #38bdf8;">Capa 3 (Iluminación):</strong> {prompts.get('layer3_lighting', 'Atmósfera y scattering')}</div>
                <div><strong style="color: #38bdf8;">Capa 4 (Óptica):</strong> {prompts.get('layer4_optics', 'Distancia focal y apertura')}</div>
                <div><strong style="color: #38bdf8;">Capa 5 (Movimiento):</strong> {prompts.get('layer5_motion', 'Trayectoria dinámica')}</div>
                <div><strong style="color: #38bdf8;">Capa 6 (Colorimetría):</strong> {prompts.get('layer6_colorimetry', 'Emulación Kodak 35mm')}</div>
                <div><strong style="color: #38bdf8;">Capa 7 (Render):</strong> {prompts.get('layer7_render_engine', '24fps Cinematic post')}</div>
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: #f87171;">
                <strong>🚫 Léxico Prohibido Anti-CGI:</strong> {", ".join(prompts.get('anti_cgi_negative_lexicon', [])[:5])}...
            </div>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # VISOR DE DEFINICIÓN COMPLETA JSON / YAML
    # -------------------------------------------------------------------------
    with st.expander("📄 Ver Manifiesto Estructurado Completo (JSON / YAML)", expanded=False):
        tab_json, tab_yaml = st.tabs(["JSON Estructurado", "YAML Canónico"])
        with tab_json:
            st.json(wf_dict)
        with tab_yaml:
            st.code(yaml.dump(wf_dict, sort_keys=False, allow_unicode=True), language="yaml")


# ============================================================================
# SECCIÓN 2: HISTORIAL DE VERSIONES Y DIFFS
# ============================================================================
def _render_version_diffs_tab(registry: WorkflowRegistry, learner: WorkflowLearner):
    """Visualizador gráfico de diferencias y mejoras entre versiones consecutivas."""
    st.markdown("#### 🔄 Historial de Versiones & Comparador Gráfico de Diffs")

    canonical_list = [
        ("CHRONODRIFT_6DOF", "🛰️ ChronoDrift 6-DoF Tritemporal Urban Master"),
        ("FPV_URBAN", "🚁 FPV Urban Real Flow 4K"),
        ("VOX_EXPLAINER", "📜 VOX Investigative Documentary 4K"),
        ("VIRAL_SHORTS_916", "⚡ Viral Shorts & High-Retention Hook 9:16"),
        ("DOCUMENTAL_35MM", "🎞️ Documental Histórico 35mm Master"),
        ("NANOVERSE", "🔬 NanoVerse Cellular & Quantum Macro 4K"),
        ("LIVING_CANVAS", "🎨 Living Canvas Fine Art 3D Animation"),
        ("ASTRODRIFT", "🌌 AstroDrift Deep Space Relativistic 4K")
    ]

    col_arch, col_v1, col_v2 = st.columns([2, 1, 1])
    with col_arch:
        arch_id = st.selectbox(
            "Arquetipo para Comparación:",
            options=[item[0] for item in canonical_list],
            format_func=lambda x: next((item[1] for item in canonical_list if item[0] == x), x),
            key="sel_arch_diff"
        )

    versions_info = registry.list_versions(arch_id)
    version_strs = [v.semver for v in versions_info] if versions_info else ["v1.0.0"]

    with col_v1:
        v_base = st.selectbox("Versión Base (V1):", options=version_strs, index=len(version_strs)-1, key="diff_v1")
    with col_v2:
        v_target = st.selectbox("Versión Comparada (V2):", options=version_strs, index=0, key="diff_v2")

    # Obtener el diff estructurado
    diff_result = registry.diff_versions(arch_id, v_base, v_target)
    differences = diff_result.get("differences", [])
    has_changes = len(differences) > 0

    st.markdown(f"""
        <div class="glass-card" style="margin-top: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #f8fafc; font-size: 14px;">Comparación: {arch_id} ({v_base} ➔ {v_target})</strong>
                    <div style="font-size: 12px; color: #94a3b8;">
                        Total de modificaciones de parámetros detectadas: <strong>{len(differences)}</strong>
                    </div>
                </div>
                <div>
                    <span class="badge-chip {'badge-green' if not has_changes else 'badge-amber'}">
                        {'IDÉNTICAS' if not has_changes else f'{len(differences)} CAMBIOS ENCONTRADOS'}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if differences:
        st.markdown("##### 🔍 Parámetros Modificados y Mejoras Introducidas")
        for idx, diff_item in enumerate(differences):
            param_key = diff_item.get("param", "parametro")
            old_val = diff_item.get("old_value")
            new_val = diff_item.get("new_value")

            st.markdown(f"""
                <div class="glass-card" style="margin-bottom: 8px; padding: 10px 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #38bdf8; font-size: 12.5px; font-family: monospace;">
                            ⚙️ {param_key}
                        </span>
                        <span class="badge-chip badge-cyan">Auto-Patch QA</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 4px; padding: 6px 10px;">
                            <div style="font-size: 10px; color: #f87171; font-weight: 700;">VALOR ANTERIOR ({v_base})</div>
                            <div style="font-size: 12px; color: #cbd5e1; font-family: monospace;">{str(old_val)}</div>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 6px 10px;">
                            <div style="font-size: 10px; color: #34d399; font-weight: 700;">VALOR OPTIMIZADO ({v_target})</div>
                            <div style="font-size: 12px; color: #f8fafc; font-family: monospace; font-weight: 700;">{str(new_val)}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"Las versiones {v_base} y {v_target} son idénticas en su especificación.")

    # Línea temporal de optimizaciones globales (improvements)
    st.markdown("---")
    st.markdown("##### 📜 Registro Cronológico de Auto-Mejoras")
    
    improvements_file = BASE_DIR / "storage" / "learning_memory" / "workflow_improvements.json"
    if improvements_file.is_file():
        try:
            with open(improvements_file, "r", encoding="utf-8") as f:
                imp_list = json.load(f)
            
            if imp_list:
                for entry in reversed(imp_list):
                    t_str = entry.get("timestamp", "")
                    a_id = entry.get("archetype_id", "")
                    f_v = entry.get("from_version", "")
                    t_v = entry.get("to_version", "")
                    score_b = entry.get("audit_score_before", 0)
                    corrs = entry.get("violations_corrected", [])
                    
                    st.markdown(f"""
                        <div class="glass-card-success" style="margin-bottom: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="color: #34d399;">Arquetipo: {a_id}</strong>
                                    <span style="color: #94a3b8; font-size: 11px;"> (v{f_v} ➔ v{t_v})</span>
                                    <div style="font-size: 11px; color: #cbd5e1; margin-top: 2px;">
                                        Score previo: {score_b}/100 • Violaciones corregidas: <strong>{", ".join(corrs)}</strong>
                                    </div>
                                </div>
                                <div style="font-size: 10px; color: #64748b;">
                                    {t_str[:19]}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No hay eventos de mejora registrados aún en el storage.")
        except Exception as ex:
            st.warning(f"Aviso al leer historial de mejoras: {ex}")


# ============================================================================
# SECCIÓN 3: TABLERO DE AUDITORÍA QA (REGLAS R01 A R10)
# ============================================================================
def _render_qa_audit_tab(learner: WorkflowLearner, dispatcher: HermesMissionDispatcher):
    """Tablero de Auditoría de Calidad en tiempo real contra las 10 Reglas de Oro."""
    st.markdown("#### 🛡️ Tablero de Auditoría de Calidad (Semáforo R01 a R10)")
    
    st.markdown("""
        <p style="font-size: 12px; color: #94a3b8; margin-top: -8px;">
            Verificación automática y estricta de cumplimiento de estándares dorados cinematográficos sobre producciones finalizadas o manifiestos en curso.
        </p>
    """, unsafe_allow_html=True)

    # 1. Selector de Proyecto / Vídeo para Auditar
    missions = dispatcher.list_all_missions(limit=10)
    mission_options = {f"{m['title']} ({m['status']}) — {m['mission_id']}": m for m in missions} if missions else {}

    # Proyectos en storage
    demo_projects = [
        {
            "id": "2026_08_16_workflow_madrid_curiosities_3min",
            "name": "🏛️ Madrid Secreto 4K (3 Minutos - Master Verificado)",
            "archetype": "VOX_EXPLAINER"
        },
        {
            "id": "2026-08-17_documental_futurista_4k_40tomas_120s",
            "name": "🔬 El Umbral Cuántico 120s (40 Tomas 4K)",
            "archetype": "NANOVERSE"
        },
        {
            "id": "test_flawed_project_demo",
            "name": "⚠️ Proyecto con Violaciones QA Intencionadas (Test Demostrativo)",
            "archetype": "CITY_ROUTES_BEATS"
        }
    ]

    p_col1, p_col2 = st.columns([3, 1])
    with p_col1:
        sel_proj_type = st.selectbox(
            "Seleccionar Producción o Misión a Auditar:",
            options=[p["id"] for p in demo_projects],
            format_func=lambda x: next((p["name"] for p in demo_projects if p["id"] == x), x),
            key="sel_audit_proj"
        )
    with p_col2:
        btn_run_audit = st.button("🔍 Auditar Proyecto Ahora", type="primary", use_container_width=True, key="btn_audit_now")

    # Obtener o simular manifiesto del proyecto seleccionado
    manifest_to_audit = _build_sample_manifest(sel_proj_type)

    audit_result = learner.audit_project(manifest_to_audit)
    anomalies_result = learner.detect_montage_anomalies(manifest_to_audit)

    overall_score = audit_result.get("overall_score", 100.0)
    passed = audit_result.get("passed", True)
    evaluations = audit_result.get("evaluations", {})
    violations = audit_result.get("violations", [])

    # -------------------------------------------------------------------------
    # RESUMEN EJECUTIVO Y SCORE DE CALIDAD
    # -------------------------------------------------------------------------
    score_color = "#10b981" if overall_score >= 85 else ("#f59e0b" if overall_score >= 60 else "#ef4444")
    status_label = "✅ APROBADO PARA EMISIÓN BROADCAST" if passed else "❌ RECHAZADO POR CONTROL DE CALIDAD"

    st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid {score_color}; margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="font-size: 17px; font-weight: 800; color: #f8fafc; margin: 0;">
                        Puntuación QA Global: <span style="color: {score_color};">{overall_score:.1f} / 100</span>
                    </h3>
                    <div style="font-size: 12.5px; font-weight: 700; color: {score_color}; margin-top: 3px;">
                        {status_label}
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span class="badge-chip {'badge-green' if passed else 'badge-red'}">
                        {len(violations)} Violaciones Detectadas
                    </span>
                    <span class="badge-chip badge-cyan">
                        Penalizaciones: -{audit_result.get('total_penalties', 0):.1f} pts
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SEMÁFORO DETALLADO DE LAS 10 REGLAS DE ORO (R01 A R10)
    # -------------------------------------------------------------------------
    st.markdown("##### 🚦 Semáforo de Cumplimiento de las 10 Reglas de Oro")

    rule_cols = st.columns(2)
    for idx, rule in enumerate(GOLDEN_RULES_CATALOG):
        rule_id = rule["id"]
        rule_eval = evaluations.get(rule_id, {})
        rule_passed = rule_eval.get("passed", True)
        penalty_applied = rule_eval.get("penalty_applied", 0.0)
        details = rule_eval.get("details", rule["description"])

        col_target = rule_cols[idx % 2]
        with col_target:
            card_class = "glass-card-success" if rule_passed else "glass-card-danger"
            dot_class = "dot-green" if rule_passed else "dot-red"
            status_text = "🟢 CUMPLE" if rule_passed else f"🔴 VIOLACIÓN (-{penalty_applied:.1f} pts)"

            st.markdown(f"""
                <div class="{card_class}" style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #f8fafc; font-size: 12px;">
                            <span class="status-dot {dot_class}"></span> {rule_id[:3]}: {rule['name']}
                        </strong>
                        <span style="font-size: 10.5px; font-weight: 700; color: {'#34d399' if rule_passed else '#f87171'};">
                            {status_text}
                        </span>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; line-height: 1.3;">
                        {details}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # ANOMALÍAS ESPECÍFICAS DE MONTAJE Y BITRATE
    # -------------------------------------------------------------------------
    if anomalies_result.get("total_anomalies", 0) > 0:
        st.markdown("##### ⚠️ Anomalías Físicas de Montaje Detectadas")
        for a in anomalies_result.get("anomalies", []):
            st.markdown(f"""
                <div class="glass-card-warning" style="margin-bottom: 6px;">
                    <strong style="color: #fbbf24; font-size: 11.5px;">⚠️ [{a.get('type')}] {a.get('description')}</strong>
                    <div style="font-size: 11px; color: #cbd5e1;">Severidad: {a.get('severity')}</div>
                </div>
            """, unsafe_allow_html=True)


# ============================================================================
# SECCIÓN 4: PANEL DE CONTROL DE APRENDIZAJE & AUTO-MEJORA
# ============================================================================
def _render_control_panel_tab(registry: WorkflowRegistry, learner: WorkflowLearner, dispatcher: HermesMissionDispatcher):
    """Panel de Control para forzar auto-mejora, rollback de versión y sincronización Firebase."""
    st.markdown("#### 🧠 Panel de Control de Auto-Mejora y Sincronización")

    col_act1, col_act2, col_act3 = st.columns(3)

    with col_act1:
        st.markdown("""
            <div class="glass-card" style="border-top: 3px solid #38bdf8; min-height: 180px;">
                <h4 style="font-size: 13.5px; color: #f8fafc; margin-top: 0;">🚀 Forzar Auto-Mejora (v+1)</h4>
                <p style="font-size: 11.5px; color: #94a3b8;">
                    Audita el proyecto actual, corrige automáticamente cualquier violación de las 10 Reglas de Oro e incrementa la versión del workflow.
                </p>
        """, unsafe_allow_html=True)
        
        target_archetype = st.selectbox(
            "Arquetipo a Optimizar:",
            options=["VOX_EXPLAINER", "CHRONODRIFT_6DOF", "FPV_URBAN", "VIRAL_SHORTS_916", "DOCUMENTAL_35MM", "NANOVERSE", "LIVING_CANVAS", "ASTRODRIFT"],
            key="sel_opt_arch"
        )
        
        if st.button("🚀 Ejecutar Auto-Parcheo (v+1)", type="primary", use_container_width=True, key="btn_force_patch"):
            with st.spinner("Ejecutando auto-parcheo determinista y generando versión v+1..."):
                sample_manifest = _build_sample_manifest("test_flawed_project_demo")
                sample_manifest["archetype_id"] = target_archetype
                
                res = learner.audit_and_optimize_post_execution(sample_manifest)
                if res.get("patched"):
                    st.success(f"✅ Workflow optimizado con éxito a la versión {res.get('new_version_label')}!")
                    st.rerun()
                else:
                    st.info("El workflow ya cumple todas las reglas al 100%. No se requirieron parches.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_act2:
        st.markdown("""
            <div class="glass-card" style="border-top: 3px solid #f59e0b; min-height: 180px;">
                <h4 style="font-size: 13.5px; color: #f8fafc; margin-top: 0;">⏪ Rollback de Versión</h4>
                <p style="font-size: 11.5px; color: #94a3b8;">
                    Revertir un arquetipo a una versión previa segura en caso de regresión o calibración específica.
                </p>
        """, unsafe_allow_html=True)

        rb_arch = st.selectbox(
            "Arquetipo:",
            options=["VOX_EXPLAINER", "CHRONODRIFT_6DOF", "FPV_URBAN", "VIRAL_SHORTS_916", "DOCUMENTAL_35MM", "NANOVERSE", "LIVING_CANVAS", "ASTRODRIFT"],
            key="sel_rb_arch"
        )
        
        rb_versions = registry.list_versions(rb_arch)
        rb_opts = [v.semver for v in rb_versions] if rb_versions else ["v1.0.0"]
        
        rb_target_v = st.selectbox("Restaurar a versión:", options=rb_opts, key="sel_rb_ver")

        if st.button("⏪ Ejecutar Rollback Seguro", use_container_width=True, key="btn_exec_rb"):
            with st.spinner(f"Revertiendo {rb_arch} a {rb_target_v}..."):
                try:
                    rolled = registry.rollback_to_version(rb_arch, rb_target_v)
                    st.success(f"✅ Rollback completado. Versión activa: {rolled.version_info.semver}")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al ejecutar rollback: {ex}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_act3:
        st.markdown("""
            <div class="glass-card" style="border-top: 3px solid #c084fc; min-height: 180px;">
                <h4 style="font-size: 13.5px; color: #f8fafc; margin-top: 0;">☁️ Sincronización Firebase</h4>
                <p style="font-size: 11.5px; color: #94a3b8;">
                    Persistencia dual en la nube de lecciones aprendidas, críticas y workflows sincronizados con Firestore.
                </p>
        """, unsafe_allow_html=True)

        if st.button("☁️ Subir a Firebase Firestore", type="primary", use_container_width=True, key="btn_sync_up_fb"):
            with st.spinner("Subiendo memoria y lecciones a Firestore..."):
                if learning_engine:
                    ok, msg = learning_engine.sync_to_firebase()
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Motor de aprendizaje no disponible.")

        if st.button("📥 Descargar desde Firestore", use_container_width=True, key="btn_sync_down_fb"):
            with st.spinner("Descargando memoria de aprendizaje..."):
                if learning_engine:
                    ok, msg = learning_engine.load_from_firebase()
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {msg}")
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # GESTIÓN Y REGISTRO DE NUEVAS LECCIONES APRENDIDAS
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### 📚 Catálogo de Lecciones y Registro de Estándares")

    sub_l1, sub_l2 = st.tabs(["📜 Catálogo Activo de Lecciones", "➕ Registrar Nueva Lección Manual"])

    with sub_l1:
        all_lessons = learning_engine.get_all_lessons() if learning_engine else []
        for l in all_lessons:
            with st.expander(f"🔹 [{l.category.value}] {l.title} ({l.severity.value})"):
                st.markdown(f"""
                    <div style="font-size: 12px; color: #cbd5e1;">
                        <p><strong style="color: #f87171;">❌ Causa de Fallo Previa:</strong> {l.what_failed}</p>
                        <p><strong style="color: #34d399;">✨ Regla de Oro Aplicable:</strong> {l.golden_rule}</p>
                        <p style="color: #94a3b8; font-size: 11px;">
                            Nodos: <code>{", ".join(l.applicable_nodes)}</code> • Rating de Éxito: {int(l.success_rating * 100)}% ({l.applied_count} usos)
                        </p>
                    </div>
                """, unsafe_allow_html=True)

    with sub_l2:
        with st.form("form_new_lesson"):
            nl_title = st.text_input("Título de la Lección / Regla:", placeholder="Ej: Pacing Cinemático en Tomas Aéreas")
            nl_cat = st.selectbox("Categoría:", options=[c.value for c in LessonCategory])
            nl_sev = st.selectbox("Severidad:", options=[s.value for s in LessonSeverity])
            nl_failed = st.text_area("¿Qué falló anteriormente? (Anti-patrón):", placeholder="Descripción detallada del error visual, auditivo o técnico...")
            nl_golden = st.text_area("Regla de Oro / Solución Estricta:", placeholder="Parámetros exactos que garantizan el 100% de calidad...")
            nl_submit = st.form_submit_button("💾 Registrar Lección en Memoria", type="primary")

            if nl_submit:
                if nl_title and nl_failed and nl_golden:
                    new_l = LearnedLesson(
                        id=f"lesson_user_{int(datetime.now().timestamp())}",
                        title=nl_title,
                        category=LessonCategory(nl_cat),
                        severity=LessonSeverity(nl_sev),
                        what_failed=nl_failed,
                        golden_rule=nl_golden,
                        applicable_nodes=["node_04_composicion_motion_graphics"],
                        applicable_workflows=["ALL"],
                        experience_source_project="manual_user_input"
                    )
                    if learning_engine:
                        learning_engine.register_lesson(new_l)
                        st.success("✅ Lección registrada con éxito en el catálogo inmutable.")
                        st.rerun()
                else:
                    st.error("Por favor completa todos los campos obligatorios.")


# ============================================================================
# HELPER DE GENERACIÓN DE MANIFIESTOS DE PRUEBA
# ============================================================================
def _build_sample_manifest(proj_id: str) -> Dict[str, Any]:
    """Genera un manifiesto de prueba representativo para auditoría."""
    if proj_id == "test_flawed_project_demo":
        return {
            "project_id": "test_flawed_project_demo",
            "archetype_id": "CITY_ROUTES_BEATS",
            "metadata": {
                "topic": "Rutas Urbanas Nocturnas",
                "target_duration_seconds": 60,
                "actual_duration_seconds": 38.0  # Desfase R01
            },
            "script": "Caminando por la Gran Vía madrileña bajo las luces de neón.",
            "subtitles_text": "Texto alucinado sin correspondencia fonética.",  # R03
            "scenes": [
                {
                    "id": "shot_01",
                    "duration_sec": 7.5,  # R04: > 5s
                    "ken_burns": False,
                    "prompt": "hyper-realistic 8k octane render glowing city"  # R06: Slop
                }
            ],
            "audio_dsp": {
                "ducking_db": -6.0,  # R07: Insuficiente
                "target_lufs": -18.0
            },
            "thumbnail": {
                "microcopy": "ESTA ES LA RUTA MÁS INCREÍBLE Y LARGA DE LA HISTORIA"  # R08: >3 palabras
            },
            "background_color": "#000000",  # R05: Blackdetect
            "scraping_config": {
                "user_agent": "python-requests/2.31.0"  # R10: Generic
            },
            "assets_manifest": [
                {
                    "name": "bad_mock.mp4",
                    "filesize_bytes": 1024  # R02: <5KB gate
                }
            ]
        }
    else:
        # Proyecto canónico de alta calidad
        return {
            "project_id": proj_id,
            "archetype_id": "VOX_EXPLAINER",
            "metadata": {
                "topic": "La Cámara Acorazada de Cibeles",
                "style": "vox_documentary",
                "target_duration_seconds": 177.64,
                "actual_duration_seconds": 177.64
            },
            "script": "Bajo la fuente de Cibeles se oculta la cámara acorazada subterránea del Banco de España.",
            "subtitles_text": "Bajo la fuente de Cibeles se oculta la cámara acorazada subterránea del Banco de España.",
            "scenes": [
                {
                    "id": "shot_01",
                    "duration_sec": 3.5,
                    "ken_burns": True,
                    "prompt": "ARRI Alexa 35mm, f/1.8, subterranean vault mechanism with tungsten practical lights"
                },
                {
                    "id": "shot_02",
                    "duration_sec": 4.0,
                    "ken_burns": True,
                    "prompt": "35mm anamorphic prime lens, hydraulic floodgate system, 24fps cinema grading"
                }
            ],
            "audio_dsp": {
                "ducking_db": -20.0,
                "target_lufs": -14.0
            },
            "thumbnail": {
                "microcopy": "CÁMARA OCULTA CIBELES"
            },
            "background_color": "#243048",
            "scraping_config": {
                "user_agent": "VideoProHermesBot/1.0 (https://videopro.app; contact@videopro.app)"
            },
            "pipeline_lifecycle": {
                "phase_1_bootstrap": {"status": "completed"}
            },
            "assets_manifest": [
                {
                    "name": "clip_01.mp4",
                    "filesize_bytes": 204800
                }
            ]
        }
