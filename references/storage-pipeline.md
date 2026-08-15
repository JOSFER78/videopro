# 📦 PIPELINE DE ALMACENAMIENTO Y CICLO DE VIDA DE PROYECTO (VIDEO PRO)

Este documento define el **estándar arquitectónico obligatorio** para la organización de archivos, gestión del almacenamiento, trazabilidad y ciclo de vida de los proyectos de vídeo en la skill `videopro` de Hermes Agent.

---

## 🎯 1. FILOSOFÍA Y PRINCIPIOS DE DISEÑO

1. **Determinismo e Inmutabilidad**: Cada ejecución de proyecto reside en una ruta única, versionada e independiente (`v1/`, `v2/`). Los activos generados no se sobreescriben a ciegas.
2. **Jerarquía Cronológica Estricta**: La estructura `projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/` elimina colisiones de nombres y permite una navegación y archivado predecibles.
3. **Cero Mocks / Cero Placeholders**: Ningún archivo corrupto, vacío o simulado (< 5 KB) puede ser consumido por el renderizador. Cualquier anomalía aborta el pipeline con `Exit Code 2`.
4. **Trazabilidad por Manifiesto (`project_manifest.json`)**: El estado del proyecto, los hashes de los activos y los metadatos de render se auditan en un manifiesto central unificado.
5. **Separación Clara entre Activos Inmutables y Temporales**: Se aíslan los datos fuente y finales de los archivos de caché o renders intermedios susceptibles de purga.

---

## 🏛️ 2. JERARQUÍA CANÓNICA DE DIRECTORIOS

Todo proyecto de vídeo generado por `videopro` debe seguir estrictamente la siguiente topología de carpetas:

```text
projects/
└── YYYY/                                  # Año de producción (ej. 2026)
    └── MM/                                # Mes de producción a 2 dígitos (ej. 08)
        └── YYYY-MM-DD_<project_slug>/     # Raíz del proyecto con fecha y slug único
            └── v1/                        # Versión del proyecto (v1, v2, etc.)
                ├── project_manifest.json  # 📋 Manifiesto JSON con estado, hashes y metadatos
                ├── RESEARCH_DOSSIER.md    # 📚 Dossier factual estilo BBC/PwC (≥2 fuentes por dato)
                ├── scenes.json            # 🎬 Definición maestra del timeline y desglose de 7 planos
                ├── vo_durations.json      # ⏱️ Timestamps exactos de locución extraídos con Whisper
                ├── assets/                # 🖼️ Banco de activos reales verificados (> 5 KB)
                │   ├── photos/            # Fotografías 4K (Nano Banana Pro / Wikimedia)
                │   ├── cutouts/           # Stickers PNG 2.5D con canal alfa (rembg)
                │   ├── broll/             # Clips de vídeo 10s (Gemini Omni Flash)
                │   ├── logos/             # Vectores limpios SVG (SimpleIcons)
                │   └── audio/             # Recursos de sonido
                │       ├── narration.mp3  # Locución principal TTS (Edge-TTS)
                │       ├── narration.vtt  # Subtítulos brutos VTT
                │       ├── bgm/           # Pistas musicales de fondo (Suno / HeartMuLa)
                │       └── sfx/           # Efectos Foley diegéticos (papel, tecleo, obturador)
                ├── scene_data/            # 🧩 JSONs modulares y estados intermedios por escena
                ├── src/                   # 💻 Código de composición (Remotion .tsx / HyperFrames HTML)
                └── out/                   # 📦 Salida final y entregables
                    ├── final.mp4          # Vídeo final H.264 (<50 MB comprimido para Telegram)
                    └── qa_report.json     # Reporte de control de calidad multimodal
```

---

## 📋 3. DESCRIPCIÓN DETALLADA DE ARCHIVOS Y SU FUNCIÓN

