# 📚 VideoPro Studio — Centro de Documentación, Guías de Uso y Laboratorio de Investigación

> [!NOTE]
> ### ⚠️ AVISO IMPORTANTE: Naturaleza Orientativa y Flexible de esta Documentación
> **Esta documentación NO es una biblia sagrada ni un conjunto de leyes dogmáticas que deban seguirse ciegamente al 100%.**  
> 
> Es un **marco de referencia técnico, orientativo e inspiracional** diseñado para aprender cómo funcionan los módulos, consultar cómo se resolvieron problemas complejos y disponer de un banco de ideas e investigaciones avanzadas.  
> 
> - **Libertad de Implementación:** No es la directriz única ni inalterable de cómo hacer las cosas. Si encuentras una forma más limpia, eficiente, moderna o sencilla de construir una funcionalidad, **tienes total libertad para adaptar, cambiar, simplificar o mejorar cualquier código o flujo**.
> - **Evolución Continua:** Las herramientas de IA, frameworks de renderizado y APIs evolucionan semanalmente. Lo que aquí se documenta es el estado del arte investigado, pero debe evolucionar según las necesidades reales del producto y el sentido común del desarrollador.

---

## 🎯 Propósito Central de esta Carpeta (`docs/`)

Este directorio cumple una **doble función práctica** tanto para desarrolladores como para creadores:

1. **Manual Operativo de Módulos (Aprender a Usar lo Existente):** Documentar con detalle técnico cómo funciona y cómo se utiliza cada capacidad, motor, canal y workflow que **ya existe en la página web** (organizados y enumerados con números de serie `01_`, `02_`... reflejando el orden visual de la interfaz).
2. **Laboratorio de Investigación & Banco de Ideas (Exploración Técnica):** Un espacio vivo de investigación avanzada donde se exploran tecnologías emergentes, físicas de movimiento, shaders GPU, psicología del sonido, ópticas de cine e ideas de proyecto que **aún no están en la página web**, para que cualquier desarrollador pueda leerlas, inspirarse y evaluar su integración si resulta de interés.

---

## 🧭 ¿Cómo Navegar por esta Documentación?

El contenido se divide en dos grandes bloques claramente diferenciados:

```
docs/
├── 🟢 BLOQUE 1: MÓDULOS ACTIVOS EN LA PÁGINA WEB (Con Número de Serie 01_, 02_...)
│   ├── capacidades/        --> Las 14 capacidades oficiales (QUÉ hace el sistema)
│   ├── nodos_y_motores/    --> Los 26 motores clasificados por categoría Firebase (CÓMO se ejecuta)
│   ├── youtube/mis_canales --> Los 5 canales y proyectos oficiales de la Bóveda
│   ├── workflows/          --> Los 8 arquetipos de producción seleccionables en Workflow Studio
│   └── firebase/           --> Arquitectura de base de datos Firestore, Storage R2 y Hosting
│
└── 🔬 BLOQUE 2: LABORATORIO DE INVESTIGACIÓN E IDEAS (Sin Número de Serie)
    └── investigaciones/    --> Tratados de ingeniería, experimentos y tecnologías para futuras mejoras
```

---

## 🟢 1. Módulos en la Página Web (Manuales de Uso Paso a Paso)

Cada uno de estos apartados está directamente conectado con una pestaña, botón o selector de la interfaz web:

