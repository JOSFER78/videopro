# 📖 Guía Maestra: Cómo Organizar y Mantener la Carpeta `docs/` en VideoPro Studio

> **Filosofía de Arquitectura:** Sincronización Canónica 1:1 entre la **Web UI (Streamlit)**, el **Core de Orquestación** y la base de datos **Firebase Firestore (`ayuda-emilio-83261`)**.

---

## 🎯 1. Principio Fundamental de Organización

En VideoPro Studio, cada carpeta dentro de `docs/` cumple un propósito único y no debe solaparse con otra. La regla de oro es:

| Concepto | Qué significa | Dónde se documenta | Ejemplo |
| :--- | :--- | :--- | :--- |
| **Canales YouTube** | Tu propiedad intelectual y series de contenido | `docs/youtube/mis_canales/` | `01_CHRONODRIFT/`, `02_TERRAMORPH/` |
| **Estrategia YouTube** | Algoritmo, retención, SEO y miniaturas | `docs/youtube/<area>/` | `demanda_y_retencion/`, `seo_y_titulos/` |
| **Capacidades** | QUÉ se hace (contratos abstractos de entrada/salida) | `docs/capacidades/<capacidad>/` | `01_llm_script_semantic_director/` |
| **Nodos y Motores** | CÓMO y CON QUÉ se ejecuta (motores concretos) | `docs/nodos_y_motores/<categoria>/<motor>/` | `visual/01_flux3_serverless_zerogpu_replicate/` |
| **Workflows** | Cadena completa seleccionable en la UI para crear un vídeo | `docs/workflows/<arquetipo>/` | `01_CHRONODRIFT_TRITEMPORAL/` |
| **Investigaciones** | Tratados técnicos, física óptica, acústica y benchmarks | `docs/investigaciones/<tema>/` | `01_cinematografia_y_dop/`, `03_acustica/` |
| **Firebase & Cloud** | Esquemas de datos, persistencia R2 y Sync Bridge | `docs/firebase/` | `02_esquemas_colecciones_firebase.md` |
| **Arquitectura** | Puertos, runtime, servicios y topología del sistema | `docs/arquitectura_y_sistema/` | `04_runtime_servicios_y_puertos.md` |
| **Dashboards Web** | Paneles interactivos HTML y herramientas visuales | `docs/dashboards_y_estudios_web/` | `organizador_docs_videopro.html` |

---

## 🏛️ 2. Mapa Detallado de Carpetas y Contenidos

### 📺 A. `docs/youtube/`
* **`mis_canales/`**: Cada canal propio tiene su subcarpeta (`01_CHRONODRIFT/`, `02_TERRAMORPH/`, `03_NANOVERSE/`, `04_LIVING_CANVAS/`, `05_ASTRODRIFT/`).  
  * Dentro de cada canal van: `channel_config.json`, manifiestos de ciudades/episodios, storyboards y anexos de episodios.
* **`demanda_y_retencion/`**: Guías de retención 70/20/10, hooks de los primeros 5 segundos y RPM.
* **`seo_y_titulos/`**: Fórmulas de titulación con CTR >14%, taxonomía de keywords y metadatos.
* **`miniaturas_y_branding/`**: Guías de composición 3D, psicología del color, plantillas Figma/JSON.
* **`benchmarking_y_competencia/`**: Auditorías forenses de canales competidores y combate anti-slop.
* **`dashboards_y_metricas/`**: Visualizadores HTML de telemetría de canales.

---

### 🎛️ B. `docs/capacidades/`
Contiene **1 subcarpeta por cada una de las 14 capacidades oficiales** del sistema más la carpeta `schemas/`:
1. `01_llm_script_semantic_director/` (Guion y dirección semántica)
2. `02_google_flow_playwright_web_4k/` (Automatización Google Flow Web 4K)
3. `03_flux3_serverless_zerogpu_replicate/` (Fotogramas 4K y animación FLUX 3)
4. `04_nanobanana_pro_2/` (Keyframing consistente Imagen 3)
5. `05_ltx_2_5_mmdit_22b/` (Vídeo 22B MMDiT con audio nativo)
6. `06_stock_scraping_real_pexels_pixabay/` (Metraje real de archivo y stock)
7. `07_flowmusic_lyria3_via_playwright/` (Música adaptativa Lyria 3)
8. `08_vibevoice_1_5b_serverless/` (Voz neuronal `es-emilio`)
9. `09_kokoro_hd_tts_foley_ducking/` (Kokoro TTS + Foley + Ducking)
10. `10_edge_tts_neural_microsoft/` (Edge-TTS rápido)
11. `11_ffmpeg_core_moviepy_assembler/` (Ensamblaje máster y EBU R128)
12. `12_remotion_engine_react_hyperframes/` (Motion graphics por código React)
13. `13_vox_subtitles_karaoke_highlight/` (Subtítulos Karaoke ASS)
14. `14_whisper_stt_word_timestamps/` (Transcripción fonética Whisper)
* **`schemas/`**: Validadores formales `capability_manifest.schema.json`, `visual_spec.schema.json`, etc.