| Archivo / Directorio | Formato | Propósito y Contenido |
| :--- | :--- | :--- |
| `project_manifest.json` | JSON | Registro maestro del ciclo de vida, progreso de fases, especificaciones de motores, lista de activos con checksums y estado de entrega. |
| `RESEARCH_DOSSIER.md` | Markdown | Documento de investigación factual estructurado en 3 actos (Hook 0-15%, Desarrollo 15-75%, Síntesis 75-100%) con validación cruzada (≥2 fuentes independientes). |
| `scenes.json` | JSON | Declaración formal de escenas, duración de planos (mínimo 7 tomas cinemáticas por bloque temático), prompts visuales, texto VO y triggers de efectos. |
| `vo_durations.json` | JSON | Marcas de tiempo milimétricas a nivel de palabra extraídas con Whisper Stable-TS para sincronización y karaoke. |
| `assets/photos/` | JPG / PNG | Imágenes base fotorrealistas generadas con Nano Banana Pro (`gemini-3.1-flash-image`) o descargadas de repositorios verificados. |
| `assets/cutouts/` | PNG (RGBA) | Gráficos recortados con canal alfa transparente generados localmente mediante `rembg`. |
| `assets/broll/` | MP4 1080p | Clips cinemáticos generados con Gemini Omni Flash (`--engine omni_flash`) en tomas continuas de 10s. |
| `assets/logos/` | SVG | Iconografía y logotipos vectoriales de marcas/tecnologías. |
| `assets/audio/` | MP3 / WAV | Locución TTS normalizada, música BGM ecualizada y librería Foley para micro-animaciones. |
| `scene_data/` | JSON | Configuraciones parciales por escena para renderizado distribuido o paralelo. |
| `src/` | TSX / HTML | Composiciones programáticas de Remotion (`src/generated/Composition.tsx`) o HyperFrames. |
| `out/final.mp4` | MP4 | Vídeo máster final codificado en H.264 CRF 28 con audio AAC 96k, verificado < 50MB. |
| `out/qa_report.json` | JSON | Dictamen de control de calidad automático (FFprobe, duración, ausencia de fotogramas negros corruptos). |

---

## 🔄 4. CICLO DE VIDA DEL PROYECTO (7 FASES OBLIGATORIAS)

```text
[Fase 1: Bootstrap & Manifest] 
       │
       ▼
[Fase 2: BBC Research & 7-Shot Storyboard] 
       │
       ▼
[Fase 3: Asset Acquisition & Validation Gate (>5KB)] 
       │
       ▼
[Fase 4: Audio Engineering, VO-First & Whisper Timestamps] 
       │
       ▼
[Fase 5: Programmatic Render & Composition] 
       │
       ▼
[Fase 6: Multimodal QA & Telegram Compression (<50MB)] 
       │
       ▼
[Fase 7: Telegram Delivery & Storage Archiving]
```

### Fase 1: Inicialización y Bootstrap (Storage Provisioning)
- **Comando**: `python3 project_manager.py create "<Título del Proyecto>"`
- **Acciones**:
  1. Calcula la fecha actual (`YYYY/MM/YYYY-MM-DD_<slug>`).
  2. Crea la estructura completa de subdirectorios bajo `v1/`.
  3. Instancia `project_manifest.json` desde `templates/project-manifest.json` con metadatos iniciales y fase 1 completada.

### Fase 2: Investigación BBC y Storyboard de 7 Planos
- **Comando**: `python3 creative_director.py --topic "<Tema>" --style vox_documentary --duration 45 --language es`
- **Acciones**:
  1. Realiza investigación factual rigurosa con fuentes primarias.
  2. Genera `RESEARCH_DOSSIER.md` documentando fuentes y afirmaciones verificadas.
  3. Genera `scenes.json` descomponiendo cada escena en **al menos 7 planos cinemáticos** (Establishing, Action, Medium, POV, Close-up, Macro Telemetry, Panoramic Reveal).
  4. Actualiza `project_manifest.json` con el recuento de fuentes y planos.

### Fase 3: Adquisición y Generación de Activos (Asset Ingestion)
- **Comando**: `python3 fetch_media.py --plan projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/scenes.json`
- **Acciones**:
  1. Genera o descarga fotos en `assets/photos/` usando Nano Banana Pro.
  2. Genera clips B-roll de 10s en `assets/broll/` usando Gemini Omni Flash.
  3. Procesa recortables transparentes en `assets/cutouts/` con `rembg`.
  4. Descarga logos vectoriales en `assets/logos/`.
  5. **Gate de Validación**: Ejecuta `scripts/verify-assets.py`. Si cualquier activo mide < 5 KB o está corrupto, aborta inmediatamente con `Exit Code 2`.
  6. Registra cada activo en el array `assets_manifest` de `project_manifest.json`.

