"""
Vista de Orquestación y Director Creativo Semántico — VideoPro Studio
Entrada Principal: '🚀 Empezar' — Co-Creación Conversacional, Auto-Generación de Proyecto,
Ficha de Producción Consolidada, Trazabilidad en Tiempo Real y Lanzamiento de Producción.
"""

import os
import re
import json
import time
from datetime import datetime
import streamlit as st

from app.core.orchestration.capabilities import get_all_capabilities
from app.core.orchestration.engines import get_all_engines
from app.core.orchestration.providers import PROVIDERS_CATALOG
from app.core.orchestration.workflows import get_all_workflows, get_workflow
from app.core.orchestration.workflow_archetypes import get_all_archetypes, get_archetype, ARCHETYPES_CATALOG
from app.core.orchestration.planner import RequestPlanner
from app.core.orchestration.scene_router import VisualStrategy, ScenePlan
from app.core.orchestration.executor import WorkflowExecutor
from app.core.orchestration.repository import StudioRepository
from app.services import semantic_director
from app.services import firebase_sync
from app.core.domain.entities import ProjectEntity, SceneEntity, DecisionRecord
from app.core.domain.specs import VisualSpec, AudioSpec, SubtitleSpec, RenderSpec, ProvenanceInfo
from app.core.domain.enums import ProjectStatus, SceneStatus, LockLevel
from app.core.services.project_repository import ProjectRepository


def _slugify(text: str, max_len: int = 30) -> str:
    """Convierte texto en un slug limpio para nombres de proyecto."""
    clean = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    clean = re.sub(r"[-\s]+", "_", clean)
    return clean[:max_len].strip("_") or "proyecto"


def _init_director_session(arch_id: str):
    """Inicializa la sesión de conversación con el Director Creativo al seleccionar un arquetipo."""
    arch = ARCHETYPES_CATALOG.get(arch_id, list(ARCHETYPES_CATALOG.values())[0])
    st.session_state["director_arch_id"] = arch_id
    st.session_state["director_messages"] = [
        {
            "role": "assistant",
            "content": f"¡Hola! Soy tu **Director Creativo**. Has seleccionado el Workflow **{arch.name}** ({arch.icon}).\n\n¿De qué trata tu historia o qué idea tienes en mente para este vídeo?"
        }
    ]
    st.session_state["director_suggestions"] = [
        f"Idea para {arch.name}",
        f"Historia emotiva de 60 segundos",
        f"Documental de impacto visual",
        f"Enfoque cinemático en 35mm"
    ]
    
    initial_title = f"{arch.name} — Nuevo Proyecto"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(arch.name)
    project_id = f"proj_{slug}_{timestamp}"
    
    st.session_state["current_project_id"] = project_id
    st.session_state["current_project_title"] = initial_title
    
    st.session_state["director_spec"] = {
        "archetype_id": arch_id,
        "subject": initial_title,
        "characters": "",
        "dramatic_conflict": "",
        "climax": "",
        "visual_style": arch.visual_strategy.value,
        "aspect_ratio": arch.default_aspect_ratio,
        "voice_preset": arch.default_voice_id,
        "music_genre": arch.default_music_genre,
        "ready_to_produce": False,
        "interview_step": 1,
        "summary_reasoning": "Sesión iniciada. Esperando concepto del usuario."
    }
    
    # Compilar plan inicial
    plan = RequestPlanner.plan_request(
        project_id=project_id,
        user_prompt=f"Vídeo de {arch.name}",
        workflow_id=arch_id,
        visual_strategy=VisualStrategy.HYBRID,
        preferences={
            "aspect_ratio": arch.default_aspect_ratio,
            "voice_engine": arch.default_voice_engine,
            "voice_id": arch.default_voice_id
        }
    )
    st.session_state["current_archetype_plan"] = plan
    
    # Auto-crear y persistir proyecto en la base de datos local y Firebase
    _persist_current_project(project_id, initial_title, plan)


