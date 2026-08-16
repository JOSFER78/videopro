# 📘 NODO 03: Motor de Ingesta, Scraping y Descarga de Medios 4K

> **Rol del Nodo:** Localizar, filtrar y descargar metraje de vídeo 4K en movimiento real y fotos de archivo de alta definición.

---

## 🎯 Reglas Operativas Estrictas:

1. **Variedad Cinemática de Planos (3 a 5 planos por curiosidad):**
   * Plano General Aéreo (Dron establishing shot).
   * Aproximación Dinámica (FPV dive / Speed ramp).
   * Plano Detalle / Macro (Mosaicos, engranajes, compuertas, ladrillo).
   * Panorámica de seguimiento en rotación.

2. **Control de Calidad y Filtro Laplaciano:**
   * Descarte automático de archivos < 1080p, con marcas de agua o borrosos (varianza laplaciana > 120).
   * Priorizar metraje en 60 FPS o 4K nativo.

3. **Cero Fotogramas Congelados:**
   * Si se utiliza una fotografía de archivo histórico, debe aplicarse **Ken Burns cinemático 3D continuo** (zoom progresivo del 1.0x al 1.25x o paneo diagonal).
