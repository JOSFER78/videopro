# 🌌 Shaders GLSL, WebGL y Transiciones de Alta Energía en HyperFrames / Remotion

> **Pilar:** Efectos Visuales & Renderizado GPU  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA  

---

## 1. Shaders GLSL de Ruido Simplex y Degradados Aurora

Para fondos abstractos orgánicos y perturbaciones biomórficas sin dependencias pesadas de textura:

### Mapeo en GPU
- **`uniform float u_time`**: Tiempo normalizado en segundos (`frame / fps`).
- **`varying vec2 vUv`**: Coordenadas UV normalizadas `[0.0, 1.0]`.

### Código GLSL (Fragment Shader Simplex Noise Aurora)
```glsl
precision highp float;
uniform float u_time;
uniform vec2 u_resolution;
uniform vec3 u_color_a; // e.g. vec3(0.08, 0.12, 0.22)
uniform vec3 u_color_b; // e.g. vec3(0.95, 0.65, 0.20)
varying vec2 vUv;

// Simplex 2D noise
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                     -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy) );
  vec2 x0 = v -   i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
        + i.x + vec3(0.0, i1.x, 1.0 ));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
  m = m*m ;
  m = m*m ;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
  vec3 g;
  g.x  = a0.x  * x0.x  + h.x  * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}

void main() {
    vec2 uv = vUv;
    float noise1 = snoise(uv * 3.0 + vec2(u_time * 0.15, u_time * 0.08));
    float noise2 = snoise(uv * 6.0 - vec2(u_time * 0.12, noise1 * 0.5));
    float combined = smoothstep(-0.2, 0.8, noise1 + noise2 * 0.5);
    
    vec3 color = mix(u_color_a, u_color_b, combined);
    gl_FragColor = vec4(color, 1.0);
}
```

---

## 2. Catálogo de Transiciones WebGL en HyperFrames

En composiciones HTML5/HyperFrames, las transiciones se aplican sobre texturas en canal alfa con duración estándar de **12-18 frames (400-600ms)**:

| Transición | Descripción Técnica | Parámetros Clave |
| :--- | :--- | :--- |
| **`glitch()`** | Aberración cromática con separación de canales RGB y desplazamiento de bloques horizontales aleatorios. | `intensity: 0.7`, `rgbShift: 0.04`, `sliceCount: 16` |
| **`zoomBlur()`** | Desenfoque radial direccional hacia el centro de interés simétrico o focal. | `strength: 0.65`, `center: [0.5, 0.5]`, `iterations: 16` |
| **`lightLeak()`** | Destello analógico cálido estilo lente vintage (celuloide 35mm). | `tint: "#FFA500"`, `blend: "screen"`, `exposure: 1.8` |
| **`whipPan()`** | Barrido horizontal ultrarrápido con motion blur direccional y rebote elástico. | `direction: "right"`, `blurLength: 48px`, `ease: "power3.inOut"` |

---

## 3. Reglas GSAP Seguras para Render Headless

Al renderizar animaciones complejas de GSAP en entornos desatendidos (Puppeteer / Remotion / HyperFrames):

1. **Timeline Pausado Inicialmente**:
   ```javascript
   const tl = gsap.timeline({ paused: true });
   window.__timelines = window.__timelines || {};
   window.__timelines.main = tl;
   ```
2. **Mitigación de "Opacity Poisoning" con `autoAlpha`**:
   - **Regla:** NUNCA usar `opacity: 0` para ocultar elementos entre escenas en timelines reutilizables.
   - **Solución:** Usar `autoAlpha` para combinar `opacity` y `visibility: hidden` evitando colisiones de renderizado y flickers:
   ```javascript
   tl.set("#scene_01", { autoAlpha: 0 }, 2.5);
   tl.set("#scene_02", { autoAlpha: 1 }, 2.5);
   ```
3. **Forzar Primer Ancla (Frame 0 Guarantee)**:
   ```javascript
   tl.set(".layer-root", { autoAlpha: 1, force3D: true }, 0.0);
   ```

---

## 4. Efectos Ópticos Fotorrealistas: Focus Hunt & Roughen Edges

### A. Focus Hunt (Búsqueda de Enfoque Analógico)
Simula el comportamiento de una óptica prime analógica ajustando el foco en directo:
1. **Filtro:** `Camera Lens Blur` con radio de `4` a `8 px`.
2. **Máscara:** Máscara elíptica invertida (*Subtract*) centrada en el sujeto de interés.
3. **Calado (*Feather*):** Calado ultra-amplio de **`300 px`** para una degradación suave sin cortes duros.
4. **Animación:** La máscara se expande o contrae en 0.8s con curva `cubic-bezier(0.25, 1, 0.5, 1)`.

### B. Roughen Edges (Textura de Papel y Fibra Periodística)
Elimina la apariencia de vector digital puro:
- **Borde (*Border*):** `3.3 px` (a resolución 4K).
- **Nitidez (*Sharpness*):** `4.58`.
- **Escala (*Scale*):** `65.0`.
- **Complejidad (*Complexity*):** `10.0`.
- **Influencia Fractal (*Fractal Influence*):** `38%`.
