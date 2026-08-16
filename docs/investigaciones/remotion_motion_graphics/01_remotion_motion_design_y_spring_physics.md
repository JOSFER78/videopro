# 🎬 Remotion Motion Design & Físicas de Resorte

> **Área:** `docs/investigaciones/remotion_motion_graphics/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 📌 1. Principio Determinista
El vídeo en Remotion es una función matemática pura del fotograma actual (`frame`):
$$\text{FrameState} = f(\text{frame}, \text{fps}, \text{props})$$

## ⚙️ 2. Primitivas de Animación
- **`interpolate()`**: Mapeo con `Easing.bezier(0.34, 1.56, 0.64, 1)` y `{ extrapolateRight: 'clamp' }`.
- **`spring()`**: Simulación armónica amortiguada con `mass: 1.1-1.2`, `stiffness: 110-120`, `damping: 14-15`.

## 💻 3. Implementación de Lower-Thirds & Stagger
Animación de tarjetas periodísticas escalonadas por frame con TypeScript y Remotion.
