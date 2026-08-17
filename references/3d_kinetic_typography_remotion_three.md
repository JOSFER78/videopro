# 🧊 Tipografía Cinética 3D y Remotion Three: Marquesinas, Cilindros Procedurales y Sincronía Frame-Accurate

> **Pilar:** Motion Graphics 3D & WebGL  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA  

---

## 1. Marquesinas y Cilindros Tipográficos 3D en Canvas2D / Three.js

Para generar cintas de texto 3D rotativas (estilo marquesina bursátil o titular documental futurista):

### A. Técnica de Dibujo en Memoria (Offscreen Canvas)
1. Se crea un lienzo HTML5 en memoria de alta resolución: **`2048 x 256 px`**.
2. Se traza el texto con tipografía de ancho fijo o condensada (`JetBrains Mono`, `Oswald` o `Bebas Neue`) con espaciado regular.
3. Se crea una textura Three.js:
   ```javascript
   const canvas = document.createElement("canvas");
   canvas.width = 2048;
   canvas.height = 256;
   const ctx = canvas.getContext("2d");
   
   // Dibujar fondo y texto
   ctx.fillStyle = "#101622";
   ctx.fillRect(0, 0, 2048, 256);
   ctx.fillStyle = "#FFD700";
   ctx.font = "bold 96px 'JetBrains Mono', monospace";
   ctx.fillText("CHRONODRIFT 2026 // URBAN TIME TRAVEL // 6-DoF FPV //", 50, 160);
   
   const texture = new THREE.CanvasTexture(canvas);
   texture.wrapS = THREE.RepeatWrapping;
   texture.wrapT = THREE.ClampToEdgeWrapping;
   texture.repeat.set(2, 1);
   ```

### B. Proyección sobre Cilindro 3D
```javascript
const geometry = new THREE.CylinderGeometry(radius = 5.0, radius = 5.0, height = 1.2, 96, 1, true);
const material = new THREE.MeshBasicMaterial({
    map: texture,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.95
});
const cylinderMesh = new THREE.Mesh(geometry, material);
scene.add(cylinderMesh);
```

### C. Animación de Desplazamiento Síncrono
En cada frame de renderizado:
```javascript
texture.offset.x = (frame / fps) * 0.12; // Velocidad calibrada constante
```

---

## 2. Remotion Three: Sincronía Frame-Accurate y Advance

Al integrar Three.js dentro de Remotion mediante `@remotion/three`:

### A. Anulación del Loop del Navegador
NUNCA utilizar `requestAnimationFrame` estándar dentro del render de Remotion. El canvas debe operar en modo estricto:
```tsx
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, useVideoConfig } from "remotion";

export const Scene3D: React.FC = () => {
    const frame = useCurrentFrame();
    const { width, height, fps } = useVideoConfig();

    return (
        <ThreeCanvas
            width={width}
            height={height}
            frameloop="never"
            advance={(scene, camera) => {
                // Remotion controla el avance de tiempo frame a frame
            }}
        >
            <ThreeContent frame={frame} fps={fps} />
        </ThreeCanvas>
    );
};
```

### B. Prevención de FOUT (Flash of Unstyled Text)
Antes de iniciar el renderizado del frame 0, forzar la resolución de todas las fuentes web:
```typescript
await document.fonts.ready;
```

---

## 3. Video Textures en Offscreen Canvas

Para mapear un clip de vídeo animado sobre superficies 3D en Remotion:
1. Montar `<Video />` en modo headless o invisible.
2. Capturar fotogramas en el hook `onVideoFrame` o `useCurrentFrame()`.
3. Actualizar la textura GPU notificando a Three.js:
   ```typescript
   texture.needsUpdate = true;
   ```
4. Renderizar con precisión de milisegundo sin saltos de fotogramas.