### Fase 4: Ingeniería de Audio y Sincronización VO-First
- **Comandos**:
  ```bash
  python3 gen_vo.py --plan projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/scenes.json
  python3 gen_captions.py --plan projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/scenes.json
  ```
- **Acciones**:
  1. Genera `assets/audio/narration.mp3` con Edge-TTS.
  2. Extrae marcas temporales precisas palabra por palabra con Whisper Stable-TS a `vo_durations.json`.
  3. Configura BGM con ducking automático (-18 dB / -22 dB durante voz) y posiciona Foley diegético.
  4. Ajusta dinámicamente las duraciones visuales de `scenes.json` a la duración real del audio.

### Fase 5: Renderizado y Composición Programática
- **Comando**: `python3 render_from_plan.py --plan projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/scenes.json`
- **Acciones**:
  1. Valida `scenes.json` y assets requeridos.
  2. Ensambla la composición mediante MoviePy 2.x, Remotion (`src/generated/Composition.tsx`) o HyperFrames.
  3. Aplica fondo industrial anti-blackdetect (`RGB (36,48,72)`).
  4. Genera `out/final.mp4`.

### Fase 6: Control de Calidad (QA Gate) y Compresión
- **Comandos**:
  ```bash
  python3 qa_check.py --file projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/out/final.mp4
  ```
- **Acciones**:
  1. Inspecciona streams con `ffprobe` (duración, resolución, bitrate, audio sync).
  2. Ejecuta verificación multimodal con `video_analyze`.
  3. Si el archivo supera 50 MB, aplica compresión estándar:
     ```bash
     ffmpeg -i in.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k out/final.mp4
     ```
  4. Escribe `out/qa_report.json` y actualiza `project_manifest.json`.

### Fase 7: Entrega, Notificación y Archivado
- **Comando**: `python3 notify_telegram.py --file projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/out/final.mp4 --caption "🍿 Documental listo!"`
- **Acciones**:
  1. Sube el MP4 al canal o chat configurado de Telegram.
  2. Marca `phase_7_qa_and_delivery` como `completed` en `project_manifest.json`.
  3. Purga cachés temporales prescindibles manteniendo inmutables los activos de `assets/` y el máster `out/final.mp4`.

---

## 🧹 5. POLÍTICAS DE GESTIÓN DE ALMACENAMIENTO Y LIMPIEZA

1. **Archivos Inmutables (NUNCA BORRAR)**:
   - `project_manifest.json`
   - `RESEARCH_DOSSIER.md`
   - `scenes.json` y `vo_durations.json`
   - `assets/**/*` (todos los activos brutos verificados)
   - `out/final.mp4` y `out/qa_report.json`
2. **Archivos Temporales Purgables**:
   - `tmp/*`, frames intermedios PNG extraídos durante QA.
   - Archivos parciales `.tmp`, fragmentos de audio sin normalizar.
   - Caché de renderizado de Remotion (`.remotion-cache`).
3. **Control de Versiones del Proyecto**:
   - Si un proyecto requiere una reelaboración profunda o nuevo render tras cambios mayores de guión, se crea una nueva carpeta `v2/` dentro del mismo directorio de proyecto `projects/YYYY/MM/YYYY-MM-DD_<slug>/v2/`, preservando intacto `v1/` para auditoría comparativa.

---

## 🛡️ 6. GATE DE INTEGRIDAD Y PREVENCIÓN DE ERRORES

- **Regla del Tamaño Mínimo (> 5 KB)**: Todo asset menor a 5.120 bytes es rechazado inmediatamente.
- **Validación de Integridad de Audio**: El timeline visual no puede discrepar más de 100ms de la duración total del audio locutado.
- **Verificación de Códecs**: El contenedor final debe ser MP4 con stream de vídeo H.264 y stream de audio AAC a 44.1kHz / 48kHz.
