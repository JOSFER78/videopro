"""
Vista de Orquestación y Director Creativo Semántico — VideoPro Studio
Entrada Principal: '🚀 Empezar' — Co-Creación Conversacional, Cadena de Pensamiento Narrativa (CoT),
Investigación Profunda de Ideas, Biblia de Personajes, Ficha de Producción Consolidada y Renderizado.
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
from webui.views.view_comfy_pipeline import render_comfy_canvas_component


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
        "chain_of_thought": "Sesión iniciada. Esperando concepto o idea libre del usuario.",
        "visual_style": arch.visual_strategy.value,
        "aspect_ratio": arch.default_aspect_ratio,
        "voice_preset": arch.default_voice_id,
        "music_genre": arch.default_music_genre,
        "ready_to_produce": False,
        "interview_step": 1,
        "summary_reasoning": "Sesión iniciada. Esperando concepto del usuario."
    }
    
    # Inicializar estado puramente en memoria (Cero escrituras a disco, cero llamadas de IA en el arranque)
    st.session_state["current_archetype_plan"] = None


def load_project_into_session(project_id: str) -> bool:
    """Carga de forma íntegra un proyecto existente desde Firestore o disco en session_state."""
    repo = ProjectRepository()
    proj_dict = repo.load_project_dict(project_id)
    if not proj_dict:
        return False

    arch_id = proj_dict.get("workflow_id", "PIXAR_3D_ANIMATION")
    arch = ARCHETYPES_CATALOG.get(arch_id, list(ARCHETYPES_CATALOG.values())[0])

    st.session_state["director_arch_id"] = arch_id
    st.session_state["current_project_id"] = project_id
    st.session_state["current_project_title"] = proj_dict.get("title") or proj_dict.get("subject", project_id)

    # 1. Cargar historial de chat si existe
    messages = proj_dict.get("messages", [])
    if messages:
        st.session_state["director_messages"] = messages
    else:
        st.session_state["director_messages"] = [
            {
                "role": "assistant",
                "content": f"¡Hola! Has cargado el proyecto **{st.session_state['current_project_title']}** ({arch.icon} {arch.name}).\n\nTodos los parámetros, tomas y ficha de producción han sido restaurados. ¿Deseas modificar algo o iniciar producción?"
            }
        ]

    # 2. Cargar director_spec
    spec = proj_dict.get("director_spec", {})
    if not spec:
        spec = {
            "archetype_id": arch_id,
            "subject": st.session_state["current_project_title"],
            "characters": "",
            "dramatic_conflict": "",
            "climax": "",
            "chain_of_thought": "Proyecto cargado desde la biblioteca.",
            "visual_style": arch.visual_strategy.value,
            "aspect_ratio": proj_dict.get("aspect_ratio", arch.default_aspect_ratio),
            "voice_preset": proj_dict.get("voice_id", arch.default_voice_id),
            "music_genre": arch.default_music_genre,
            "ready_to_produce": True,
            "interview_step": 3,
            "summary_reasoning": "Proyecto cargado desde Firestore / disco."
        }
    st.session_state["director_spec"] = spec

    # 3. Cargar escenas en el Plan
    scenes_data = proj_dict.get("scenes", [])
    if scenes_data:
        plan_scenes = []
        for s in scenes_data:
            v_spec = s.get("visual_spec", {}) if isinstance(s.get("visual_spec"), dict) else {}
            plan_scenes.append(
                ScenePlan(
                    scene_id=s.get("scene_id", f"{project_id}_sc_{s.get('index', 0)}"),
                    scene_index=int(s.get("index", 0)),
                    prompt=s.get("prompt") or v_spec.get("subject", "Toma cinemática"),
                    recommended_engine=s.get("engine") or s.get("recommended_engine") or v_spec.get("engine", "nanobanana"),
                    assigned_provider=s.get("assigned_provider", "local"),
                    shot_type=s.get("shot_type", "Cinematic Medium Shot"),
                    duration_seconds=float(s.get("duration") or s.get("duration_seconds") or v_spec.get("duration_s", 4.5)),
                    aspect_ratio=proj_dict.get("aspect_ratio", arch.default_aspect_ratio)
                )
            )
        from app.core.orchestration.planner import ExecutionPlan
        plan = ExecutionPlan(
            project_id=project_id,
            workflow_id=arch_id,
            workflow_version=1,
            visual_strategy=VisualStrategy.HYBRID,
            steps=[],
            scenes=plan_scenes,
            estimated_total_duration_seconds=sum(sc.duration_seconds for sc in plan_scenes)
        )
        st.session_state["current_archetype_plan"] = plan
    else:
        plan = RequestPlanner.plan_request(
            project_id=project_id,
            user_prompt=st.session_state["current_project_title"],
            workflow_id=arch_id,
            visual_strategy=VisualStrategy.HYBRID,
            preferences={
                "aspect_ratio": proj_dict.get("aspect_ratio", arch.default_aspect_ratio),
                "voice_engine": arch.default_voice_engine,
                "voice_id": proj_dict.get("voice_id", arch.default_voice_id)
            }
        )
        st.session_state["current_archetype_plan"] = plan

    return True


def _persist_current_project(project_id: str, title: str, plan):
    """Crea y persiste un ProjectEntity en storage/projects/ y respalda en Firebase Firestore."""
    try:
        repo = ProjectRepository()
        scenes_list = []
        scenes_export = []
        for sc in getattr(plan, "scenes", []):
            scenes_list.append(
                SceneEntity(
                    scene_id=f"{project_id}_sc_{sc.scene_index}",
                    index=sc.scene_index,
                    title=f"Toma {sc.scene_index + 1}: {sc.prompt[:30]}",
                    status=SceneStatus.PENDING,
                    visual_spec=VisualSpec(
                        subject=sc.prompt,
                        duration_s=float(getattr(sc, "duration_seconds", 4.0))
                    )
                )
            )
            scenes_export.append({
                "scene_id": f"{project_id}_sc_{sc.scene_index}",
                "index": sc.scene_index,
                "prompt": sc.prompt,
                "engine": getattr(sc, "recommended_engine", "nanobanana"),
                "shot_type": getattr(sc, "shot_type", "Cinematic Medium Shot"),
                "duration": float(getattr(sc, "duration_seconds", 4.0))
            })

        arch_id = st.session_state.get("director_arch_id", "PIXAR_3D_ANIMATION")
        arch = ARCHETYPES_CATALOG.get(arch_id, list(ARCHETYPES_CATALOG.values())[0])
        cur_spec = st.session_state.get("director_spec", {})
        cur_messages = st.session_state.get("director_messages", [])

        proj = ProjectEntity(
            project_id=project_id,
            title=title,
            status=ProjectStatus.DRAFT,
            version=1,
            created_at=time.time(),
            render_spec=RenderSpec(
                resolution="1080p",
                fps=24,
                codec="h264",
                burned_subtitles=True
            ),
            scenes=scenes_list
        )
        
        # Guardar en la estructura estándar: storage/projects/YYYY/MM/DD/workflow_id/project_name/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        target_dir = repo.get_project_dir_structured(arch_id, title or project_id)
        os.makedirs(target_dir, exist_ok=True)
        rel_storage_path = os.path.relpath(target_dir, os.path.join(base_dir, "storage", "projects"))
        parts = rel_storage_path.split(os.sep)

        full_project_data = {
            "project_id": project_id,
            "task_id": project_id,
            "title": title,
            "subject": cur_spec.get("subject", title),
            "workflow_id": arch_id,
            "workflow_name": arch.name,
            "workflow_icon": arch.icon,
            "year": parts[0] if len(parts) >= 5 else datetime.now().strftime("%Y"),
            "month": parts[1] if len(parts) >= 5 else datetime.now().strftime("%m"),
            "day": parts[2] if len(parts) >= 5 else datetime.now().strftime("%d"),
            "folder_name": parts[4] if len(parts) >= 5 else os.path.basename(target_dir),
            "storage_path": os.path.relpath(target_dir, base_dir),
            "status": "DRAFT",
            "aspect_ratio": getattr(plan, "aspect_ratio", cur_spec.get("aspect_ratio", "16:9")),
            "voice_id": getattr(plan, "voice_id", cur_spec.get("voice_preset", "vibevoice")),
            "director_spec": cur_spec,
            "scenes": scenes_export,
            "messages": cur_messages,
            "updated_at": time.time()
        }
        with open(os.path.join(target_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump(full_project_data, f, indent=2, ensure_ascii=False)

        # Respaldo relacional en Firestore en segundo plano (Zero UI Latency)
        try:
            firebase_sync.backup_project_to_firebase_async(full_project_data)
        except Exception:
            pass

        # Invalidar caché de escaneo de proyectos
        try:
            from webui.views.view_projects import invalidate_projects_cache
            invalidate_projects_cache()
        except Exception:
            pass
    except Exception as e:
        import traceback
        traceback.print_exc()


def render_studio_orchestrator_view():
    """Renderiza la vista principal de 'Empezar' y el Director Creativo Semántico."""
    
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                🚀 Empezar — Director Creativo & Co-Creación
                <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 12px;">INVESTIGACIÓN & GUION PROFUNDO</span>
            </h2>
            <p style="font-size: 12.5px; color: #94a3b8; margin: 0;">
                Diálogo interactivo, investigación profunda con Cadena de Pensamiento (CoT), selección de opciones y consolidación automática.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_director, tab_planner, tab_workflows, tab_engines, tab_jobs, tab_ontology = st.tabs([
        "🚀 Empezar & Co-Creación",
        "🎯 Request Planner Libre",
        "🎛️ Registro de Workflows",
        "⚙️ Capacidades & Motores",
        "📈 Trazabilidad de Jobs",
        "🏛️ Ontología (4 Niveles & Firebase)"
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
        # COLUMNA IZQUIERDA: CONFIGURACIÓN & CO-CREACIÓN
        # -----------------------------------------------------
        with col_chat:
            st.markdown("##### 📝 Nuevo Proyecto & Premisa")
            
            p_title_input = st.text_input(
                "Nombre del Proyecto:",
                value=st.session_state.get("current_project_title", f"{arch.name} — Proyecto"),
                key="input_init_proj_title"
            )
            st.session_state["current_project_title"] = p_title_input

            p_idea_input = st.text_area(
                "Idea, Concepto o Guion Base:",
                placeholder=f"Ej: Documental sobre los misterios ocultos de la ciudad con recreaciones visuales e investigación de archivo...",
                key="input_init_proj_idea",
                height=90
            )

            if st.button("🚀 Comenzar Co-Creación con el Director", type="primary", use_container_width=True, key="btn_start_cocreation"):
                if p_idea_input.strip():
                    _handle_user_director_message(p_idea_input, selected_arch_id)
                    st.rerun()
                elif p_title_input.strip():
                    _handle_user_director_message(f"Crear una producción basada en el título: {p_title_input}", selected_arch_id)
                    st.rerun()
                else:
                    st.warning("Introduce un título o idea para comenzar.")

            st.markdown("<hr style='margin: 8px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
            st.markdown("##### 💬 Pulido Conversacional de la Historia")
            
            # Contenedor con scroll para el historial de mensajes
            chat_container = st.container(height=260, border=True)
            with chat_container:
                for msg in st.session_state.get("director_messages", []):
                    if msg["role"] == "user":
                        st.chat_message("user").markdown(msg["content"])
                    else:
                        st.chat_message("assistant", avatar="🎬").markdown(msg["content"])

            # Sugerencias interactivas de co-creación (Pills con las opciones del Director)
            suggestions = st.session_state.get("director_suggestions", [])
            if suggestions:
                st.markdown("<div style='font-size:11.5px; font-weight:700; color:#38bdf8; margin: 4px 0 2px 0;'>💡 Ángulos Sugeridos por el Director:</div>", unsafe_allow_html=True)
                for i, sug_txt in enumerate(suggestions):
                    clean_lbl = sug_txt.replace("**", "").replace("###", "").strip()
                    if st.button(f"👉 {clean_lbl}", key=f"sug_btn_{i}", use_container_width=True):
                        _handle_user_director_message(f"Elegir esta opción y desarrollar su guion a fondo: {sug_txt}", selected_arch_id)
                        st.rerun()

            # Caja de texto para continuar el diálogo
            with st.expander("✏️ Continuar Diálogo / Ajustar Detalles", expanded=False):
                user_director_input = st.text_area(
                    "Tu respuesta / ajuste:",
                    placeholder="Escribe tu indicación o detalle que quieras modificar...",
                    key="input_user_director_text",
                    height=65
                )
                if st.button("Enviar Ajuste 💬", use_container_width=True, key="btn_send_director_msg"):
                    if user_director_input.strip():
                        _handle_user_director_message(user_director_input, selected_arch_id)
                        st.rerun()

            # -------------------------------------------------
            # CADENA DE PENSAMIENTO & RAZONAMIENTO NARRATIVO (CoT)
            # -------------------------------------------------
            spec = st.session_state.get("director_spec", {})
            cot_text = spec.get("chain_of_thought", "")
            if cot_text and len(cot_text) > 10 and cot_text != "Análisis narrativo inicial.":
                with st.expander("🧠 Cadena de Pensamiento & Razonamiento Narrativo del Director", expanded=False):
                    st.markdown(f"""
                        <div style="padding: 8px 12px; background: rgba(15, 23, 42, 0.85); border-left: 3px solid #818cf8; border-radius: 4px; font-size: 11.5px; color: #cbd5e1; line-height: 1.5;">
                            <b>Análisis Simbólico & Estético:</b><br>{cot_text}
                        </div>
                    """, unsafe_allow_html=True)

        # -----------------------------------------------------
        # COLUMNA DERECHA: FICHA DE PRODUCCIÓN EN VIVO
        # -----------------------------------------------------
        with col_ficha:
            is_ready = spec.get("ready_to_produce", False)
            step_num = spec.get("interview_step", 1)
            project_id = st.session_state.get("current_project_id", "proj_videopro_draft")
            project_title = st.session_state.get("current_project_title", spec.get("subject", arch.name))
            plan = st.session_state.get("current_archetype_plan")

            # Encabezado con estado del pulido
            st.markdown("##### 📋 Ficha de Producción & Consolidación")
            
            badge_color = "#10b981" if is_ready else "#f59e0b"
            badge_text = "🟢 LISTO PARA PRODUCCIÓN" if is_ready else f"🟡 EN INVESTIGACIÓN (Paso {step_num}/3)"
            
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

                # Desglose de Escenas con Guion Literario y Ruteo Óptico (Editable)
                st.markdown("**🎬 Desglose de Escenas & Guion Profundo:**")
                with st.container(height=170, border=True):
                    for sc in plan.scenes:
                        with st.expander(f"Toma {sc.scene_index + 1}: {sc.prompt[:40]}... ({sc.recommended_engine})", expanded=False):
                            c_sc_p, c_sc_eng = st.columns([7, 3])
                            with c_sc_p:
                                edited_prompt = st.text_area(f"Prompt Visual Toma {sc.scene_index + 1}:", value=sc.prompt, height=65, key=f"p_sc_{sc.scene_index}")
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
            # DIRECTRICES DE APRENDIZAJE ACTIVAS (SELF-LEARNING MEMORY)
            # -------------------------------------------------
            try:
                from app.services.learning_memory_engine import learning_engine
                guidelines = learning_engine.get_active_guidelines(selected_arch_id)
                active_rules = guidelines.get("rules", [])
                if active_rules:
                    with st.expander(f"🧠 Directrices & Reglas Áureas de Aprendizaje Inyectadas ({len(active_rules)} Activas)", expanded=False):
                        st.caption("Estas reglas se aplican automáticamente al guion, ritmo visual, tipografía y motores para evitar errores pasados:")
                        for r in active_rules:
                            sev_icon = "🔴" if r["severity"] == "CRITICAL" else ("🟠" if r["severity"] == "STRICT" else "🔵")
                            st.markdown(f"""
                                <div style="background: rgba(15, 23, 42, 0.7); border-left: 3px solid #38bdf8; padding: 6px 10px; border-radius: 0 6px 6px 0; margin-bottom: 6px; font-size: 11.5px;">
                                    <strong>{sev_icon} {r.get('title', '')}</strong> ({r.get('category', '')})<br>
                                    <span style="color: #4ade80;">✨ Estándar:</span> {r.get('golden_rule', r.get('golden_standard', ''))}
                                </div>
                            """, unsafe_allow_html=True)
            except Exception:
                pass

            # -------------------------------------------------
            # BOTÓN DE LANZAMIENTO Y SEGUIMIENTO EN VIVO
            # -------------------------------------------------
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            
            # Notificación visual cuando los datos están listos
            if is_ready or len(st.session_state.get("director_messages", [])) >= 3:
                st.markdown("""
                    <div style="padding: 8px 12px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; margin-bottom: 6px; font-size: 11.5px; color: #34d399; display: flex; align-items: center; gap: 6px;">
                        <span>🎉</span> <b>¡Proyecto consolidado!</b> Listo para rodar y renderizar en el pipeline con memoria de experiencia.
                    </div>
                """, unsafe_allow_html=True)


            c_btn1, c_btn2 = st.columns([6, 4])
            with c_btn1:
                if st.button("🚀 Iniciar Producción y Renderizado", type="primary", use_container_width=True, key="btn_exec_director_job"):
                    if plan:
                        progress_slot = st.empty()
                        with progress_slot.container():
                            st.info(f"⏳ **Iniciando Producción Cinemática** para `{project_title}`...")
                            prog_bar = st.progress(0.1, text="[1/5] Compilando Escenas y Guion Literario...")
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

        # -------------------------------------------------
        # LIENZO VISUAL COMFYUI SINCRONIZADO EN TIEMPO REAL
        # -------------------------------------------------
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        with st.expander(f"🎨 Lienzo Visual ComfyUI del Workflow: {arch.name} (Interactuar & Modificar)", expanded=False):
            st.caption("Lienzo de nodos activo con cables Bezier y asistente agéntico. Los cambios se sincronizan en tiempo real con este proyecto y Firestore.")
            current_graph = arch.pipeline_graph
            render_comfy_canvas_component(current_graph, height=720)

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
    # TAB 3: REGISTRO DE WORKFLOWS Y LIENZO VISUAL COMFYUI
    # =========================================================
    with tab_workflows:
        st.markdown("#### 🎛️ Registro Maestro de Workflows & Lienzo Visual ComfyUI")
        st.caption("Visualiza, edita y sincroniza cualquier flujo de producción con el motor ComfyUI 60 FPS.")

        c_wf_sel, c_wf_btn = st.columns([7, 3], vertical_alignment="center")
        with c_wf_sel:
            tab3_arch_opts = list(ARCHETYPES_CATALOG.keys())
            tab3_sel_arch = st.selectbox(
                "Selecciona el Workflow a Visualizar en el Lienzo:",
                options=tab3_arch_opts,
                index=0,
                format_func=lambda x: f"{ARCHETYPES_CATALOG[x].icon} {ARCHETYPES_CATALOG[x].name} ({ARCHETYPES_CATALOG[x].category.upper()})",
                key="tab3_arch_selector"
            )
        with c_wf_btn:
            if st.button("🚀 Usar este Workflow en Co-Creación", type="primary", use_container_width=True, key="btn_tab3_use_wf"):
                st.session_state["director_arch_id"] = tab3_sel_arch
                _init_director_session(tab3_sel_arch)
                st.rerun()

        arch_to_show = ARCHETYPES_CATALOG[tab3_sel_arch]
        st.markdown(f"**Estrategia Óptica:** `{arch_to_show.visual_strategy.value.upper()}` | **Relación:** `{arch_to_show.default_aspect_ratio}` | **Locución:** `{arch_to_show.default_voice_engine}`")

        # Renderizar el Lienzo ComfyUI
        render_comfy_canvas_component(arch_to_show.pipeline_graph, height=800)

        # Definición canónica JSON colapsable
        with st.expander(f"📄 Manifiesto JSON Canónico ({arch_to_show.name})", expanded=False):
            st.json(arch_to_show.pipeline_graph)

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

    # =========================================================
    # TAB 6: ONTOLOGÍA DEL SISTEMA (4 NIVELES & FIREBASE)
    # =========================================================
    with tab_ontology:
        from app.core.orchestration.videopro_system_registry import (
            SYSTEM_APIS, SYSTEM_CAPABILITIES, SYSTEM_NODES, SYSTEM_WORKFLOWS, sync_entire_ontology_to_firebase
        )

        st.markdown("### 🏛️ Arquitectura de 4 Niveles — VideoPro & Hermes Engine")
        st.caption("Jerarquía clara y unificada entre APIs/Proveedores, Capacidades Atómicas, Nodos de Producción y Workflows de Canales YouTube.")

        c_sync1, c_sync2 = st.columns([8, 2], vertical_alignment="center")
        with c_sync1:
            st.info("🔥 **Sincronización en la Nube:** Los 4 niveles están respaldados en tiempo real en Firebase Firestore (`ayuda-emilio-83261`).")
        with c_sync2:
            if st.button("🔄 Sync Firebase", use_container_width=True):
                ok = sync_entire_ontology_to_firebase()
                if ok:
                    st.success("¡Sincronizado en Firestore!")
                else:
                    st.error("Error al sincronizar.")

        # Sub-tabs para los 4 Niveles
        sub_ont1, sub_ont2, sub_ont3, sub_ont4 = st.tabs([
            "📡 1. APIs & Recursos",
            "⚡ 2. Capacidades Atómicas",
            "🧱 3. Nodos de Producción",
            "🎬 4. Workflows / Canales YouTube"
        ])

        with sub_ont1:
            st.markdown("##### 📡 Nivel 1: APIs, Servidores y Servicios Base")
            st.caption("Proveedores de infraestructura, serverless, bases de datos y motores de código.")
            for api_id, api_obj in SYSTEM_APIS.items():
                with st.expander(f"🔌 `{api_obj.id}` — {api_obj.name} ({api_obj.category.value})", expanded=False):
                    st.markdown(f"• **Categoría:** `{api_obj.category.value}`")
                    st.markdown(f"• **Base URL / Endpoint:** `{api_obj.base_url or 'N/A (Local / Cloud Native)'}`")
                    st.markdown(f"• **Serverless Gratuito:** `{'Sí' if api_obj.is_serverless_free else 'No'}`")
                    st.markdown(f"• **Estado:** `🟢 {api_obj.status}`")

        with sub_ont2:
            st.markdown("##### ⚡ Nivel 2: Capacidades Atómicas (Capabilities)")
            st.caption("Unidades ejecutables que consumen una o más APIs para realizar una tarea específica.")
            for cap_id, cap_obj in SYSTEM_CAPABILITIES.items():
                with st.expander(f"⚙️ `{cap_obj.id}` — {cap_obj.name} [{cap_obj.output_type}]", expanded=False):
                    st.markdown(f"• **Descripción:** {cap_obj.description}")
                    st.markdown(f"• **Tipo de Salida:** `{cap_obj.output_type}`")
                    st.markdown(f"• **APIs Requeridas:** `{', '.join(cap_obj.required_apis) if cap_obj.required_apis else 'Motor Interno'}`")

        with sub_ont3:
            st.markdown("##### 🧱 Nivel 3: Nodos de Producción (Nodes)")
            st.caption("Agrupación funcional de capacidades coordinadas que resuelven una etapa completa.")
            for node_id, node_obj in SYSTEM_NODES.items():
                with st.expander(f"📦 Nodo {node_obj.number}: **{node_obj.name}** (`{node_obj.id}`)", expanded=True):
                    st.markdown(f"• **Rol Funcional:** {node_obj.role_description}")
                    st.markdown("• **Capacidades que Agrupa:**")
                    for c_id in node_obj.capabilities:
                        c_meta = SYSTEM_CAPABILITIES.get(c_id)
                        c_label = c_meta.name if c_meta else c_id
                        st.markdown(f"  - ⚡ `{c_id}`: *{c_label}*")

        with sub_ont4:
            st.markdown("##### 🎬 Nivel 4: Workflows / Pipelines por Canal de YouTube")
            st.caption("La secuencia completa y optimizada de nodos diseñada específicamente para un canal de YouTube.")
            for wf_id, wf_obj in SYSTEM_WORKFLOWS.items():
                with st.expander(f"🎥 **{wf_obj.name}** (`{wf_obj.id}`)", expanded=True):
                    st.markdown(f"• **Descripción:** {wf_obj.description}")
                    st.markdown(f"• **Canal Objetivo:** `{wf_obj.channel_target.channel_name}` ({wf_obj.channel_target.niche})")
                    st.markdown(f"• **Formato & Estilo Visual:** `{wf_obj.channel_target.format}` — *{wf_obj.channel_target.visual_style}*")
                    st.markdown("• **Secuencia Ordenada de Nodos:**")
                    for n_idx, n_id in enumerate(wf_obj.ordered_nodes, 1):
                        n_meta = SYSTEM_NODES.get(n_id)
                        n_label = n_meta.name if n_meta else n_id
                        st.markdown(f"  {n_idx}. 🧱 **Nodo {n_meta.number if n_meta else n_idx}:** {n_label} (`{n_id}`)")



def _handle_user_director_message(user_text: str, arch_id: str):
    """Procesa el mensaje del usuario con el Director Creativo Semántico y actualiza el plan/proyecto."""
    arch = ARCHETYPES_CATALOG.get(arch_id, list(ARCHETYPES_CATALOG.values())[0])
    
    # 1. Agregar mensaje del usuario al historial
    messages = st.session_state.get("director_messages", [])
    messages.append({"role": "user", "content": user_text})
    
    # 2. Obtener respuesta del Director Semántico
    with st.spinner("El Director Creativo está investigando y estructurando la historia con Cadena de Pensamiento..."):
        res = semantic_director.chat_with_director(messages, user_text)
    
    # 3. Guardar respuesta y sugerencias
    assistant_content = res.get("response_text") or res.get("reply") or "El Director Creativo ha procesado tu historia."
    messages.append({"role": "assistant", "content": assistant_content})
    st.session_state["director_messages"] = messages
    st.session_state["director_suggestions"] = res.get("suggestions", [])
    
    spec = res.get("spec", {})
    st.session_state["director_spec"] = spec
    
    # 4. Generar título contextual y mantener el mismo ID de proyecto en la sesión
    subject = spec.get("subject") or user_text
    st.session_state["current_project_title"] = subject
    
    project_id = st.session_state.get("current_project_id")
    if not project_id:
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
    
    # 6. Integrar tomas profundas generadas por el Director si existen
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
