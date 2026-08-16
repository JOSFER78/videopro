# 🏔️ DaVinci Resolve Fusion + QGIS: Solución al Z-Fighting en 3D

> **Área:** `docs/investigaciones/cartografia_tactil_vox/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 🛡️ La Regla del Z-Shift +0.001
Cuando el mapa base y la máscara de relieve/país colisionan en la misma profundidad Z, el motor de renderizado 3D produce parpadeo (*Z-fighting*).
- **Solución:** En el nodo `Imageplane3D` de la máscara superior, desplazar físicamente en Z por exactamente **`+0.001`**.
- **Paint Tool:** En modo `Stroke Tool` (sin multi-stroke) con `Spacing = 0.75 - 0.80`.
