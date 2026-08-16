---
name: inv
description: Workflow Interactivo y Multi-Agente de Ingesta, Debate y Documentación Técnica en docs/.
---

# 🔬 Workflow Interactivo y Multi-Agente de Investigaciones (`/inv`)

> **Regla de Oro:** Este workflow **NUNCA debe generar la documentación de golpe sin interactuar antes**. Debe entrevistar primero al usuario mediante preguntas interactivas (`ask_question`), aclarar cada detalle del trabajo y desplegar un comité de **subagentes en paralelo** antes de la redacción final en `docs/`.

---

## 🔄 Fases Obligatorias de Ejecución

### 🗣️ FASE 1: Entrevista Interactiva Obligatoria con el Usuario
1. **NO actuar de forma precipitada.** Al recibir la petición `/inv`, analiza el tema planteado y formula una serie de preguntas de clarificación utilizando la herramienta `ask_question`.
2. **Preguntas Clave del Árbol de Decisiones:**
   - **Pilar y Destino:** ¿Pertenece a un módulo activo de la web (`01_modulos_web/`), canal (`02_canales_youtube/`), workflow (`03_workflows_produccion/`), nueva investigación (`04_investigaciones/`) o infraestructura (`05_infraestructura_y_cloud/`)?
   - **Alcance y Stack Técnico:** ¿Qué tecnologías, librerías, APIs o frameworks específicos deben implementarse?
   - **Estilo y Nivel de Detalle:** ¿Tratado exhaustivo con código ejecutable completo, snippets rápidos o arquitectura matemática?
   - **Fuentes Externas / NotebookLM:** ¿Se deben consultar cuadernos específicos de NotebookLM (`nlm notebook query`), repositorios GitHub o datasets reales?

---

### 🤖 FASE 2: Despliegue de Subagentes Especializados en Paralelo
Una vez alineados los requisitos con el usuario, lanza al menos **2 a 4 subagentes concurrentes** (`invoke_subagent`):
- 🕵️ **Subagente 1 (Investigador & Extractor de Datos):** Consulta cuadernos de NotebookLM, APIs o código existente para recopilar especificaciones y sintaxis exacta.
- 📐 **Subagente 2 (Arquitecto de Código & Modelos):** Diseña los contratos tipados (TypeScript / JSON Schema / GLSL / FFmpeg) y la arquitectura modular.
- 🛡️ **Subagente 3 (Auditor de Calidad & Cero Mocks):** Verifica que todo el código sea 100% real, funcional y libre de placeholders o datos inventados.

---

### ✍️ FASE 3: Síntesis de Ingeniería e Integración en `docs/`
Integra los resultados de los subagentes en un tratado técnico en Markdown que cumpla el **Estándar de Ingeniería Completo**:
1. **Encabezado y Metadatos:** Título, Pilar, Fecha, Autor y Estado (`🟢 ESPECIFICACIÓN TÉCNICA ACTIVA`).
2. **Fundamentos Matemáticos / Físicos:** Fórmulas de movimiento, curvas de decibelios o mapeos espaciales.
3. **Contratos de Configuración:** Interfaces TypeScript o esquemas JSON.
4. **Código 100% Real y Funcional:** Scripts completos (Remotion TSX, GLSL, FFmpeg CLI, Python).
5. **Casos de Uso Cinemáticos:** Parámetros recomendados para producción.
6. **Mitigación de Edge Cases:** Prevención de pantallas negras, memory leaks o clics de fase de audio.

---

### 📇 FASE 4: Auto-Indexación y Verificación
1. **Actualizar `README.md`:** Añadir el enlace a la nueva investigación en el `README.md` del pilar y en `docs/INDICE_MAESTRO.md`.
2. **Aviso de Flexibilidad:** Recordar siempre que la documentación es un marco orientativo y flexible para inspirar e innovar, no un dogma sagrado.
3. **Validación del Pipeline:** Ejecutar `scripts/validate_chronodrift_pipeline.py` para asegurar que el sistema compila al 100%.
4. **Commit en Git:** Confirmar los cambios en el repositorio de la VPS con un mensaje descriptivo.
