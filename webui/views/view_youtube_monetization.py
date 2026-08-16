"""
webui/views/view_youtube_monetization.py — Hub de Monetización, Exploración en Vivo y Gestor de Canales (CERO MOCKS)
"""

import streamlit as st
import json
import os
import subprocess
from app.core.youtube_niche_explorer import render_live_niche_explorer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHANNELS_DIR = os.path.join(BASE_DIR, "docs", "02_canales_youtube", "mis_canales")
MANIFESTS_DIR = os.path.join(BASE_DIR, "data", "tritemporal_manifests")
AUDIO_DIR = os.path.join(BASE_DIR, "data", "tritemporal_audio")
GROUNDING_DIR = os.path.join(BASE_DIR, "data", "tritemporal_grounding")


def scan_real_channels():
    """Escanea el directorio físico de canales y cuenta los archivos reales de producción."""
    channels = []
    if not os.path.exists(CHANNELS_DIR):
        return channels

    for entry in sorted(os.listdir(CHANNELS_DIR)):
        c_path = os.path.join(CHANNELS_DIR, entry)
        if os.path.isdir(c_path):
            config_file = os.path.join(c_path, "channel_config.json")
            display_name = entry
            handle = f"@{entry}"
            niche = "Canal en Configuración"
            rpm = "$18.00"
            status = "🔵 PLANIFICADO"
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    c_info = cfg.get("channel", {})
                    display_name = c_info.get("name", entry)
                    handle = c_info.get("handle", handle)
                    niche = c_info.get("niche", niche)
                    rpm = f"${cfg.get('monetization', {}).get('estimated_rpm_tier1', 20.0):.2f}"
                except Exception:
                    pass

            # Conteo de episodios y manifiestos reales en data/
            manifest_count = 0
            if entry == "01_CHRONODRIFT" and os.path.exists(MANIFESTS_DIR):
                manifest_count = len([f for f in os.listdir(MANIFESTS_DIR) if f.endswith(".json")])
            
            # Cálculo de estado empírico
            if manifest_count >= 10:
                status = "🟢 IMPLEMENTADO (PRODUCCIÓN)"
                progress = 100
            elif os.path.exists(config_file):
                status = "🟡 EN DESARROLLO (CONFIG ACTIVA)"
                progress = 40
            else:
                status = "🔵 PLANIFICADO (ESTUDIO INICIAL)"
                progress = 15

            channels.append({
                "id": entry,
                "name": display_name,
                "handle": handle,
                "nicho": niche,
                "rpm": rpm,
                "manifest_count": manifest_count,
                "status": status,
                "progress": progress,
                "path": c_path
            })
    return channels


