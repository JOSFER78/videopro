"""
Módulo de Navegación Superior Unificada y Sistema de Estilos Compactos — VideoPro
Estilo 100% sobrio, limpio, compacto (Single-Screen) y sin emoticonos.
Enrutador de vistas SPA (Single-Page Application).
"""

import streamlit as st

NAV_VIEWS = [
    ("main", "Generador Principal"),
    ("settings_projects", "Proyectos y Ajustes"),
    ("ltx_flux", "Estudio LTX & FLUX"),
    ("audio_studio", "Audio & Música"),
    ("cinema_vault", "Galería & Cine"),
    ("docs", "Guía Técnica")
]


def render_top_navigation():
    """
    Renderiza la barra de navegación superior compacta y los estilos globales de densidad óptima.
    """
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "main"

    active = st.session_state["active_view"]

    # Inyección de estilos globales para diseño compacto (todo visible en una pantalla)
    st.markdown("""
    <style>
    /* Ocultar barra lateral y elementos innecesarios */
    section[data-testid="stSidebar"], .stAppDeployButton, [data-testid="stSidebarCollapsedControl"] {
    }
    
    /* Contenedor principal ultra compacto */
    .block-container {
    }

    /* Reducir espaciado vertical entre bloques */
    [data-testid="stVerticalBlock"] {
    }

    /* Títulos compactos y sobrios */
    h1 {
    }
    h2 {
    }
    h3, h4 {
    }
    .stCaption, [data-testid="stCaptionContainer"] {
    }

    /* Pestañas compactas */
    button[data-baseweb="tab"] {
    }

    /* Botones compactos y elegantes */
    .stButton > button {
    }

    /* Inputs, Selectboxes y Textareas compactos */
    div[data-baseweb="input"] input, div[data-baseweb="select"] {
    }
    label[data-testid="stWidgetLabel"] p {
    }
    .stTextArea textarea {
    }

    /* Contenedores con bordes limpios y sin padding excesivo */
    div[data-testid="stVerticalBlockBorderWrapper"] {
    }

    /* Métricas compactas */
    div[data-testid="stMetric"] {
    }
    div[data-testid="stMetricValue"] {
    }
    div[data-testid="stMetricLabel"] {
    }

    /* Separadores sutiles */
    hr {
    }
    </style>
    """, unsafe_allow_html=True)

    # Barra horizontal de navegación usando columnas compactas
    cols = st.columns(len(NAV_VIEWS))
    for i, (view_key, view_label) in enumerate(NAV_VIEWS):
        is_active = (active == view_key)
        btn_type = "primary" if is_active else "secondary"
        with cols[i]:
            if st.button(view_label, key=f"nav_btn_{view_key}", type=btn_type, use_container_width=True):
                if st.session_state["active_view"] != view_key:
                    st.session_state["active_view"] = view_key
                    st.rerun()

    # Si estamos en una vista secundaria, botón de retorno sutil
    if active != "main":
        col_b, col_empty = st.columns([2.2, 7.8], vertical_alignment="center")
        with col_b:
            if st.button("← Volver al Generador Principal", key="btn_global_return_home", type="secondary", use_container_width=True):
                st.session_state["active_view"] = "main"
                st.rerun()
        st.markdown("<hr style='margin: 0.2rem 0 0.5rem 0;'>", unsafe_allow_html=True)
