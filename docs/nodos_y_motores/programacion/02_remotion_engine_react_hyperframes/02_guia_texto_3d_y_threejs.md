# 🧊 Tratado de Tipografía Cinética 3D y React Three Fiber en Remotion

> **Categoría:** Gráficos 3D & Tipografía Cinética  
> **Ubicación:** `docs/investigaciones/01_cinematografia_y_dop/` / `docs/nodos_y_motores/programacion/02_remotion_engine_react_hyperframes/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

---

## 📌 1. Arquitectura de Renderizado 3D Síncrono (`@remotion/three`)

La renderización de Three.js y React Three Fiber (R3F) en entornos tradicionales opera mediante un bucle continuo de animación no determinista (`requestAnimationFrame`). Para integrarlo en Remotion sin pérdida de cuadros:

1. **Reemplazo del Canvas:** Se utiliza exclusivamente `<ThreeCanvas />` del paquete `@remotion/three`.
2. **Control Determinista del Bucle:** Remotion fuerza internamente `frameloop: "never"`.
3. **Avance Manual:** La escena se evalúa fotograma por fotograma llamando síncronamente al método `advance()` del renderer de WebGL antes de capturar el buffer.

---

## 🌀 2. Cilindros y Marquesinas Tipográficas Procedurales en Canvas2D

Para obtener texto 3D ultra-nítido sin sobrecargar la GPU con mallas de texto complejas (FontLoader/TextGeometry), la técnica estándar de la industria consiste en:
- Dibujar el texto en alta resolución sobre un **Canvas2D de HTML5 en memoria** (ej. 2048x256 px).
- Convertir el Canvas en un `THREE.CanvasTexture` con `wrapS = THREE.RepeatWrapping`.
- Proyectarlo sobre un `THREE.CylinderGeometry` con caras visibles en ambos lados (`side: THREE.DoubleSide`).
- Animar el desplazamiento horizontal continuo de la textura: `texture.offset.x += delta * speed`.

```tsx
import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

export const KineticMarqueeCylinder: React.FC<{
  text: string;
  radius?: number;
  height?: number;
}> = ({ text, radius = 4, height = 1.0 }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [texture, setTexture] = useState<THREE.CanvasTexture | null>(null);

  useEffect(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 2048;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');

    if (ctx) {
      ctx.fillStyle = '#0A5F46'; // Verde analógico
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = '900 110px "Space Grotesk", sans-serif';
      ctx.fillStyle = '#F4F1EA'; // Texto crema
      ctx.textBaseline = 'middle';
      ctx.textAlign = 'center';

      const repeated = `${text}  ✦  ${text}  ✦  ${text}  ✦  `;
      ctx.fillText(repeated, canvas.width / 2, canvas.height / 2);
    }

    const t = new THREE.CanvasTexture(canvas);
    t.wrapS = THREE.RepeatWrapping;
    t.wrapT = THREE.ClampToEdgeWrapping;
    t.minFilter = THREE.LinearFilter;
    t.magFilter = THREE.LinearFilter;
    t.generateMipmaps = false;
    setTexture(t);
  }, [text]);

  useFrame((state, delta) => {
    if (texture) {
      texture.offset.x += delta * 0.09;
    }
  });

  if (!texture) return null;

  return (
    <mesh ref={meshRef} rotation={[0.12, 0, 0.04]}>
      <cylinderGeometry args={[radius, radius, height, 96, 1, true]} />
      <meshBasicMaterial map={texture} side={THREE.DoubleSide} transparent toneMapped={false} />
    </mesh>
  );
};
```

---

## 📽️ 3. Proyección de Vídeo en Geometrías 3D (OffscreenCanvas & Video Texture)

Para proyectar clips de vídeo reales sobre pantallas 3D o edificios sin bloqueos de memoria:
- Montar `<Video />` en modo `headless`.
- Capturar cada fotograma mediante `onVideoFrame`.
- Dibujar en un `OffscreenCanvas` y actualizar `texture.needsUpdate = true`.
- Invocar `advance(performance.now())` en entornos de renderizado headless.
