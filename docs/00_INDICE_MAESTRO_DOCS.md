# 📚 Índice Maestro de Documentación — VideoPro Studio

> **Versión Canónica:** `2.3.0` | **Sincronización:** Firebase Firestore (`ayuda-emilio-83261`) | **UI:** Streamlit WebUI

Bienvenido al centro de documentación unificado de **VideoPro Studio**. La estructura está organizada en **8 pilares canónicos** simétricos con las colecciones de Firestore, las vistas de la UI y el core de orquestación.

---

## 🏛️ Los 8 Pilares Canónicos

### [01. Arquitectura y Sistema](01_arquitectura_y_sistema/)
* [01_arquitectura_general_videopro.md](01_arquitectura_y_sistema/01_arquitectura_general_videopro.md): Auditoría completa del sistema, diagramas y contratos.
* [02_nomenclatura_oficial_naming.md](01_arquitectura_y_sistema/02_nomenclatura_oficial_naming.md): Taxonomía oficial inequívoca (Capability, Engine, Provider, Node, Workflow).
* [03_matriz_realidad_y_sistemas.md](01_arquitectura_y_sistema/03_matriz_realidad_y_sistemas.md): Matriz de verdad técnica (componentes activos vs planificados).
* [03_sistemas_reales_infraestructura.md](01_arquitectura_y_sistema/03_sistemas_reales_infraestructura.md): Infraestructura física en la VPS Oracle y proveedores cloud.
* [04_runtime_servicios_y_puertos.md](01_arquitectura_y_sistema/04_runtime_servicios_y_puertos.md): Mapeo de puertos (8080 API, 8501 WebUI, 7001 Dev, 8742 Antigravity).
* [05_arquitectura_orquestador_studio.md](01_arquitectura_y_sistema/05_arquitectura_orquestador_studio.md): Director Creativo Semántico y Cadena de Pensamiento (CoT).
* [06_mapa_global_sistema.md](01_arquitectura_y_sistema/06_mapa_global_sistema.md): Mapa integral de servicios, demonios y flujos de datos.

### [02. Firebase y Persistencia](02_firebase_y_persistencia/)
* [01_arquitectura_firestore_y_r2.md](02_firebase_y_persistencia/01_arquitectura_firestore_y_r2.md): Persistencia híbrida NoSQL Firestore + Cloudflare R2 Zero Egress.
* [02_esquemas_colecciones_firebase.md](02_firebase_y_persistencia/02_esquemas_colecciones_firebase.md): Especificación de `videopro_settings`, `videopro_projects` y `videopro_system`.
* [03_sync_bridge_y_hosting.md](02_firebase_y_persistencia/03_sync_bridge_y_hosting.md): Módulo `firebase_sync.py`, auto-guardado en segundo plano y CDN hosting.

### [03. Capacidades y Nodos](03_capacidades_y_nodos/)
* [00_INDICE_CAPACIDADES.md](03_capacidades_y_nodos/00_INDICE_CAPACIDADES.md): Las 14 capacidades oficiales de VideoPro (QUÉ se hace).
* [01_inteligencia_investigacion_guion.md](03_capacidades_y_nodos/01_inteligencia_investigacion_guion.md): `research`, `script`, `scene_planning`.
* [02_visual_motores_y_keyframes.md](03_capacidades_y_nodos/02_visual_motores_y_keyframes.md): `image_generation`, `video_generation`, `post_processing`.
* [03_audio_voz_musica_y_foley.md](03_capacidades_y_nodos/03_audio_voz_musica_y_foley.md): `voice_generation`, `speech_to_text`, `music_generation`, `foley_sfx`.
* [04_ensamblaje_subtitulos_y_render.md](03_capacidades_y_nodos/04_ensamblaje_subtitulos_y_render.md): `subtitle_generation`, `rendering`, `storage`, `notification`.
* [05_catalogo_nodos_y_sockets.md](03_capacidades_y_nodos/05_catalogo_nodos_y_sockets.md): Puertos de entrada/salida (Sockets) y parámetros configurables.

### [04. Motores y Proveedores](04_motores_y_proveedores/)
* **01. Visual:** `flux3/`, `google_flow_web/`, `nanobanana_pro/`, `ltx_video_2_5/`, `stock_scraping_real/`
* **02. Voz y Audio:** `vibevoice_neural/`, `kokoro_tts_foley/`, `edge_tts_multilingual/`
* **03. Música y Psicoacústica:** `flowmusic_lyria3/`, `mastering_audiophilo_asmr/`
* **04. Programación y Ensamblaje:** `ffmpeg_moviepy_engine/`, `remotion_react_hyperframes/`, `vox_subtitles_whisper/`
* **05. LLM Directores:** `antigravity_bridge_8742/`, `cloudflare_ai_serverless/`

