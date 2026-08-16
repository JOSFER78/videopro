# 📐 Arquitectura de Sub-Páginas Jerárquicas y UX Pedagógica

> **Pilar:** `02_canales_youtube` / `autoasistencia_ia_y_ux_guiada`  
> **Estado:** `🟢 ESPECIFICACIÓN TÉCNICA ACTIVA`  
> **Patrón:** Progressive Disclosure & 1-Task-Per-View

---

## 🎯 1. Principio: Eliminación de la Sobrecarga Cognitiva

Las interfaces que intentan mostrar todas las opciones en un único formulario monolítico saturan al creador novato con más de 20 controles técnicos simultáneos.

La **Arquitectura Jerárquica Progresiva** resuelve este problema descomponiendo cualquier flujo complejo en **4 Sub-Páginas Secuenciales y Focalizadas**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  BREADCRUMB: 🏠 VideoPro Studio  ›  📺 Canales & Proyectos  ›  ⚙️ Configurar & Personalizar │
└────────────────────────────────────────────────────────────────────────────────────────┘
  │
  ├─► [ 1. 🎓 Aprender & Conceptos ]    ──► "¿Qué es esto y qué arquetipo me conviene?"
  ├─► [ 2. 📊 Diagnosticar mi Canal ]   ──► "¿Tengo todo listo y mi nicho tiene RPM?"
  ├─► [ 3. ⚙️ Configurar & Crear ]      ──► "1 sola decisión a la vez (Stepper atómico)"
  └─► [ 4. 🚀 Lanzar & Publicar ]       ──► "Pre-flight check + Render 1-Click + Export"
```

---

## 🧭 2. El Stepper Secundario y Breadcrumbs Dinámicos (`webui/components/hierarchical_subnav.py`)

Para que el usuario siempre sepa **dónde está, qué ha hecho y qué falta por hacer**, se utiliza un componente de sub-navegación con:
1. **Breadcrumbs Dinámicos:** Muestra la ruta jerárquica con enlaces interactivos.
2. **Botones de Paso (Stepper Tabs):** Con iconos visuales, números de fase y checkmarks automáticos `✓` al completar cada etapa.
3. **Barra de Progreso Integrada (0% a 100%):** Feedback visual inmediato del avance global del proyecto.

---

## 📋 3. Especificación de las 4 Sub-Páginas

### 🎓 Sub-Página 1: Aprender & Conceptos Básicos
- **Objetivo:** Comprensión mental del modelo y selección de arquetipos narrativos sin tocar código.
- **Contenido:**
  - Selector de Arquetipos Visuales mediante tarjetas interactivas (`CHRONODRIFT`, `FPV_URBAN`, `HISTORICAL_SCRAPING`, etc.).
  - Glosario de términos clave (Prompt semántico, Consistencia 4-Anclas, Pacing WPS).
  - Previsualizador de calidad esperada.

### 📊 Sub-Página 2: Diagnosticar mi Canal / Proyecto
- **Objetivo:** Verificación rápida de la viabilidad económica y el estado técnico del sistema.
- **Contenido:**
  - Calculadora de Viabilidad y RPM en vivo ($14 - $35 USD por cada 1.000 vistas).
  - Health check en tiempo real de motores conectados (LLM, Voz, Generadores de Vídeo, Almacenamiento).
  - Semáforo de preparación del proyecto (0 a 100 puntos).

### ⚙️ Sub-Página 3: Configurar & Crear (Enfoque "1 Sola Tarea a la Vez")
- **Objetivo:** Guiar la configuración en micro-pasos atómicos para no abrumar:
  - **Paso 3.1: Narrativa & Script:** 1 solo input de tema con sugerencias de ganchos virales.
  - **Paso 3.2: Estilo Visual:** Selector de motor y paleta lumínica con ejemplos gráficos.
  - **Paso 3.3: Locución & Música:** Selector auditivo de voces y slider de auto-ducking musical.
  - **Paso 3.4: Formato & Subtítulos:** Selector de relación de aspecto (16:9 / 9:16) y estilos tipográficos.

### 🚀 Sub-Página 4: Lanzar & Publicar
- **Objetivo:** Pre-vuelo de calidad y disparo del renderizado maestro.
- **Contenido:**
  - Pre-Flight Checklist automático (Audio normalizado a -14 LUFS, 4K Upscale listo, metadatos SEO generados).
  - Botón de disparo maestro (*"🎬 Generar Vídeo Completo"*).
  - Panel de exportación local y publicación directa a YouTube Studio.
