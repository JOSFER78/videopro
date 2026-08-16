# 🎬 Tratado de Motion Design Determinista y Físicas de Resorte en Remotion

> **Categoría:** Ingeniería Audiovisual & Programación de Vídeo  
> **Ubicación:** `docs/investigaciones/01_cinematografia_y_dop/` / `docs/nodos_y_motores/programacion/02_remotion_engine_react_hyperframes/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

---

## 📌 1. El Paradigma Determinista: El Vídeo como Función Pura del Frame

Remotion basa su arquitectura en la premisa matemática inalterable de que **el vídeo es una función pura del número de fotograma actual (`frame`)**.

$$\text{FrameState} = f(\text{frame}, \text{fps}, \text{props})$$

A diferencia de las animaciones web tradicionales impulsadas por el reloj interno del navegador (`requestAnimationFrame`, `Date.now()` o `performance.now()`), en Remotion se descarta cualquier dependencia temporal asíncrona. Esto garantiza que un renderizado frame a frame en un clúster de CPUs (o en AWS Lambda) produzca **exactamente los mismos píxeles** sin desincronización de audio ni saltos de cuadros.

---

## ⚙️ 2. Primitivas Fundamentales de Animación

### A. `interpolate()` con Curvas Bézier y Clamping
`interpolate()` mapea un valor de entrada (el fotograma actual obtenido con `useCurrentFrame()`) hacia un rango de salida (opacidad, escala, traslación, rotación).

```tsx
import { interpolate, Easing } from 'remotion';

// Mapeo no lineal con aceleración suave estilo documental
const opacity = interpolate(
  frame,
  [0, 15, 45, 60],
  [0, 1, 1, 0],
  {
    easing: Easing.bezier(0.34, 1.56, 0.64, 1), // Rebote elástico sutil
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }
);
```

> [!IMPORTANT]
> **Regla de Clamping Obligatoria:** El parámetro `{ extrapolateRight: 'clamp' }` es indispensable para evitar que las propiedades continúen creciendo o decreciendo indefinidamente más allá de la ventana de animación estipulada.

---

### B. `spring()`: Físicas de Masa-Resorte Reales
En lugar de curvas precalculadas, `spring()` simula un oscilador armónico amortiguado que produce una sensación táctil orgánica:

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const entrance = spring({
  frame,
  fps,
  config: {
    mass: 1.2,       // Inercia del cuerpo (1.0 = estándar, 1.5 = pesado)
    stiffness: 110,   // Tensión de retorno (100-150 para UI cinemática)
    damping: 14,      // Fricción/amortiguamiento (14-18 para asentamiento suave)
  },
});
```

---

## 💻 3. Componente de Ejemplo: Lower-Third Cinemático con Stagger

```tsx
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';

export const VoxDocumentaryLowerThird: React.FC<{
  title: string;
  subtitle: string;
  category: string;
}> = ({ title, subtitle, category }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Físicas de entrada escalonadas (Staggered Spring)
  const badgeSpring = spring({ frame: frame - 5, fps, config: { mass: 0.8, stiffness: 140, damping: 16 } });
  const titleSpring = spring({ frame: frame - 12, fps, config: { mass: 1.1, stiffness: 115, damping: 15 } });
  const subSpring = spring({ frame: frame - 18, fps, config: { mass: 1.0, stiffness: 100, damping: 18 } });

  const cardOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const cardTranslateX = interpolate(titleSpring, [0, 1], [-80, 0]);

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', padding: '80px 100px' }}>
      <div
        style={{
          opacity: cardOpacity,
          transform: `translateX(${cardTranslateX}px)`,
          backgroundColor: '#F4F1EA',
          borderLeft: '8px solid #0A5F46',
          padding: '24px 36px',
          borderRadius: '4px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.35)',
          maxWidth: '850px',
        }}
      >
        <div style={{
          fontFamily: 'JetBrains Mono',
          fontSize: '14px',
          fontWeight: 700,
          color: '#0A5F46',
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          opacity: badgeSpring
        }}>
          {category}
        </div>
        <div style={{
          fontFamily: 'Space Grotesk',
          fontSize: '38px',
          fontWeight: 900,
          color: '#1A1A1A',
          margin: '6px 0',
          lineHeight: 1.1,
        }}>
          {title}
        </div>
        <div style={{
          fontFamily: 'Inter',
          fontSize: '18px',
          color: '#555555',
          opacity: subSpring,
        }}>
          {subtitle}
        </div>
      </div>
    </AbsoluteFill>
  );
};
```
