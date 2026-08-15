# IDEA — VideoPro Studio (Estudio Cinematográfico Híbrido Autónomo)

## Propósito
Transformar ideas y guiones en producciones audiovisuales cinematográficas completas de forma 100% autónoma en VPS, combinando:
- Inferencia de voz ultra-realista local sin coste de API (VibeVoice 1.5B en español).
- Generación de escenas multimodal de 3 vías: Stock Footage local/Pexels, Keyframes 35mm fotorrealistas con FLUX.1 y síntesis de vídeo IA mediante automatización desatendida en Google Flow (Gemini Omni Flash) vía Playwright/CDP.
- Postproducción automática con MoviePy y FFmpeg (ducking musical, subtítulos dinámicos palabra por palabra y transiciones).

## Principios de Diseño
1. **Calidad de Estudio a Coste Cero de Inferencia Externa:** Uso exhaustivo de modelos open-source y pipelines locales (`es-emilio`, Whisper, FLUX, FFmpeg).
2. **Modularidad Multimodal:** Cada escena elige la mejor vía de producción según el contexto narrativo (archivo real vs plano macroscópico vs animación generativa).
3. **Consistencia Visual Férrea:** Inyección de fotograma de referencia e identidad visual (35mm Kodak Vision3) a lo largo de todas las tomas.