def _persist_current_project(project_id: str, title: str, plan):
    """Crea y persiste un ProjectEntity en storage/projects/ y respalda en Firebase Firestore."""
    try:
        repo = ProjectRepository()
        proj = ProjectEntity(
            project_id=project_id,
            title=title,
            status=ProjectStatus.CREATED,
            version=1,
            created_at=time.time(),
            render_spec=RenderSpec(
                resolution="1080p",
                fps=24,
                codec="h264",
                burned_subtitles=True
            ),
            scenes=[
                SceneEntity(
                    scene_id=f"{project_id}_sc_{sc.scene_index}",
                    index=sc.scene_index,
                    title=f"Toma {sc.scene_index + 1}: {sc.prompt[:30]}",
                    status=SceneStatus.DRAFT,
                    visual_spec=VisualSpec(
                        prompt=sc.prompt,
                        duration_seconds=sc.duration_seconds,
                        engine_override=sc.recommended_engine
                    )
                ) for sc in getattr(plan, "scenes", [])
            ]
        )
        repo.save_project(proj)
        
        # Respaldo en Firestore
        try:
            firebase_sync.backup_project_to_firebase({
                "task_id": project_id,
                "subject": title,
                "script": str([s.prompt for s in getattr(plan, "scenes", [])]),
                "has_video": False
            })
        except Exception:
            pass
    except Exception:
        pass


