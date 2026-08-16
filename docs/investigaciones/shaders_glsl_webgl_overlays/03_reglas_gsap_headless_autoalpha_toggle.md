# 🛡️ Reglas GSAP Seguras para Render Headless

> **Área:** `docs/investigaciones/shaders_glsl_webgl_overlays/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

1. **Timeline Pausado:** `{ paused: true }` y `window.__timelines.main = tl;`.
2. **Mitigación de Opacity Poisoning con `autoAlpha`:** `tl.set("#s1", { autoAlpha: 0 }, 2.5); tl.set("#s2", { autoAlpha: 1 }, 2.5);`.
3. **Forzar Primer Ancla:** `tl.set("#s3", { opacity: 1 }, 5.0);`.
