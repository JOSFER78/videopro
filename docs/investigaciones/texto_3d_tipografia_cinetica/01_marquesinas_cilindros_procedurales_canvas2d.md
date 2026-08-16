# 🧊 Marquesinas y Cilindros Tipográficos 3D en Canvas2D

> **Área:** `docs/investigaciones/texto_3d_tipografia_cinetica/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 📌 Técnica de Dibujo en Memoria
- Trazado de texto de alta definición sobre un canvas HTML5 de **2048x256 px**.
- Conversión a `THREE.CanvasTexture` con `wrapS = THREE.RepeatWrapping`.
- Proyección sobre `THREE.CylinderGeometry(radius, radius, height, 96, 1, true)`.
- Animación síncrona: `texture.offset.x += delta * 0.05`.
