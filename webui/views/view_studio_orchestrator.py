"""
Vista de Orquestación y Arquitectura de Studio — VideoPro Studio
Panel de Control Central: Arquetipos de Producción, Entrevistas Adaptativas, Workflows, Capabilities, Engines y Job Trace.
"""

import os
import json
import streamlit as st
from datetime import datetime

from app.core.orchestration.capabilities import get_all_capabilities
from app.core.orchestration.engines import get_all_engines
from app.core.orchestration.providers import PROVIDERS_CATALOG
from app.core.orchestration.workflows import get_all_workflows, get_workflow
from app.core.orchestration.workflow_archetypes import get_all_archetypes, get_archetype, ARCHETYPES_CATALOG
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
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">SPECIALIZED PIPELINES</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Arquetipos especializados con Pipelines de Nodos dedicados y Entrevista Adaptativa: <code>Pixar 3D</code>, <code>Histórico & Scraping</code>, <code>City Beats</code>, <code>Viral Shorts</code> y <code>Video Ensayos</code>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_archetypes, tab_planner, tab_workflows, tab_engines, tab_jobs = st.tabs([
        "🎬 Arquetipos & Entrevista Guiada",
        "🎯 Request Planner & Simulador",
        "🎛️ Registro de Workflows & Versiones",
        "⚙️ Capacidades & Motores",
        "📈 Trazabilidad de Jobs"
    ])

    # =========================================================
    # TAB 1: ARQUETIPOS DE PRODUCCIÓN & ENTREVISTA ADAPTATIVA
    # =========================================================
    with tab_archetypes:
        st.markdown("#### 🎬 Arquetipos de Producción Especializados")
        st.caption("Cada tipo de vídeo tiene sus propios motores, su propio pipeline de nodos y su cuestionario de entrevista específico.")

        archetypes = get_all_archetypes()
        arch_opts = [a.id for a in archetypes]
        
        col_a1, col_a2 = st.columns([4, 6], gap="medium")
        with col_a1:
            selected_arch_id = st.selectbox(
                "Selecciona Tipo de Vídeo / Arquetipo:",
                options=arch_opts,
                index=0,
                format_func=lambda x: f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name}"
            )
            arch = ARCHETYPES_CATALOG[selected_arch_id]
            st.markdown(f"""
                <div style="padding: 12px; background: rgba(30, 41, 59, 0.5); border-radius: 8px; border: 1px solid #334155; margin-top: 8px;">
                    <div style="font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 4px;">{arch.icon} {arch.name}</div>
                    <div style="font-size: 11.5px; color: #94a3b8; margin-bottom: 8px;">{arch.description}</div>
                    <div style="font-size: 11px; color: #cbd5e1;">
                        • <b>Audiencia:</b> {arch.target_audience}<br>
                        • <b>Formato:</b> {arch.default_aspect_ratio}<br>
                        • <b>Estrategia Visual:</b> {arch.visual_strategy.value.upper()}<br>
                        • <b>Voz por Defecto:</b> {arch.default_voice_engine} ({arch.default_voice_id})<br>
                        • <b>Banda Sonora:</b> {arch.default_music_genre}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col_a2:
            st.markdown("##### 🎙️ Entrevista Adaptativa del Asistente:")
            answers = {}
            for q in arch.interview_schema:
                if q.question_type == "select":
                    def_idx = q.options.index(q.default_value) if q.default_value in q.options else 0
                    answers[q.key] = st.selectbox(f"**{q.question}**", options=q.options, index=def_idx, help=q.description, key=f"int_{arch.id}_{q.key}")
                elif q.question_type == "number":
                    answers[q.key] = st.number_input(f"**{q.question}**", value=int(q.default_value or 5), help=q.description, key=f"int_{arch.id}_{q.key}")
                else:
                    answers[q.key] = st.text_input(f"**{q.question}**", value=str(q.default_value or ""), help=q.description, key=f"int_{arch.id}_{q.key}")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Compilar Pipeline & Generar Plan Especializado", type="primary", use_container_width=True, key="btn_compile_arch_plan"):
                plan = RequestPlanner.plan_from_interview(
                    archetype_id=arch.id,
                    interview_answers=answers,
                    project_id=f"proj_{arch.id.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                st.session_state["current_archetype_plan"] = plan
                st.session_state["selected_arch_obj"] = arch

        if "current_archetype_plan" in st.session_state:
            plan = st.session_state["current_archetype_plan"]
            arch_obj = st.session_state.get("selected_arch_obj", arch)
            st.markdown("<hr style='margin: 14px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
            st.markdown(f"### 📋 Plan Resuelto para `{arch_obj.name}`")
            
            c_pl1, c_pl2, c_pl3 = st.columns(3)
            with c_pl1:
                st.metric("Total Escenas Planificadas", f"{len(plan.scenes)} Escenas")
            with c_pl2:
                st.metric("Duración Total", f"{plan.estimated_total_duration_seconds:.1f}s")
            with c_pl3:
                st.metric("Coste Estimado", "$0.0000 ($0 Serverless / Token Pool)")

            st.markdown("#### 🎬 Desglose de Escenas y Motores Asignados:")
            for sc in plan.scenes:
                with st.expander(f"Escena {sc.scene_index + 1}: {sc.prompt} ({sc.recommended_engine.upper()})", expanded=True):
                    st.markdown(f"• **Motor Visual:** <code>{sc.recommended_engine}</code> | **Proveedor:** <code>{sc.assigned_provider}</code>")
                    st.markdown(f"• **Tipo de Toma:** <code>{sc.shot_type}</code> | **Duración:** {sc.duration_seconds}s")
                    st.markdown(f"• **Fallbacks:** {', '.join(sc.fallback_engines) if sc.fallback_engines else 'Ninguno'}")

            st.markdown("#### 🎛️ Pipeline de Nodos Asociado:")
            with st.expander("Ver Topología de Nodos del Pipeline", expanded=False):
                st.json(arch_obj.pipeline_graph)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("⚡ Ejecutar Producción de este Arquetipo", type="primary", key="btn_exec_archetype_job"):
                job = RequestPlanner.create_job_from_plan(plan)
                executor = WorkflowExecutor()
                with st.spinner(f"Ejecutando Pipeline de {arch_obj.name}..."):
                    res_job = executor.execute_job(job)
                    StudioRepository.save_job(res_job)
                st.success(f"✅ Producción de {arch_obj.name} finalizada con éxito. Job ID: `{res_job.job_id}`.")
                st.rerun()

    # =========================================================
    # TAB 2: REQUEST PLANNER & SIMULADOR
    # =========================================================
    with tab_planner:
        st.markdown("#### 🎯 Generador de Plan de Ejecución Libre")
        st.caption("Introduce una petición libre para ver cómo el Request Planner descompone la tarea en Capabilities y asigna motores por escena.")

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

    # =========================================================
    # TAB 3: WORKFLOWS & VERSIONING LOOP
    # =========================================================
    with tab_workflows:
        st.markdown("#### 🎛️ Registro de Workflows & Bucle de Perfeccionamiento")
        st.caption("Guarda versiones incrementales de tus workflows (v1.0, v1.1, v2.0) a medida que perfeccionas prompts, nodos y fallbacks.")
        
        for wf in get_all_workflows():
            with st.expander(f"{wf.name} ({wf.version_label}) — {wf.id}", expanded=False):
                st.write(wf.description)
                st.markdown(f"• **Arquetipo Vinculado:** <code>{wf.archetype_id or 'General'}</code>")
                st.markdown(f"• **Capacidades Requeridas:** {', '.join([c.value for c in wf.required_capabilities])}")
                st.markdown(f"• **Total Nodos:** {len(wf.nodes)} | **Conexiones:** {len(wf.connections)}")
                
                # Bucle de versionado
                c_v1, c_v2 = st.columns([7, 3])
                with c_v1:
                    new_v_label = st.text_input(f"Etiqueta de Nueva Versión para {wf.id}:", value=f"v{wf.version}.1", key=f"lbl_{wf.id}")
                with c_v2:
                    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
                    if st.button(f"💾 Congelar Snapshot {new_v_label}", key=f"btn_ver_{wf.id}"):
                        new_wf = wf.copy(deep=True)
                        new_wf.version += 1
                        new_wf.version_label = new_v_label
                        StudioRepository.save_workflow(new_wf)
                        st.success(f"Snapshot `{new_v_label}` guardado en el repositorio.")
                        st.rerun()

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
            st.info("No hay Jobs registrados todavía. Genera uno desde la pestaña Arquetipos o Request Planner.")
        else:
            for j in recent_jobs:
                j_id = j.get("job_id", "job_unknown")
                j_stat = j.get("status", "unknown")
                j_wf = j.get("workflow_id", "custom")
                j_dur = j.get("total_duration_seconds", 0.0)
                
                with st.expander(f"Job: {j_id} | {j_wf} | Estado: {j_stat.upper()} ({j_dur}s)"):
                    st.json(j)
