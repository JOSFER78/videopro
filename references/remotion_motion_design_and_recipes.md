# 🎬 Remotion Motion Design, Físicas de Resorte y Recetario Maestro

> **Pilar:** Programación de Vídeo Determinista (Video-as-Code)  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA  

---

## 1. Principio Fundamental: Determinismo Temporal

En Remotion, cualquier elemento visual en la pantalla es una función matemática pura del fotograma actual (`frame`), la tasa de refresco (`fps`) y los parámetros de configuración (`props`):
$$\text{FrameState} = f(\text{frame}, \text{fps}, \text{props})$$

### Reglas de Oro
1. **Nunca usar `Date.now()`, `Math.random()` sin semilla o estados mutables asíncronos** en el árbol de renderizado.
2. **Utilizar `random(seed)` de Remotion** para generar variabilidad visual reproducible cuadro a cuadro.
3. **Clampear siempre las interpolaciones finales**:
   ```typescript
   interpolate(frame, [0, durationInFrames], [0, 1], {
     extrapolateLeft: 'clamp',
     extrapolateRight: 'clamp',
     easing: Easing.bezier(0.34, 1.56, 0.64, 1),
   });
   ```

---

## 2. Físicas de Resorte (*Spring Physics*) y Oscilador Armónico Amortiguado

Remotion modela la ecuación diferencial de segundo orden del oscilador armónico amortiguado:
$$m \frac{d^2 x}{dt^2} + c \frac{dx}{dt} + k x = 0$$

Donde:
- $m =$ `mass` (inercia del objeto).
- $k =$ `stiffness` (fuerza recuperadora del resorte).
- $c =$ `damping` (resistencia al movimiento / amortiguamiento).

### Tabla Canónica de Presets de Resorte

| Preset | `damping` | `stiffness` | `mass` | `overshootClamping` | Caso de Uso |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **gentle** | 20 | 100 | 1.0 | `false` | Entrada sutil de fondos y viñetas suaves |
| **snappy** | 15 | 200 | 1.0 | `false` | Botones, interacciones rápidas y tabs |
| **bouncy** | 8 | 180 | 1.0 | `false` | Iconos lúdicos y badges elásticos |
| **smooth** | 30 | 80 | 1.0 | `true` | Transiciones cinematográficas relajadas |
| **stiff** | 25 | 300 | 1.0 | `true` | Alineación precisa y visualizaciones técnicas |
| **vox-dossier** | 14 | 100 | 0.8 | `false` | Tarjetas de documento / periódico en perspectiva |
| **headline-stagger** | 12 | 120 | 0.6 | `false` | Titulares periodísticos con desfase temporal |

---

## 3. Stagger Psicoacústico Multi-Capa (Vox Pattern)

Para guiar la atención del espectador de manera natural y evitar sobrecarga cognitiva instantánea, los elementos gráficos deben entrar en secuencia desfasada (*stagger*):

```typescript
// Capa 0: Documento / Base (Frame 0)
const docSpring = spring({
  frame,
  fps,
  config: { damping: 14, mass: 0.8, stiffness: 100 },
});

// Capa 1: Titular Periodístico (Desfase: +3 frames)
const titleFrame = Math.max(0, frame - 3);
const titleSpring = spring({
  frame: titleFrame,
  fps,
  config: { damping: 12, mass: 0.6, stiffness: 120 },
});

// Capa 2: Resaltador Flúor Animado (Desfase: +6 frames)
const highlightFrame = Math.max(0, frame - 6);
const highlightProgress = interpolate(highlightFrame, [0, 15], [0, 100], {
  extrapolateRight: 'clamp',
});
```

---

## 4. Visualización de Datos, HUDs y Prevención de *Layout Shift*

### El Problema de la Vibración Tipográfica
En tipografías proporcionales estándar, los anchos de los glifos numéricos varían sustancialmente (un `1` mide significativamente menos que un `8` o `0`). En contadores rápidos, esto provoca que todo el texto adyacente vibre horizontalmente (*Layout Shift*).

### La Regla Obligatoria `tabular-nums`
En cualquier componente de telemetría, cronómetro o contador de datos:
```css
font-variant-numeric: tabular-nums;
font-feature-settings: "tnum";
font-family: "Inter", "Roboto Mono", "DejaVu Sans Mono", monospace;
```

### Componente Contador Determinista Cuadro a Cuadro
```typescript
export const TabularCounter: React.FC<{ startValue: number; endValue: number; durationFrames: number }> = ({
  startValue,
  endValue,
  durationFrames,
}) => {
  const frame = useCurrentFrame();
  const currentValue = Math.round(
    interpolate(frame, [0, durationFrames], [startValue, endValue], {
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    })
  );

  return (
    <span style={{ fontVariantNumeric: 'tabular-nums', fontFeatureSettings: '"tnum"' }}>
      {currentValue.toLocaleString('es-ES')}
    </span>
  );
};
```

---

## 5. Recetario Maestro de Componentes (Motion Recipes)

### Receta 1: Tactile Paper Parallax 3D & Micro-tilt
Crea una sensación de profundidad física sobre documentos, planos o periódicos:
- Contenedor con `perspective: '1200px'` y `transformStyle: 'preserve-3d'`.
- Cámara con zoom lento $1.0 \to 1.12$ y rotación $Z \in [-1.5^\circ, +0.5^\circ]$.
- Sombra multicapa difusa:
  ```css
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.65), 0 10px 20px rgba(0, 0, 0, 0.4);
  ```

### Receta 2: Kinetic Text Highlight (Subrayador Dinámico)
Simula el trazo manual de un rotulador flúor sobre un documento escaneado:
- Fondo `rgba(250, 204, 21, 0.45)` o `#FACC15` en capa absoluta inferior (`zIndex: 1`).
- Texto tipográfico nítido en capa superior (`zIndex: 2`).
- Ancho animado de $0\%$ a $100\%$ en $15\text{ frames}$ tras el stagger del título.

### Receta 3: Callout Pinpoint con Crosshair Elástico
Fija la atención sobre una coordenada de interés en la escena:
- Círculo de mira exterior de radio $28\text{ px}$ con borde `#FACC15`.
- Mirilla de cruz en 4 cuadrantes.
- Directriz (*Leader Line*) inclinada a $45^\circ$ conectada a la tarjeta de metadatos.
- Pulso armónico continuo: $\text{scale} = 1.0 + \sin(\text{frame} \cdot 0.15) \cdot 0.08$.

### Receta 4: Split Screen Slider Paramétrico
División de pantalla dinámica para comparar dos fuentes o épocas:
```typescript
const splitPosition = interpolate(frame, [0, 45], [0, 50], {
  extrapolateRight: 'clamp',
  easing: Easing.bezier(0.25, 0.1, 0.25, 1),
});
```
- Capa izquierda con `clipPath: \`inset(0 ${100 - splitPosition}% 0 0)\``.
- Capa derecha con `clipPath: \`inset(0 0 0 ${splitPosition}%)\``.
- Línea divisoria vertical de $2\text{ px}$ en `#38BDF8` con sombra de borde.