---

### 🧩 C. `docs/nodos_y_motores/`
Clasificados estrictamente por las **6 categorías de Firebase Firestore (`providers_registry`)**:
* **`visual/`**: `01_flux3_serverless_zerogpu_replicate/`, `02_google_flow_playwright_web_4k/`, `03_nanobanana_pro_2/`, `04_ltx_2_5_mmdit_22b/`, `05_wan_2_1_alibaba/`, `06_minimax_h3_hailuo/`, `07_seadance_2_5_bytedance/`, `08_stock_pexels_video/`, `09_stock_pixabay_video/`, `10_scraping_real_ddg_wikimedia/`.
* **`music/`**: `01_google_flow_music_lyria_3/` (con suites de 15 min, presets DSP y prompts), `02_suno_ai_api_v3_v4/`, `03_foley_director_ducking_master/`.
* **`voice/`**: `01_vibevoice_1_5b_serverless/`, `02_kokoro_hd_tts_foley_ducking/`, `03_edge_tts_neural/`, `04_elevenlabs_cinema/`, `05_fish_audio_s2_1_pro/`, `06_minimax_speech_01/`.
* **`programacion/`**: `01_ffmpeg_core_moviepy_assembler/`, `02_remotion_engine_react_hyperframes/`, `03_vox_subtitles_karaoke_highlight/`, `04_whisper_stt_word_timestamps/`.
* **`llm/`**: `01_antigravity_bridge_8742/`, `02_google_gemini_ai_studio/`, `03_openai_gpt_suite/`, `04_deepseek_9router_hub/`, `05_cloudflare_workers_ai/`, `06_siliconflow_hub/`.
* **`cloud/`**: `01_cloudflare_r2_object_storage/`, `02_firebase_firestore_hosting_sync/`.

---

### 🔬 D. `docs/investigaciones/`
Organizada en **6 áreas temáticas de ingeniería y ciencia audiovisual**:
1. **`01_cinematografia_y_dop/`**: DoP 7 Capas, Óptica Panavision C-Series, Colorimetría ACEScg, Cinemática de cámara 6-DoF y Guías de Metodología Documental.
2. **`02_consistencia_visual_y_actores/`**: Protocolo de 4 Anclas (Passport, Wardrobe, Rig, World), Matriz Radial 5 Vistas y Tail-Frame Flow.
3. **`03_ingenieria_acustica_y_psicoacustica/`**: Mastering EBU R128 (-14 LUFS), Sidechain Ducking (-22dB), Frecuencias 432Hz/528Hz, Efectos Binaurales y Mastering para Cascos de Lujo.
4. **`04_automatizacion_web_y_playwright/`**: Playwright Stealth CDP, Shadow DOM de Google Flow, bypass Cloudflare y APIs backend.
5. **`05_arquitectura_fpv_y_tours_urbanos/`**: GeoScraping 6+1, Dossier Tritemporal de Shibuya 2326 y Técnica Freeze 3D.
6. **`06_motores_generativos_y_benchmarks/`**: Comparativas de rendimiento, latencia y costes por segundo entre FLUX 3, LTX-2.5, Veo 3.1, Wan 2.1 y Remotion React.
* **`templates/`**: Plantillas para nuevos dossiers de investigación (`RESEARCH_DOSSIER_TEMPLATE.md`, `VISUAL_BIBLE_TEMPLATE.md`).

---

## 🛠️ 3. Reglas para Añadir o Modificar Documentación

1. **Si creas un nuevo Canal de YouTube:**
   - Crea su carpeta en `docs/youtube/mis_canales/0X_NOMBRE_CANAL/`.
   - Añade su `channel_config.json`, su `01_naming_branding_y_estudio.md` y sus escaletas.
   - Registra el canal en `docs/youtube/mis_canales/dashboard_canales_youtube.html`.

2. **Si integras un nuevo Motor o Proveedor:**
   - Ubícalo en `docs/nodos_y_motores/<categoria>/0X_nombre_motor/`.
   - Indica en el encabezado su estado: `🟢 ACTIVO` o `🟡 DISPONIBLE`.
   - Documenta su SLA, comandos CLI/API, variables de entorno y formato de audio/vídeo.

3. **Si realizas una nueva Investigación Técnica:**
   - Ubica el documento Markdown en la carpeta temática correspondiente de `docs/investigaciones/` (`01_`, `02_`, `03_`, `04_`, `05_` o `06_`).
   - Usa la plantilla `docs/investigaciones/templates/RESEARCH_DOSSIER_TEMPLATE.md`.
   - Enlaza el documento en el README de esa subcarpeta.

4. **Nomenclatura Estricta de Archivos:**
   - Minúsculas separadas por guiones bajos (snake_case): `01_guia_maestra_operativa.md`.
   - Los números de prefijo (`01_`, `02_`) determinan el orden pedagógico de lectura.
   - Queda **estrictamente prohibido** dejar archivos `.md` o `.html` sueltos en la raíz de `docs/` salvo el índice maestro (`00_INDICE_MAESTRO_DOCS.md` / `README.md`) y esta guía.
