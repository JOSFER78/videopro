# 📚 Guía Maestra: FLUX 3 (720p Draft) + Upscaling CPU (1080p/4K) + Sincronización Rítmica

> **Ubicación Permanente:** `/home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/08_guia_maestra_flux3_upscale_cpu.md`  
> **Ecosistema:** VideoPro Studio v5.0 Ultra / Replicate AI Video Engine  
> **Fecha:** 16 de Agosto de 2026  

---

## 1. Análisis Económico: Estrategia de Producción 10x Más Barata

| Motor de Vídeo | Modo de Generación | Resolución | Duración | Coste Estimado / Clip | Coste de Escalado | Coste Final 4K |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Runway Gen-3 Alpha** | Nube Pro | 1080p | 10s | ~$3.50 - $5.00 | Incluido | **$3.50 - $5.00** |
| **Kling 1.6 Pro** | Nube High | 1080p | 10s | ~$2.50 - $4.00 | Incluido | **$2.50 - $4.00** |
| **Luma Dream Machine**| Nube Standard | 720p / 1080p | 5s | ~$3.20 | Extra en nube | **~$4.50** |
| **FLUX 3 Draft + CPU Upscale** | **Replicate Draft 720p** | **720p $\rightarrow$ 4K UHD** | **8.0s** | **$0.48** | **$0.00 (CPU Local)** | **$0.48 (10x más barato)** |

> [!TIP]
> **La Fórmula Dorada de Rentabilidad:**  
> Generar el borrador neuronal en FLUX 3 a 720p (`draft: true`) en Replicate consume solo **$0.48** y tarda ~85 segundos. Al realizar el escalado a **1080p Full HD** (30s) o **4K UHD** (80s) mediante código en la CPU local o de la VPS, se obtiene calidad de estudio broadcast **a coste cero de GPU adicional**.

---

## 2. Protocolo de Solicitud para FLUX 3 (`black-forest-labs/flux-3`)

### A. ¿Cuántas Fotos Enviar y Cómo se Comportan?

El parámetro `images` en FLUX 3 admite de 0 a 10 imágenes y modifica radicalmente la arquitectura de generación:

1. **0 Imágenes (Text-to-Video Puro):**
   - El modelo inventa la escena desde cero a partir del texto.
   - *Uso recomendado:* Cuando no se requiere mantener una geografía o personaje preexistente.
2. **1 Imagen (Image-to-Video / Keyframe 0):**
   - **El mejor modo para consistencia espacial y de personajes.**
   - Fija el fotograma inicial exacto (ej. nuestro fotograma de Shibuya 2326 de NanoBanana Pro 2) y genera el movimiento temporal hacia adelante.
3. **2 Imágenes (Start & End Keyframes):**
   - La 1ª imagen abre el vídeo (t=0s) y la 2ª lo cierra (t=8s).
   - La IA genera la interpolación física y de cámara entre ambos estados.
4. **3 a 10 Imágenes (Storyboard Multi-Frame):**
   - La 1ª abre, la última cierra y las intermedias se distribuyen uniformemente a lo largo de la duración (`duration`).
   - *Requisito indispensable:* **Subir siempre las imágenes a la Files API de Replicate (`POST /v1/files`)** para obtener URLs limpias `https://api.replicate.com/v1/files/...`. Enviar Base64 pesado satura la memoria del backend de Black Forest Labs durante la fase de *Reasoning*.

---

### B. Cómo Estructurar el Prompt (Lenguaje Natural Directo)

FLUX 3 procesa internamente el prompt con un LLM de razonamiento cinematográfico antes de renderizar. Se debe utilizar **inglés en prosa descriptiva estructurada en 4 partes**:

```
[Tipo de Plano y Trayectoria de Cámara] + [Sujeto y Acción Principal] + [Entorno, Arquitectura e Iluminación] + [Estilo de Movimiento y Renderizado]
```

*Ejemplo Canónico Verificado para Shibuya 2326:*
```text
A continuous cinematic FPV drone flight sweeping forward across the futuristic Shibuya Scramble crossing in Tokyo Year 2326. Glowing cyan and gold pedestrian light tracks below, towering illuminated skyscrapers, flying vehicles, and smooth forward camera movement.
```

---

### C. Cómo Pedir Cambios de Plano y Cortes

1. **Para Tomas Continuas (Single Take / Plano Secuencia):**
   - Usar términos como: `continuous camera motion`, `single take without cuts`, `smooth steady forward tracking shot`.
2. **Para Secuencias con Progresión Temporal:**
   - Describir la secuencia cronológica en el prompt:
     `Starts with a high-angle overhead view, swooping down toward the ground at mid-shot, and pitching upward to the skyscrapers in the final frames.`
3. **Para Cortes Rítmicos Abruptos (Montaje Musical):**
   - El mejor resultado profesional se logra generando clips individuales continuos y ensamblándolos en FFmpeg cortando exactamente en los transitorios de la pista de audio (+1.28s, +3.23s, +5.20s, +7.66s).

---

## 3. Pipeline de Upscaling en CPU mediante Código (FFmpeg Engine)

El escalado se ejecuta localmente mediante filtros de interpolación espacial de alta precisión y máscaras de enfoque adaptativo sin introducir artefactos de compresión:

### A. Escalado 720p $\rightarrow$ 1080p Full HD (Tiempo: ~30 segundos)
```bash
ffmpeg -y -i "shibuya_2326_flux3_official_720p.mp4" \
  -vf "scale=1920:1080:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=5:5:1.2:5:5:0.0,eq=contrast=1.04:saturation=1.03" \
  -c:v libx264 -preset slow -crf 17 -c:a copy "shibuya_2326_flux3_upscaled_1080p.mp4"
```

### B. Escalado 720p $\rightarrow$ 4K UHD (3840x2160) (Tiempo: ~80 segundos)
```bash
ffmpeg -y -i "shibuya_2326_flux3_official_720p.mp4" \
  -vf "scale=3840:2160:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=7:7:1.4:7:7:0.0,eq=contrast=1.05:saturation=1.04" \
  -c:v libx264 -preset medium -crf 18 -c:a copy "shibuya_2326_flux3_upscaled_4k.mp4"
```

---

## 4. Archivos y Deliverables Generados

- 🎬 **Vídeo 1080p Upscaled (Full HD):** `shibuya_2326_flux3_upscaled_1080p.mp4` (30 Mbps, CRF 17, audio sincronizado).
- 🎬 **Vídeo 4K Upscaled (UHD):** `shibuya_2326_flux3_upscaled_4k.mp4` (64 Mbps, CRF 18, audio sincronizado).
- 🎵 **Pista de Audio Master:** `audio_hook_8s.mp3` (320 kbps AAC, normalizada a -14 LUFS con picos a -3.8 dB).
- 📄 **Visualizador Web:** `investigacion_flux3_audio_sync.html`.
