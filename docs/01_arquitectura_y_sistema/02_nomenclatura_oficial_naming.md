# VIDEOPRO — DICCIONARIO Y VOCABULARIO OFICIAL DE ARQUITECTURA (NAMING.md)

**Versión:** 1.0.0 — Canónica  
**Estado:** `CURRENT / OFFICIAL SOURCE OF TRUTH`  
**Última Actualización:** Agosto 2026

Este documento establece la **nomenclatura oficial, inequívoca y formal** para todos los componentes, conceptos, entidades y capas de VideoPro. Ningún documento o fragmento de código debe contradecir las definiciones aquí descritas.

---

## 1. ENTIDADES PRINCIPALES DEL SISTEMA

### 1.1 `VideoPro`
* **Definición:** Es la **aplicación principal** y el ecosistema completo de producción audiovisual.
* **Componentes que incluye:**
  - Frontend interactivo (Streamlit — Puerto `7001`).
  - Backend REST API (FastAPI — Puerto `8080`).
  - Repositorio unificado de metadatos y almacenamiento.
  - Orquestador de Workflows, Director Creativo y Planificador de Escenas.
* **Regla:** Nunca llamar "VideoPro" a servicios externos (como RunPod, Replicate o Google Flow).

### 1.2 `VideoPro Studio`
* **Definición:** Es el **entorno de trabajo y suite de creación** dentro de VideoPro que engloba el Generador Cinemático, el Director Creativo Semántico, el Diseñador de Workflows y la Bóveda de Medios.

### 1.3 `Workflow`
* **Definición:** Es una **definición abstracta de proceso de producción** seleccionable y configurable por el usuario.
* **Ejemplos:** `PIXAR_3D_ANIMATION`, `HISTORICAL_SCRAPING`, `CITY_ROUTES_BEATS`, `DOCUMENTARY_MASTER`.
* **Regla:** Un Workflow **NO** es un motor, ni un proveedor de nube, ni un servidor.

### 1.4 `Pipeline`
* **Definición:** Es la **secuencia ordenada y cableada de operaciones** que materializa un Workflow específico.
* **Relación:**
  $$\text{Workflow} = \text{Definición seleccionable} \iff \text{Pipeline} = \text{Secuencia de ejecución cableada}$$

### 1.5 `Node`
* **Definición:** Es una **unidad funcional modular e independiente** dentro de un Pipeline. Posee puertos de entrada (Sockets In), puertos de salida (Sockets Out) y parámetros dinámicos.
* **Ejemplos:** `Research Node`, `Script Node`, `Voice Node`, `Visual Node`, `Music Node`, `Subtitle Node`, `Render Node`.

### 1.6 `Workflow Designer`
* **Definición:** Es la **herramienta visual de edición e inspección de grafos de nodos** integrada en VideoPro Studio.
* **Regla de Nomenclatura:** **NO debe llamarse "ComfyUI"**. El Workflow Designer es la interfaz nativa de VideoPro inspirada en diseño de grafos.

---

## 2. CAPACIDADES, MOTORES Y PROVEEDORES

```text
┌────────────────────────────────────────────────────────┐
│                      CAPABILITY                        │
│          (Contrato abstracto: QUÉ se hace)             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                        ENGINE                          │
│          (Algoritmo o Modelo: CÓMO se hace)            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                       PROVIDER                         │
│       (Infraestructura física: DÓNDE se ejecuta)       │
└────────────────────────────────────────────────────────┘
```

### 2.1 `Capability` (Capacidad)
* **Definición:** Contrato formal de entrada/salida para una función técnica audiovisual (ej. `video_generation`, `voice_generation`, `script`, `research`, `music_generation`, `rendering`).

### 2.2 `Engine` (Motor)
* **Definición:** Software, modelo de IA o algoritmo que implementa una Capacidad.
* **Ejemplos Reales Activos:**
  - `google_flow`: Motor de generación de tomas cinemáticas y vuelos orbitales 4K vía automatización headless.
  - `flux_video`: Motor de keyframes y planos visuales con FLUX.1/FLUX.3.
  - `nanobanana`: Motor de renderizado visual 2K/4K y restauración 2.5D.
  - `vibevoice`: Motor neuronal de síntesis de voz con cadencia documental (`es-emilio`).
  - `whisper`: Motor de transcripción fonética y timestamps palabra por palabra.
  - `ffmpeg`: Motor de composición de vídeo, etalonaje y auto-ducking acústico.
  - `remotion`: Motor de renderizado de infografías React TSX / HyperFrames.

