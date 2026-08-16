"""
webui/components/hierarchical_subnav.py
Componente reutilizable de Breadcrumbs y Stepper Jerárquico para VideoPro Studio
"""

import streamlit as st

SUBPAGES = [
    {"id": "learn", "icon": "🎓", "title": "Aprender & Conceptos"},
    {"id": "diagnose", "icon": "📊", "title": "Diagnosticar Canal"},
    {"id": "configure", "icon": "⚙️", "title": "Configurar & Crear"},
    {"id": "launch", "icon": "🚀", "title": "Lanzar & Publicar"}
]

def render_hierarchical_subnav(module_name="Studio", current_project="01_CHRONODRIFT"):
    """Renderiza el header con Breadcrumbs dinámicos, tabs estilizadas y progreso."""
    
    # Inicializar estado si no existe
    if "current_subpage_index" not in st.session_state:
        st.session_state.current_subpage_index = 0

    current_idx = st.session_state.current_subpage_index
    current_subpage = SUBPAGES[current_idx]

    # Inyección de estilos Glassmorphism
    st.markdown("""
        <style>
            .vp-breadcrumb-container {
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
                color: #94a3b8;
                margin-bottom: 12px;
                padding: 6px 14px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(51, 65, 85, 0.4);
                border-radius: 8px;
            }
            .vp-breadcrumb-active {
                color: #38bdf8;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. BREADCRUMBS
    st.markdown(f"""
        <div class="vp-breadcrumb-container">
            <span>🏠 VideoPro</span>
            <span>›</span>
            <span>📂 {module_name}</span>
            <span>›</span>
            <span style="color: #cbd5e1;">{current_project}</span>
            <span>›</span>
            <span class="vp-breadcrumb-active">{current_subpage['icon']} {current_subpage['title']}</span>
        </div>
    """, unsafe_allow_html=True)

    # 2. PESTAÑAS SECUNDARIAS / STEPPER
    cols = st.columns(len(SUBPAGES))
    for i, sp in enumerate(SUBPAGES):
        with cols[i]:
            is_active = (i == current_idx)
            is_done = (i < current_idx)
            
            label = f"{sp['icon']} {i+1}. {sp['title']}"
            if is_done:
                label = f"✓ {sp['icon']} {sp['title']}"
            
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_step_{sp['id']}", type=btn_type, use_container_width=True):
                st.session_state.current_subpage_index = i
                st.rerun()

    # 3. BARRA DE PROGRESO GLOBAL
    progress_pct = int(((current_idx + 1) / len(SUBPAGES)) * 100)
    st.progress(progress_pct / 100, text=f"Progreso del Flujo: Paso {current_idx + 1} de {len(SUBPAGES)} ({progress_pct}%)")
    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(51,65,85,0.4); margin: 16px 0 20px 0;'>", unsafe_allow_html=True)

    return current_subpage["id"]

def advance_to_subpage(step_id_or_index):
    """Función de utilidad para avanzar secuencialmente."""
    if isinstance(step_id_or_index, int):
        st.session_state.current_subpage_index = max(0, min(step_id_or_index, len(SUBPAGES) - 1))
    elif isinstance(step_id_or_index, str):
        for idx, sp in enumerate(SUBPAGES):
            if sp["id"] == step_id_or_index:
                st.session_state.current_subpage_index = idx
                break
    st.rerun()
