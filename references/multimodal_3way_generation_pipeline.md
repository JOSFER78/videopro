# 🎨 Pipeline Multimodal de 3 Vías — VideoPro Studio

## 1. Visión General del Pipeline Multimodal

VideoPro Studio implementa una arquitectura desacoplada de triple vía para la adquisición y síntesis visual por escena, permitiendo seleccionar de forma independiente el motor óptimo según la naturaleza de cada plano dramático o informativo:

```
                               ┌──────────────────────────────────────────────┐
                               │        DIRECTOR CREATIVO MULTIMODAL          │
                               │        (VideoPro Semantic Director)          │
                               └──────────────────────┬───────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         ▼                                            ▼                                            ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     VÍA 1: STOCK & REAL MEDIA   │      │    VÍA 2: FLUX.1 / NANO BANANA  │      │     VÍA 3: GOOGLE FLOW CDP      │
│  (Wikipedia, Commons, GNews)    │      │  (Keyframe 0 + 35mm Kodak RAW)  │      │  (Gemini Omni Flash + Lip-Sync) │
└────────────────┬────────────────┘      └────────────────┬────────────────┘      └────────────────┬────────────────┘
                 │                                        │                                        │
                 ▼                                        ▼                                        ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│ • Wikipedia Summary REST API    │      │ • Nano Banana Pro (4K Invariant)│      │ • Brave/Chromium CDP :9222      │
│ • Wikimedia Commons 8K (CC-BY)  │      │ • FLUX.1 DiT Reference Anchors  │      │ • Headless Canvas / Xvfb :99    │
│ • Google News RSS + OpenGraph   │      │ • Ken Burns 2.5D Synth (FFmpeg) │      │ • <FIRST_FRAME> + Ref Injection │
│ • DuckDuckGo HTML Fallback      │      │ • Kodak Vision3 500T Grain      │      │ • Native 48kHz Audio + Lip-Sync │
└────────────────┬────────────────┘      └────────────────┬────────────────┘      └────────────────┬────────────────┘
                 │                                        │                                        │
                 └────────────────────────────────────────┼────────────────────────────────────────┘
                                                          │
                                                          ▼
                                       ┌──────────────────────────────────────┐
                                       │   VALIDATION GATE (> 5 KB & PIL)     │
                                       │   Abort on Failure (Exit Code 2)     │
                                       └──────────────────┬───────────────────┘
                                                          │
                                                          ▼
                                       ┌──────────────────────────────────────┐
                                       │    CINEMATIC FFmpeg / REMOTION       │
                                       │    (Sidechain Ducking + ASS Karaoke) │
                                       └──────────────────────────────────────┘
```

---

## 2. Vía 1: Stock DB & Ingesta de Medios Reales (Cero Mocks)

### Fuentes de Datos y Estrategia Multiorigen:
1. **Wikipedia Summary REST API**:
   - Extracción de retratos y entidades canónicas verificadas (`originalimage` o `thumbnail`).
   - Endpoint: `https://es.wikipedia.org/api/rest_v1/page/summary/{entity}`
2. **Wikimedia Commons API**:
   - Búsqueda en namespace 6 (`File:`) para edificios, arquitectura histórica, mapas antiguos y documentos desclasificados.
   - Endpoint: `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6`
3. **Google News RSS + OpenGraph Scraper**:
   - Extracción en tiempo real de noticias de última hora y raspado de metadatos `og:image` y `twitter:image`.
4. **DuckDuckGo HTML Scraper**:
   - Rastreo web ligero y rescate de imágenes de archivo sin API keys.

### Reglas de Validación de Medios Reales:
- **Cabecera Institucional Obligatoria**: `User-Agent: VideoPro/4.0 (HermesBot; research-archivist)` para prevenir bloqueos HTTP 403 Forbidden.
- **Validación Fisiológica PIL**: Todo archivo se verifica con `Image.open(file).verify()`, asegurando resolución mínima de $400 \times 300\text{ px}$ y tamaño $> 1000\text{ bytes}$.
- **Coste y Latencia**: $0.00 USD, inferencia $< 1.2\text{ s}$.

