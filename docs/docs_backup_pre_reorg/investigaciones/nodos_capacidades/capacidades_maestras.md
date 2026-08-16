# 📋 Investigación de Capacidades Maestras, Infraestructura y Proveedores de VideoPro

Este directorio almacena la investigación exhaustiva, taxonomía técnica oficial y matriz interactiva tipo Excel de todos los motores, infraestructuras reales, comportamientos y preferencias de calidad de **VideoPro**.

---

## 📁 Archivos Incluidos

1. **`proveedores_excel.html`**:
   - Hoja de cálculo interactiva editable con sticky headers, casillas atómicas de selección, asistente de IA (Gemini 3.7 / Bridge 8742), comprobador en tiempo real de puertos y exportador a Markdown.
2. **`capacidades_maestras.md`**:
   - Catálogo técnico de todos los motores verificados (FLUX 3, LTX-2.5, Google Flow, Google Flow Music, Kokoro HD, NanoBanana Pro 2, Cloudflare R2, DuckDuckGo/Wikimedia, Paneles Vox, Foley Director, TwelveLabs, Subtítulos ASS).

---

## 🎯 Taxonomía de Motores e Infraestructuras Reales Verificadas

| Proveedor / Sistema | Infraestructura Real | Preferencias de Calidad | Reglas de Descarte |
| :--- | :--- | :--- | :--- |
| **FLUX 3 Video** | GPU Gratis (ZeroGPU) / GPU Pago (Replicate H100) | 1080p/4K nativo a 24fps (9:16 y 16:9) | 🚫 Descartar 480p / 720p bajo bitrate |
| **LTX-2.5 MMDiT (22B)** | GPU Gratis (ZeroGPU) / GPU Pago (Replicate H100) | Audio máster 48kHz WAV + Lip-sync 24fps | 🚫 Descartar audio 16kHz / 480p |
| **Google Flow** | Navegador Web (Playwright flow.google.com) | Vídeo cinemático 1080p/4K | 🚫 Descartar < 1080p |
| **Google Flow Music (Lyria 3)** | Navegador Web (Playwright flowmusic.app) | Pista máster 48kHz WAV | 🚫 Descartar MP3 < 128kbps |
| **Cloudflare R2 Storage** | Cloudflare R2 API (S3 Boto3 - Zero Egress) | Masters 1080p/4K con Presigned URLs (15 min) | 🚫 Descartar local > 30 días en VPS |
| **NanoBanana Pro 2 (Imagen 3)** | Antigravity Bridge (8742) / AI Studio | Generar siempre en 2K / 4K | 🚫 Descartar NanoBanana Lite (<1024px) |
| **Kokoro HD (Español)** | CPU Local Servidor ($0 en puerto 7892) | 24kHz High-Fidelity (Dora/Santiago/Alex) | 🚫 Descartar voces 8kHz/16kHz |
| **Foley Director & Ducking** | CPU Local 48kHz WAV + FFmpeg sidechain | 48kHz WAV + Ducking -22dB | 🚫 Descartar SFX sin normalizar |
| **Paneles & Rótulos Vox** | FFmpeg drawbox/drawtext/overlay | Transparencia oscura + acento amarillo Vox | 🚫 Descartar fuentes sin antialiasing |
| **Subtítulos Dinámicos ASS** | CPU Local ASS + Groq Whisper | 1-2 palabras dinámicas (Vox) | 🚫 Descartar textos largos (>4 palabras) |
