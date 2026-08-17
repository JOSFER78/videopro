# Workflow de Canales Automatizados de YouTube con VideoPro (Anti-AI Slop)

## 1. Principios de Retención y Valor Añadido
- **Grounding Fáctico y Multi-Ángulo:** Uso de imágenes reales de Street View en 6 ángulos canónicos (0°, 90°, 180°, 270°, picado -20°, contrapicado +25°) combinadas con polígonos 3D de OpenStreetMap para anclar la geometría y evitar alucinaciones espaciales.
- **Narrativa Tritemporal con Match-Cut:** Evolución temporal continua en el mismo eje de cámara (Pasado histórico ~1626, Presente real ~2026, Futuro proyectado ~2226 con base científica del IPCC/MIT).
- **Shotlist Canónico de 7 Planos FPV:**
  1. `01_TERMINAL_DIVE` (0-3s): Picado vertical a alta velocidad (hook visual).
  2. `02_CANYON_DRIFT` (3-10s): Vuelo rasante entre rascacielos con telemetría HUD.
  3. `03_TUNNEL_PIERCE` (10-18s): Entrada a pasajes estrechos o callejones con foley diegético.
  4. `04_MONUMENT_ORBIT` (18-25s): Órbita 360° en torno a hitos con rótulos 3D flotantes.
  5. `05_PEDESTRIAN_SWOOP` (25-32s): Vuelo a ras de suelo a escala humana.
  6. `06_VERTICAL_SURGE` (32-38s): Ascenso en espiral por fachadas de torres.
  7. `07_SKYLINE_SUNSET_ASCENSION` (38-45s): Revelación panorámica final.

## 2. Pipeline de Generación con Gemini Omni Flash
- **Motor:** `gemini-omni-flash-preview` en Google Flow (descartando expresamente Veo 3).
- **Keyframing:** 7 keyframes consistentes por plano generados con Nano Banana Pro para fijar iluminación, arquitectura y física aerodinámica de 6 ejes.
- **Audio:** Sincronización VO-First con Whisper, BGM Flow Chillhop a 118 BPM, ducking dinámico a -18 dB durante la voz y masterización EBU R128 a -14 LUFS.

## 3. Estructura Estándar de Proyectos de Canal en `docs/investigaciones/youtube/`
Cada canal automatizado debe estructurarse con 8 entregables estándar:
1. `01_naming_branding_y_estudio_demanda_marketing.md` (Auditoría fonética, SEO y psicología).
2. `02_investigacion_nicho_y_audiencia.md` (Público objetivo, curva de retención y modo dual).
3. `03_workflow_tecnico_videopro.md` (Pipeline de render y keyframing).
4. `04_plan_comercial_y_monetizacion.md` (RPMs Tier-1, sponsors y productos 8K).
5. `05_plan_marketing_y_crecimiento.md` (Ruta 0-100k y Shorts con VTR >120%).
6. `06_branding_diseno_y_miniaturas.md` (Regla de 3 elementos para CTR >14%).
7. `07_escaleta_10_primeros_episodios.md` (Guiones y shotlists listos para producción).
8. `channel_config.json` (Manifiesto de configuración consumible por VideoPro).
