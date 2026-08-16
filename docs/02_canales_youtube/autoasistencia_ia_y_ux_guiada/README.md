# 🤖 Autoasistencia de IA y UX Guiada (Copilot Universal & Sub-Páginas)

> [!IMPORTANT]
> **AVISO DE FLEXIBILIDAD Y ADAPTABILIDAD:**
> Este documento representa un **marco de referencia técnico, arquitectónico y conceptual**, diseñado para inspirar e instruir a desarrolladores y creadores sobre la implementación de sistemas agénticos de autoasistencia y experiencias de usuario sin sobrecarga cognitiva. **No es una directriz dogmática ni una biblia inmutable**: cualquier parámetro, flujo o componente puede adaptarse según las necesidades de producción.

---

## 🎯 Propósito de este Módulo

Esta sección documenta la arquitectura del **Copilot Agéntico de IA Universal** y el **Sistema de Sub-Páginas Jerárquicas** diseñado para eliminar la frustración y la curva de aprendizaje en creadores principiantes dentro de VideoPro Studio.

### 📚 Índice de Investigaciones y Tratados Técnicos

| Documento | Enfoque Principal | Estado |
| :--- | :--- | :---: |
| [**01. Copilot Agéntico Universal y Observabilidad en Tiempo Real**](./01_copilot_agentico_universal_y_observabilidad_en_tiempo_real.md) | Observador de estado de Streamlit, cliente LLM asíncrono con streaming SSE (:8742), despachador de tool calling / acciones asistidas y componente visual Floating Drawer. | 🟢 Activo |
| [**02. Arquitectura de Sub-Páginas Jerárquicas y UX Pedagógica**](./02_arquitectura_subpaginas_jerarquicas_y_ux_pedagogica.md) | Desglose de vistas complejas en 4 fases progresivas (Aprender ➔ Diagnosticar ➔ Configurar ➔ Lanzar), Breadcrumbs interactivos y micro-steppers. | 🟢 Activo |

---

## 🏛️ Filosofía de Diseño: "Complejidad Oculta, Claridad Visible"

1. **Autoasistencia Semántica en Tiempo Real:** El usuario puede preguntar en español coloquial *"¿Qué hace esta pantalla?"* o *"¿Por qué falla mi render?"*, y la IA analiza la pantalla activa, los formularios y los logs para responder con analogías simples de nivel principiante.
2. **Capacidad Actuadora (UI Tool Calling):** El Copilot no solo aconseja, sino que puede rellenar formularios, cambiar de vista o disparar auditorías de pipeline cuando el usuario lo autoriza.
3. **Cero Sobrecarga (1-Task-per-View):** Las pantallas ya no contienen 20 controles juntos; se dividen en sub-páginas secuenciales donde cada paso toma una sola decisión clara.
