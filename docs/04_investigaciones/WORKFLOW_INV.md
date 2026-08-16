---
name: inv
description: Ingestar, estructurar y documentar automáticamente investigaciones técnicas y nuevas ideas en la jerarquía de docs/ de VideoPro.
---

# Workflow de Ingesta y Documentación de Investigaciones (`/inv`)

Este workflow se activa cuando el usuario escribe `/inv` acompañado de notas, enlaces, ideas o temas de investigación técnica para **VideoPro Studio**.

---

## 📋 Pasos de Ejecución

### 1. 🔍 Analizar y Sintetizar la Información
- Lee atentamente las notas, transcripciones, prompts o ideas enviadas por el usuario.
- Si el usuario menciona **NotebookLM**, utiliza `nlm notebook query` en el cuaderno correspondiente (ej. `editor videos` ID: `adb74854-2fac-4c7e-87ef-97f9d87c7c72`) para extraer todos los detalles técnicos, recetas y bibliotecas relevantes.

---

### 2. 📂 Clasificar en el Macro-Pilar Correcto de `docs/`
Determina a cuál de los **5 Pilares Jerarquizados** pertenece la información:

| Caso | Dónde Documentar | Regla de Nomenclatura |
| :--- | :--- | :--- |
| **Módulo o motor presente en la Web UI / Firebase** | `docs/01_modulos_web/` (`capacidades/` o `motores_y_proveedores/`) | **Con número de serie** (`01_`, `02_`...) |
| **Canal propio o estrategia de YouTube** | `docs/02_canales_youtube/` (`mis_canales/` o `estrategia_y_crecimiento/`) | **Con número de serie** en `mis_canales/` |
| **Flujo de creación de vídeo (Workflow Studio)** | `docs/03_workflows_produccion/` | **Con número de serie** (`01_` a `08_`) |
| **Investigación nueva, laboratorio técnico o idea futura** | `docs/04_investigaciones/` (`visual_y_3d/`, `audio_y_foley/`, `motion_y_codigo/`, `benchmarks_y_evaluacion/`) | **SIN número de serie** |
| **Infraestructura Cloud, Firebase o puertos** | `docs/05_infraestructura_y_cloud/` | Documento descriptivo |

---

### 3. ✍️ Redactar con Estándar de Ingeniería Completo
Redacta el documento Markdown siguiendo esta estructura rigurosa (sin placeholders, sin mocks ni pseudocódigo):
1. **Encabezado Técnico:** Título, pilar, fecha y estado (`🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA`).
2. **Fundamentos Teóricos / Matemáticos:** Ecuaciones de movimiento, curvas EBU R128, osciladores de resorte o shaders.
3. **Contratos y Configuraciones Tipadas:** Interfaces TypeScript o esquemas JSON.
4. **Código y Comandos 100% Reales:** Snippets completos y ejecutables (React/Remotion TSX, Shaders GLSL, comandos FFmpeg CLI o Python).
5. **Casos de Uso Cinemáticos:** Parámetros recomendados para producción.
6. **Mitigación de Edge Cases:** Prevención de pantallas negras, memory leaks o clics de fase de audio.

---

### 4. 📇 Actualizar Índices y READMEs
- Asegúrate de que la carpeta de destino mantenga su `README.md` actualizado con el enlace a la nueva investigación.
- Si es una investigación relevante, añádela a `docs/INDICE_MAESTRO.md`.
- Recuerda siempre la regla: *la documentación es un marco orientativo y flexible para inspirar e innovar, no un dogma sagrado*.

---

### 5. 💾 Sincronizar y Confirmar en Git
- Guarda el archivo en la VPS (`ubuntu@143.47.35.167`) bajo `/home/ubuntu/workspace/pro/hermes/10_videopro/docs/...`.
- Realiza un commit en Git con un mensaje descriptivo: `docs(investigaciones): añadir tratado sobre <tema>`.
- Informa al usuario con un resumen conciso de lo documentado y su enlace.
