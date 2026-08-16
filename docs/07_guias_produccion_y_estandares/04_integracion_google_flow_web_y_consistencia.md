# 🎬 INTEGRACIÓN MAESTRA: GOOGLE FLOW WEB + PLAYWRIGHT + VIDEOPRO
### *Generación de Referencias Fotográficas, Prompts Cinematográficos y Control de Consistencia Visual*

---

## 1. 🎯 DIAGNÓSTICO DEL PERFIL OPERATIVO Y DESAFÍO TÉCNICO

El entorno de producción de **videopro** cuenta con una ventaja competitiva determinante: **acceso a Google Flow con créditos Gemini Ultra** (con su capacidad de generar vídeo con **lip-sync nativo** y **foley/audio estéreo físico a 48kHz**), pero con una restricción operativa clara: **no existe API REST pública**; el motor opera **exclusivamente vía interfaz web**.

### La Ley Fundamental del Vídeo con IA
> **El vídeo no se crea desde la nada; se anima a partir de una verdad visual ya fijada.**  
> Pedirle a Google Flow que "invente" al personaje o la escena en cada plano mediante un prompt de texto aislado genera *face drift*, deformaciones de vestuario e inconsistencia espacial.  
> **El 90% del éxito en el vídeo depende de la foto maestra inyectada como referencia (Keyframe 0 / Ingrediente).**

---

## 2. 🏗️ ARQUITECTURA DE LA TUBERÍA INTEGRAL (PIPELINE EN 5 FASES)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   FASE 1: ORQUESTACIÓN Y DIRECCIÓN (Hermes / videopro)                 │
│  - Desglose Factual (Fact Dossier) -> Hechos vs Recreación vs Metáfora Visual          │
│  - Cinematic Interpreter -> Traduce locución a lenguaje de planos y subtexto          │
│  - Compilación de Biblias (Personajes, Locaciones, Atrezzo, Grano de Cámara)           │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              FASE 2: FÁBRICA DE INGREDIENTES Y FOTOS MAESTRAS (Keyframe 0)             │
│  - Generación del Pack de Turnaround del Personaje (Frontal, Perfil, 3/4, Cuerpo)      │
│  - Generación de la Foto Maestra de Inicio para CADA plano de la escena                │
│  - Almacenamiento y registro con hash en VideoStorageManager (assets/keyframes/)       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              FASE 3: RUNNER PLAYWRIGHT / CDP HEADLESS PARA GOOGLE FLOW                 │
│  - Sesión persistente con cookies en Xvfb (Display :99)                                │
│  - Inyección de Foto de Referencia en el Dropzone/Slot de Ingredientes                 │
│  - Selección del Modelo (Gemini Omni Flash / Veo con suscripción Ultra)                │
│  - Inyección del Prompt Dinámico de Animación + Diálogo Lip-Sync                       │
│  - Polling de estado y descarga desatendida del MP4 a storage canónico                │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              FASE 4: AUDITORÍA MULTIMODAL DE CONTINUIDAD (Quality Gate)                │
│  - Extracción de fotogramas clave del clip con FFmpeg                                 │
│  - Validación contra la Biblia Visual: ¿Face Drift < 0.15? ¿Eje de 180° respetado?    │
│  - Veredicto: [APROBADO -> Lock] o [REINTENTO -> Ajuste de Prompt/Semilla en Flow]     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              FASE 5: POSTPRODUCCIÓN Y MASTERIZACIÓN FINAL (videopro)                   │
│  - Ensamblaje en Remotion / MoviePy / FFmpeg concat demuxer                            │
│  - Mezcla BGM con ducking dinámico (-18dB) y masterización a -14 LUFS                  │
│  - Subtitulado cinemático sin ImageMagick (Pillow PIL) y exportación final             │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 📸 LA ESTRATEGIA EN 2 NIVELES: "FOTO PARA VÍDEO" vs "PROMPT DE ANIMACIÓN"

Para lograr consistencia absoluta, separamos la creación en dos capas independientes:

