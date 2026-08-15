import streamlit as st
from app.services.storage.factory import StorageFactory

def render_step_5_master_render(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>🚀 PASO 5:</span> Ensamblado Master FFmpeg, QC EBU R128 & Visor
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Renderiza la composición final acelerada por hardware, normalizada a -14 LUFS y con subida opcional a Cloudflare R2.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9], gap="medium")

    with col1:
        st.markdown("##### 🎛️ Parámetros de Renderizado")
        st.write(f"• **Tema:** {params.video_subject or '_Sin tema definido_'}")
        st.write(f"• **Motor Visual:** {getattr(params, 'video_source', 'FLUX 3')}")
        st.write(f"• **Formato:** {getattr(params, 'video_aspect', '9:16')}")
        st.write(f"• **Voz:** {getattr(params, 'voice_name', 'Kokoro HD Dora')}")
        st.write(f"• **Almacenamiento:** Cloudflare R2 (Zero Egress) + Local Cache")

        st.markdown("---")
        if st.button("🎬 GENERAR VÍDEO FINAL MASTER", type="primary", use_container_width=True, icon=":material/play_circle:"):
            if not params.video_script:
                st.warning("⚠️ No hay guion definido. Vuelve al Paso 1 para redactar o generar el guion.")
            else:
                st.session_state["generation_in_progress"] = True
                st.toast("🚀 Iniciando pipeline de renderizado en segundo plano...")

    with col2:
        st.markdown("##### 📺 Reproductor & Estado de Render")
        if st.session_state.get("generation_in_progress", False):
            st.progress(65, text="Ensamblando pistas con FFmpeg y aplicando Ducking...")
            st.info("Renderizando plano 02 de 03 a 1080p 24fps...")
        else:
            st.info("Pulsa 'GENERAR VÍDEO FINAL MASTER' para iniciar la composición.")
