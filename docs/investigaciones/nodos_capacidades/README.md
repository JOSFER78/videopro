# 📋 Biblioteca Maestra de Capacidades, Infraestructura y Proveedores de VideoPro

> **Índice Rápido:** Consulta [`00_INDICE_CAPACIDADES.md`](00_INDICE_CAPACIDADES.md) para el catálogo completo con enlaces directos a todas las guías maestras.

Este directorio almacena la investigación exhaustiva, taxonomía técnica oficial y matriz interactiva tipo Excel de todos los motores, infraestructuras reales, comportamientos y preferencias de calidad de **VideoPro**.

---

## 📁 Estructura del Directorio de Capacidades

```bash
docs/investigaciones/nodos_capacidades/
├── 00_INDICE_CAPACIDADES.md                         # Índice y mapa completo de capacidades
├── README.md                                        # Este documento
├── capacidades_maestras.md                          # Catálogo técnico de infraestructura verificada
├── proveedores_excel.html                           # Matriz interactiva editable tipo Excel
├── workflow_designer_studio.html                    # Diseñador visual de nodos y grafos
├── comfy_pipeline_studio.html                       # Estudio interactivo de pipeline Comfy
├── flux3/                                           # Módulo FLUX 3 (Black Forest Labs)
│   ├── 00_INDICE_FLUX3.md
│   ├── 01_guia_maestra_operativa_flux3.md
│   ├── 02_benchmark_google-flow-web_vs_flux3.md
│   ├── 08_guia_maestra_flux3_upscale_cpu.md
│   └── 09_metodologia_anti_cgi_y_consistencia_facial.md
├── google-flow-web/                                     # Módulo Google Flow & Gemini Omni Flash
│   └── 01_guia_maestra_google-flow-web_web_y_cdp.md
├── flowmusic-via-playwright/                                      # Módulo Flow Music & Audio 3D / ASMR
│   ├── 00_plan_maestro_flowmusic-via-playwright.md
│   ├── 03_automatizacion_autonoma_playwright_cdp.md
│   ├── 04_estrategia_quema_creditos_y_lotes_flowmusic.md
│   ├── bso_larga_duracion/
│   ├── efectos_neurales_mhz_3d_asmr/
│   ├── mastering_cascos_lujo/
│   ├── prompts/
│   └── templates/
├── ltx-video-2-5/                                       # Módulo LTX-2.5 MMDiT 22B Multimodal
│   └── 01_guia_maestra_ltx-video-2-5_2_5.md
└── kokoro-tts-foley/                              # Módulo Kokoro HD TTS & Foley Director
    └── 01_guia_maestra_kokoro_y_foley_director.md
```

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