### [05. Workflows y Arquetipos](05_workflows_y_arquetipos/)
* [00_INDICE_WORKFLOWS.md](05_workflows_y_arquetipos/00_INDICE_WORKFLOWS.md): Catálogo de los 8 arquetipos oficiales de producción.
* [01_chronodrift_tritemporal_4k.md](05_workflows_y_arquetipos/01_chronodrift_tritemporal_4k.md): `CHRONODRIFT_TRITEMPORAL` (1626 ➔ 2026 ➔ 2226).
* [02_fpv_urban_real_flow.md](05_workflows_y_arquetipos/02_fpv_urban_real_flow.md): `FPV_URBAN_REAL_FLOW` (Tours Urbanos Beat-Sync).
* [03_pixar_3d_animation.md](05_workflows_y_arquetipos/03_pixar_3d_animation.md): `PIXAR_3D_ANIMATION` (Cuentos & Animación 3D).
* [04_historical_scraping.md](05_workflows_y_arquetipos/04_historical_scraping.md): `HISTORICAL_SCRAPING` (Documental Histórico).
* [05_deep_explainer_essay.md](05_workflows_y_arquetipos/05_deep_explainer_essay.md): `DEEP_EXPLAINER_ESSAY` (Videoensayo Vox).
* [06_viral_shorts_hook.md](05_workflows_y_arquetipos/06_viral_shorts_hook.md): `VIRAL_SHORTS_HOOK` (TikTok/Reels Alta Retención).
* [07_city_routes_beats.md](05_workflows_y_arquetipos/07_city_routes_beats.md): `CITY_ROUTES_BEATS` (Vídeo Musical Urbano).
* [08_madrid_curiosities_real_flow.md](05_workflows_y_arquetipos/08_madrid_curiosities_real_flow.md): `MADRID_CURIOSITIES_REAL_FLOW` (Madrid Secreto 4K).

### [06. Canales de YouTube — Ecosistema](06_canales_youtube_ecosistema/)
* **01. CHRONODRIFT:** Tours FPV tritemporales con 12 ciudades globales y 10 episodios.
* **02. TERRAMORPH:** Geología extrema, cataclismos y evolución planetaria.
* **03. NANOVERSE:** Biología celular y medicina molecular.
* **04. LIVING CANVAS:** Historia del arte animada y pinturas clásicas vivas.
* **05. ASTRODRIFT:** Astronomía cinemática y exploración espacial JWST.

### [07. Guías de Producción y Estándares](07_guias_produccion_y_estandares/)
* [01_metodologia_documental_cinematografica.md](07_guias_produccion_y_estandares/01_metodologia_documental_cinematografica.md): Metodología de investigación y storyboard.
* [02_arquitectura_documentary_director.md](07_guias_produccion_y_estandares/02_arquitectura_documentary_director.md): Algoritmo de montaje elástico VO-First.
* [03_contratos_y_prompts_maestros.md](07_guias_produccion_y_estandares/03_contratos_y_prompts_maestros.md): Prompts maestros y validación JSON Schema.
* [04_integracion_google_flow_web_y_consistencia.md](07_guias_produccion_y_estandares/04_integracion_google_flow_web_y_consistencia.md): Protocolo de consistencia óptica.
* [05_arquitectura_fpv_tours_storytelling_urbano.md](07_guias_produccion_y_estandares/05_arquitectura_fpv_tours_storytelling_urbano.md): Plan de vuelo 3D 6-DoF.
* [06_prompting_dop_7_capas.md](07_guias_produccion_y_estandares/06_prompting_dop_7_capas.md): Estándar DoP de 7 capas visuales.
* [07_consistencia_actores_4_anclas.md](07_guias_produccion_y_estandares/07_consistencia_actores_4_anclas.md): Protocolo de consistencia facial y vestuario.
* [08_mastering_audio_48khz_ducking.md](07_guias_produccion_y_estandares/08_mastering_audio_48khz_ducking.md): Estándar ITU-R BS.1770-4 (-14 LUFS) y ducking -22dB.

### [08. Dashboards y Estudios Web](08_dashboards_y_estudios_web/)
* `dashboard_ciudades_tritemporales.html`: Time-slider interactivo (1626 / 2026 / 2226) y HUD tritemporal.
* `dashboard_canales_youtube.html`: Métricas, benchmarking y retención de los 5 canales.
* `workflow_designer_studio.html`: Diseñador visual de grafos y pipelines por nodos.
* `proveedores_excel.html`: Calculadora interactiva de costes por token/segundo.
* `comfy_pipeline_studio.html`: Simulador de cableado de sockets y flujo de datos.
* `10_dashboard_demanda_retencion_ciudades.html`: Matriz de demanda y retención de audiencia.
* `organizador_docs_videopro.html`: Visualizador de la arquitectura documental 1:1.
