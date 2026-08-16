import os
import streamlit as st

def render_view():
    st.title("Guía Maestra de Producción Cinematográfica")
    st.caption("Manual de ingeniería audiovisual para LTX-2.5 & FLUX 3: Gramática DoP, Consistencia de Actores, Rótulos y Foley.")

    tab_dop, tab_actors, tab_script, tab_gfx, tab_audio, tab_raw = st.tabs([
        "DoP Prompting (7 Capas)",
        "Consistencia & Actores (4 Anclas)",
        "Guion & Escaleta Temporal",
        "Rótulos Vox & Bloomberg",
        "Foley 48kHz & Ducking",
        "Manual Raw (.md)"
    ])

    with tab_dop:
        st.subheader("Gramática DoP de Hollywood y Netflix (4 y 7 Capas)")
        st.caption("Estructura de lenguaje físico y óptico para texturas, óptica anamórfica y cinemática 6-DoF.")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            with st.container(border=True):
                st.markdown("#### Gramática Ágil de 4 Capas (B-Roll / Rápido)")
                st.code("[Capa 1: Sujeto & Micro-acción] + [Capa 2: Entorno & Atmósfera] + [Capa 3: Cámara & Óptica] + [Capa 4: Iluminación & ACEScg]", language="text")
                st.markdown("""
                - **Capa 1:** Identidad, vestimenta texturizada, micro-acting.
                - **Capa 2:** Geometría Z-depth, capas volumétricas.
                - **Capa 3:** ARRI Alexa 65 / Panavision C-Series, f/1.8.
                - **Capa 4:** Contraste 8:1, Mie scattering, Kodak 5219.
                """)
        
        with col_g2:
            with st.container(border=True):
                st.markdown("#### Gramática Maestra de 7 Capas (Master Shots)")
                st.markdown("""
                1. **L-1 Sensor Spec:** ARRI Alexa 65 ALEV III A3X, 2.39:1 anamórfico.
                2. **L-2 Subject Dynamics:** Poros dérmicos, transpiración, microtensión.
                3. **L-3 Spatial Staging:** Foreground / Midground / Background.
                4. **L-4 Optics:** Cooke S7/i 50mm, f/1.8, bokeh elíptico.
                5. **L-5 Atmospheric:** Dispersión volumétrica de Mie (g=0.75).
                6. **L-6 Color Science:** ACEScg AP1 linear, Kodak Vision3 500T 5219.
                7. **L-7 6-DoF 3-Phase:** Inception (0-30%) -> Dynamic Arc (30-75%) -> Settling (75-100%).
                """)

    with tab_actors:
        st.subheader("Motor de Continuidad de Actores y Entornos (4 Anclas)")
        c_a1, c_a2, c_a3, c_a4 = st.columns(4)
        with c_a1:
            with st.container(border=True):
                st.markdown("**Ancla 1: Character Passport**")
                st.caption("Vector facial 512-dim inmutable inyectado mediante PuLID / IP-Adapter.")
        with c_a2:
            with st.container(border=True):
                st.markdown("**Ancla 2: Wardrobe DNA**")
                st.caption("Segmentación semántica de prendas (SAM-2) y textura textil exacta.")
        with c_a3:
            with st.container(border=True):
                st.markdown("**Ancla 3: 3D Hero Rigging**")
                st.caption("Control métrico de profundidad Z y matriz de proyección de cámara.")
        with c_a4:
            with st.container(border=True):
                st.markdown("**Ancla 4: World State**")
                st.caption("Persistencia de fondo 3D y 9 armónicos esféricos para luz continua.")

    with tab_script:
        st.subheader("Guionización y Escaleta Técnica")
        st.markdown("""
        - **Velocidad de Locución:** 2.2 a 2.4 palabras por segundo (135 - 145 PPM).
        - **Fórmula de Frames:** $\\text{Frames} = \\text{Segundos} \\times 24\\text{ fps}$.
        - **J-Cut (-0.5s / 12 frames):** El audio entra antes del corte visual.
        - **L-Cut (+0.5s / 12 frames):** La cola del audio persiste en el siguiente plano.
        """)

    with tab_gfx:
        st.subheader("Rótulos y Gráficos Vox / Bloomberg")
        with st.expander("Ver Componente: Vox Lower Third (React/TSX)", expanded=True):
            st.code('''import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const VoxLowerThird = ({ category = "SPECIAL REPORT", headline = "THE CHOKEPOINT OF 2NM SILICON" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const containerSpring = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });
  const translateX = interpolate(containerSpring, [0, 1], [-60, 0]);

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', padding: '60px 80px' }}>
      <div style={{ transform: "translateX(" + translateX + "px)", display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ backgroundColor: '#00F0FF', color: '#000', fontWeight: 900, padding: '6px 14px', borderRadius: '2px', width: 'fit-content' }}>
          {category}
        </div>
        <div style={{ backgroundColor: 'rgba(10, 12, 16, 0.85)', padding: '16px 24px', fontSize: '28px', color: '#FFF', maxWidth: '850px' }}>
          {headline}
        </div>
      </div>
    </AbsoluteFill>
  );
};''', language="typescript")

    with tab_audio:
        st.subheader("Foley Acústico 48kHz y Sidechain Ducking")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            with st.container(border=True):
                st.markdown("#### Matemáticas de Rejilla BPM a 24 FPS")
                st.markdown("""
                - **120 BPM:** 1 Beat = **12 frames** (0.5s) | 1 Compás (4/4) = **48 frames** (2.0s).
                - **100 BPM:** 1 Beat = **14.4 frames** (0.6s) | 1 Compás (4/4) = **57.6 frames** (2.4s).
                - **90 BPM:** 1 Beat = **16 frames** (0.66s) | 1 Compás (4/4) = **64 frames** (2.66s).
                - **80 BPM:** 1 Beat = **18 frames** (0.75s) | 1 Compás (4/4) = **72 frames** (3.0s).
                """)
        with c_m2:
            with st.container(border=True):
                st.markdown("#### Parámetros del Sidechain Ducking")
                st.markdown("""
                - **Atenuación Música:** **-14.0 dB a -18.0 dB** durante la voz.
                - **Lookahead:** 15 ms.
                - **Attack / Release:** 25 ms / 300 ms.
                - **Master Final:** **-14 LUFS Integrated** / **-1.0 dBFS True Peak**.
                """)

    with tab_raw:
        st.subheader("Documento Markdown Completo")
        docs_content = ""
        possible_doc_paths = [
            "/home/ubuntu/workspace/pro/hermes/10_videopro/docs/GUIA_MAESTRA_PRODUCCION_CINEMATOGRAFICA_SOTA.md",
            "/home/ubuntu/MoneyPrinterTurbo/docs/GUIA_MAESTRA_PRODUCCION_CINEMATOGRAFICA_SOTA.md"
        ]
        for dp in possible_doc_paths:
            if os.path.exists(dp):
                try:
                    with open(dp, "r", encoding="utf-8") as f:
                        docs_content = f.read()
                    break
                except Exception:
                    pass

        if docs_content:
            st.download_button(
                "Descargar Guía Maestra (.md)",
                data=docs_content,
                file_name="GUIA_MAESTRA_PRODUCCION_CINEMATOGRAFICA_SOTA.md",
                mime="text/markdown"
            )
            st.markdown(docs_content)
        else:
            st.info("Documento no encontrado.")
