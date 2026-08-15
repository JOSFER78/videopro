import streamlit as st

def render_step_4_typography(params):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 18px; border-radius: 12px; margin-bottom: 20px;">
        <div style="font-size: 16px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
            <span>✍️ PASO 4:</span> Rótulos Vox, Resaltado Flúor & Subtítulos Dinámicos
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            Configura el estilo tipográfico periodístico estilo Vox, títulos inferiores (Lower-Thirds) y sincronización Karaoke.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("##### 📺 Estilo de Subtítulos Dinámicos ASS")
        sub_styles = [
            "Estilo Vox / Johnny Harris (Amarillo 1-2 palabras dinámicas)",
            "Estilo TikTok Pop (Verde Neón con Rebote)",
            "Estilo Onirópolis Steampunk (Ámbar Gótico)",
            "Estilo Clásico Blanco con Sombra Negra",
            "🚫 Sin Subtítulos (Vídeo limpio)"
        ]
        cur_style = st.selectbox("Plantilla de Subtítulos:", sub_styles, key="w_step4_sub_style")
        params.subtitle_style = cur_style

        st.markdown("##### 🔤 Tipografía y Posición")
        font_options = ["Montserrat ExtraBold", "Inter Black", "Bebas Neue", "Cinzel Decorative"]
        st.selectbox("Fuente Tipográfica:", font_options, key="w_step4_font")
        st.slider("Margen Inferior (Offset Vertical):", 20, 120, 45, key="w_step4_margin")

    with col2:
        st.markdown("##### 📰 Rótulos Periodísticos & Tarjetas Vox")
        st.checkbox("✨ Rótulos Lower-Thirds Animados (Nombres y Cargos)", value=True, key="w_step4_lt")
        st.checkbox("✨ Efecto Rotulador Flúor en Palabras Clave", value=True, key="w_step4_fluor")
        st.checkbox("✨ Recortes de Prensa / Documentos Históricos Animados", value=True, key="w_step4_press")
        st.checkbox("🚫 Descartar bloques de texto de más de 4 palabras por pantalla", value=True, key="w_step4_disc_long")
