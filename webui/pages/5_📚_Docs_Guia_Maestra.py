import streamlit as st
import os

st.set_page_config(
    page_title="Guía Maestra de Producción Cinematográfica SOTA",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos Dark Glassmorphism Premium
st.markdown("""
<style>
    .docs-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }
    .doc-badge {
        display: inline-block;
        background: rgba(0, 242, 254, 0.15);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.4);
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .stat-pill {
        background: rgba(236, 72, 153, 0.15);
        color: #ec4899;
        border: 1px solid rgba(236, 72, 153, 0.3);
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="docs-header">
    <div class="doc-badge">DOCUMENTACIÓN TÉCNICA OFICIAL</div>
    <h1 style="color:#ffffff; margin:0; font-size:32px; font-weight:900;">📚 Guía Maestra de Producción Cinematográfica SOTA</h1>
    <p style="color:#94a3b8; margin:6px 0 0 0; font-size:15px;">
        Manual de ingeniería audiovisual para <b>LTX-2.5 & FLUX 3</b>: Gramática DoP de Hollywood, Matriz de 5 Vistas para Actores, Rótulos Vox/Bloomberg y Foley 48kHz.
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs interactivas
tab_dop, tab_actors, tab_script, tab_gfx, tab_audio, tab_raw = st.tabs([
    "🎥 1. DoP Prompting (7 Capas)",
    "👤 2. Consistencia & Actores (4 Anclas)",
    "📜 3. Guion & Escaleta Temporal",
    "📊 4. Rótulos Vox & Bloomberg",
    "🎧 5. Foley 48kHz & Ducking",
    "📥 6. Manual Raw (.md)"
])

# =============================================================================
# TAB 1: DoP PROMPTING
# =============================================================================
with tab_dop:
    st.markdown("### 🎥 Gramática DoP de Hollywood y Netflix (4 y 7 Capas)")
    st.caption("Estructura de lenguaje físico y óptico para eliminar el 'AI glaze' y forzar texturas, óptica anamórfica y cinemática 6-DoF.")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.container(border=True):
            st.markdown("#### 🧱 Gramática Ágil de 4 Capas (B-Roll / Rápido)")
            st.code("[Capa 1: Sujeto & Micro-acción] + [Capa 2: Entorno & Atmósfera] + [Capa 3: Cámara & Óptica] + [Capa 4: Iluminación & ACEScg]", language="text")
            st.markdown("""
            - **Capa 1:** Identidad, vestimenta texturizada, micro-acting.
            - **Capa 2:** Geometría Z-depth, capas volumétricas.
            - **Capa 3:** ARRI Alexa 65 / Panavision C-Series, f/1.8.
            - **Capa 4:** Contraste 8:1, Mie scattering, Kodak 5219.
            """)
    
    with col_g2:
        with st.container(border=True):
            st.markdown("#### 🏛️ Gramática Maestra de 7 Capas (Master Shots)")
            st.markdown("""
            1. **L-1 Sensor Spec:** ARRI Alexa 65 ALEV III A3X, 2.39:1 anamórfico.
            2. **L-2 Subject Dynamics:** Poros dérmicos, transpiración, microtensión.
            3. **L-3 Spatial Staging:** Foreground / Midground / Background.
            4. **L-4 Optics:** Cooke S7/i 50mm, f/1.8, bokeh elíptico, blue streaks.
            5. **L-5 Atmospheric:** Dispersión volumétrica de Mie (g=0.75), Tyndall rays.
            6. **L-6 Color Science:** ACEScg AP1 linear, Kodak Vision3 500T 5219.
            7. **L-7 6-DoF 3-Phase:** Inception (0-30%) -> Dynamic Arc (30-75%) -> Settling (75-100%).
            """)

    st.divider()
    st.markdown("### 🧪 Generador / Simulador de Prompt DoP")
    
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        sel_cam = st.selectbox("Cámara & Sensor", ["ARRI Alexa 65 Large Format (ALEV III)", "RED V-Raptor XL 8K VV", "Hasselblad X2D 100C Medium Format", "IMAX 70mm Film Camera"])
        sel_lens = st.selectbox("Óptica Anamórfica", ["Panavision C-Series 40mm T1.4 Anamorphic", "Cooke S7/i 50mm Full Frame Plus", "ARRI Master Prime 35mm f/1.3", "Angenieux Optimo 28-76mm Zoom"])
    with c_p2:
        sel_light = st.selectbox("Esquema de Iluminación", ["Tungsten 3200K Key + Cold 5600K Rim (8:1 Contrast)", "Golden Hour Direct + Soft Bounce (4:1 Contrast)", "Cyberpunk Cyan/Amber Dual Volumetric Mie (10:1 Contrast)", "Sterile Cleanroom Overhead Diffuse (1:1 Contrast)"])
        sel_film = st.selectbox("Ciencia de Color / Emulsión", ["ACEScg Linear + Kodak Vision3 500T 5219", "ACEScg Linear + Fujifilm Eterna 500", "ARRI Log-C Film Emulation", "Technicolor 3-Strip Vintage"])
    with c_p3:
        sel_motion = st.selectbox("Vector Cinemático 6-DoF", ["Inception Push (0.8 m/s) -> Dynamic 30° Arc (1.8 m/s) -> Horizon Settling", "Low Tracking Dolly Forward + Fast Foreground Parallax", "Crane Up 1.5m + Smooth Tilt Down 15°", "Static Master Lock-off with High-Speed Subject Action"])
        sel_foley = st.selectbox("Capa de Audio Foley 48kHz", ["[Audio: Low sub-bass drone, mechanical clicks, cleanroom reverb]", "[Audio: High-speed engine rev, asphalt tire friction, whoosh]", "[Audio: Rhythmic keyboard clicks, distant telephone rings, room tone]", "[Audio: Heavy rain on reinforced glass, fabric rustle, holographic hum]"])

    subject_txt = st.text_area("Descripción de Sujeto y Entorno", value="Female aerospace engineer inspecting a glowing quantum turbine inside an orbital hangar. Delicate facial micro-expressions, matte carbon-fiber flight suit with visible ballistic weave.")

    built_prompt = f"Cinematic master shot. {subject_txt} Captured on {sel_cam} with {sel_lens} at f/1.8. Staged with foreground cable conduit, midground hero subject, and deep atmospheric background with Mie volumetric scattering light shafts. Lighting: {sel_light}. Rendered in {sel_film}, deep rich blacks, organic 35mm fine grain, authentic skin texture without artificial AI smoothing.\n\n[Camera Vector 6-DoF] {sel_motion}. Native 180-degree shutter angle, zero digital jitter.\n\n{sel_foley}"
    
    st.markdown("#### 📋 Prompt Generado Listo para Copiar:")
    st.code(built_prompt, language="text")

# =============================================================================
# TAB 2: CONSISTENCIA & ACTORES
# =============================================================================
with tab_actors:
    st.markdown("### 👤 Motor de Continuidad de Actores y Entornos (4 Anclas)")
    st.caption("Cómo capturar las referencias exactas y calibrar el motor para evitar mutaciones faciales o cambios de ropa.")

    st.markdown("""
    <div style="background:rgba(15, 23, 42, 0.8); border:1px solid rgba(0, 242, 254, 0.2); border-radius:8px; padding:16px 20px; margin-bottom:16px;">
        <h4 style="color:#00f2fe; margin:0 0 8px 0;">📐 Matriz Radial de 5 Vistas a 60° Obligatoria</h4>
        <p style="color:#cbd5e1; font-size:14px; margin:0;">
            Un solo fotograma frontal es insuficiente. Debes generar o aportar una matriz de <b>5 vistas horizontales equidistantes</b>:
            <br><code>[-120° Tres Cuartos Posterior]</code> <code>[-60° Perfil 3/4]</code> <code>[0° Frontal Canónica]</code> <code>[+60° Perfil 3/4]</code> <code>[+120° Tres Cuartos Posterior]</code>
            <br>+ <b>1 Macro Primer Plano (Textura epidérmica/iris)</b> + <b>1 Plano Entero (Proporción esquelética 1:7.5)</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_a1, c_a2, c_a3, c_a4 = st.columns(4)
    with c_a1:
        with st.container(border=True):
            st.markdown("**🛡️ Ancla 1: Character Passport**")
            st.markdown("<span class='stat-pill'>ArcFace CosSim ≥ 0.880</span>", unsafe_allow_html=True)
            st.caption("Vector facial 512-dim inmutable inyectado mediante PuLID / IP-Adapter en capas desacopladas.")
    with c_a2:
        with st.container(border=True):
            st.markdown("**👗 Ancla 2: Wardrobe DNA**")
            st.markdown("<span class='stat-pill'>CIEDE2000 ΔE < 2.50</span>", unsafe_allow_html=True)
            st.caption("Segmentación semántica de prendas (SAM-2) y matrices de Gram para textura textil exacta.")
    with c_a3:
        with st.container(border=True):
            st.markdown("**🦴 Ancla 3: 3D Hero Rigging**")
            st.markdown("<span class='stat-pill'>DWPose 133 Keypoints</span>", unsafe_allow_html=True)
            st.caption("Control métrico de profundidad Z y matriz de proyección de cámara P = K[R|t].")
    with c_a4:
        with st.container(border=True):
            st.markdown("**🌍 Ancla 4: World State**")
            st.markdown("<span class='stat-pill'>LightGlue > 120 Inliers</span>", unsafe_allow_html=True)
            st.caption("Persistencia de fondo 3D y 9 armónicos esféricos (L2) para luz ambiental continua.")

# =============================================================================
# TAB 3: GUION & ESCALETA
# =============================================================================
with tab_script:
    st.markdown("### 📜 Guionización y Escaleta Técnica (Step Outline)")
    st.caption("Sincronización milimétrica entre palabras por segundo (WPS), timecode de vídeo y cortes visuales.")

    st.markdown("""
    #### ⏱️ Reglas de Oro de Cadencia:
    - **Velocidad de Locución:** **2.2 a 2.4 palabras por segundo** (135 - 145 PPM).
    - **Fórmula de Frames:** $\\text{Frames} = \\text{Segundos} \\times 24\\text{ fps}$.
    - **J-Cut (-0.5s / 12 frames):** El audio del plano siguiente entra antes de que la imagen corte.
    - **L-Cut (+0.5s / 12 frames):** La cola del audio del plano anterior persiste en el nuevo plano.
    """)

    st.table([
        {"Shot": "SH_01 (0-5s)", "Frames": "120f", "Plano": "Wide Establishing", "Palabras": "14 palabras (~4.8s)", "Gráfico": "Vox Lower Third", "Foley": "Sub-bass boom + Room Tone"},
        {"Shot": "SH_02 (5-10s)", "Frames": "120f", "Plano": "Macro Close-up", "Palabras": "12 palabras (~4.5s)", "Gráfico": "Bloomberg Stat Card", "Foley": "Pinza robótica + Servo"},
        {"Shot": "SH_03 (10-16s)", "Frames": "144f", "Plano": "Medium Arc Shot", "Palabras": "14 palabras (~5.2s)", "Gráfico": "Bloomberg Ticker Ticker", "Foley": "Teclado mecánico + Pitido"},
        {"Shot": "SH_04 (16-22s)", "Frames": "144f", "Plano": "Dutch Tracking", "Palabras": "13 palabras (~5.0s)", "Gráfico": "Vox Highlight Callout", "Foley": "Hiss nitrógeno + Soldadura"},
        {"Shot": "SH_05 (22-30s)", "Frames": "192f", "Plano": "Horizon Pull-Back", "Palabras": "11 palabras (~4.6s + Outro)", "Gráfico": "Master Outro Card", "Foley": "Crescendo orquestal + Riser"}
    ])

# =============================================================================
# TAB 4: RÓTULOS & REMOTION
# =============================================================================
with tab_gfx:
    st.markdown("### 📊 Rótulos, Títulos y Gráficos Vox / Bloomberg (Remotion React/TSX)")
    st.caption("Componentes profesionales con física spring(), interpolación de opacidad y estética Dark Glassmorphism.")

    with st.expander("📦 Ver Componente: Vox Lower Third (React/TSX)", expanded=True):
        st.code('''// VoxLowerThird.tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

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
        <div style={{ backgroundColor: 'rgba(10, 12, 16, 0.85)', backdropFilter: 'blur(16px)', borderLeft: '4px solid #FFE600', padding: '16px 24px', fontSize: '28px', color: '#FFF', maxWidth: '850px' }}>
          {headline}
        </div>
      </div>
    </AbsoluteFill>
  );
};''', language="typescript")

# =============================================================================
# TAB 5: AUDIO & FOLEY
# =============================================================================
with tab_audio:
    st.markdown("### 🎧 Foley Acústico 48kHz, Sincronía BPM y Sidechain Ducking")
    st.caption("Pipeline de audio diegético y mezcla automática para mantener inteligibilidad vocal absoluta.")

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        with st.container(border=True):
            st.markdown("#### 🎵 Matemáticas de Rejilla BPM a 24 FPS")
            st.markdown("""
            - **120 BPM:** 1 Beat = **12 frames** (0.5s) | 1 Compás (4/4) = **48 frames** (2.0s).
            - **100 BPM:** 1 Beat = **14.4 frames** (0.6s) | 1 Compás (4/4) = **57.6 frames** (2.4s).
            - **90 BPM:** 1 Beat = **16 frames** (0.66s) | 1 Compás (4/4) = **64 frames** (2.66s).
            - **80 BPM:** 1 Beat = **18 frames** (0.75s) | 1 Compás (4/4) = **72 frames** (3.0s).
            """)
    with c_m2:
        with st.container(border=True):
            st.markdown("#### 🎚️ Parámetros del Sidechain Ducking")
            st.markdown("""
            - **Atenuación Música:** **-14.0 dB a -18.0 dB** durante la voz.
            - **Lookahead:** 15 ms (atenúa antes de la primera consonante).
            - **Attack / Release:** 25 ms / 300 ms.
            - **Master Final:** **-14 LUFS Integrated** / **-1.0 dBFS True Peak**.
            """)

# =============================================================================
# TAB 6: RAW MARKDOWN
# =============================================================================
with tab_raw:
    st.markdown("### 📥 Documento Markdown Completo")
    st.caption("Puedes leer o descargar el documento completo para tu base de conocimientos.")
    
    docs_content = ""
    docs_path = "/home/ubuntu/MoneyPrinterTurbo/docs/GUIA_MAESTRA_PRODUCCION_CINEMATOGRAFICA_SOTA.md"
    if os.path.exists(docs_path):
        with open(docs_path, "r", encoding="utf-8") as f:
            docs_content = f.read()

    st.download_button(
        "📥 Descargar GUIA_MAESTRA_PRODUCCION_CINEMATOGRAFICA_SOTA.md",
        data=docs_content,
        file_name="GUIA_MAESTRA_PRODUCCION_CINEMATOGRAFICA_SOTA.md",
        mime="text/markdown"
    )
    
    st.markdown(docs_content)
