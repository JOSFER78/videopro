"""
view_hermes_mission_control.py
Cabina de Mando y Telemetría en Tiempo Real de Hermes Agent — VideoPro Studio.
Permite supervisar la ejecución autónoma de misiones:
1. Selector y estado de misiones activas y archivadas (con sincronización Firestore).
2. Pestaña "Mente de Hermes (Live Thinking)": Consola en vivo del razonamiento CoT.
3. Pestaña "Árbol de Producción de 7 Nodos": Progreso visual interactivo de cada nodo.
4. Pestaña "Bóveda de Activos VOX": Galería de mapas QGIS, periódicos 3D y blueprints generados.
5. Pestaña "Master Final & Mosaico QA": Reproductor de vídeo y visualizador del Contact Sheet 4K.
"""

import os
import json
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.services.hermes_mission_dispatcher import HermesMissionDispatcher, HermesMissionStatus
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG


def render_hermes_mission_control_view():
    """Renderiza la Cabina de Mando de Hermes Agent."""
    dispatcher = HermesMissionDispatcher()

    # Encabezado Ejecutivo
    st.markdown("""
        <div style="margin-bottom: 14px; padding: 14px 18px; background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.85)); border-radius: 10px; border: 1px solid rgba(56,189,248,0.3); box-shadow: 0 4px 20px rgba(0,0,0,0.45);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="font-size: 20px; font-weight: 800; color: #f8fafc; margin: 0; display: flex; align-items: center; gap: 8px;">
                        <span style="color: #38bdf8;">🤖</span> Hermes Mission Control — Cabina de Mando Agéntica
                    </h2>
                    <p style="font-size: 12px; color: #94a3b8; margin: 3px 0 0 0;">
                        Supervisión del cerebro autónomo de Hermes: razonamiento CoT en vivo, ejecución de los 7 nodos, activos documentales y telemetría de emisión.
                    </p>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35); padding: 3px 10px; border-radius: 12px; display: flex; align-items: center; gap: 5px;">
                        <span style="width: 7px; height: 7px; background: #38bdf8; border-radius: 50%; display: inline-block;"></span> AGENTE ACTIVO (COT ON)
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Selector de Misiones
    missions = dispatcher.list_all_missions(limit=15)
    
    if not missions:
        # Si no hay misiones, crear una misión demostrativa con los datos de Madrid Secreto
        demo_mission = dispatcher.create_mission(
            workflow_id="workflow_vox_investigative_doc",
            title="Madrid Secreto: Curiosidades y Pasajes Ocultos (3 min)",
            topic="Secretos bajo el asfalto de Madrid (Cibeles, Chamberí, Posición Jaca, Reloj Sol)",
            interview_answers={
                "pacing": "Broadcast Activo (Cortes 3-5s)",
                "visual_style": "Vox Full Parallax con Roughen Edges",
                "map_style": "Cartografía QGIS 4K con Dash=78",
                "audio_ducking": "-18dB Sidechain"
            },
            target_channel="Madrid Secreto & Rutas Históricas 4K",
            duration_target_sec=177.64
        )
        dispatcher.append_thinking_log(
            demo_mission["mission_id"],
            "Planificando matriz Storyboard Studio: Escena 1 (Mapa QGIS Dash=78), Escena 2 (Prensa 1919 Roughen), Escena 3 (Blueprint -14M), Escena 4 (Patente 1866).",
            new_status=HermesMissionStatus.COMPLETED,
            progress_percent=100.0
        )
        demo_mission["artifacts"]["master_video_path"] = "/home/ubuntu/workspace/pro/hermes/10_videopro/storage/projects/2026/08/16/workflow_madrid_curiosities_3min/madrid_secreto_3min/renders/cinematic_vox_test_15s.mp4"
        demo_mission["artifacts"]["qa_contact_sheet_path"] = "/home/ubuntu/.gemini/antigravity-ide/brain/9a6e71e0-e405-4a79-af69-534959cf61c6/vox_master_qa_sheet.jpg"
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_01_investigacion_y_storyboard", "COMPLETED", 100)
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_02_audio_first_y_foley", "COMPLETED", 100)
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_03_generacion_activos_vox", "COMPLETED", 100)
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_04_composicion_3d_parallax", "COMPLETED", 100)
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_05_subtitulos_y_hud", "COMPLETED", 100)
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_06_masterizacion_ebu_r128", "COMPLETED", 100)
        dispatcher.update_node_progress(demo_mission["mission_id"], "node_07_qa_contact_sheet_sync", "COMPLETED", 100)
        missions = [demo_mission]

    col_sel, col_btn = st.columns([4, 1])
    
    mission_options = {f"{m['title']} ({m['status']}) — {m['mission_id']}": m['mission_id'] for m in missions}
    
    with col_sel:
        selected_label = st.selectbox(
            "Seleccionar Misión / Producción en Curso:",
            options=list(mission_options.keys()),
            index=0,
            label_visibility="collapsed"
        )
    with col_btn:
        if st.button("🔄 Actualizar Telemetría", use_container_width=True):
            st.rerun()

    active_mission_id = mission_options[selected_label]
    mission = dispatcher.get_mission(active_mission_id)

    if not mission:
        st.error("No se pudo cargar la telemetría de la misión seleccionada.")
        return

    # Barra Superior de Estado y KPIs
    status = mission.get("status", "PENDING")
    status_color = "#34d399" if status == "COMPLETED" else ("#38bdf8" if status in ("REASONING", "PRODUCING_ASSETS", "COMPOSING") else "#f59e0b")
    progress_val = float(mission.get("progress_percent", 0.0))

    st.markdown(f"""
        <div style="margin-bottom: 12px; padding: 10px 14px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; gap: 16px; align-items: center;">
                <div>
                    <span style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Misión</span>
                    <div style="font-size: 13px; font-weight: 700; color: #f8fafc;">{mission.get('title')}</div>
                </div>
                <div>
                    <span style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Arquetipo</span>
                    <div style="font-size: 13px; font-weight: 600; color: #38bdf8;">{mission.get('workflow_id')}</div>
                </div>
                <div>
                    <span style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Canal Destino</span>
                    <div style="font-size: 13px; font-weight: 600; color: #a855f7;">{mission.get('target_channel')}</div>
                </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <div style="text-align: right;">
                    <span style="font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase;">Estado Agéntico</span>
                    <div style="font-size: 12px; font-weight: 800; color: {status_color};">● {status}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.progress(progress_val / 100.0, text=f"Progreso Global de Producción: {progress_val:.1f}%")

    # Pestañas Principales de la Cabina de Mando
    tab_thinking, tab_nodes, tab_assets, tab_player = st.tabs([
        "🧠 Mente de Hermes (Live Thinking)",
        "🎛️ Árbol de 7 Nodos",
        "🎞️ Activos Documentales VOX",
        "🏆 Master Final & Mosaico QA"
    ])

    # -------------------------------------------------------------
    # TAB 1: MENTE DE HERMES (LIVE THINKING LOGS)
    # -------------------------------------------------------------
    with tab_thinking:
        st.markdown("""
            <div style="margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">
                Consola de Razonamiento CoT (Chain-of-Thought) en Tiempo Real:
            </div>
        """, unsafe_allow_html=True)

        thinking_logs = mission.get("thinking_logs", [])
        logs_html = "".join([
            f"<div style='margin-bottom: 6px; font-family: monospace; font-size: 11.5px; line-height: 1.5; color: {'#38bdf8' if '🤖' in l or 'Hermes' in l else ('#34d399' if '✅' in l or 'ÉXITO' in l else '#cbd5e1')};'>{l}</div>"
            for l in thinking_logs
        ])

        st.markdown(f"""
            <div style="height: 340px; overflow-y: auto; background: #020617; border-radius: 8px; border: 1px solid #1e293b; padding: 12px 16px; box-shadow: inset 0 2px 8px rgba(0,0,0,0.6);">
                {logs_html}
            </div>
        """, unsafe_allow_html=True)

        st.caption("ℹ️ Hermes Agent razona autónomamente en cada paso, desglosa el guion en Storyboard Studio y aplica correcciones automáticas ante fallos de APIs.")

    # -------------------------------------------------------------
    # TAB 2: ÁRBOL DE 7 NODOS DE PRODUCCIÓN
    # -------------------------------------------------------------
    with tab_nodes:
        st.markdown("""
            <div style="margin-bottom: 10px; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">
                Estado de la Cadena de Montaje por Nodos Funcionales:
            </div>
        """, unsafe_allow_html=True)

        nodes_state = mission.get("nodes_state", {})
        node_cols = st.columns(2)

        ordered_node_keys = [
            ("node_01_investigacion_y_storyboard", "1. Investigación & Storyboard Studio", "Arco dramático y desglose en matriz de planos 4K"),
            ("node_02_audio_first_y_foley", "2. Audio-First & Foley Diegético", "Pista WAV máster, locución neural y foley físico sincronizado"),
            ("node_03_generacion_activos_vox", "3. Activos Auténticos VOX 4K", "Mapas QGIS Dash=78, Periódicos 1919 Roughen, Blueprints -14M"),
            ("node_04_composicion_3d_parallax", "4. Composición 3D Parallax", "Montaje en perspectiva con físicas spring() y stagger 3-5 frames"),
            ("node_05_subtitulos_y_hud", "5. Subtítulos & Telemetría HUD", "Subtítulos en píldora con active highlighting y mirillas de tracking"),
            ("node_06_masterizacion_ebu_r128", "6. Masterización EBU R128", "Mezcla DSP con sidechain ducking (-18 dB) y normalización a -14 LUFS"),
            ("node_07_qa_contact_sheet_sync", "7. QA Loop & Cloud Sync", "Mosaico QA 4K de verificación y persistencia en Firestore y R2")
        ]

        for idx, (n_key, n_title, n_desc) in enumerate(ordered_node_keys):
            col_target = node_cols[idx % 2]
            n_data = nodes_state.get(n_key, {"status": "PENDING", "progress": 0})
            n_status = n_data.get("status", "PENDING")
            
            icon = "✅" if n_status == "COMPLETED" else ("⏳" if n_status == "RUNNING" else "⚪")
            border_c = "#34d399" if n_status == "COMPLETED" else ("#38bdf8" if n_status == "RUNNING" else "#334155")

            with col_target:
                st.markdown(f"""
                    <div style="margin-bottom: 8px; padding: 10px 12px; background: #0f172a; border-radius: 8px; border: 1px solid {border_c};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 12.5px; font-weight: 700; color: #f8fafc;">{icon} {n_title}</div>
                            <span style="font-size: 10px; font-weight: 700; color: {border_c};">{n_status}</span>
                        </div>
                        <p style="font-size: 11px; color: #94a3b8; margin: 3px 0 0 0;">{n_desc}</p>
                    </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: BÓVEDA DE ACTIVOS DOCUMENTALES VOX
    # -------------------------------------------------------------
    with tab_assets:
        st.markdown("""
            <div style="margin-bottom: 10px; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">
                Activos Auténticos Diseñados y Generados por Hermes Agent:
            </div>
        """, unsafe_allow_html=True)

        asset_cols = st.columns(2)
        with asset_cols[0]:
            st.markdown("""
                <div style="padding: 10px 12px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 8px;">
                    <div style="font-size: 12px; font-weight: 700; color: #38bdf8;">🗺️ Escena 1: Cartografía Vectorial QGIS (Dash=78)</div>
                    <p style="font-size: 11px; color: #94a3b8; margin: 2px 0 0 0;">
                        Trazado continuo de ruta con guiones de pluma (Dash=78 / Trim Paths), compás náutico y textura de papel prensa (Multiply).
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <div style="padding: 10px 12px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 8px;">
                    <div style="font-size: 12px; font-weight: 700; color: #facc15;">📰 Escena 2: Prensa 3D con Roughen Edges & Resaltador Flúor</div>
                    <p style="font-size: 11px; color: #94a3b8; margin: 2px 0 0 0;">
                        Heraldo de Madrid 1919 con bordes rasgados procedimentales (Border 3.3px, Sharpness 4.58), rotulador flúor animado y sello oficial con rebote.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with asset_cols[1]:
            st.markdown("""
                <div style="padding: 10px 12px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 8px;">
                    <div style="font-size: 12px; font-weight: 700; color: #38bdf8;">📐 Escena 3: Blueprint DEM Búnker -14M (Offset Z +0.001)</div>
                    <p style="font-size: 11px; color: #94a3b8; margin: 2px 0 0 0;">
                        Corte transversal de ingeniería subterránea con cotas de nivel, separación de capas anti Z-fighting y líneas guía de telemetría.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <div style="padding: 10px 12px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 8px;">
                    <div style="font-size: 12px; font-weight: 700; color: #a855f7;">⚙️ Escena 4: Patente Horológica 1866 & Telemetría HUD</div>
                    <p style="font-size: 11px; color: #94a3b8; margin: 2px 0 0 0;">
                        Engranajes cinemáticos del reloj de José Rodríguez Losada, péndulo de compensación y telemetría de hora oficial en monospace.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 4: MASTER FINAL & MOSAICO QA
    # -------------------------------------------------------------
    with tab_player:
        artifacts = mission.get("artifacts", {})
        master_mp4 = artifacts.get("master_video_path")
        qa_sheet = artifacts.get("qa_contact_sheet_path")

        col_vid, col_qa = st.columns([1, 1])

        with col_vid:
            st.markdown("#### 🎬 Máster Documental Final (1080p / 4K)")
            if master_mp4 and os.path.isfile(master_mp4):
                st.video(master_mp4)
                st.caption(f"📁 Ruta: `{master_mp4}`")
            else:
                st.info("El máster final se mostrará aquí una vez que Hermes complete la etapa de masterización.")

        with col_qa:
            st.markdown("#### 📸 Mosaico QA de Verificación (Contact Sheet)")
            if qa_sheet and os.path.isfile(qa_sheet):
                st.image(qa_sheet, caption="Mosaico QA con telemetría de los 4 planos documentales")
            else:
                st.info("El mosaico de control de calidad se generará automáticamente tras la verificación.")
