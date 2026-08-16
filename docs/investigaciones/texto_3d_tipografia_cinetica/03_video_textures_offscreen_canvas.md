# 📽️ Proyección de Vídeo Headless sobre Mallas 3D

> **Área:** `docs/investigaciones/texto_3d_tipografia_cinetica/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 📌 Protocolo de Alto Rendimiento
1. Montar `<Video headless onVideoFrame={onVideoFrame} />`.
2. El callback copia el cuadro a un `OffscreenCanvas`.
3. Actualizar `texture.needsUpdate = true`.
4. En renderizado headless, invocar `advance(performance.now())`.