def render_youtube_monetization_view():
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 20px; font-weight: 800; color: #f8fafc; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                💰 Hub de Monetización YouTube & Explorador en Vivo
                <span style="font-size: 11px; font-weight: 700; background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 2px 8px; border-radius: 12px;">100% REAL & NATIVO</span>
            </h2>
            <p style="font-size: 12px; color: #94a3b8; margin: 0;">
                Ecosistema de canales propios, análisis de demanda en vivo sin API keys y auditoría de producción cinematográfica.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Gestor de Canales (Datos Reales)",
        "🔍 Explorador de Nichos en Vivo (Zero-API)",
        "💸 Calculadora de Ingresos y Mid-Rolls",
        "🛡️ Auditoría de Pipeline en Vivo"
    ])

    # -------------------------------------------------------------
    # TAB 1: GESTOR DE CANALES
    # -------------------------------------------------------------
    with tab1:
        st.markdown("### 🎬 Estado del Ecosistema en Disco")
        real_channels = scan_real_channels()

        for c in real_channels:
            with st.container(border=True):
                col_c1, col_c2, col_c3 = st.columns([5, 3, 2], vertical_alignment="center")
                with col_c1:
                    st.markdown(f"**{c['name']}** (`{c['handle']}`)")
                    st.caption(f"Nicho: {c['nicho']} | Manifiestos en Disco: **{c['manifest_count']} episodios**")
                with col_c2:
                    st.markdown(f"Estado: `{c['status']}`")
                    st.progress(c['progress'] / 100.0)
                with col_c3:
                    st.metric(label="eRPM Estimado Tier 1", value=c['rpm'])

        # Formulario para planificar un nuevo canal físico en disco
        with st.expander("➕ Planificar y Registrar Nuevo Canal Físico"):
            c_slug = st.text_input("Identificador Único (ej. 06_OCEANMORPH):", placeholder="06_NOMBRE_CANAL")
            c_name = st.text_input("Nombre Público del Canal:", placeholder="OceanMorph (@OceanMorphAI)")
            c_nicho = st.selectbox("Nicho Temático:", [
                "Documental Científico & Océanos",
                "Historia & Hemerotecas 4K",
                "Tecnología & IA Futurista",
                "Astrofísica & Cosmología",
                "Música Generativa & Foley 15min"
            ])
            c_rpm = st.number_input("eRPM Estimado Tier 1 ($):", value=22.50, step=0.5)

            if st.button("🚀 Crear Carpeta y Configuración Real", type="primary"):
                if not c_slug:
                    st.error("Debes indicar un identificador de canal.")
                else:
                    new_channel_dir = os.path.join(CHANNELS_DIR, c_slug.strip().upper())
                    os.makedirs(new_channel_dir, exist_ok=True)
                    
                    cfg_payload = {
                        "channel": {
                            "id": c_slug.strip().upper(),
                            "name": c_name if c_name else c_slug,
                            "handle": f"@{c_slug.lower()}",
                            "niche": c_nicho
                        },
                        "monetization": {
                            "estimated_rpm_tier1": float(c_rpm),
                            "midroll_cues_seconds": [240, 480],
                            "audio_standard": "EBU_R128_-14LUFS"
                        },
                        "created_at": "2026-08-16T21:37:00Z"
                    }
                    with open(os.path.join(new_channel_dir, "channel_config.json"), "w", encoding="utf-8") as f:
                        json.dump(cfg_payload, f, indent=2)
                    
                    with open(os.path.join(new_channel_dir, "README.md"), "w", encoding="utf-8") as f:
                        f.write(f"# 🎬 Canal {c_name}\n\nNicho: {c_nicho}\nCreado desde VideoPro Studio.\n")
                        
                    st.success(f"✅ Canal '{c_slug}' creado físicamente en `{new_channel_dir}` con su `channel_config.json`!")
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 2: EXPLORADOR DE NICHOS EN VIVO (ZERO-API ENGINE)
    # -------------------------------------------------------------
    with tab2:
        render_live_niche_explorer()

    # -------------------------------------------------------------
    # TAB 3: CALCULADORA DE INGRESOS Y MID-ROLLS
    # -------------------------------------------------------------
    with tab3:
        st.markdown("### 💸 Proyección de Ingresos por Canal y Optimización de Mid-Rolls")
        
        c_calc1, c_calc2 = st.columns(2)
        with c_calc1:
            vistas_mes = st.slider("Vistas Mensuales Estimadas:", min_value=10000, max_value=2000000, value=250000, step=10000)
            rpm_rate = st.slider("eRPM Promedio ($ por 1.000 vistas):", min_value=5.0, max_value=40.0, value=24.5, step=0.5)
            afiliados_ingreso = st.number_input("Ingresos por Afiliados / Patrocinios ($):", value=450, step=50)
            midrolls_count = st.radio("Estrategia de Mid-Rolls:", ["Sin Mid-Rolls (1x)", "2 Mid-Rolls (Minutos 4:00 y 8:00 en Remotion)"])
        
        with c_calc2:
            multiplicador = 1.38 if "2 Mid-Rolls" in midrolls_count else 1.0
            ingreso_adsense = (vistas_mes / 1000.0) * rpm_rate * multiplicador
            ingreso_total = ingreso_adsense + afiliados_ingreso
            
            st.markdown("#### 📈 Estimación Financiera Mensual:")
            st.metric("Ingresos AdSense Netos", f"${ingreso_adsense:,.2f}", f"+{((multiplicador-1)*100):.0f}% por Mid-Rolls" if multiplicador > 1 else None)
            st.metric("Ingresos Totales (AdSense + Afiliados)", f"${ingreso_total:,.2f}", f"+${ingreso_total * 12:,.2f} / año")
            
            st.info("💡 **Arquitectura Remotion:** Las marcas de corte en los frames exactos `7.200` (4:00 @ 30fps) y `14.400` (8:00 @ 30fps) con audio ducking a `-24 dB` previenen la caída de retención post-anuncio.")

    # -------------------------------------------------------------
    # TAB 4: AUDITORÍA DE PIPELINE EN VIVO
    # -------------------------------------------------------------
    with tab4:
        st.markdown("### 🛡️ Auditoría y Validación de Integridad del Pipeline")
        st.caption("Ejecuta en tiempo real la suite de validación de esquemas JSON, storyboards y audio engineering.")
        
        if st.button("🚀 Ejecutar Validación End-to-End en Vivo", type="primary"):
            with st.spinner("Ejecutando validate_chronodrift_pipeline.py..."):
                val_script = os.path.join(BASE_DIR, "scripts", "validate_chronodrift_pipeline.py")
                try:
                    res = subprocess.run(["python3", val_script], capture_output=True, text=True, timeout=15)
                    if res.returncode == 0:
                        st.success("🏆 Validación Completada: 100% de los Componentes Pasaron con Éxito.")
                        st.code(res.stdout, language="bash")
                    else:
                        st.error(f"Errores encontrados (Código {res.returncode}):")
                        st.code(res.stderr + "\n" + res.stdout, language="bash")
                except Exception as ex:
                    st.error(f"Error al ejecutar validación: {ex}")