---

## 3. Vía 2: FLUX.1 & Nano Banana Pro (Keyframe 0 + 35mm Kodak RAW)

### Principio de Anclaje Visual (Keyframe 0):
- Para mantener la consistencia física de personajes, vehículos y localizaciones complejas sin mutaciones (*character drift*), se genera primero una imagen ancla maestra 4K utilizando **Nano Banana Pro** (`gemini-3.1-flash-image` / `--model nanobanana`) o **FLUX 1.1 Pro**.

### Síntesis Cinemática 2.5D con Muestreo Subpíxel:
- Conversión matemática del fotograma fijo en vídeo MP4 a 24/60 fps mediante `ffmpeg zoompan` subpíxel y superposición de grano de película analógico:

```bash
ffmpeg -y -loop 1 -i keyframe_0.png -t 5.0 \
  -filter_complex "\
    [0:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,\
    zoompan=z='min(1.0+0.0012*on,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30,\
    noise=alls=8:allf=t+u,\
    format=yuv420p[v_out]" \
  -map "[v_out]" -c:v libx264 -crf 18 -preset medium master_scene_2.5d.mp4
```

### Paleta y Óptica Fotorrealista:
- Óptica prime simulada: 35mm anamórfico f/1.8, 50mm f/1.4, 85mm portrait f/1.2.
- Grano cinematográfico: Kodak Vision3 500T 35mm.
- Colorimetría: ARRI Alexa LF Log-C con contraste suave y negros con elevación industrial `#243048`.

---

## 4. Vía 3: Google Flow CDP / Playwright (Gemini Omni Flash)

### Automatización Desatendida en VPS:
- Conexión vía Chrome DevTools Protocol (`http://localhost:9222`) sobre display virtual `Xvfb :99`.
- Inyección directa del Keyframe 0 en el slot de `@ingredientes` de Google Flow.

### Sintaxis Oficial Omni Flash:
- `<FIRST_FRAME>` = Imagen de partida exacta en $t=0$.
- `<IMAGE_REF_0>` … `<IMAGE_REF_N>` = Referencias de consistencia 3D, estilo y mapa de trayectoria.
- Diálogos hablados lip-sync sincronizados: Encerrar frases habladas entre comillas dobles `""`.
- Sonido ambiental nativo 48kHz: Describir sonidos en el prompt (`Audio: rugido de motores y viento racheado`).

### Prompt Canónico 7D para Google Flow:
```text
[# Sources <FIRST_FRAME>@Image1]
[# References <IMAGE_REF_0>@Image2]

Image1 is the EXACT starting frame: hyperrealistic documentary master shot, 8K resolution.
Chief Geophysicist Dr. Elena Rossi (Character_Bible_01) standing inside a geothermal observation module in Iceland.
Wearing a heavy expedition parka with safety harnesses and polarized visor.
35mm anamorphic prime lens f/1.8, natural volumetric lighting from geothermal steam backlit by low arctic sun.
Visible analog film grain (Kodak Vision3 500T 35mm), ARRI Alexa LF Log-C color science.

Perform ONE continuous 10-second camera shot starting from Image1:
The camera glides past her shoulder in a slow cinematic push-in with authentic spatial parallax, revealing the volcanic caldera steaming in the background.

Audio: Deep subsonic rumble of tectonic activity, howling arctic wind, and crisp clicks of telemetry equipment.
Dialogue: "Los sensores detectan una anomalía térmica a tres kilómetros."

No cuts. No plastic skin. No CGI bloom. No morphing.
```

### Fallback Automático:
Si la sesión de Google Flow experimenta saturación o latencia de red, el orquestador conmuta automáticamente a **Vía 2 (FLUX Keyframe 0 + Ken Burns 2.5D)**, garantizando que el pipeline de render nunca se detenga.