### 🎛️ A. Capacidades Maestras (`docs/capacidades/`)
Manuales de entrada/salida y contratos JSON de las 14 capacidades formales del pipeline:
- [`01_llm_script_semantic_director`](file:///docs/capacidades/01_llm_script_semantic_director/): Guion, escaleta y dirección semántica.
- [`02_google_flow_playwright_web_4k`](file:///docs/capacidades/02_google_flow_playwright_web_4k/): Generación de vídeo 4K en Google Flow vía Playwright.
- [`03_flux3_serverless_zerogpu_replicate`](file:///docs/capacidades/03_flux3_serverless_zerogpu_replicate/): Fotogramas 4K y animación con FLUX 3 en Replicate H100 y ZeroGPU.
- [`04_nanobanana_pro_2`](file:///docs/capacidades/04_nanobanana_pro_2/): Keyframing consistente con Gemini 3.1 Flash Image.
- [`05_ltx_2_5_mmdit_22b`](file:///docs/capacidades/05_ltx_2_5_mmdit_22b/): Generación de vídeo nativo 22B MMDiT con audio espacial.
- [`06_stock_scraping_real_pexels_pixabay`](file:///docs/capacidades/06_stock_scraping_real_pexels_pixabay/): Metraje real de archivo y curaduría B-roll.
- [`07_flowmusic_lyria3_via_playwright`](file:///docs/capacidades/07_flowmusic_lyria3_via_playwright/): Música generativa adaptativa Google Lyria 3.
- [`08_vibevoice_1_5b_serverless`](file:///docs/capacidades/08_vibevoice_1_5b_serverless/): Síntesis de voz neuronal ultrarrealista (`es-emilio`).
- [`09_kokoro_hd_tts_foley_ducking`](file:///docs/capacidades/09_kokoro_hd_tts_foley_ducking/): Voz rápida, foley analógico y sidechain ducking.
- [`10_edge_tts_neural_microsoft`](file:///docs/capacidades/10_edge_tts_neural_microsoft/): Locución Microsoft Edge-TTS.
- [`11_ffmpeg_core_moviepy_assembler`](file:///docs/capacidades/11_ffmpeg_core_moviepy_assembler/): Motor de ensamblaje máster, filtros y normalización EBU R128 (-14 LUFS).
- [`12_remotion_engine_react_hyperframes`](file:///docs/capacidades/12_remotion_engine_react_hyperframes/): Gráficos programáticos React Video-as-Code.
- [`13_vox_subtitles_karaoke_highlight`](file:///docs/capacidades/13_vox_subtitles_karaoke_highlight/): Subtitulado cinemático estilo Vox con formato ASS.
- [`14_whisper_stt_word_timestamps`](file:///docs/capacidades/14_whisper_stt_word_timestamps/): Transcripción fonética con timestamps palabra por palabra.
- `schemas/`: Validadores JSON Schema para garantizar la integridad de los datos.

### 🧩 B. Catálogo de Nodos y Motores (`docs/nodos_y_motores/`)
Guías de configuración y credenciales de los 26 motores del registry, clasificados por categorías de Firebase:
- `visual/`: Motores de vídeo e imagen (`01_flux3_...` a `10_scraping_real_ddg_wikimedia/`).
- `music/`: Bandas sonoras y mastering (`01_google_flow_music_lyria_3/`, `02_suno_ai_api_v3_v4/`, `03_foley_director_ducking_master/`).
- `voice/`: Locución y clonación de voz (`01_vibevoice_...` a `06_minimax_speech_01/`).
- `programacion/`: Motores de render por código (`01_ffmpeg_...` a `04_whisper_stt_word_timestamps/`).
- `llm/`: Modelos de lenguaje y dirección (`01_antigravity_bridge_8742/` a `06_siliconflow_hub/`).
- `cloud/`: Infraestructura en la nube (`01_cloudflare_r2_...`, `02_firebase_...`).

### 📺 C. Canales de YouTube (`docs/youtube/mis_canales/`)
Configuración de los canales propios:
- `01_CHRONODRIFT/`: Viajes temporales urbanos 4K.
- `02_TERRAMORPH/`: Transformación geológica y megaestructuras.
- `03_NANOVERSE/`: Exploración microscópica y biológica.
- `04_LIVING_CANVAS/`: Arte viviente e historia cultural.
- `05_ASTRODRIFT/`: Astrofísica y cosmología profunda.

### 🎬 D. Arquetipos de Producción (`docs/workflows/`)
Los 8 flujos de producción preconfigurados en la pestaña "Workflow Studio" (`01_CHRONODRIFT_TRITEMPORAL` a `08_AI_SLOP_PURGE_AND_REMASTER`).

---

## 🔬 2. Laboratorio de Investigación e Ideas (Fuera de la Página Web)

Ubicadas en `docs/investigaciones/`, estas carpetas **no tienen número de serie** porque son estudios avanzados, tratados de ingeniería y bancos de ideas de nuevas tecnologías que todavía no forman parte de los botones de la web:

| Carpeta de Investigación | ¿Qué contiene y para qué sirve? |
| :--- | :--- |
| **`remotion_motion_graphics/`** | Tratados sobre cómo programar motion design en React: físicas de resorte (`spring()`), curvas Bézier, prevención de layout shift con `tabular-nums`, y recetarios de lower-thirds. |
| **`cartografia_tactil_vox/`** | Técnicas para animar mapas 4K al estilo Vox/Johnny Harris: eliminación de fondos con Linear Color Key, rutas punteadas con Dash 78 y solución a colisiones 3D (*Z-fighting*) en DaVinci Resolve Fusion y QGIS. |
| **`texto_3d_tipografia_cinetica/`** | Guías para crear texto tridimensional procedural en Canvas2D, sincronización frame-accurate con `@remotion/three`, y proyección de clips de vídeo en mallas 3D en tiempo real. |
| **`shaders_glsl_webgl_overlays/`** | Catálogo de efectos por GPU en GLSL: degradados orgánicos con Ruido Simplex, transiciones WebGL (`glitch`, `zoomBlur`, `lightLeak`, `whipPan`) y reglas GSAP seguras para render headless. |
| **`ingenieria_acustica_foley_sfx/`** | Ingeniería de sonido analógico: jerarquía psicoacústica de 3 capas, catálogo de texturas grabadas con micrófonos Neumann KM184, sidechain ducking automatizado en FFmpeg a `-22 dB` y micro-crossfade de 30ms anti-chasquidos. |
| **`cinematografia_dop_opticas/`** | Tratados de dirección de fotografía (DoP 7 capas), lentes anamórficas Panavision C-Series, espacio de color ACEScg y cinemática de cámara 6-DoF. |
| **`consistencia_visual_actores/`** | Protocolo de 4 anclas (*Passport, Wardrobe, Rig, World*), matriz radial de 5 vistas y metodología Tail-Frame Flow para consistencia de personajes con IA. |
| **`arquitectura_fpv_tours_urbanos/`** | GeoScraping 6+1, dossier tritemporal de Shibuya 2326 y técnica Freeze 3D con separación de planos de profundidad. |
| **`motores_generativos_benchmarks/`** | Comparativas empíricas de calidad, resolución, latencia y costes por segundo entre FLUX 3, Google Flow, LTX-Video 2.5, Wan 2.1 y Hailuo. |
| **`automatizacion_web_y_playwright/`** | Técnicas de control desatendido con Playwright Stealth CDP, interacción con Shadow DOM y conexión con APIs backend. |
| **`templates/`** | Plantillas estandarizadas para redactar nuevos dossiers de investigación (`RESEARCH_DOSSIER_TEMPLATE.md`, `VISUAL_BIBLE_TEMPLATE.md`). |

---

## 🛠️ Guía para el Desarrollador de la Web

Cuando vayas a crear o modificar una pantalla de la web:
1. **Para implementar un botón o flujo existente:** Consulta el manual correspondiente en `docs/capacidades/` o `docs/nodos_y_motores/` (respetando los números de serie).
2. **Para añadir una nueva funcionalidad o efecto visual/sonoro:** Explora el laboratorio en `docs/investigaciones/`. Allí encontrarás fórmulas matemáticas, código TypeScript/GLSL y comandos FFmpeg ya probados y listos para ser adaptados a tu gusto.
3. **Recuerda:** Úsalo como punto de partida y referencia, con total libertad para innovar.
