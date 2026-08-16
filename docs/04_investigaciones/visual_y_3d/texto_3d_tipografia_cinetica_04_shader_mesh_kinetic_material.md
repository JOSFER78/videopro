# 🎨 Shader de Material Cinético: Oscurecimiento de Backface

> **Área:** `docs/investigaciones/texto_3d_tipografia_cinetica/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

```glsl
#include <color_fragment>
if (!gl_FrontFacing) {
  // Oscurece la cara interna al 70% para ganar contraste físico y profundidad
  vec3 shadowCol = vec3(0.0);
  diffuseColor.rgb = mix(diffuseColor.rgb, shadowCol, 0.7);
}
```