### 2.3 `Provider` (Proveedor de Infraestructura)
* **Definición:** El entorno de hardware o servicio cloud donde se ejecuta un Engine.
* **Ejemplos:** `local_vps` (servidor actual), `zerogpu_serverless` (Hugging Face / Free Pool), `cloudflare_r2` (almacenamiento de objetos).

### 2.4 `Adapter` (Adaptador)
* **Definición:** Capa de código aislada (`app/core/orchestration/adapters/`) que traduce las peticiones de VideoPro al protocolo específico de un Engine/Provider externo.

---

## 3. SERVICIOS E INTEGRACIONES EXTERNAS

### 3.1 `ComfyUI Runtime`
* **Definición:** Runtime externo independiente para la ejecución de grafos de nodos ComfyUI (`PLANNED / FUTURE INTEGRATION`).
* **Regla:** VideoPro cuenta con un `ComfyUIAdapter` preparado para despachar tareas a servidores ComfyUI externos cuando estén conectados, pero **VideoPro Studio NO es ComfyUI**.

### 3.2 `RunPod`
* **Definición:** Proveedor de infraestructura cloud GPU bajo demanda (`INFRASTRUCTURE PROVIDER — PLANNED`).
* **Estado:** Planificado como backend de cómputo GPU remoto.

### 3.3 `Hermes`
* **Definición:** Sistema externo de investigación documental, búsqueda web profunda y orquestación de subagentes (`EXTERNAL RESEARCH / AGENT SYSTEM`).
* **Relación:** VideoPro se comunica con Hermes para extraer hechos históricos, datos y fotografías de dominio público.

### 3.4 `Antigravity Bridge`
* **Definición:** Adaptador local de inferencia LLM (`LOCAL BRIDGE`) ejecutándose en el puerto `8742` para acceder a modelos como Gemini 3.7 Flash.

---

## 4. PERSISTENCIA Y ALMACENAMIENTO

### 4.1 `Firebase Firestore`
* **Definición:** Base de datos NoSQL en la nube utilizada para **persistir metadatos, estado de proyectos, configuraciones y sincronización en tiempo real** (Colecciones: `videopro_settings`, `workflows`, `projects`).
* **Regla:** Firestore almacena **únicamente metadatos y esquemas**, NUNCA archivos pesados binarios de vídeo.

### 4.2 `Cloudflare R2`
* **Definición:** Almacenamiento de objetos compatible con S3 (`OBJECT STORAGE`) utilizado para alojar **artefactos multimedia finales e intermedios** (vídeos MP4, audios MP3, imágenes 4K, pistas BGM).

---

## 5. DEPENDENCIAS HISTÓRICAS Y RUNTIME

### 5.1 `MoneyPrinterTurbo`
* **Definición:** Proyecto open-source base a partir del cual evolucionó VideoPro.
* **Relación Real Actual:**
  - **Runtime:** VideoPro comparte el entorno virtual de librerías Python (`/home/ubuntu/MoneyPrinterTurbo/.venv`) donde están instaladas las dependencias de PyTorch, Streamlit, FastAPI, MoviePy y FFmpeg.
  - **Código:** Todo el código principal de VideoPro reside y opera de forma desacoplada dentro de `/home/ubuntu/workspace/pro/hermes/10_videopro`.

---

## 6. EJECUCIÓN Y TRAZABILIDAD

* **`Project`:** Contenedor de alto nivel creado por el usuario con su concepto, guion y ajustes.
* **`Job`:** Instancia de ejecución de un Workflow con ID único (`job_id`), registro de tiempo, métricas y trazabilidad paso a paso.
* **`JobStep`:** Unidad mínima de ejecución dentro de un Job que evalúa un nodo del pipeline.
* **`Artifact`:** Fichero multimedia resultante de un Job o JobStep (MP4, MP3, PNG, ASS).
