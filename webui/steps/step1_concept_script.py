import os
import time
from datetime import datetime
import streamlit as st
from app.services import llm
from app.config import config
from app.core.providers import registry, health_checker


def render_step_1_concept(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>💡 PASO 1:</span> Identidad del Proyecto, Concepto & Guion 5D
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Inicia nombrando tu proyecto (organizado automáticamente por Año/Mes/Día), define la temática y co-crea el guion estructurado con el Director IA.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 1. IDENTIDAD Y CREACIÓN DEL PROYECTO (AÑO / MES / DÍA / NOMBRE)
    # ---------------------------------------------------------
    now = datetime.now()
    yyyy = now.strftime("%Y")
    mm = now.strftime("%m")
    dd = now.strftime("%d")

    current_proj_name = getattr(params, "project_name", "") or getattr(params, "video_subject", "") or "Nuevo Vídeo Documental"
    
    col_p1, col_p2 = st.columns([1.2, 0.8], gap="medium")
    with col_p1:
        st.markdown("##### 📁 Identidad del Proyecto")
        proj_name_input = st.text_input(
            "Nombre / Título del Proyecto:",
            value=current_proj_name,
            placeholder="Ej: Documental Agujeros Negros 4K",
            key="w_step1_proj_name",
            help="Define la carpeta del proyecto en storage/tasks/YYYY/MM/DD/YYYY-MM-DD_nombre/"
        )
        if proj_name_input != getattr(params, "project_name", ""):
            params.project_name = proj_name_input
            if not getattr(params, "video_subject", ""):
                params.video_subject = proj_name_input

    with col_p2:
        slug = "".join(c if c.isalnum() else "_" for c in proj_name_input.strip().lower())[:25].strip("_") or "proyecto"
        folder_preview = f"storage/tasks/{yyyy}/{mm}/{dd}/{yyyy}-{mm}-{dd}_{slug}/"
        st.markdown(f"""
        <div style='background:rgba(15,23,42,0.8); border:1px solid #1e293b; border-radius:8px; padding:10px 14px; margin-top:18px;'>
            <div style='font-size:11px; color:#94a3b8; font-weight:600;'>Jerarquía de Almacenamiento</div>
            <div style='font-size:11.5px; font-family:monospace; color:#38bdf8; word-break:break-all; margin-top:2px;'>
                📂 {folder_preview}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 14px 0; border-color: #1e293b;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 2. DIRECTOR IA Y PARÁMETROS NARRATIVOS
    # ---------------------------------------------------------
    col1, col2 = st.columns([1.2, 0.8], gap="medium")

    # Consultar estado en vivo y LLMs habilitados en la Matriz
    matrix = health_checker.get_all_providers_matrix()

    llm_candidates = {
        "antigravity": f"🍌 Antigravity Bridge (Gemini 3.7 — Local 8742) [{matrix.get('openai', {}).get('badge', '🟢 Local')}]",
        "gemini": f"Google Gemini (AI Studio Cloud) [{matrix.get('gemini', {}).get('badge', '⚪ Sin configurar')}]",
        "groq": f"Groq Cloud (Llama 3.3 70B Fast) [{matrix.get('groq', {}).get('badge', '⚪ Sin configurar')}]",
        "cloudflare_ai": f"Cloudflare Workers AI (Serverless Edge) [{matrix.get('cloudflare_ai', {}).get('badge', '⚪ Sin configurar')}]",
        "openai": f"OpenAI Oficial Cloud (GPT-4o) [{matrix.get('openai', {}).get('badge', '⚪ Sin configurar')}]",
        "anthropic": f"Anthropic Claude (3.5 Sonnet) [{matrix.get('anthropic', {}).get('badge', '⚪ Sin configurar')}]",
        "deepseek": f"DeepSeek Oficial (R1/V3) [{matrix.get('deepseek', {}).get('badge', '⚪ Sin configurar')}]"
    }

    # Filtrar estrictamente por los habilitados en la Matriz
    enabled_llms = {}
    for llm_id, label in llm_candidates.items():
        if registry.is_provider_enabled(llm_id):
            enabled_llms[llm_id] = label

    if not enabled_llms:
        enabled_llms["antigravity"] = "🍌 Antigravity Bridge (Gemini 3.7 / Puerto 8742)"

    with col1:
        st.markdown("##### 🧠 Director de Guion & Modelo de Lenguaje")
        cur_llm_keys = list(enabled_llms.keys())
        prev_llm = st.session_state.get("selected_llm_director", cur_llm_keys[0])
        prev_idx = cur_llm_keys.index(prev_llm) if prev_llm in cur_llm_keys else 0

        selected_llm = st.selectbox(
            "Seleccionar Director IA:",
            options=cur_llm_keys,
            index=prev_idx,
            format_func=lambda x: enabled_llms[x],
            key="w_step1_llm_director"
        )
        st.session_state["selected_llm_director"] = selected_llm

        st.markdown("##### 📝 Tema y Parámetros del Guion")
        video_subject = st.text_input(
            "Tema central del vídeo:",
            value=params.video_subject or proj_name_input,
            placeholder="Ej: El misterio de los agujeros negros y la dilatación temporal",
            key="w_step1_subject"
        )
        if video_subject != params.video_subject:
            params.video_subject = video_subject

        c_tone, c_lang = st.columns(2)
        with c_tone:
            tone_options = [
                "Documental Periodístico (Estilo Vox / Johnny Harris)",
                "Cinemático Épico (Hollywood)",
                "Meme / Humor Viral (TikTok)",
                "Divulgación Científica & Datos"
            ]
            narrative_tone = st.selectbox("Tono Narrativo:", tone_options, key="w_step1_tone")
        with c_lang:
            lang_options = ["Español (España/Latam)", "English (US/UK)", "Português", "Français"]
            video_lang = st.selectbox("Idioma de la Locución:", lang_options, key="w_step1_lang")

        st.markdown("##### ✍️ Guion Completo")
        current_script = st.session_state.get("video_script", params.video_script or "")
        script_input = st.text_area(
            "Texto del Guion (o redacta libremente con el botón inferior):",
            value=current_script,
            height=180,
            key="w_step1_script_text"
        )
        if script_input != params.video_script:
            params.video_script = script_input
            st.session_state["video_script"] = script_input

        btn_label = f"✨ Redactar Guion 5D con {selected_llm.capitalize()}"
        if selected_llm == "antigravity":
            btn_label = "✨ Redactar Guion 5D con Antigravity Bridge (Gemini 3.7)"

        if st.button(btn_label, type="primary", use_container_width=True, icon=":material/auto_awesome:"):
            if not video_subject:
                st.warning("Introduce primero un tema central para el vídeo.")
            else:
                with st.spinner(f"El Director IA ({selected_llm}) está redactando la estructura cinematográfica..."):
                    try:
                        def gen_script_closure(app_cfg):
                            if selected_llm == "antigravity":
                                app_cfg["llm_provider"] = "openai"
                                app_cfg["openai_base_url"] = "http://127.0.0.1:8742/v1"
                                app_cfg["openai_model_name"] = "gemini-3.7-flash-high"
                                app_cfg["openai_api_key"] = "local-antigravity-cli"
                            elif selected_llm == "gemini":
                                app_cfg["llm_provider"] = "gemini"
                            elif selected_llm == "groq":
                                app_cfg["llm_provider"] = "groq"
                            elif selected_llm == "deepseek":
                                app_cfg["llm_provider"] = "deepseek"
                            elif selected_llm == "anthropic":
                                app_cfg["llm_provider"] = "anthropic"

                            return llm.generate_script(
                                video_subject=video_subject,
                                language="es" if "Español" in video_lang else "en",
                                paragraph_number=3,
                                video_script_prompt=f"Tono: {narrative_tone}. Estructura con ritmo dinámico de 2.3 palabras por segundo.",
                                custom_system_prompt="",
                                app_config=app_cfg
                            )
                        res = config.execute_with_runtime_config_snapshot(gen_script_closure)
                        if res:
                            st.session_state["video_script"] = res
                            params.video_script = res
                            st.toast("¡Guion 5D generado correctamente!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generando guion con {selected_llm}: {e}")

    with col2:
        st.markdown("##### 🎬 Escaleta de Escenas Desglosadas")
        if params.video_script:
            paragraphs = [p.strip() for p in params.video_script.split("\n") if p.strip()]
            st.caption(f"Total de tomas estimadas: **{len(paragraphs)} planos**")
            for idx, p in enumerate(paragraphs, 1):
                with st.expander(f"Plano {idx:02d} ({len(p.split())} palabras)", expanded=(idx==1)):
                    st.write(p)
                    st.caption("Cadencia estimada: ~" + str(round(len(p.split()) / 2.3, 1)) + "s")
        else:
            st.info("Escribe o genera un guion a la izquierda para visualizar el desglose de escenas.")
