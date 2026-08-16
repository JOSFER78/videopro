"""
webui/views/view_youtube_monetization.py
================================================================================
CENTRO DE MANDO, APRENDIZAJE Y GESTIÓN DE CANALES (HERMES YOUTUBE ENGINE)
================================================================================
Vista integral para VideoPro Studio / Hermes Agent.
- Tab 1: 🎓 Academia YouTube & Calculadora de Monetización
- Tab 2: 🎬 Gestión Integral de Canales (01_CHRONODRIFT a 05_ASTRODRIFT + Nuevos)
- Tab 3: 🔍 Explorador de Nichos en Vivo (Zero-API Blue Ocean Engine)
- Tab 4: 🎯 Generador SEO en 6 Bloques & Checklist de Lanzamiento
- Tab 5: 📱 Pipeline Multiplataforma & Orquestación Hermes
- Tab 6: 📊 Dashboards Interactivos e Inteligencia Visual
- Tab 7: 🛡️ Suite de Auditoría de Pipeline & Control Anti-Slop
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import math
import os
import subprocess
from pathlib import Path
from datetime import datetime

from app.core.youtube_channel_manager import YouTubeChannelManager
from app.core.youtube_niche_explorer import render_live_niche_explorer

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHANNELS_DIR = BASE_DIR / "docs" / "02_canales_youtube" / "mis_canales"


def inject_custom_styles():
    st.markdown("""
        <style>
        .yt-card {
            background: rgba(17, 24, 39, 0.75);
            border: 1px solid rgba(55, 65, 81, 0.6);
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 14px;
            backdrop-filter: blur(12px);
        }
        .yt-badge {
            font-size: 11px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        .badge-green {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }
        .badge-cyan {
            background: rgba(0, 240, 255, 0.12);
            color: #00f0ff;
            border: 1px solid rgba(0, 240, 255, 0.3);
        }
        .badge-amber {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }
        .badge-purple {
            background: rgba(139, 92, 246, 0.15);
            color: #8b5cf6;
            border: 1px solid rgba(139, 92, 246, 0.35);
        }
        .metric-title {
            font-size: 11px;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 20px;
            font-weight: 800;
            color: #f8fafc;
            font-family: 'JetBrains Mono', monospace, sans-serif;
        }
        .highlight-box {
            background: rgba(15, 23, 42, 0.85);
            border-left: 4px solid #00f0ff;
            padding: 12px 16px;
            border-radius: 4px 8px 8px 4px;
            margin: 10px 0;
            font-size: 13px;
            color: #cbd5e1;
        }
        .ep-card {
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_youtube_monetization_view():
    inject_custom_styles()

    # Inicializar estado en sesión
    if "checklist_yt" not in st.session_state:
        st.session_state["checklist_yt"] = {f"yt_{i}": False for i in range(1, 11)}
    if "checklist_tt" not in st.session_state:
        st.session_state["checklist_tt"] = {f"tt_{i}": False for i in range(1, 9)}
    if "checklist_ig" not in st.session_state:
        st.session_state["checklist_ig"] = {f"ig_{i}": False for i in range(1, 9)}

    # Encabezado principal
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 10px;">
                    💰 Centro de Mando, Aprendizaje & Gestión de Canales YouTube
                    <span class="yt-badge badge-green">HERMES ENGINE v3.0</span>
                </h1>
                <p style="font-size: 12.5px; color: #94a3b8; margin: 2px 0 0 0;">
                    Monetización Tier 1 ($18-$35+ RPM), gestión del ciclo de vida de canales 01 a 05, explorador Zero-API y dashboards interactivos.
                </p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="yt-badge badge-cyan">TIER 1 HIGH-RPM</span>
                <span class="yt-badge badge-purple">PRODUCCIÓN 4K UHD</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "🎓 1. Academia & Calculadora",
        "🎬 2. Gestión de Canales",
        "🔍 3. Explorador Zero-API",
        "🎯 4. Generador SEO & Checklist",
        "📱 5. Pipeline Multiplataforma",
        "📊 6. Dashboards Interactivos",
        "🛡️ 7. Auditoría & Anti-Slop"
    ])

    # ==========================================================================
    # TAB 1: ACADEMIA & CALCULADORA
    # ==========================================================================
    with tabs[0]:
        st.markdown("### 🎓 Academia de Monetización y Arbitraje de Alto RPM")
        st.caption("Estrategias matemáticas, blindaje anti-slop y modelos de negocio para desbloquear el YPP y generar ingresos pasivos recurrentes.")

        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            with st.container(border=True):
                st.markdown('<div class="metric-title">Umbral YPP 2026</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">1.000 / 4.000h</div>', unsafe_allow_html=True)
                st.caption("10 vídeos de 10m a 5m de retención = 48k vistas totales para monetizar")
        with col_a2:
            with st.container(border=True):
                st.markdown('<div class="metric-title">Reparto AdSense</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">55% Creador</div>', unsafe_allow_html=True)
                st.caption("45% YouTube para vídeos largos (>8 min con Mid-rolls)")
        with col_a3:
            with st.container(border=True):
                st.markdown('<div class="metric-title">RPM Promedio Tier 1</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-value" style="color: #10b981;">$22.40</div>', unsafe_allow_html=True)
                st.caption("USA, UK, DE, AU pagan hasta 27x más que mercados Tier 3")
        with col_a4:
            with st.container(border=True):
                st.markdown('<div class="metric-title">Retención Clave (AVD)</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-value" style="color: #00f0ff;">> 60%</div>', unsafe_allow_html=True)
                st.caption("Activación del algoritmo de recomendación viral")

        st.markdown("---")

        st.markdown("#### 🌍 Comparativa de Arbitraje Geográfico de Tráfico")
        c_tier1, c_tier2, c_tier3 = st.columns(3)
        with c_tier1:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #10b981; margin-top: 0;">🥇 Tier 1 (USA, UK, DE, AU, CA)</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        <strong>RPM Estimado:</strong> $18.50 – $35.00+ USD<br>
                        <strong>Ingreso por 100k vistas:</strong> $2,250 – $3,500 USD<br>
                        <strong>Ingreso por 1M vistas:</strong> $22,500 – $35,000 USD
                    </p>
                    <p style="font-size: 11.5px; color: #94a3b8;">
                        Anunciantes corporativos de SaaS, finanzas, hardware y viajes premium pujan CPCs de hasta $45.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with c_tier2:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #f59e0b; margin-top: 0;">🥈 Tier 2 (España, Francia, LATAM)</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        <strong>RPM Estimado:</strong> $3.00 – $8.00 USD<br>
                        <strong>Ingreso por 100k vistas:</strong> $350 – $800 USD<br>
                        <strong>Ingreso por 1M vistas:</strong> $3,500 – $8,000 USD
                    </p>
                    <p style="font-size: 11.5px; color: #94a3b8;">
                        Excelente para volumen cultural y comentarios, pero con monetización 4x a 5x menor que Tier 1.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with c_tier3:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #ef4444; margin-top: 0;">🥉 Tier 3 (India, SEA, África)</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        <strong>RPM Estimado:</strong> $0.30 – $1.80 USD<br>
                        <strong>Ingreso por 100k vistas:</strong> $30 – $180 USD<br>
                        <strong>Ingreso por 1M vistas:</strong> $300 – $1,800 USD
                    </p>
                    <p style="font-size: 11.5px; color: #94a3b8;">
                        Alto volumen pero bajo rendimiento publicitario. VideoPro prioriza locución e indexación en inglés neutro.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("#### 🛡️ El Pentágono Editorial Anti-Slop de VideoPro")
        c_slop1, c_slop2 = st.columns(2)
        with c_slop1:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #00f0ff; margin-top: 0;">1. 📜 Guion Semántico con Tesis</h4>
                    <p style="font-size: 12.5px; color: #cbd5e1;">
                        Arco narrativo de 3 actos con premisa dramática real en lugar de lecturas monótonas de enciclopedia.
                    </p>
                    <h4 style="color: #00f0ff; margin-top: 10px;">2. 🎥 Cámaras 6-DoF & Freeze 3D</h4>
                    <p style="font-size: 12.5px; color: #cbd5e1;">
                        Vuelos espaciales cinemáticos con splines de cámara real y efectos de tiempo congelado en 4K UHD.
                    </p>
                    <h4 style="color: #00f0ff; margin-top: 10px;">3. ⚓ Consistencia de 4 Anclas</h4>
                    <p style="font-size: 12.5px; color: #cbd5e1;">
                        Identidad visual fija de escenarios y personajes basada en pasaportes y planos topográficos reales.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        with c_slop2:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #8b5cf6; margin-top: 0;">4. 📊 Telemetría Gráfica Vox / Bloomberg</h4>
                    <p style="font-size: 12.5px; color: #cbd5e1;">
                        Mínimo 3 rótulos dinámicos con datos numéricos y citas científicas en Remotion por episodio.
                    </p>
                    <h4 style="color: #8b5cf6; margin-top: 10px;">5. 🎧 Foley 48kHz con Sidechain Ducking</h4>
                    <p style="font-size: 12.5px; color: #cbd5e1;">
                        Audio masterizado estrictamente a <strong>-14 LUFS</strong> bajo norma EBU R128 con atenuación de música a -18dB bajo la voz.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # CALCULADORA FINANCIERA DINÁMICA
        st.markdown("#### 💸 Calculadora Financiera Interactiva de Rendimiento")
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            vistas_estimadas = st.slider("Vistas Mensuales Globales del Canal:", min_value=10000, max_value=3000000, value=250000, step=10000)
            rpm_seleccionado = st.slider("RPM Promedio Base ($ por 1.000 vistas):", min_value=5.0, max_value=40.0, value=22.5, step=0.5)
            midroll_boost = st.checkbox("Activar 2 Mid-rolls Estratégicos (4:00 y 8:00) [+38% RPM]", value=True)
            afiliados_ingreso = st.number_input("Ingresos por Afiliados y Productos Digitales ($/mes):", value=650, step=50)

        with col_c2:
            multiplier = 1.38 if midroll_boost else 1.0
            effective_rpm = rpm_seleccionado * multiplier
            ingreso_adsense = (vistas_estimadas / 1000.0) * effective_rpm
            ingreso_total_mes = ingreso_adsense + afiliados_ingreso
            ingreso_total_ano = ingreso_total_mes * 12

            with st.container(border=True):
                st.markdown("##### 📈 Proyección Financiera Estimada:")
                st.metric("Ingreso Total Mensual", f"${ingreso_total_mes:,.2f}", f"+${ingreso_total_ano:,.2f} / año")
                col_sub1, col_sub2 = st.columns(2)
                col_sub1.metric("AdSense Neto", f"${ingreso_adsense:,.2f}", f"RPM Real: ${effective_rpm:.2f}")
                col_sub2.metric("Afiliados / Digital", f"${afiliados_ingreso:,.2f}", f"${afiliados_ingreso * 12:,.2f} / año")

                st.info("💡 **Dato Clave:** Con un canal promediando 250k vistas mensuales en Tier 1, los ingresos superan los **$75,000 USD anuales** desatendidos.")

    # ==========================================================================
    # TAB 2: GESTIÓN INTEGRAL DE CANALES
    # ==========================================================================
    with tabs[1]:
        st.markdown("### 🎬 Gestión y Ciclo de Vida del Ecosistema de Canales")
        st.caption("Expedientes de producción, escaletas completas de 10 episodios, especificaciones de branding y registro en disco.")

        channels = YouTubeChannelManager.list_channels()
        channel_names = [f"{c['id']} — {c['nombre']}" for c in channels]
        
        c_sel_col, c_kpi_col = st.columns([4, 6], vertical_alignment="center")
        with c_sel_col:
            selected_idx = st.selectbox("Seleccionar Canal para Inspeccionar:", range(len(channels)), format_func=lambda i: channel_names[i])
        
        selected_channel_summary = channels[selected_idx]
        channel_id = selected_channel_summary["id"]
        detail = YouTubeChannelManager.get_channel_detail(channel_id)

        with c_kpi_col:
            k1, k2, k3 = st.columns(3)
            k1.metric("Estado", detail.get("status", "PLANIFICADO"))
            k2.metric("RPM Tier 1", detail.get("target_rpm_usd", "$18.00 - $25.00"))
            k3.metric("Salud Editorial", f"{detail.get('salud_score', 80)}/100")

        st.markdown("---")

        tab_ch_overview, tab_ch_episodes, tab_ch_branding, tab_ch_docs = st.tabs([
            "📋 Ficha Técnica",
            "🎬 Escaleta de 10 Episodios",
            "🎨 Branding & Miniaturas",
            "📖 Documentación Técnica"
        ])

        with tab_ch_overview:
            st.markdown(f"#### 🏷️ Ficha de Canal: {detail.get('brand_name')} (`{detail.get('handle')}`)")
            st.markdown(f"**Tagline:** *{detail.get('tagline')}*")
            st.markdown(f"**Nicho Temático:** {detail.get('nicho')}")
            st.markdown(f"**Audiencia Objetivo:** {detail.get('target_geo')}")
            
            with st.container(border=True):
                st.markdown("##### 🛠️ Pipeline de Producción Asignado:")
                st.code(detail.get('pipeline', 'FLUX 3 + LTX-2.5 + Remotion + EBU R128 -14 LUFS'), language="text")
                st.markdown("##### 💰 Fuentes de Monetización Activas:")
                for f in detail.get('fuentes_ingreso', []):
                    st.markdown(f"- 💵 **{f}**")

        with tab_ch_episodes:
            episodes = detail.get("episodes", [])
            st.markdown(f"#### 📜 Escaleta de Producción ({len(episodes)} Episodios Estructurados)")
            if episodes:
                for ep in episodes:
                    with st.expander(f"🎬 Episodio {ep['number']:02d}: {ep['title']}", expanded=(ep['number'] == 1)):
                        if ep.get("hook"):
                            st.markdown(f"""
                                <div class="highlight-box">
                                    <strong>⚡ Gancho de Inicio (0–5s):</strong><br>
                                    {ep['hook']}
                                </div>
                            """, unsafe_allow_html=True)
                        
                        if ep.get("acts"):
                            st.markdown("**🏛️ Estructura en 3 Actos:**")
                            for act in ep["acts"]:
                                st.markdown(f"- {act}")
                        
                        if ep.get("seo_titles"):
                            st.markdown("**🎯 Opciones de Títulos SEO (Alto CTR):**")
                            for stitle in ep["seo_titles"]:
                                st.code(stitle, language="text")
                        
                        if not ep.get("hook") and not ep.get("acts") and ep.get("raw_block"):
                            st.markdown(ep["raw_block"][:600] + "...")
            else:
                st.info(f"No se encontró escaleta estructurada para {channel_id}.")

        with tab_ch_branding:
            st.markdown("#### 🎨 Especificaciones de Branding & Plantillas de Miniaturas")
            thumb_cfg = detail.get("thumbnails_config", {})
            if thumb_cfg:
                c_th1, c_th2 = st.columns(2)
                with c_th1:
                    st.markdown("##### 📐 Especificaciones de Lienzo")
                    st.markdown(f"- **Dimensiones:** `{thumb_cfg.get('canvas_specs', {}).get('width', 1920)}x{thumb_cfg.get('canvas_specs', {}).get('height', 1080)}`")
                    st.markdown(f"- **CTR Objetivo:** `{thumb_cfg.get('target_ctr_threshold', '> 14.0%')}`")
                    st.markdown(f"- **Zona Muerta (Esquina Inferior Derecha):** `{thumb_cfg.get('dead_zone_restriction', {}).get('width_px', 340)}x{thumb_cfg.get('dead_zone_restriction', {}).get('height_px', 210)} px` (para contador de tiempo)")
                with c_th2:
                    st.markdown("##### 🧠 Tríada Cognitiva (Regla de 3 Anclas)")
                    triad = thumb_cfg.get("cognitive_triad_rule", {})
                    st.markdown(f"1. **Ancla 1:** {triad.get('element_1_role', 'Sujeto Hipercontrastado')}")
                    st.markdown(f"2. **Ancla 2:** {triad.get('element_2_role', 'Capa HUD 3D Holográfica')}")
                    st.markdown(f"3. **Ancla 3:** {triad.get('element_3_role', 'Microcopy Magnético (<= 3 palabras)')}")

                st.markdown("##### 🎨 Tokens Cromáticos y Contraste WCAG:")
                colors = thumb_cfg.get("color_tokens", {})
                if colors:
                    cols = st.columns(len(colors))
                    for i, (cname, cval) in enumerate(colors.items()):
                        with cols[i]:
                            hex_col = cval.get('hex', '#00e5ff')
                            st.markdown(f"""
                                <div style="background: {hex_col}; height: 28px; border-radius: 6px; border: 1px solid #334155;"></div>
                                <div style="font-size: 11px; font-weight: 700; margin-top: 4px;">{cname}</div>
                                <div style="font-size: 10px; color: #94a3b8;">{hex_col}</div>
                            """, unsafe_allow_html=True)
            else:
                st.info("Configuración de miniaturas estándar aplicada según la Biblia Visual de VideoPro.")

        with tab_ch_docs:
            st.markdown("#### 📖 Documentación Canónica Asociada")
            docs = detail.get("docs_available", [])
            if docs:
                for doc in docs:
                    st.markdown(f"- 📄 **{doc['title']}** (`{doc['filename']}`) — *{doc['size_kb']} KB*")
            else:
                st.caption("No se encontraron archivos markdown auxiliares.")

        st.markdown("---")

        # FORMULARIO DE REGISTRO DE NUEVO CANAL
        with st.expander("➕ Planificar y Registrar Nuevo Canal en Disco"):
            st.caption("Genera la estructura de carpetas, esquemas y escaleta canónica en `docs/02_canales_youtube/mis_canales/`.")
            c_slug_in = st.text_input("Identificador Único (ej. 06_OCEANMORPH):", placeholder="06_OCEANMORPH")
            c_name_in = st.text_input("Nombre Público del Canal:", placeholder="OceanMorph (@OceanMorphAI)")
            c_handle_in = st.text_input("Handle Oficial:", placeholder="@OceanMorphOfficial")
            c_tagline_in = st.text_input("Tagline / Eslogan:", placeholder="Deep Ocean Exploration & Alien Abyssal Worlds 4K")
            c_nicho_in = st.selectbox("Nicho Temático:", [
                "Documental Científico & Océanos Profundos",
                "Historia & Hemerotecas 4K",
                "Tecnología & IA Futurista",
                "Astrofísica & Agujeros Negros",
                "Música Generativa & Foley Inmersivo"
            ])
            c_rpm_in = st.selectbox("RPM Objetivo Proyectado:", ["$18.00 – $26.00 USD (Tier 1)", "$22.00 – $32.00 USD (High Tech/Space)", "$15.00 – $20.00 USD (Educación)"])

            if st.button("🚀 Crear Canal en el Ecosistema VideoPro", type="primary"):
                if c_slug_in and c_name_in:
                    res = YouTubeChannelManager.create_new_channel(
                        channel_slug=c_slug_in,
                        brand_name=c_name_in,
                        handle=c_handle_in if c_handle_in else f"@{c_slug_in.lower()}",
                        tagline=c_tagline_in if c_tagline_in else "Canal Automatizado VideoPro",
                        niche=c_nicho_in,
                        target_rpm=c_rpm_in
                    )
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.warning("Por favor introduce el identificador y nombre del canal.")

    # ==========================================================================
    # TAB 3: EXPLORADOR ZERO-API
    # ==========================================================================
    with tabs[2]:
        render_live_niche_explorer()

    # ==========================================================================
    # TAB 4: GENERADOR SEO & CHECKLIST DE LANZAMIENTO
    # ==========================================================================
    with tabs[3]:
        st.markdown("### 🎯 Generador SEO en 6 Bloques & Checklist de Lanzamiento")
        st.caption("Crea metadatos de alto CTR y verifica que tu canal cumpla los estándares de producción antes del lanzamiento.")

        col_chk1, col_chk2, col_chk3 = st.columns(3)
        with col_chk1:
            with st.container(border=True):
                st.markdown("##### 🔴 YouTube Master Channel")
                items_yt = [
                    (1, "Banner 2560x1440 4K (Safe zone 1546x423)"),
                    (2, "Avatar 800x800 centrado"),
                    (3, "Verificación en 2 pasos y YPP activado"),
                    (4, "Descripción de canal con 10 LSI keywords"),
                    (5, "Valores predeterminados de subida configurados"),
                    (6, "Marca de agua 150x150 en todo el vídeo"),
                ]
                for idx, texto in items_yt:
                    key = f"yt_{idx}"
                    st.session_state["checklist_yt"][key] = st.checkbox(texto, value=st.session_state["checklist_yt"][key], key=f"chk_{key}")

        with col_chk2:
            with st.container(border=True):
                st.markdown("##### 🟣 TikTok Spinoff Hub")
                items_tt = [
                    (1, "Cuenta TikTok Creator activada"),
                    (2, "Bio con propuesta de valor (<80 caracteres)"),
                    (3, "Enlace directo hacia YouTube"),
                    (4, "Vídeos en 9:16 (1080x1920) a 60 FPS"),
                    (5, "Subtítulos Karaoke dinámicos en tercio inferior"),
                    (6, "Hook dopamínico en los primeros 1.5 segundos"),
                ]
                for idx, texto in items_tt:
                    key = f"tt_{idx}"
                    st.session_state["checklist_tt"][key] = st.checkbox(texto, value=st.session_state["checklist_tt"][key], key=f"chk_{key}")

        with col_chk3:
            with st.container(border=True):
                st.markdown("##### 🟠 Instagram Reels Hub")
                items_ig = [
                    (1, "Perfil de Empresa / Creador configurado"),
                    (2, "Portadas con cuadrícula 1:1 estética"),
                    (3, "Audio original masterizado a -14 LUFS"),
                    (4, "Comentario fijado con llamada a la acción"),
                    (5, "Textos alternativos (Alt text) para Explore"),
                ]
                for idx, texto in items_ig:
                    key = f"ig_{idx}"
                    st.session_state["checklist_ig"][key] = st.checkbox(texto, value=st.session_state["checklist_ig"][key], key=f"chk_{key}")

        st.markdown("---")

        st.markdown("#### 📝 Generador de Metadatos Canónicos en 6 Bloques")
        
        c_meta1, c_meta2 = st.columns(2)
        with c_meta1:
            g_canal = st.selectbox("Canal Asignado:", [c["nombre"] for c in channels])
            g_tema = st.text_input("Tema o Suceso Histórico / Científico:", value="Tokio: De la Aldea Edo de 1630 a la Mega-Pirámide Shimizu 2226")
            g_lsi = st.text_input("Palabras Clave Secundarias:", value="Tokio 4K, Edo Period, Shimizu Pyramid, Time Travel, Urban Reconstruction")
            g_duracion = st.selectbox("Duración Estimada:", ["10:00 min (Estándar Mid-rolls)", "12:30 min (Long-form High AVD)", "08:45 min (Compacto)"])

        with c_meta2:
            st.markdown("##### 📌 Título de Alto CTR Sugerido:")
            titulo_sugerido = f"¿Cómo Era Tokio Hace 400 Años? De Aldea Samurái a Megaciudad 2226 (Vuelo 4K)"
            st.code(titulo_sugerido, language="markdown")

            st.markdown("##### 🏷️ Bloque de Tags SEO:")
            tags_sugeridos = f"tokio 4k, historia de tokio, shimizu mega pyramid, viajes en el tiempo 4k, chronodrift, videopro, {g_lsi.lower()}"
            st.code(tags_sugeridos, language="text")

        st.markdown("##### 📄 Plantilla de Descripción Completa (6 Bloques):")
        bloques_md = f"""<!-- 1. GANCHO SEO (Primeros 150 caracteres) -->
Explora cómo era {g_tema} en una reconstrucción cinematográfica 4K ultra-realista con control de cámara 6-DoF y sonido espacial.

<!-- 2. SINOPSIS EXTENSA & LSI KEYWORDS (200 palabras) -->
En este episodio de {g_canal}, desglosamos la ingeniería, contexto histórico y proyecciones científicas de {g_tema}. Analizamos la evolución arquitectónica grounded con datos de OpenStreetMap y estudios urbanos de vanguardia.

<!-- 3. CAPÍTULOS DE YOUTUBE (Formato estricto) -->
00:00 - Introducción y Salto Temporal
02:15 - El Pasado Documentado (Siglo XVII)
05:30 - El Presente Real en 4K 60fps (2026)
08:00 - La Megaestructura Futura (Siglo XXIII)
09:45 - Conclusiones y Próximo Destino

<!-- 4. ENLACES Y RECURSOS -->
🔗 Recursos y Paquetes de Activos: https://videopro.studio/vault/{g_canal.lower()}
▸ Síguenos en TikTok / Instagram: @{g_canal.replace(' ', '').lower()}

<!-- 5. CRÉDITOS TÉCNICOS -->
🛠️ Renderizado: Gemini Omni Flash & FLUX 3 | Audio: EBU R128 (-14.0 LUFS) con Flow Music

<!-- 6. HASHTAGS -->
#Historia4K #Documental #Reconstruccion3D #CiudadesDelFuturo #VideoPro"""

        st.code(bloques_md, language="markdown")

    # ==========================================================================
    # TAB 5: PIPELINE MULTIPLATAFORMA & HERMES
    # ==========================================================================
    with tabs[4]:
        st.markdown("### 📱 Pipeline Multiplataforma & Orquestación Hermes")
        st.caption("Reciclaje inteligente a formato 9:16 (Shorts, TikTok, Reels) y subidas desatendidas con control de jitter.")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #00f0ff; margin-top: 0;">⚡ Retención Dopamínica (Primeros 3 Segundos)</h4>
                    <ul style="font-size: 13px; color: #cbd5e1;">
                        <li><strong>0.0s - 0.5s:</strong> Flash sutil de 2 frames + SFX <em>Sub-Bass Drop 40Hz</em>.</li>
                        <li><strong>0.0s - 1.8s:</strong> Zoom-in digital continuo de 1.0x a 1.15x con física de resorte (<em>spring easing</em>).</li>
                        <li><strong>0.2s:</strong> Entrada de titular cinético con subtítulos dinámicos estilo Karaoke ASS en tercio inferior.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        with col_p2:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #8b5cf6; margin-top: 0;">📐 Re-encuadre 9:16 en Remotion (VerticalReframe.tsx)</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        Superposición del plano 16:9 master sobre un fondo desenfocado con <strong>Blur Gaussiano de 35px</strong> y brillo al 45%, eliminando bandas negras sin recorte destructivo.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("#### 🤖 Orquestador Desatendido Hermes Multi-API")
        st.code("""
           [HERMES CHIEF ORCHESTRATOR]
                        │
         Invoca: delegate_task(...)
                        │
    ┌───────────────────┼───────────────────┐
    ▼                   ▼                   ▼
[YouTube Subagent] [TikTok Subagent] [Instagram Subagent]
 (Data API v3)      (Content API v2)  (Graph API v21.0)
        """, language="text")

        c_o1, c_o2, c_o3 = st.columns(3)
        with c_o1:
            st.markdown("**1. Jitter Anti-Detección:**")
            st.caption("Desplazamiento aleatorio de +120s a +480s entre subidas para emular comportamiento humano natural.")
        with c_o2:
            st.markdown("**2. Backoff Exponencial:**")
            st.caption("Reintentos automáticos escalonados ante errores 429 Too Many Requests.")
        with c_o3:
            st.markdown("**3. Pre-flight Check:**")
            st.caption("Validación de H.264 High Profile, AAC 48kHz estricto y normalización EBU R128 (-14 LUFS).")

    # ==========================================================================
    # TAB 6: DASHBOARDS INTERACTIVOS
    # ==========================================================================
    with tabs[5]:
        st.markdown("### 📊 Dashboards Interactivos e Inteligencia Visual")
        st.caption("Inspecciona los tableros visuales HTML de retención, demanda urbana y estado global de los canales.")

        dashboards = YouTubeChannelManager.get_dashboard_html_paths()
        if dashboards:
            dash_choice = st.selectbox("Seleccionar Dashboard para Visualizar:", list(dashboards.keys()))
            dash_path = dashboards[dash_choice]

            if os.path.exists(dash_path):
                with open(dash_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                components.html(html_content, height=820, scrolling=True)
            else:
                st.error(f"No se pudo encontrar el archivo en {dash_path}")
        else:
            st.info("No se encontraron archivos HTML de dashboards en `docs/02_canales_youtube/`.")

    # ==========================================================================
    # TAB 7: AUDITORÍA & ANTI-SLOP
    # ==========================================================================
    with tabs[6]:
        st.markdown("### 🛡️ Suite de Auditoría de Pipeline y Control Anti-Slop")
        st.caption("Ejecuta en tiempo real la suite de validación de esquemas JSON, storyboards 6-DoF y audio engineering.")

        col_btn_aud, col_info_aud = st.columns([3, 7], vertical_alignment="center")
        with col_btn_aud:
            run_aud_btn = st.button("🚀 Ejecutar Validación End-to-End", type="primary", use_container_width=True)
        with col_info_aud:
            st.markdown("Valida: `channel_config.json`, Manifiestos 6-DoF, Storyboards 7-Planos y Manifiestos de Audio.")

        if run_aud_btn:
            with st.spinner("Ejecutando validate_chronodrift_pipeline.py..."):
                val_script = BASE_DIR / "scripts" / "validate_chronodrift_pipeline.py"
                try:
                    res = subprocess.run(["python3", str(val_script)], capture_output=True, text=True, timeout=20)
                    if res.returncode == 0:
                        st.success("🏆 AUDITORÍA COMPLETADA CON ÉXITO: 100% de los Componentes Pasaron la Validación.")
                        st.code(res.stdout, language="bash")
                    else:
                        st.error(f"Errores encontrados durante la validación (Código {res.returncode}):")
                        st.code(res.stderr + "\n" + res.stdout, language="bash")
                except Exception as ex:
                    st.error(f"Error al ejecutar el script de validación: {ex}")
        else:
            st.info("Haz clic en **Ejecutar Validación End-to-End** para auditar en tiempo real el pipeline completo.")
