"""
webui/components/copilot_drawer.py
================================================================================
ASISTENTE DE IA CONVERSACIONAL INTERACTIVO & MULTIMODAL (HERMES COPILOT)
================================================================================
Permite interactuar fluidamente mediante chat en vivo o mensajes de voz grabados
con transcripción instantánea (Whisper) y respuestas dinámicas generadas por LLM.
"""

import streamlit as st
from typing import Dict, Any, Optional
from app.core.copilot.copilot_engine import CopilotEngine
from app.core.copilot.state_observer import StateObserver
from app.core.copilot.voice_transcriber import VoiceTranscriber


def render_copilot_drawer(
    view_name: str = "youtube_monetization",
    active_tab_name: Optional[str] = None,
    channel_id: Optional[str] = None
):
    """Renderiza el coasistente conversacional interactivo (texto + voz)."""

    # Inicializar historial conversacional
    if "copilot_chat_messages" not in st.session_state:
        st.session_state["copilot_chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "¡Hola! Soy **Hermes Copilot**, tu coasistente interactivo en VideoPro Studio. "
                    "Puedo guiarte paso a paso en la creación de tus canales, optimización de monetización, "
                    "configuración de audios o resolución de dudas. Puedes **escribirme en el chat** o **grabarme un mensaje de voz**."
                )
            }
        ]

    if "copilot_chat_expanded" not in st.session_state:
        st.session_state["copilot_chat_expanded"] = True

    screen_summary = StateObserver.get_screen_summary(view_name, active_tab_name, channel_id)

    # Estilos CSS
    st.markdown("""
        <style>
        .copilot-chat-container {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.88) 100%);
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(16px);
        }
        .copilot-status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 14px;
        }
        .copilot-badge-live {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10b981;
            color: #10b981;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }
        .copilot-badge-pulse {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #10b981;
        }
        .chat-scroll-area {
            max-height: 420px;
            overflow-y: auto;
            padding-right: 8px;
            margin-bottom: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f"""
            <div class="copilot-chat-container">
                <div class="copilot-status-bar">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="copilot-badge-live">
                            <span class="copilot-badge-pulse"></span>
                            HERMES COPILOT CONVERSACIONAL
                        </span>
                        <span style="font-size: 12.5px; color: #94a3b8;">
                            Contexto activo: <strong style="color: #e2e8f0;">{screen_summary['title']}</strong>
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("💬 Conversar con el Asistente de IA (Chat & Notas de Voz)", expanded=st.session_state["copilot_chat_expanded"]):
            # Barra de herramientas superior del chat
            t_col1, t_col2 = st.columns([8, 2])
            with t_col2:
                if st.button("🗑️ Limpiar Chat", use_container_width=True):
                    st.session_state["copilot_chat_messages"] = [
                        {
                            "role": "assistant",
                            "content": "¡Chat reiniciado! ¿En qué puedo ayudarte ahora?"
                        }
                    ]
                    st.rerun()

            # Renderizar historial de mensajes
            for msg in st.session_state["copilot_chat_messages"]:
                avatar = "🤖" if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

            # Entrada dual: Mensaje de Voz transcrito + Entrada de texto
            st.markdown("---")
            v_col1, v_col2 = st.columns([1, 1])

            user_query = None

            with v_col1:
                st.markdown("🎙️ **Hablar por Voz (Transcripción Instantánea):**")
                audio_val = st.audio_input("Graba tu mensaje de voz aquí:", key="copilot_voice_input")
                if audio_val is not None:
                    # Comprobar si ya se procesó este audio para no repetir en cada rerun
                    audio_bytes = audio_val.read()
                    audio_hash = hash(audio_bytes)
                    if st.session_state.get("last_processed_audio_hash") != audio_hash:
                        st.session_state["last_processed_audio_hash"] = audio_hash
                        with st.spinner("🎙️ Transcribiendo audio con Faster-Whisper..."):
                            transcribed_text = VoiceTranscriber.transcribe_audio_bytes(audio_bytes, language="es")
                        
                        if transcribed_text:
                            st.success(f"🗣️ Mensaje transcrito: *\"{transcribed_text}\"*")
                            user_query = transcribed_text
                        else:
                            st.warning("No se pudo detectar voz clara en el audio grabado. Intenta hablar más cerca del micrófono.")

            with v_col2:
                st.markdown("⌨️ **Escribir por Texto:**")
                text_input_val = st.chat_input("Escribe tu consulta o duda para Hermes Copilot...", key="copilot_text_input")
                if text_input_val:
                    user_query = text_input_val

            # Procesar el mensaje del usuario de forma dinámica si hay entrada
            if user_query:
                # 1. Agregar mensaje del usuario al historial
                st.session_state["copilot_chat_messages"].append({
                    "role": "user",
                    "content": user_query
                })

                # 2. Generar respuesta dinámica con el LLM
                with st.spinner("🤖 Hermes Copilot está pensando y redactando tu respuesta..."):
                    reply = CopilotEngine.generate_chat_reply(
                        messages=st.session_state["copilot_chat_messages"],
                        view_context=screen_summary
                    )

                # 3. Guardar respuesta del asistente
                st.session_state["copilot_chat_messages"].append({
                    "role": "assistant",
                    "content": reply
                })

                st.rerun()
