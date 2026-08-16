# 🔍 Efectos Ópticos: Focus Hunt & Roughen Edges

> **Área:** `docs/investigaciones/shaders_glsl_webgl_overlays/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 1. Focus Hunt (Búsqueda de Enfoque)
`Camera Lens Blur` (radio 4-8) + máscara elíptica inversa (Subtract) con **calado de 300 px**, animando expansión negativa hacia el centro.

## 2. Roughen Edges (Textura de Papel Prensa)
Borde 3.3 px, Nitidez 4.58, Escala 65, Complejidad 10, Influencia Fractal 38%.