```
                           ┌─────────────────────────────────────────────────┐
                           │            NIVEL 1: FOTO MAESTRA                │
                           │   Fija la IDENTIDAD, TEXTURA y ESPACIO          │
                           │   (DNA del personaje, luz de época, vestuario)  │
                           └────────────────────────┬────────────────────────┘
                                                    │
                                        (Se inyecta como Keyframe 0)
                                                    │
                                                    ▼
                           ┌─────────────────────────────────────────────────┐
                           │        NIVEL 2: PROMPT DE ANIMACIÓN FLOW        │
                           │   Fija el MOVIMIENTO, la CÁMARA y el AUDIO      │
                           │   (Acción física sobria, lente, diálogo)        │
                           └─────────────────────────────────────────────────┘
```

### Nivel 1: Prompt Maestro de Identidad (Generador de Fotos Canónicas)
Fija la apariencia inmutable antes de animar.

```text
[PROMPT FOTO MAESTRA DE IDENTIDAD - PERSONAJE JUAN GARCÍA]
35mm historical documentary still, RAW photo.
SUBJECT: Juan García, 34-year-old Spanish man, sharp defined jawline, light olive skin with realistic weathered texture and subtle pores, wavy dark brown hair parted sideways, prominent straight nose, deep dark brown eyes, a fine faint scar above his left eyebrow.
WARDROBE: Worn heavy wool military jacket in faded drab olive with frayed lapels, beige unbuttoned cotton shirt underneath, period tailor-made brown wool trousers, dark scuffed leather boots.
PERIOD & ENVIRONMENT: Rural Spanish crossroads, early autumn 1944. Soft morning ground mist, dusty gravel road with sparse dry grass.
LIGHTING & ATMOSPHERE: Early morning low golden hour sunlight from screen-left, cast long dramatic shadows, naturalistic atmospheric haze, Kodak Vision3 500T 35mm film grain, ARRI Alexa color science.
NEGATIVE: oversaturated, glossy skin, plastic textures, modern clothes, blur, distorted hands.
```

A partir de este prompt maestro, el sistema genera la **Batería de Ingredientes** que se almacena en el proyecto:
- `01_juan_frontal.png` (Rostro neutro de frente)
- `02_juan_perfil_izq.png` (Perfil estricto)
- `03_juan_3cuartos.png` (Ángulo 3/4 con mirada dramática)
- `04_juan_cuerpo_entero.png` (Proporciones corporales y vestuario completo)
- `05_juan_caminando_espalda.png` (Referencia para planos de seguimiento)
- `06_juan_primer_plano_maleta.png` (Atrezzo de mano: maleta de cuero gastada)

---

### Nivel 2: Prompt Dinámico de Dirección para Google Flow
Este prompt se inyecta en la interfaz web de Google Flow **junto con la foto maestra subida al slot de imagen**. No describe la cara desde cero; describe qué ocurre con esa imagen.

```text
[PROMPT GOOGLE FLOW - TOMA 01: LLEGADA AL PUEBLO]
Animate from input image reference.
ACTION: The man in the wool jacket (Juan) starts walking slowly down the dusty road away from camera toward the distant stone village, gripping the weathered leather suitcase with his right hand. Calm, heavy, measured footsteps.
CAMERA: Smooth low-angle tracking shot following behind him at a constant distance. 35mm anamorphic prime lens, subtle handheld organic camera float, shallow depth of field focusing on the texture of his jacket and swinging suitcase.
LIGHTING: Consistent warm morning backlight filtering through his silhouette, soft lens flare on top-left edge.
AUDIO & DIALOGUE: Subtle crunch of gravel under boots, gentle dry autumn wind blowing through grass, distance crow cawing. No music.
CONTINUITY: Strictly preserve character facial structure, scar over eyebrow, jacket fabric weave, and color palette from the reference image.
```

---

## 4. 🤖 AUTOMATIZACIÓN ROBUSTA DE GOOGLE FLOW VÍA PLAYWRIGHT / CDP

