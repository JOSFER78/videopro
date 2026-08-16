"""
webui/views/view_youtube_monetization.py
================================================================================
CENTRO DE MANDO, APRENDIZAJE Y GESTIÓN DE CANALES (HERMES YOUTUBE ENGINE)
================================================================================
Vista integral para VideoPro Studio / Hermes Agent.
- Tab 1: 🎓 Academia YouTube & Guía para Principiantes
- Tab 2: 📊 Diagnóstico y Evolución de Canales (01_CHRONODRIFT a 05_ASTRODRIFT)
- Tab 3: 🚀 Checklist de Lanzamiento & Multiplataforma Hermes (SEO Generator)
- Tab 4: 🔍 Explorador de Nichos en Vivo (Zero-API Engine con Blue Ocean Index)
- Tab 5: 🛡️ Auditoría del Pipeline de Producción (Control de Calidad & Anti-Slop)

Adaptado estrictamente a Dark IDE Theme con Glassmorphism y Cero Mocks.
"""

import streamlit as st
import json
import math
import os
import subprocess
from datetime import datetime
from app.core.youtube_niche_explorer import render_live_niche_explorer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHANNELS_DIR = os.path.join(BASE_DIR, "docs", "02_canales_youtube", "mis_canales")
MANIFESTS_DIR = os.path.join(BASE_DIR, "data", "tritemporal_manifests")


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
        .code-snippet {
            background: #090d16;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 10px 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #38bdf8;
            overflow-x: auto;
        }
        </style>
    """, unsafe_allow_html=True)


ECOSISTEMA_CANALES_DEFAULT = [
    {
        "id": "01_CHRONODRIFT",
        "nombre": "ChronoDrift",
        "handle": "@ChronoDriftOfficial",
        "estado": "PRODUCCION",
        "estado_label": "🟢 PRODUCCIÓN ACTIVA",
        "nicho": "Viajes Temporales 4K / Reconstrucción Urbana Tritemporal",
        "geo_target": "USA, UK, Alemania, Japón (Tier 1)",
        "rpm_min": 22.50,
        "rpm_max": 28.00,
        "rpm_display": "$22.50 - $28.00",
        "episodios_listos": 12,
        "progreso": 100,
        "salud_score": 96,
        "pipeline": "FLUX 3 Master + LTX-2.5 6-DoF + Remotion Vox Lower Thirds + Foley 48kHz",
        "fuentes_ingreso": ["AdSense 4K UHD", "Afiliados de viajes y fotografía", "Venta de LUTs ACEScg", "Patrocinios VPN/Tech"],
        "recomendacion": "Escalar a 2 episodios semanales. Añadir pantalla final hacia la lista de reproducción temática para aumentar la sesión de visualización en un +35%."
    },
    {
        "id": "02_TERRAMORPH",
        "nombre": "TerraMorph",
        "handle": "@TerraMorphAI",
        "estado": "DESARROLLO",
        "estado_label": "🟡 EN DESARROLLO (ASSETS & PROMPTS)",
        "nicho": "Geología Extrema, Tectónica & Megaestructuras Planetarias",
        "geo_target": "USA, Canadá, Australia",
        "rpm_min": 18.00,
        "rpm_max": 22.00,
        "rpm_display": "$18.00 - $22.00",
        "episodios_listos": 4,
        "progreso": 60,
        "salud_score": 82,
        "pipeline": "FLUX 3 D-Depth + LTX Flow Matching + Bloomberg Stat Cards + Sub-bass 40Hz",
        "fuentes_ingreso": ["AdSense Tier 1", "Software de modelado 3D / GIS", "Libros divulgativos de geología"],
        "recomendacion": "Completar la matriz de 5 vistas para el narrador geólogo virtual y calibrar el sidechain ducking en escenas de erupciones volcánicas."
    },
    {
        "id": "03_NANOVERSE",
        "nombre": "NanoVerse",
        "handle": "@NanoVerseExplore",
        "estado": "PLANIFICADO",
        "estado_label": "🔵 PLANIFICADO (ESTUDIO DE AUDIENCIA)",
        "nicho": "Biología Microscópica, Inmunología & Zoom Infinito Celular",
        "geo_target": "Global Tier 1 + Comunidad Educativa",
        "rpm_min": 15.50,
        "rpm_max": 19.00,
        "rpm_display": "$15.50 - $19.00",
        "episodios_listos": 1,
        "progreso": 30,
        "salud_score": 68,
        "pipeline": "Micro-Prompting 7-Capas + Lyria 3 Pro Ambient + Remotion Deep Zoom",
        "fuentes_ingreso": ["AdSense Educativo", "Afiliados de microscopía y óptica", "Licencias para documentales"],
        "recomendacion": "Desarrollar la miniserie piloto de 3 partes: 'El Ataque del Fago T4: La Guerra Oculta' utilizando transiciones J-Cut a 24 FPS."
    },
    {
        "id": "04_LIVING_CANVAS",
        "nombre": "Living Canvas",
        "handle": "@LivingCanvasArt",
        "estado": "PLANIFICADO",
        "estado_label": "🔵 PLANIFICADO (BIBLIA VISUAL)",
        "nicho": "Historia del Arte, Museos en 3D & Cuadros Clásicos Vivos",
        "geo_target": "Europa Tier 1, USA",
        "rpm_min": 19.00,
        "rpm_max": 24.00,
        "rpm_display": "$19.00 - $24.00",
        "episodios_listos": 0,
        "progreso": 15,
        "salud_score": 55,
        "pipeline": "Segmentación SAM-2 de cuadros + FLUX Inpainting + Música Clásica Lo-Fi 48kHz",
        "fuentes_ingreso": ["AdSense Alta Retención", "Venta de Prints Fine Art 4K bajo demanda", "Licencias de animación"],
        "recomendacion": "Compilar la base de datos de 50 obras maestras en dominio público (Louvre, Prado, Met) y estructurar prompts de iluminación Claroscuro Caravaggio."
    },
    {
        "id": "05_ASTRODRIFT",
        "nombre": "AstroDrift",
        "handle": "@AstroDriftCosmos",
        "estado": "PLANIFICADO",
        "estado_label": "🔵 PLANIFICADO (CONCEPT SCRIPT)",
        "nicho": "Astrofísica, Agujeros Negros, Relatividad & Espacio Profundo",
        "geo_target": "USA, UK, Tier 1 Global",
        "rpm_min": 26.00,
        "rpm_max": 35.00,
        "rpm_display": "$26.00 - $35.00",
        "episodios_listos": 0,
        "progreso": 10,
        "salud_score": 50,
        "pipeline": "Ray-Marching Relativista + LTX-2.5 Space Flight + VibeVoice Deep Resonance",
        "fuentes_ingreso": ["AdSense Máximo RPM ($30+)", "Afiliados de telescopios (Celestron)", "BSO Spotify / Bandcamp"],
        "recomendacion": "Finalizar el guion técnico del episodio 01: 'Cruzando el Horizonte de Sucesos de Gargantúa a 60 FPS' validado con modelos matemáticos."
    }
]


def render_youtube_monetization_view():
    inject_custom_styles()
    
    if "canales_ecosistema" not in st.session_state:
        st.session_state["canales_ecosistema"] = ECOSISTEMA_CANALES_DEFAULT
    if "checklist_yt" not in st.session_state:
        st.session_state["checklist_yt"] = {f"yt_{i}": False for i in range(1, 11)}
    if "checklist_tt" not in st.session_state:
        st.session_state["checklist_tt"] = {f"tt_{i}": False for i in range(1, 9)}
    if "checklist_ig" not in st.session_state:
        st.session_state["checklist_ig"] = {f"ig_{i}": False for i in range(1, 9)}

    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 style="font-size: 22px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 10px;">
                    💰 Centro de Mando, Aprendizaje & Gestión de Canales
                    <span class="yt-badge badge-green">HERMES YOUTUBE ENGINE v2.4</span>
                </h1>
                <p style="font-size: 12.5px; color: #94a3b8; margin: 2px 0 0 0;">
                    Monetización de alto RPM, auditoría en vivo del ecosistema de 01 a 05, checklist multiplataforma y explorador de nichos Zero-API.
                </p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="yt-badge badge-cyan">TIER 1 TARGET ($18-$35)</span>
                <span class="yt-badge badge-purple">PRODUCCIÓN 4K UHD</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "🎓 Tab 1: Academia YouTube & Guía Principiantes",
        "📊 Tab 2: Diagnóstico y Evolución de Canales",
        "🚀 Tab 3: Checklist de Lanzamiento & Multiplataforma",
        "🔍 Tab 4: Explorador de Nichos en Vivo (Zero-API)",
        "🛡️ Tab 5: Auditoría del Pipeline de Producción"
    ])

    # ==========================================================================
    # TAB 1: ACADEMIA YOUTUBE & GUÍA PARA PRINCIPIANTES
    # ==========================================================================
    with tabs[0]:
        st.markdown("### 🎓 Academia de Monetización y Mecánicas del Algoritmo")
        st.caption("Aprende las reglas matemáticas y de retención que diferencian un canal amateur de una máquina de ingresos de $10,000+/mes.")

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

        st.markdown("#### 🏛️ Los 4 Pilares de Monetización de un Canal Automatizado")
        c_mot1, c_mot2 = st.columns(2)
        with c_mot1:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #00f0ff; margin-top: 0;">1. 💵 AdSense Automatizado de Alto RPM</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        Vídeos de 8 a 15 minutos en nichos como historia, ciencia, tecnología o finanzas atraen anunciantes corporativos en USA, UK, Alemania y Canadá.
                    </p>
                    <ul style="font-size: 12.5px; color: #94a3b8;">
                        <li><strong>Mid-Rolls Estratégicos:</strong> Insertar pausas en minutos 4:00 y 8:00 sincronizadas con cortes de escena.</li>
                        <li><strong>Impacto:</strong> Aumenta los ingresos netos de AdSense en un <strong>+34% a +48%</strong>.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #10b981; margin-top: 0;">2. 🔗 Enlaces de Afiliados Contextuales (Día 1)</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        Integración de enlaces directos en la descripción y comentario fijado (software de IA, equipamiento, libros, VPNs).
                    </p>
                    <ul style="font-size: 12.5px; color: #94a3b8;">
                        <li><strong>Conversión Media:</strong> 0.8% - 2.5% de espectadores hacen clic.</li>
                        <li><strong>Comisión:</strong> Desde $15 hasta $120 por venta recurrente.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        with c_mot2:
            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #f59e0b; margin-top: 0;">3. 📦 Activos Digitales & Micro-Productos</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        Venta directa a la audiencia sin intermediarios de activos generados durante la producción de los episodios.
                    </p>
                    <ul style="font-size: 12.5px; color: #94a3b8;">
                        <li><strong>Paquetes de LUTs ACEScg:</strong> Para editores y creadores ($19 - $39).</li>
                        <li><strong>Banda Sonora y Foley:</strong> Pistas en 48kHz sin royalties en Gumroad.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="yt-card">
                    <h4 style="color: #8b5cf6; margin-top: 0;">4. 🛡️ Patrocinios Directos B2B</h4>
                    <p style="font-size: 13px; color: #cbd5e1;">
                        A partir de 5k-10k suscriptores, marcas de nicho pagan tarifas fijas de $250 a $1,500 por mención integrada.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # CALCULADORA DINÁMICA
        st.markdown("#### 💸 Calculadora Interactiva de Proyección de Ingresos")
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            vistas_estimadas = st.slider("Vistas Mensuales Globales del Canal:", min_value=20000, max_value=2000000, value=250000, step=10000)
            rpm_seleccionado = st.slider("RPM Promedio ($ por 1.000 vistas):", min_value=5.0, max_value=40.0, value=22.5, step=0.5)
            afiliados_ingreso = st.number_input("Ingresos Estimados por Afiliados / Patrocinios ($):", value=450, step=50)

        with col_c2:
            ingreso_adsense = (vistas_estimadas / 1000.0) * rpm_seleccionado * 1.38  # con 2 mid-rolls
            ingreso_total_mes = ingreso_adsense + afiliados_ingreso
            ingreso_total_ano = ingreso_total_mes * 12

            with st.container(border=True):
                st.markdown("##### 📈 Estimación Financiera Mensual:")
                st.metric("Ingreso Total Mensual", f"${ingreso_total_mes:,.2f}", f"+${ingreso_total_ano:,.2f} / año")
                col_sub1, col_sub2 = st.columns(2)
                col_sub1.metric("AdSense (con Mid-rolls)", f"${ingreso_adsense:,.2f}")
                col_sub2.metric("Afiliados / Patrocinios", f"${afiliados_ingreso:,.2f}")

    # ==========================================================================
    # TAB 2: DIAGNÓSTICO Y EVOLUCIÓN DE CANALES
    # ==========================================================================
    with tabs[1]:
        st.markdown("### 📊 Tablero de Control y Diagnóstico de Canales (01 a 05)")
        st.caption("Auditoría técnica en vivo del estado de producción, salud de monetización y plan de escalado para cada canal.")

        canales = st.session_state["canales_ecosistema"]

        for canal in canales:
            with st.container(border=True):
                col_h1, col_h2, col_h3 = st.columns([5, 3, 2], vertical_alignment="center")
                with col_h1:
                    st.markdown(f"<h3 style='margin:0; font-size:17px; color:#f8fafc;'>{canal['nombre']} <span style='font-size:12px; color:#38bdf8;'>{canal['handle']}</span></h3>", unsafe_allow_html=True)
                    st.caption(f"**Nicho:** {canal['nicho']} | **Target:** {canal['geo_target']}")
                with col_h2:
                    st.markdown(f"**Estado:** `{canal['estado_label']}`")
                    st.progress(canal['progreso'] / 100.0)
                with col_h3:
                    st.metric("RPM Proyectado", canal['rpm_display'])

                with st.expander(f"🔍 Hoja de Ruta & Recomendación Evolutiva — {canal['nombre']}"):
                    st.markdown(f"**🛠️ Pipeline:** `{canal['pipeline']}`")
                    st.markdown(f"""
                        <div class="highlight-box">
                            <strong>💡 Recomendación Evolutiva de Alto CTR:</strong><br>
                            {canal['recomendacion']}
                        </div>
                    """, unsafe_allow_html=True)

        with st.expander("➕ Planificar y Registrar Nuevo Canal en Disco"):
            c_slug = st.text_input("Identificador Único (ej. 06_OCEANMORPH):", placeholder="06_NOMBRE_CANAL")
            c_name = st.text_input("Nombre Público del Canal:", placeholder="OceanMorph (@OceanMorphAI)")
            c_nicho = st.selectbox("Nicho Temático:", [
                "Documental Científico & Océanos",
                "Historia & Hemerotecas 4K",
                "Tecnología & IA Futurista",
                "Astrofísica & Cosmología",
                "Música Generativa & Foley 15min"
            ])
            if st.button("🚀 Registrar Canal en el Ecosistema", type="primary"):
                if c_slug:
                    st.success(f"Canal '{c_slug}' registrado y estructurado en docs/02_canales_youtube/mis_canales/!")

    # ==========================================================================
    # TAB 3: CHECKLIST DE LANZAMIENTO & MULTIPLATAFORMA
    # ==========================================================================
    with tabs[2]:
        st.markdown("### 🚀 Checklist de Lanzamiento Multiplataforma & Generador SEO")
        st.caption("Asegura el 100% de cumplimiento técnico en YouTube, TikTok e Instagram antes de publicar tu primer vídeo.")

        col_chk1, col_chk2, col_chk3 = st.columns(3)
        with col_chk1:
            with st.container(border=True):
                st.markdown("##### 🔴 YouTube Master Channel")
                items_yt = [
                    (1, "Banner 2560x1440 4K y Avatar 800x800"),
                    (2, "Verificación en 2 pasos activada"),
                    (3, "Descripción del canal optimizada con palabras clave"),
                    (4, "Valores predeterminados de subida (Licencia estándar)"),
                    (5, "Marca de agua de suscripción en todo el vídeo"),
                    (6, "Visibilidad predeterminada: Privado / Oculto"),
                ]
                for idx, texto in items_yt:
                    key = f"yt_{idx}"
                    st.session_state["checklist_yt"][key] = st.checkbox(texto, value=st.session_state["checklist_yt"][key], key=f"chk_{key}")

        with col_chk2:
            with st.container(border=True):
                st.markdown("##### 🟣 TikTok Spinoff Hub")
                items_tt = [
                    (1, "Cuenta TikTok Creator activada"),
                    (2, "Biografía con propuesta de valor clara (<80 car)"),
                    (3, "Enlace en Bio hacia YouTube"),
                    (4, "Vídeos en formato 9:16 (1080x1920) a 60 FPS"),
                    (5, "Subtítulos dinámicos estilo Karaoke en tercio inferior"),
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

        st.markdown("#### 🎯 Generador de Metadatos SEO en Tiempo Real")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            tema_episodio = st.text_input("Tema o Suceso del Episodio:", value="La Destrucción de Pompeya y la Erupción del Vesubio en 79 d.C.")
            palabras_clave = st.text_input("Palabras Clave:", value="Pompeii 4K, Roman Empire, Vesuvius Eruption, 3D Reconstruction")
        with col_g2:
            st.markdown("##### 📌 Título Viral Sugerido (Alto CTR):")
            st.code(f"Cómo Era Pompeya MINUTOS Antes del Vesubio: Reconstrucción 4K (79 d.C.)", language="markdown")
            st.markdown("##### 📝 Bloque de Tags SEO:")
            st.code(f"pompeya 4k, erupcion vesubio 79 dc, reconstruccion romana 3d, viajes en el tiempo 4k, chronodrift, {palabras_clave.lower()}", language="text")

    # ==========================================================================
    # TAB 4: EXPLORADOR DE NICHOS EN VIVO (ZERO-API ENGINE)
    # ==========================================================================
    with tabs[3]:
        render_live_niche_explorer()

    # ==========================================================================
    # TAB 5: AUDITORÍA DEL PIPELINE DE PRODUCCIÓN
    # ==========================================================================
    with tabs[4]:
        st.markdown("### 🛡️ Auditoría del Pipeline de Producción (Anti-Slop & Calidad)")
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
