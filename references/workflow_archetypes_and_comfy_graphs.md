# 🎬 CATÁLOGO MAESTRO DE ARQUETIPOS DE PRODUCCIÓN & GRAFOS MODULARES

Fuente de Verdad extraída de `app/core/orchestration/workflow_archetypes.py` y `docs/03_workflows_produccion/` en VideoPro (`/home/ubuntu/workspace/pro/hermes/10_videopro`).

---

## 🏛️ 1. ARQUETIPO: VOX & JOHNNY HARRIS INVESTIGATIVE JOURNALISM

- **ID:** `vox_investigative_journalism` | **Relación de Aspecto:** `16:9` / `9:16`
- **Estrategia Visual:** `HYBRID` (Documentos históricos + Mapas 3D + Motion Graphics 2.5D + Metraje Real)
- **Voz Recomendada:** `vibevoice` / `es-ES-AlvaroNeural` (tono periodístico serio y analítico)
- **Música:** Minimalist cinematic / Acoustic tension (pianos oscuros, texturas analógicas)
- **Grafo de Nodos de Producción:**
  1. `node_01_guion_investigacion`: Dossier factual con ≥2 fuentes por dato y desglose en 3 actos.
  2. `node_02_locucion_whisper`: Generación de voz neutra y alineación de marcas de tiempo milimétricas.
  3. `node_03_cartografia_tactil_qgis`: Renderizado de mapas 4K, capas de relieve DEM y rutas con trazo punteado `dash78`.
  4. `node_04_documentos_homografia_3d`: Superposición de patentes/periódicos con homografía de perspectiva 3D, rotación física de ±2.5° y resaltador flúor.
  5. `node_05_foley_diegético`: Mezcla de ruidos de papel, máquina de escribir, obturadores analógicos y golpes de sello.
  6. `node_06_master_render_ffmpeg`: Ducking de audio (-20 dB), crossfade de 30ms y codificación ProRes/H.264.

---

## 🧸 2. ARQUETIPO: PIXAR 3D STORYTELLING & CHARACTER ANIMATION

- **ID:** `pixar_3d_animation` | **Relación de Aspecto:** `16:9` / `9:16`
- **Estrategia Visual:** `AI_GENERATED` (Render 3D CGI fotorrealista)
- **Motor Óptico:** Gemini Omni Flash (`gemini-omni-flash-preview`) / Nano Banana Pro (`gemini-3.1-flash-image`)
- **Voz:** Expresiva, cálida y dinámica (`es-ES-ElviraNeural` / `es-MX-JorgeNeural`)
- **Estilo Prompts:** `Subsurface Scattering, Anamorphic 35mm f/1.8, Volumetric Rim Light, Octane Render 3D Pixar Style`.
- **Grafo de Nodos:**
  1. `node_character_sheet`: Definición de consistencia facial, paleta y accesorios del personaje.
  2. `node_storyboard_3d`: 7 planos cinemáticos por secuencia con progresión emocional.
  3. `node_omni_flash_animation`: Generación de tomas continuas de 10s con física de ropa y pelo.
  4. `node_orchestral_score`: Banda sonora orquestal con instrumentación emotiva.

---

## 🏙️ 3. ARQUETIPO: CHRONODRIFT 6-DoF URBAN TIME TRAVEL

- **ID:** `chronodrift_urban_6dof` | **Relación de Aspecto:** `16:9` (4K 60fps)
- **Estrategia Visual:** Vuelo FPV continuo a través de 3 épocas (1626 ➔ 2026 ➔ 2226) sin cortes.
- **Ingesta:** 6 perspectivas ortogonales canónicas (`CAM_N`, `CAM_E`, `CAM_S`, `CAM_W`, `CAM_PITCH_DOWN`, `CAM_PITCH_UP`) + Malla OSM 3D Overpass.
- **Shotlist Maestro (42s):**
  - `01_TERMINAL_DIVE` (0-6s, 850m ➔ 140 km/h)
  - `02_CANYON_DRIFT` (6-12s, rasante urbano a 110 km/h)
  - `03_TUNNEL_PIERCE` (12-18s, match-cut temporal)
  - `04_MONUMENT_ORBIT` (18-24s, órbita 360°)
  - `05_PEDESTRIAN_SWOOP` (24-30s, 1.5m AGL)
  - `06_VERTICAL_SURGE` (30-36s, trepada supersónica 300m)
  - `07_SKYLINE_SUNSET` (36-42s, gran angular panorámico)

---

## 🌍 4. ARQUETIPO: BBC / NATGEO FACTUAL 4K NATURE & SCIENCE

- **ID:** `bbc_natgeo_factual` | **Relación de Aspecto:** `16:9`
- **Estrategia Visual:** Tomas macro de alta velocidad, telemetría científica HUD y planos panorámicos ARRI Alexa LF.
- **Paleta y Grano:** Kodak Vision3 500T 5219, iluminación volumétrica real, desenfoque óptico natural.
- **Audio:** Paisaje sonoro biaural, captación ambiente hiperrealista y locución serena y autorizada.

---

## ⚡ 5. ARQUETIPO: VIRAL SHORTS / REELS HIGH-RETENTION

- **ID:** `viral_shorts_high_retention` | **Relación de Aspecto:** `9:16` Vertical (1080x1920)
- **Estrategia Visual:** Retención agresiva con hook visual en los primeros 1.5 segundos.
- **Reglas Críticas:**
  - Cambio visual o zoom dinámico cada 2-3 segundos.
  - Subtítulos karaoke amarillos al centro (75% altura para no tapar UI).
  - Efectos de sonido punchy en cada palabra clave o transición.
  - Duración óptima: 30 a 55 segundos con bucle perfecto (*seamless loop*).
