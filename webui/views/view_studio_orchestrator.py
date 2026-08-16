"""
Vista de Orquestación y Arquitectura de Studio — VideoPro Studio
Panel de Control Central: Capabilities, Engines, Providers, Workflows, Request Planner y Job Trace.
"""

import os
import json
import streamlit as st
from datetime import datetime

from app.core.orchestration.capabilities import get_all_capabilities
from app.core.orchestration.engines import get_all_engines
from app.core.orchestration.providers import PROVIDERS_CATALOG
from app.core.orchestration.workflows import get_all_workflows, get_workflow
from app.core.orchestration.planner import RequestPlanner
from app.core.orchestration.scene_router import VisualStrategy
from app.core.orchestration.executor import WorkflowExecutor
from app.core.orchestration.repository import StudioRepository


def render_studio_orchestrator_view():
    """Renderiza el panel de control del Studio de Orquestación."""
    st.markdown("""
        <div style="margin-bottom: 14px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                🏛️ Studio Workflow Orchestrator
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">MULTI-ENGINE ARCHITECTURE</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Arquitectura formal desacoplada: <code>Request ➔ Planner ➔ Workflow ➔ Capabilities ➔ Engines ➔ Providers ➔ Jobs</code>
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_overview, tab_planner, tab_workflows, tab_engines, tab_jobs = st.tabs([
        "📊 Vista General del Ecosistema",
        "🎯 Request Planner & Simulador",
        "🎛️ Registro de Workflows",
        "⚙️ Capacidades & Motores",
        "📈 Trazabilidad de Jobs"
    ])

    # =========================================================
    # TAB 1: VISTA GENERAL
    # =========================================================
    with tab_overview:
        caps = get_all_capabilities()
        engs = get_all_engines()
        wfs = get_all_workflows()
        jobs = StudioRepository.list_jobs(limit=100)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Capacidades (QUÉ)", f"{len(caps)} Registradas")
        with c2:
            st.metric("Motores (CÓMO)", f"{len(engs)} Activos")
        with c3:
            st.metric("Workflows Oficiales", f"{len(wfs)} Plantillas")
        with c4:
            st.metric("Jobs Ejecutados", f"{len(jobs)} Registrados")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        ```text
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                         CICLO DE PRODUCCIÓN STUDIO                      │
        │                                                                         │
        │   PETICIÓN HUMANA                                                       │
        │        ↓                                                                │
        │   REQUEST PLANNER ───► Resuelve estrategia visual y motores por escena  │
        │        ↓                                                                │
        │   WORKFLOW ──────────► Define el grafo de dependencias y políticas      │
        │        ↓                                                                │
        │   CAPABILITIES ──────► QUÉ se realiza (Script, Voice, Visual, Render)   │
        │        ↓                                                                │
        │   ENGINES ───────────► CÓMO se realiza (Flow, FLUX, VibeVoice, FFmpeg)  │
        │        ↓                                                                │
        │   PROVIDERS ─────────► DÓNDE se ejecuta (Local VPS, ZeroGPU, RunPod)    │
        │        ↓                                                                │
        │   EXECUTION JOB ─────► Trazabilidad, Reintentos, Fallbacks y R2 Storage │
        └─────────────────────────────────────────────────────────────────────────┘
        ```
        """)

    # =========================================================
    # TAB 2: REQUEST PLANNER & SIMULADOR
    # =========================================================
    with tab_planner:
        st.markdown("#### 🎯 Generador de Plan de Ejecución (Execution Plan)")
        st.caption("Introduce una petición para ver cómo el Request Planner descompone la tarea en Capabilities y asigna motores por escena.")

        col_p1, col_p2 = st.columns([6, 4], gap="medium")
        with col_p1:
            p_prompt = st.text_area("Petición de Producción / Prompt:", value="Crear documental cinemático de 60 segundos sobre los rascacielos futuristas de Tokio con planos aéreos y primeros planos de arquitectos", height=85)
            
            c_p_sub1, c_p_sub2 = st.columns(2)
            with c_p_sub1:
                p_dur = st.number_input("Duración Objetivo (segundos):", min_value=10, max_value=600, value=60, step=10)
            with c_p_sub2:
                p_strat = st.selectbox(
                    "Estrategia Visual:",
                    options=[VisualStrategy.HYBRID, VisualStrategy.AUTOMATIC, VisualStrategy.SINGLE_ENGINE, VisualStrategy.MANUAL],
                    format_func=lambda x: {
                        VisualStrategy.HYBRID: "Híbrido Multimotor (Stock + Flow + FLUX + NanoBanana)",
                        VisualStrategy.AUTOMATIC: "IA Automática (Según tipo de plano)",
                        VisualStrategy.SINGLE_ENGINE: "Motor Único para todo el vídeo",
                        VisualStrategy.MANUAL: "Manual por escena"
                    }.get(x, x)
                )

        with col_p2:
            wf_opts = [w.id for w in get_all_workflows()]
            p_wf = st.selectbox("Plantilla de Workflow Base:", options=wf_opts, index=0)
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Generar Plan de Ejecución & Trazar", type="primary", use_container_width=True):
                plan = RequestPlanner.plan_request(
                    project_id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    user_prompt=p_prompt,
                    target_duration=p_dur,
                    workflow_id=p_wf,
                    visual_strategy=p_strat
                )
                st.session_state["current_plan"] = plan

        if "current_plan" in st.session_state:
            plan = st.session_state["current_plan"]
            st.markdown("<hr style='margin: 12px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
            st.markdown(f"### 📋 Plan Resuelto: `{plan.workflow_id}` (v{plan.workflow_version})")
            
            c_pl1, c_pl2, c_pl3 = st.columns(3)
            with c_pl1:
                st.metric("Pasos de Capacidad", f"{len(plan.steps)} Pasos")
            with c_pl2:
                st.metric("Escenas Planificadas", f"{len(plan.scenes)} Escenas")
            with c_pl3:
                st.metric("Coste Estimado", f"${plan.estimated_total_cost:.4f} ($0)")

            st.markdown("#### 🎬 Asignación de Motores por Escena (Scene-Level Routing):")
            for sc in plan.scenes:
                with st.expander(f"Escena {sc.scene_index + 1}: {sc.prompt} ({sc.recommended_engine.upper()})"):
                    st.markdown(f"• **Motor Recomendado:** <code>{sc.recommended_engine}</code> | **Proveedor:** <code>{sc.assigned_provider}</code>")
                    st.markdown(f"• **Tipo de Plano:** <code>{sc.shot_type}</code> | **Duración:** {sc.duration_seconds}s")
                    st.markdown(f"• **Cadena de Fallbacks:** {', '.join(sc.fallback_engines) if sc.fallback_engines else 'Ninguno'}")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("⚡ Ejecutar Plan de Producción (Job)", type="primary", key="btn_exec_plan_demo"):
                job = RequestPlanner.create_job_from_plan(plan)
                executor = WorkflowExecutor()
                with st.spinner("Ejecutando Job a través de adaptadores..."):
                    res_job = executor.execute_job(job)
                    StudioRepository.save_job(res_job)
                st.success(f"✅ Job `{res_job.job_id}` completado en {res_job.total_duration_seconds}s.")
                st.rerun()

    # =========================================================
    # TAB 3: WORKFLOWS
    # =========================================================
    with tab_workflows:
        st.markdown("#### 🎛️ Registro Oficial de Workflows")
        for wf in get_all_workflows():
            with st.expander(f"{wf.name} (v{wf.version}) — {wf.id}", expanded=False):
                st.write(wf.description)
                st.markdown(f"**Capacidades Requeridas:** {', '.join([c.value for c in wf.required_capabilities])}")
                st.markdown(f"**Total Nodos:** {len(wf.nodes)} | **Conexiones:** {len(wf.connections)}")
                st.json(wf.dict())

    # =========================================================
    # TAB 4: CAPACIDADES & MOTORES
    # =========================================================
    with tab_engines:
        st.markdown("#### ⚙️ Motores (Engines) y Proveedores (Providers)")
        for eng in get_all_engines():
            provs = PROVIDERS_CATALOG.get(eng.id, [])
            with st.expander(f"{eng.name} — [{eng.cost_type.value.upper()}]"):
                st.write(eng.description)
                st.markdown(f"• **Capacidades:** {', '.join([c.value for c in eng.capabilities])}")
                st.markdown(f"• **Prioridad:** {eng.priority} | **Estado:** {eng.health.value}")
                st.markdown(f"• **Fallbacks:** {', '.join(eng.fallbacks) if eng.fallbacks else 'Ninguno'}")
                st.markdown("**Proveedores de Infraestructura:**")
                for pr in provs:
                    st.markdown(f"  - 🏢 <b>{pr.name}</b> (<code>{pr.infra_type.value}</code>) — Coste: ${pr.cost_per_second}/s", unsafe_allow_html=True)

    # =========================================================
    # TAB 5: JOBS & TRAZABILIDAD
    # =========================================================
    with tab_jobs:
        st.markdown("#### 📈 Historial y Trazabilidad de Jobs de Producción")
        recent_jobs = StudioRepository.list_jobs(limit=25)
        if not recent_jobs:
            st.info("No hay Jobs registrados todavía. Genera uno desde la pestaña Request Planner.")
        else:
            for j in recent_jobs:
                j_id = j.get("job_id", "job_unknown")
                j_stat = j.get("status", "unknown")
                j_wf = j.get("workflow_id", "custom")
                j_dur = j.get("total_duration_seconds", 0.0)
                
                with st.expander(f"Job: {j_id} | {j_wf} | Estado: {j_stat.upper()} ({j_dur}s)"):
                    st.json(j)