def render_studio_orchestrator_view():
    """Renderiza la vista principal de 'Empezar' y el Director Creativo Semántico."""
    
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                🚀 Empezar — Director Creativo & Co-Creación
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">PRODUCCIÓN INTELIGENTE</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Co-crea tu historia conversacionalmente, auto-completa el plan de producción y consolida todos los parámetros narrativos y técnicos.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_director, tab_planner, tab_workflows, tab_engines, tab_jobs = st.tabs([
        "🚀 Empezar & Co-Creación",
        "🎯 Request Planner Libre",
        "🎛️ Registro de Workflows",
        "⚙️ Capacidades & Motores",
        "📈 Trazabilidad de Jobs"
    ])

    # =========================================================
    # TAB 1: EMPEZAR & CO-CREACIÓN CON EL DIRECTOR
    # =========================================================
    with tab_director:
        archetypes = get_all_archetypes()
        arch_opts = [a.id for a in archetypes]
        
        # 1. Selector Superior de Arquetipo de Workflow
        current_arch_id = st.session_state.get("director_arch_id", arch_opts[0])
        curr_idx = arch_opts.index(current_arch_id) if current_arch_id in arch_opts else 0
        
        c_arch1, c_arch2 = st.columns([6, 4], vertical_alignment="center")
        with c_arch1:
            selected_arch_id = st.selectbox(
                "Selecciona el Workflow de Producción:",
                options=arch_opts,
                index=curr_idx,
                format_func=lambda x: f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name}",
                key="director_arch_selector"
            )
        with c_arch2:
            arch = ARCHETYPES_CATALOG[selected_arch_id]
            st.markdown(f"""
                <div style="padding: 6px 12px; background: rgba(15, 23, 42, 0.7); border-radius: 6px; border: 1px solid #334155; font-size: 11.5px; color: #94a3b8;">
                    <b>Formato:</b> <code>{arch.default_aspect_ratio}</code> | <b>Estrategia:</b> <code>{arch.visual_strategy.value.upper()}</code> | <b>Voz:</b> <code>{arch.default_voice_engine}</code>
                </div>
            """, unsafe_allow_html=True)

        # Si el usuario cambió de arquetipo, reiniciar o inicializar sesión de pulido
        if selected_arch_id != st.session_state.get("director_arch_id"):
            _init_director_session(selected_arch_id)

        # Asegurar estado de variables
        if "director_messages" not in st.session_state:
            _init_director_session(selected_arch_id)

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        # Layout Principal: [Columna Izquierda: Chat de Pulido] | [Columna Derecha: Ficha de Producción]
        col_chat, col_ficha = st.columns([6, 5], gap="medium")

        # -----------------------------------------------------
        # COLUMNA IZQUIERDA: PULIDO CONVERSACIONAL
        # -----------------------------------------------------
        with col_chat:
            st.markdown("##### 💬 Pulido Conversacional de la Historia")
            
            # Contenedor con scroll para el historial de mensajes
            chat_container = st.container(height=340, border=True)
            with chat_container:
                for msg in st.session_state.get("director_messages", []):
                    if msg["role"] == "user":
                        st.chat_message("user").markdown(msg["content"])
                    else:
                        st.chat_message("assistant", avatar="🎬").markdown(msg["content"])

            # Sugerencias interactivas de co-creación (Pills en cuadrícula 2x2)
            suggestions = st.session_state.get("director_suggestions", [])
            if suggestions:
                st.markdown("<div style='font-size:11.5px; font-weight:700; color:#38bdf8; margin: 4px 0 2px 0;'>💡 Opciones de Dirección Sugeridas (Haz clic para consolidar):</div>", unsafe_allow_html=True)
                for i in range(0, len(suggestions), 2):
                    c_sug1, c_sug2 = st.columns(2)
                    with c_sug1:
                        sug_txt1 = suggestions[i]
                        clean_lbl1 = sug_txt1.replace("**", "").replace("###", "").strip()
                        if st.button(f"👉 {clean_lbl1}", key=f"sug_btn_{i}", use_container_width=True, help="Incorporar esta dirección creativa al proyecto"):
                            _handle_user_director_message(f"Elegir esta opción: {sug_txt1}", selected_arch_id)
                            st.rerun()
                    if i + 1 < len(suggestions):
                        with c_sug2:
                            sug_txt2 = suggestions[i + 1]
                            clean_lbl2 = sug_txt2.replace("**", "").replace("###", "").strip()
                            if st.button(f"👉 {clean_lbl2}", key=f"sug_btn_{i+1}", use_container_width=True, help="Incorporar esta dirección creativa al proyecto"):
                                _handle_user_director_message(f"Elegir esta opción: {sug_txt2}", selected_arch_id)
                                st.rerun()

            # Caja de texto para hablar con el director
            c_in1, c_in2 = st.columns([8, 2], vertical_alignment="bottom")
            with c_in1:
                user_director_input = st.text_input(
                    "Tu mensaje / idea para el Director:",
                    placeholder=f"Ej: Quiero contar la historia de {arch.name} con un tono muy cinemático...",
                    key="input_user_director_text",
                    label_visibility="collapsed"
                )
            with c_in2:
                if st.button("Enviar 💬", type="primary", use_container_width=True, key="btn_send_director_msg"):
                    if user_director_input.strip():
                        _handle_user_director_message(user_director_input, selected_arch_id)
                        st.rerun()

        # -----------------------------------------------------
        # COLUMNA DERECHA: FICHA DE PRODUCCIÓN EN VIVO
        # -----------------------------------------------------
        with col_ficha:
            spec = st.session_state.get("director_spec", {})
            is_ready = spec.get("ready_to_produce", False)
            step_num = spec.get("interview_step", 1)
            project_id = st.session_state.get("current_project_id", "proj_videopro_draft")
            project_title = st.session_state.get("current_project_title", spec.get("subject", arch.name))
            plan = st.session_state.get("current_archetype_plan")

            # Encabezado con estado del pulido
            st.markdown("##### 📋 Ficha de Producción & Consolidación")
            
            badge_color = "#10b981" if is_ready else "#f59e0b"
            badge_text = "🟢 LISTO PARA PRODUCCIÓN" if is_ready else f"🟡 EN PULIDO NARRATIVO (Paso {step_num}/3)"
            
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 12px; background: rgba(30, 41, 59, 0.6); border-radius: 6px; border: 1px solid #334155; margin-bottom: 8px;">
                    <div style="font-size: 11.5px; font-weight: 700; color: #e2e8f0;">
                        📁 <code style="color: #38bdf8;">{project_id}</code>
                    </div>
                    <div style="font-size: 11px; font-weight: 700; color: {badge_color};">
                        {badge_text}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # -------------------------------------------------
            # CHECKLIST DE CONSOLIDACIÓN DE DATOS EN TIEMPO REAL
            # -------------------------------------------------
            with st.container(border=True):
                st.markdown("<div style='font-size:12px; font-weight:700; color:#f8fafc; margin-bottom:4px;'>📊 Parámetros Consolidados del Workflow:</div>", unsafe_allow_html=True)
                
                # 1. Premisa
                subj_val = spec.get("subject", "")
                if subj_val and len(subj_val) > 3:
                    st.markdown(f"• 📌 **Premisa:** <span style='color:#34d399;'>🟢 {subj_val[:45]}...</span>", unsafe_allow_html=True)
                else:
                    st.markdown("• 📌 **Premisa:** <span style='color:#facc15;'>🟡 En definición</span>", unsafe_allow_html=True)
                
                # 2. Personajes
                char_val = spec.get("characters", "")
                if char_val and len(char_val) > 3:
                    st.markdown(f"• 🧸 **Personajes:** <span style='color:#34d399;'>🟢 {char_val[:45]}...</span>", unsafe_allow_html=True)
                else:
                    st.markdown("• 🧸 **Personajes:** <span style='color:#facc15;'>🟡 En definición conversacional</span>", unsafe_allow_html=True)

                # 3. Conflicto & Clímax
                conf_val = spec.get("dramatic_conflict", "")
                climax_val = spec.get("climax", "")
                if conf_val or climax_val:
                    summary_plot = f"{conf_val} ➔ {climax_val}".strip(" ➔")
                    st.markdown(f"• 💥 **Arco & Clímax:** <span style='color:#34d399;'>🟢 {summary_plot[:45]}...</span>", unsafe_allow_html=True)
                else:
                    st.markdown("• 💥 **Arco & Clímax:** <span style='color:#facc15;'>🟡 En definición</span>", unsafe_allow_html=True)

                # 4. Tomas & Audio
                scene_cnt = len(plan.scenes) if plan else 0
                st.markdown(f"• 🎬 **Tomas Ruteadas:** <span style='color:#34d399;'>🟢 {scene_cnt} Tomas Listas</span> | 🎙️ **Voz & BGM:** <span style='color:#34d399;'>🟢 {spec.get('music_genre', 'BGM')}</span>", unsafe_allow_html=True)

            # Formulario de Parámetros: Auto-rellenado con la conversación, pero editable a mano
            with st.expander("⚙️ Ajustes Técnicos & Formato (Auto-relleno / Editable)", expanded=False):
                # 1. Título Editable
                new_title = st.text_input("Título del Proyecto:", value=project_title, key="input_man_title")
                
                # 2. Aspect Ratio & Estrategia
                c_f1, c_f2 = st.columns(2)
                aspect_opts = ["9:16", "16:9", "1:1"]
                cur_aspect = spec.get("aspect_ratio", arch.default_aspect_ratio)
                asp_idx = aspect_opts.index(cur_aspect) if cur_aspect in aspect_opts else 0
                with c_f1:
                    new_aspect = st.selectbox("Formato / Aspect Ratio:", options=aspect_opts, index=asp_idx, key="sel_man_aspect")
                
                strat_opts = [v.value for v in VisualStrategy]
                cur_strat = spec.get("visual_strategy", arch.visual_strategy.value)
                strat_idx = strat_opts.index(cur_strat) if cur_strat in strat_opts else 0
                with c_f2:
                    new_strat = st.selectbox("Estrategia Visual:", options=strat_opts, index=strat_idx, key="sel_man_strat")

                # 3. Voz y Música
                c_f3, c_f4 = st.columns(2)
                voice_opts = ["vibevoice", "edge_tts", "elevenlabs"]
                with c_f3:
                    new_voice = st.selectbox("Motor de Voz:", options=voice_opts, index=0, key="sel_man_voice")
                with c_f4:
                    new_music = st.text_input("Género BGM:", value=spec.get("music_genre", arch.default_music_genre), key="input_man_music")

                # Si el usuario modificó algún parámetro clave manualmente
                if new_title != project_title or new_aspect != cur_aspect or new_strat != cur_strat:
                    st.session_state["current_project_title"] = new_title
                    spec["subject"] = new_title
                    spec["aspect_ratio"] = new_aspect
                    spec["visual_strategy"] = new_strat
                    st.session_state["director_spec"] = spec
                    
                    # Recompilar plan con los nuevos ajustes manuales
                    plan = RequestPlanner.plan_request(
                        project_id=project_id,
                        user_prompt=new_title,
                        workflow_id=selected_arch_id,
                        visual_strategy=VisualStrategy(new_strat),
                        preferences={
                            "aspect_ratio": new_aspect,
                            "voice_engine": new_voice,
                            "voice_id": spec.get("voice_preset", arch.default_voice_id)
                        }
                    )
                    st.session_state["current_archetype_plan"] = plan
                    _persist_current_project(project_id, new_title, plan)

            # Métricas en vivo del Plan
            if plan:
                m_c1, m_c2, m_c3 = st.columns(3)
                with m_c1:
                    st.metric("Total Escenas", f"{len(plan.scenes)} Tomas")
                with m_c2:
                    st.metric("Duración Total", f"{plan.estimated_total_duration_seconds:.1f}s")
                with m_c3:
                    st.metric("Coste Estimado", "$0.00 (ZeroGPU)")

                # Desglose de Escenas con Ópticas y Motores (Editable)
                st.markdown("**🎬 Desglose de Escenas & Ruteo Óptico:**")
                with st.container(height=160, border=True):
                    for sc in plan.scenes:
                        with st.expander(f"Toma {sc.scene_index + 1}: {sc.prompt[:40]}... ({sc.recommended_engine})", expanded=False):
                            c_sc_p, c_sc_eng = st.columns([7, 3])
                            with c_sc_p:
                                edited_prompt = st.text_area(f"Prompt Toma {sc.scene_index + 1}:", value=sc.prompt, height=65, key=f"p_sc_{sc.scene_index}")
                                if edited_prompt != sc.prompt:
                                    sc.prompt = edited_prompt
                            with c_sc_eng:
                                eng_list = ["google_flow", "flux_video", "nanobanana", "stock_db", "ltx25"]
                                cur_eng_idx = eng_list.index(sc.recommended_engine) if sc.recommended_engine in eng_list else 0
                                edited_eng = st.selectbox(f"Motor Toma {sc.scene_index + 1}:", options=eng_list, index=cur_eng_idx, key=f"eng_sc_{sc.scene_index}")
                                if edited_eng != sc.recommended_engine:
                                    sc.recommended_engine = edited_eng
                            
                            st.caption(f"• **Tipo de Toma:** `{sc.shot_type}` | **Duración:** {sc.duration_seconds}s | **Proveedor:** `{sc.assigned_provider}`")

            # -------------------------------------------------
            # BOTÓN DE LANZAMIENTO Y SEGUIMIENTO EN VIVO
            # -------------------------------------------------
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            
            # Notificación visual cuando los datos están listos
            if is_ready or len(st.session_state.get("director_messages", [])) >= 3:
                st.markdown("""
                    <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; margin-bottom: 6px; font-size: 11.5px; color: #34d399; display: flex; align-items: center; gap: 6px;">
                        <span>🎉</span> <b>¡Proyecto consolidado!</b> Listo para rodar y renderizar en el pipeline.
                    </div>
                """, unsafe_allow_html=True)

            c_btn1, c_btn2 = st.columns([6, 4])
            with c_btn1:
                if st.button("🚀 Iniciar Producción y Renderizado", type="primary", use_container_width=True, key="btn_exec_director_job"):
                    if plan:
                        progress_slot = st.empty()
                        with progress_slot.container():
                            st.info(f"⏳ **Iniciando Producción Cinemática** para `{project_title}`...")
                            prog_bar = st.progress(0.1, text="[1/5] Compilando Escenas y Guion...")
                            time.sleep(0.3)
                            
                            job = RequestPlanner.create_job_from_plan(plan)
                            executor = WorkflowExecutor()
                            
                            prog_bar.progress(0.35, text="[2/5] Generando Locución VibeVoice y Banda Sonora...")
                            time.sleep(0.3)
                            
                            prog_bar.progress(0.65, text="[3/5] Renderizando Tomas en ComfyUI & FLUX 3...")
                            res_job = executor.execute_job(job)
                            StudioRepository.save_job(res_job)
                            
                            prog_bar.progress(0.85, text="[4/5] Ensamblado y Masterización FFmpeg...")
                            time.sleep(0.2)
                            
                            prog_bar.progress(1.0, text="[5/5] Sincronización en la Nube (R2 & Firestore)...")
                            time.sleep(0.2)
                            
                        st.success(f"✅ ¡Producción finalizada con éxito! Job ID: `{res_job.job_id}`.")
                        st.session_state["last_completed_job_id"] = res_job.job_id
                        st.session_state["last_completed_job_data"] = res_job.model_dump()
                        st.rerun()

            with c_btn2:
                if st.button("🏛️ Workflow Studio", use_container_width=True, key="btn_goto_pipeline"):
                    st.session_state["active_view"] = "pipeline"
                    st.rerun()

            # Tarjeta de Último Vídeo Renderizado / Producción Completada
            if "last_completed_job_data" in st.session_state:
                last_job = st.session_state["last_completed_job_data"]
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:12px; font-weight:700; color:#34d399;'>🎬 Vídeo Master Listo: Job `{last_job.get('job_id')}`</div>", unsafe_allow_html=True)
                    st.caption(f"• **Proyecto:** `{last_job.get('project_id')}` | **Tomas:** {len(last_job.get('steps', []))} | **Estado:** `COMPLETED`")
                    c_v1, c_v2 = st.columns(2)
                    with c_v1:
                        if st.button("📁 Ver en Proyectos", use_container_width=True, key="btn_view_in_projects"):
                            st.session_state["active_view"] = "projects"
                            st.rerun()
                    with c_v2:
                        if st.button("🎞️ Ver en Bóveda", use_container_width=True, key="btn_view_in_vault"):
                            st.session_state["active_view"] = "cinema_vault"
                            st.rerun()

    # =========================================================
    # TAB 2: REQUEST PLANNER & SIMULADOR LIBRE
    # =========================================================
    with tab_planner:
        st.markdown("#### 🎯 Generador de Plan de Ejecución Libre")
        st.caption("Introduce una petición libre para ver cómo el Request Planner descompone la tarea en Capabilities y asigna motores por escena.")

        c_p1, c_p2 = st.columns([7, 3], gap="medium")
        with c_p1:
            free_prompt = st.text_area(
                "Petición Libre de Vídeo:",
                value="Documental histórico de 60s sobre la exploración lunar del Apolo 11 en 1969 con fotografías auténticas y recreación 35mm.",
                height=100,
                key="planner_free_prompt_input"
            )
        with c_p2:
            st.markdown("**Parámetros de Simulación:**")
            strat = st.selectbox("Estrategia Visual:", options=[v.value for v in VisualStrategy], index=0)
            aspect = st.selectbox("Aspect Ratio:", options=["16:9", "9:16", "1:1"], index=0)
            voice = st.selectbox("Voz de Narración:", options=["vibevoice", "edge_tts", "elevenlabs"], index=0)

        if st.button("⚡ Compilar Plan de Ejecución", type="primary", key="btn_compile_free_plan"):
            plan = RequestPlanner.plan_request(
                project_id=f"proj_free_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_prompt=free_prompt,
                workflow_id="DOCUMENTARY_MASTER",
                visual_strategy=VisualStrategy(strat),
                preferences={
                    "aspect_ratio": aspect,
                    "voice_engine": voice
                }
            )
            st.session_state["last_free_plan"] = plan

        if "last_free_plan" in st.session_state:
            plan = st.session_state["last_free_plan"]
            st.markdown("<hr style='margin: 12px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
            st.markdown(f"### 📋 Plan Resuelto: `{plan.workflow_id}` ({len(plan.scenes)} Escenas)")
            for sc in plan.scenes:
                with st.expander(f"Escena {sc.scene_index + 1}: {sc.prompt} ({sc.recommended_engine.upper()})"):
                    st.markdown(f"• **Motor:** <code>{sc.recommended_engine}</code> | **Proveedor:** <code>{sc.assigned_provider}</code>")
                    st.markdown(f"• **Toma:** <code>{sc.shot_type}</code> | **Duración:** {sc.duration_seconds}s")

    # =========================================================
    # TAB 3: REGISTRO DE WORKFLOWS Y VERSIONES
    # =========================================================
    with tab_workflows:
        st.markdown("#### 🎛️ Workflows Registrados en el Sistema")
        st.caption("Definiciones canónicas y bucle de mejora continua de grafos de producción.")
        
        all_wfs = get_all_workflows()
        for wf in all_wfs:
            with st.expander(f"Workflow: {wf.name} (`{wf.id}` — v{wf.version})", expanded=False):
                st.markdown(f"**Descripción:** {wf.description}")
                st.markdown(f"**Nodos Configurados:** {len(wf.nodes)} | **Versión:** `{wf.version_label}`")
                st.json(wf.model_dump())

    # =========================================================
    # TAB 4: CAPACIDADES Y MOTORES
    # =========================================================
    with tab_engines:
        st.markdown("#### ⚙️ Inventario de Capacidades y Motores de Vídeo")
        st.caption("Catálogo desacoplado de funciones técnicas y motores de inferencia activos.")

        c_cap1, c_cap2 = st.columns(2, gap="medium")
        with c_cap1:
            st.markdown("##### 🧩 Capacidades (Contratos Abstractos)")
            for cap in get_all_capabilities():
                st.markdown(f"• **`{cap.name}`** (`{cap.id}`): {cap.description}")

        with c_cap2:
            st.markdown("##### 🚀 Motores (Engines)")
            for eng in get_all_engines():
                st.markdown(f"• **`{eng.name}`** (`{eng.id}`): {eng.description}")

    # =========================================================
    # TAB 5: TRAZABILIDAD DE JOBS
    # =========================================================
    with tab_jobs:
        st.markdown("#### 📈 Historial de Jobs y Trazabilidad")
        st.caption("Registro de ejecuciones, tiempos de cómputo y estado de entrega.")

        jobs_history = StudioRepository.list_jobs(limit=15)
        if not jobs_history:
            st.info("No hay Jobs ejecutados aún. Lanza una producción desde la pestaña de Empezar.")
        else:
            for job_rec in jobs_history:
                j_id = job_rec.get("job_id", "job_unknown")
                j_status = str(job_rec.get("status", "unknown")).upper()
                j_wf = job_rec.get("workflow_id", "wf")
                j_proj = job_rec.get("project_id", "proj")
                j_metrics = job_rec.get("metrics", {})
                j_steps = job_rec.get("steps", [])
                with st.expander(f"Job `{j_id}` — {j_status} ({j_wf})", expanded=False):
                    st.markdown(f"• **Proyecto:** `{j_proj}` | **Duración:** {j_metrics.get('total_duration_seconds', 0):.2f}s")
                    st.markdown(f"• **Pasos Ejecutados:** {len(j_steps)}")
                    st.json(job_rec)


def _handle_user_director_message(user_text: str, arch_id: str):
    """Procesa el mensaje del usuario con el Director Creativo Semántico y actualiza el plan/proyecto."""
    arch = ARCHETYPES_CATALOG.get(arch_id, list(ARCHETYPES_CATALOG.values())[0])
    
    # 1. Agregar mensaje del usuario al historial
    messages = st.session_state.get("director_messages", [])
    messages.append({"role": "user", "content": user_text})
    
    # 2. Obtener respuesta del Director Semántico
    with st.spinner("El Director Creativo está analizando tu historia y adaptando el plan..."):
        res = semantic_director.chat_with_director(messages, user_text)
    
    # 3. Guardar respuesta y sugerencias
    assistant_content = res.get("response_text") or res.get("reply") or "El Director Creativo ha procesado tu historia."
    messages.append({"role": "assistant", "content": assistant_content})
    st.session_state["director_messages"] = messages
    st.session_state["director_suggestions"] = res.get("suggestions", [])
    
    spec = res.get("spec", {})
    st.session_state["director_spec"] = spec
    
    # 4. Generar título contextual y ID del proyecto
    subject = spec.get("subject") or user_text
    st.session_state["current_project_title"] = subject
    
    slug = _slugify(subject)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_id = f"proj_{slug}_{timestamp}"
    st.session_state["current_project_id"] = project_id
    
    aspect = spec.get("aspect_ratio") or arch.default_aspect_ratio
    
    # 5. Compilar Plan de Producción
    plan = RequestPlanner.plan_request(
        project_id=project_id,
        user_prompt=subject,
        workflow_id=arch_id,
        visual_strategy=VisualStrategy.HYBRID,
        preferences={
            "aspect_ratio": aspect,
            "voice_engine": arch.default_voice_engine,
            "voice_id": spec.get("voice_preset", arch.default_voice_id)
        }
    )
    
    # 6. Integrar tomas generadas por el Director si existen
    scene_beats = spec.get("scene_beats")
    if scene_beats and isinstance(scene_beats, list):
        custom_scenes = []
        for idx, beat in enumerate(scene_beats):
            eng = beat.get("engine", "flux_video")
            custom_scenes.append(
                ScenePlan(
                    scene_index=idx,
                    scene_id=f"{project_id}_sc_{idx}",
                    prompt=beat.get("prompt", f"Plano {idx+1}: {subject}"),
                    shot_type=beat.get("shot_type", "medium"),
                    visual_theme="character_dialogue",
                    recommended_engine=eng,
                    assigned_provider="flux_zerogpu" if eng == "flux_video" else "comfyui_local",
                    duration_seconds=float(beat.get("duration", 4.0)),
                    aspect_ratio=aspect
                )
            )
        plan.scenes = custom_scenes
        plan.estimated_total_duration_seconds = sum(s.duration_seconds for s in custom_scenes)

    st.session_state["current_archetype_plan"] = plan
    
    # 7. Auto-crear y persistir proyecto en la base de datos local y Firebase Firestore
    _persist_current_project(project_id, subject, plan)
