import streamlit as st
from app.services import llm
from app.config import config

def render_step_1_concept(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>💡 PASO 1:</span> Concepto Creativo, Tono & Guion 5D
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Define la temática y co-crea el guion estructurado con el Director de IA (Gemini 3.7 en Puerto 8742).
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 0.8], gap="medium")

    with col1:
        st.markdown("##### 📝 Tema y Parámetros del Guion")
        video_subject = st.text_input(
            "Tema central del vídeo:",
            value=params.video_subject or "",
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

        if st.button("✨ Redactar Guion 5D con Director IA (Gemini 3.7)", type="primary", use_container_width=True, icon=":material/auto_awesome:"):
            if not video_subject:
                st.warning("Introduce primero un tema central para el vídeo.")
            else:
                with st.spinner("El Director IA está redactando la estructura cinematográfica..."):
                    try:
                        def gen_script_closure(app_cfg):
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
                        st.error(f"Error generando guion: {e}")

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