Dado que Google Flow sólo admite acceso web, el script de automatización debe ser infalible frente a recargas, modales y demoras de renderizado:

### Componentes Clave de la Automatización:

```
   playwright_flow_runner.py
   ├── 1. Session Manager       ──> Reutiliza ~/.config/google-flow-session (Cookies + Auth persistente)
   ├── 2. Modal Buster          ──> Cierra popups de "Novedades de Flow", tips o alertas
   ├── 3. Model Selector        ──> Selecciona "Gemini Omni Flash" / "Ultra" mediante selectores dinámicos
   ├── 4. Ingredient Uploader   ──> Inyecta automáticamente el archivo PNG en el <input type="file">
   ├── 5. Prompt & Audio Inject ──> Escribe el prompt dinámico y directivas de diálogo/lip-sync
   ├── 6. Render Waiter         ──> Polling de barra de progreso con timeout de 300s
   └── 7. Canonical Downloader  ──> Descarga el MP4 directamente a scenes/scene_XX/shot_YY.mp4
```

### Patrón de Inyección de Imagen en Playwright (Python):
```python
async def upload_keyframe_ingredient(page, image_path: Path):
    """Sube la imagen maestra al slot de referencia de Google Flow."""
    file_input = page.locator('input[type="file"]').first
    await file_input.set_input_files(str(image_path))
    await page.wait_for_selector('[data-testid="ingredient-thumbnail"], .image-preview', timeout=15000)
    print(f"✅ Ingrediente inyectado con éxito: {image_path.name}")
```

---

## 5. 🔍 SISTEMA DE SEGUIMIENTO DE CONSISTENCIA (CONTINUITY MATRIX)

Para que una escena de 5 planos se perciba como una sola película y no como clips inconexos:

| Regla de Continuidad | Mecanismo de Control en `videopro` | Acción de Corrección Automática |
| :--- | :--- | :--- |
| **Vector de Mirada (Eje 180°)** | El plano N define si el personaje mira a *Screen-Left* o *Screen-Right*. | Si en el plano N-1 miraba a la derecha, el contraplano N debe forzar mirada a la izquierda. |
| **Persistencia de Atrezzo** | Registro de objetos en `Prop Bible` (ej. maleta en mano derecha). | El prompt prohíbe cambiar la mano o que el objeto desaparezca entre cortes. |
| **Coherencia Lumínica** | Registro de la hora solar y temperatura Kelvin en `Location Bible`. | Prohíbe que un plano luzca a mediodía si la escena es al amanecer (5200K vs 3200K). |
| **Fotograma Cola -> Fotograma Cabeza** | En tomas continuas, el último frame del plano N-1 se extrae con FFmpeg y se pasa como imagen inicial del plano N. | Evita saltos de posición o cambio repentino de postura corporal (*jump cuts* involuntarios). |

---

## 6. 🚀 PLAN DE INTEGRACIÓN EN LA SKILL `videopro`

1. **Estructura Canónica del Proyecto:**
   ```bash
   /home/ubuntu/proyectos_video/documental_marte/
   ├── project_manifest.json          # Metadatos, biblia y estado del DAG
   ├── assets/
   │   ├── character_turnarounds/     # Frontal, perfil, 3/4 de cada personaje
   │   ├── keyframes_master/          # Las fotos maestras de inicio de cada plano
   │   └── raw_clips/                 # Vídeos MP4 descargados de Google Flow
   └── rendered/
       └── final_documentary.mp4      # Montaje final masterizado
   ```

2. **Comando Unificado de Producción:**
   Runner maestro `run_documentary_flow.py` que:
   - Lee el dossier de investigación y compila las biblias.
   - Genera/registra las fotos maestras (keyframes).
   - Lanza en segundo plano el worker de Playwright en Xvfb para procesar plano a plano en Google Flow.
   - Audita los fotogramas y ensambla el master final con audio y subtítulos.
