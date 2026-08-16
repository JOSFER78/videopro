# Google Flow: Límites, Coherencia Visual Netflix y Pipeline Multi-Clip

Fuente de verdad para la producción en **Google Flow** con **Gemini Omni Flash** (`gemini-omni-flash-preview`).

---

## 1. Límites Operativos y Capacidades de Google Flow

| Parámetro | Límite Oficial | Práctica Recomendada |
| :--- | :--- | :--- |
| **Duración por Clip** | **10 segundos** máximo por generación | Dividir narrativas largas en clips de 8–10s concatenados |
| **Imágenes de Referencia** | Hasta **7 imágenes** por proyecto/generación | 1 `<FIRST_FRAME>` (apertura) + hasta 6 `<IMAGE_REF_0..5>` (estilo, sujeto, cámara) |
| **Pistas de Audio** | Hasta **3 pistas** de audio por proyecto | 1 locución principal (Voiceover) + 2 pistas Foley / FX / BGM |
| **Resolución & FPS** | 1080p / 24fps–60fps | 16:9 (1920x1080) cinemático o 9:16 vertical |
| **Modelo de Vídeo** | Gemini Omni Flash | `--engine omni_flash` |

---

## 2. Estrategia de Coherencia Visual "Estilo Netflix" (Pre-Generación)

Para evitar que los personajes, atmósferas y arquitecturas muten entre clip y clip:

### Paso 1: Generación de Fotogramas Clave Ancla (Keyframes)
- **NUNCA** arrancar la generación de vídeo desde texto puro si se requiere alta fidelidad.
- Generar primero las **7 imágenes ancla hiperrealistas** (usando Nano Banana Pro / `gemini-3.1-flash-image`):
  - **Mismo estilo de lente:** (ej. *35mm anamorphic lens, shallow depth of field, subtle film grain, cinematic volumetric lighting*).
  - **Misma paleta cromática:** (ej. paleta Marte 2200: óxido rojizo `#8B2500`, ámbar industrial `#FF8C00`, titanio pulido `#4A5568`, luz solar difusa tenue).
  - **Mismo sujeto/arquitectura:** Vistas multi-ángulo del mismo hábitat o personaje con vestimenta idéntica.

### Paso 2: Inyección de Roles en el Prompt Omni Flash
```text
[# Sources <FIRST_FRAME>@Image1]
[# References <IMAGE_REF_0>@Image2 <IMAGE_REF_1>@Image3 <IMAGE_REF_2>@Image4]

Image1 is the EXACT starting frame: hyperrealistic documentary footage, 4K Netflix production quality...
Image2 is the CHARACTER ANCHOR: same astronaut suit, identical helmet reflection...
Image3 is the ENVIRONMENT REFERENCE: same underground lava tube habitat with aeroponic towers...

Perform ONE continuous 10-second camera shot starting from Image1...
```

---

## 3. Ensamblado de Documentales de Larga Duración (60s – 90s)

Para un documental de **90 segundos**:
1. **Storyboard Modular:** 9 escenas × ~10 segundos = 90s.
2. **Encadenamiento (Continuation):**
   - Clip 1 (0–10s): Generado con `Image1` (`<FIRST_FRAME>`) + Refs.
   - Clip 2 (10–20s): Extraer el último fotograma del Clip 1 con FFmpeg (`ffmpeg -sseof -1 -i clip1.mp4 -update 1 -q:v 1 last_frame.jpg`) y usarlo como `<FIRST_FRAME>` del Clip 2.
   - Repetir el proceso para los clips 3 a 9 para lograr continuidad física perfecta.
3. **Pista de Audio Maestra:**
   - La locución completa de 90s (generada por servidor de voz local / Edge-TTS) dicta el timeline.
   - FFmpeg o MoviePy ajusta la velocidad/corte de los clips para alinearse con los silencios del guión.

---

## 4. Checklist Pre-Vuelo (Verificación del Entorno)

Antes de lanzar producción, verificar SIEMPRE:
```bash
# 1. Brave CDP en puerto 9222 para Google Flow
ss -tlnp | grep 9222 || echo "ALERTA: Brave CDP 9222 caído"

# 2. Backend de VideoMastery en puerto 9130
curl -s http://127.0.0.1:9130/health || echo "ALERTA: Backend 9130 caído"

# 3. Servidor de voz natural / Edge-TTS
which edge-tts && echo "Edge-TTS OK"
```
