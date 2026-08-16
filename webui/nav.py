"""
Módulo de Navegación Superior Unificada — VideoPro
Estilo 100% sobrio, limpio y sin emoticonos.
Enrutador de vistas SPA (Single-Page Application).
"""

import streamlit as st

NAV_VIEWS = [
    ("main", "Generador Principal"),
    ("ltx_flux", "LTX & FLUX"),
    ("voice", "Voice Studio"),
    ("api_hub", "API Hub"),
    ("cinema", "Cinema Player"),
    ("flow_music", "Flow Music"),
    ("matriz", "Matriz Live"),
    ("settings_projects", "Ajustes y Proyectos"),
    ("boveda", "Bóveda"),
    ("docs", "Guía")
]


def render_top_navigation():
    """
    Renderiza la barra de navegación superior interactiva.
    Permite cambiar de vista instantáneamente sin recargas de página ni menús laterales molestos.
    """
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "main"

    active = st.session_state["active_view"]

    # Inyección de estilos sobrios y neutrales para la navegación
    st.markdown("""
    <style>
    /* Ocultar barra lateral automática de Streamlit para mantener interfaz limpia */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    .stAppDeployButton, [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    
    /* Contenedor de barra superior */
    div.nav-bar-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 12px;
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Barra horizontal de navegación usando columnas
    cols = st.columns(len(NAV_VIEWS))
    for i, (view_key, view_label) in enumerate(NAV_VIEWS):
        is_active = (active == view_key)
        btn_type = "primary" if is_active else "secondary"
        with cols[i]:
            if st.button(view_label, key=f"nav_btn_{view_key}", type=btn_type, use_container_width=True):
                if st.session_state["active_view"] != view_key:
                    st.session_state["active_view"] = view_key
                    st.rerun()

    # Si estamos en una vista secundaria, mostrar botón de retorno inmediato
    if active != "main":
        st.markdown("<div style='margin-top: 4px; margin-bottom: 8px;'></div>", unsafe_allow_html=True)
        col_back, col_space = st.columns([2.5, 7.5], vertical_alignment="center")
        with col_back:
            if st.button("← Volver al Generador Principal", key="btn_global_return_home", type="secondary", use_container_width=True):
                st.session_state["active_view"] = "main"
                st.rerun()
        st.markdown("---")
