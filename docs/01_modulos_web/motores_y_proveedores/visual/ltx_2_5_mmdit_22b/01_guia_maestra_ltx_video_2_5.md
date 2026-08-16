# 🚀 Guía Maestra: LTX-2.5 MMDiT (22B) & Generación Audiovisual Nativa

> **Ubicación:** `docs/investigaciones/nodos_capacidades/ltx-video-2-5/01_guia_maestra_ltx_video_2_5.md`  
> **Motor:** LTX-2.5 MMDiT 22B (Lightricks)  
> **Capacidades Clave:** Difusión de vídeo a 24fps + Generación nativa de audio máster 48kHz WAV + Lip-sync  
> **Infraestructura:** ZeroGPU (Gratis / Desarrollo) / Replicate H100 (Producción)  

---

## 1. Arquitectura y Visión General de LTX-2.5

**LTX-2.5** es una arquitectura basada en **MMDiT (Multi-Modal Diffusion Transformer) de 22 mil millones de parámetros**, diseñada para generar conjuntamente pistas de vídeo fotorrealista y bandas sonoras completas de 48kHz con sincronización labial y física acústica coherente.

```mermaid
graph TD
    A[Prompt Audiovisual] --> B[LTX-2.5 MMDiT 22B Transformer]
    B --> C[Flujo Latente Visual (24 fps 1080p)]
    B --> D[Flujo Latente Acústico (48kHz WAV)]
    C --> E[Decodificador VAE Espaciotemporal]
    D --> F[Decodificador Neural de Audio Hi-Fi]
    E --> G[Vídeo Final Sincronizado MP4/MOV]
    F --> G
```

---

## 2. Infraestructura y Modos de Ejecución

LTX-2.5 se despliega en dos capas según la etapa del proyecto:

| Nivel de Entorno | Infraestructura | Coste | Resolución & Frames | Caso de Uso |
| :--- | :--- | :--- | :--- | :--- |
| **Desarrollo / Prototipado** | **ZeroGPU (HuggingFace Spaces)** | **$0.00** | 720p @ 24fps (5s clips) | Pruebas de concepto, validación de prompts y encuadres |
| **Producción Final** | **Replicate H100 (API dedicada)** | **Bajo demanda (~$0.03/s)** | 1080p/4K @ 24fps (hasta 15s) | Masters finales para YouTube, documentales y B-Roll |

---

## 3. Guía de Prompting para LTX-2.5 (Vídeo + Audio Multimodal)

A diferencia de modelos que solo procesan imágenes, LTX-2.5 requiere describir simultáneamente el comportamiento visual y los elementos acústicos directos:

```text
[Visual Scene]: Medium close-up of an astronaut speaking inside a lunar module cockpit, illuminated by amber control panels and blue Earthlight reflection in the helmet visor. Shot on 35mm cinema lens, realistic facial micro-expressions.
[Camera Movement]: Subtle handheld camera shake, slow push towards the face.
[Acoustic Environment]: Pressurized cabin tone, gentle oxygen circulation hum, radio static click.
[Spoken Dialogue / Lip-Sync]: Clear spoken words through radio filter: "Houston, all telemetry systems are stable and ready."
[Audio Quality & Style]: 48kHz studio broadcast quality, crisp transients, no background distortion.
```

---

## 4. Reglas de Descarte y Control de Calidad (QA)

- 🚫 **Descartar renders con audio a 16kHz o 22kHz**: LTX-2.5 debe ejecutarse siempre con el decodificador de 48kHz activado.
- 🚫 **Descartar resoluciones inferiores a 720p**: Nunca renderizar a 480p para evitar artefactos de cuantización en el reescalado.
- 🚫 **Descartar desfases labiales superiores a 2 fotogramas**: Si el lip-sync presenta deriva, re-generar fijando el seed o ajustando la cadencia de la frase en el prompt.

---

## 5. Documentos y Referencias Relacionadas

- [Capacidades Maestras e Infraestructura](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/nodos_capacidades/capacidades_maestras.md)
- [Matriz Interactiva de Proveedores](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/nodos_capacidades/proveedores_excel.html)
- [Metodología Documental Cinematográfica](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/01_metodologia_documental_cinematografica.md)
