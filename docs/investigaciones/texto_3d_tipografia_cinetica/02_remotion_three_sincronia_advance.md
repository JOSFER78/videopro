# ⚡ Remotion Three: Sincronía Frame-Accurate y Advance

> **Área:** `docs/investigaciones/texto_3d_tipografia_cinetica/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 📌 Arquitectura `<ThreeCanvas />`
- Anulación del bucle continuo del navegador: `frameloop: "never"`.
- Remotion evalúa y avanza la escena frame a frame invocando `advance()`.
- Prevención de FOUT mediante `document.fonts.ready`.
