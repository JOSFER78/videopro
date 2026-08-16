# 🌌 Tratado de Shaders GLSL, Overlays de Grano y Transiciones WebGL

> **Categoría:** Post-Procesamiento Cinemático & Shaders GPU  
> **Ubicación:** `docs/investigaciones/06_motores_generativos_y_benchmarks/` / `docs/nodos_y_motores/programacion/02_remotion_engine_react_hyperframes/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

---

## 📌 1. Fundamentos de Sombreadores en GPU (Fragment & Vertex Shaders)

Los shaders GLSL procesan cada píxel en paralelo directamente en la GPU del renderizador, permitiendo generar efectos orgánicos de fluidos, aberración cromática y deformaciones espaciales que serían imposibles en CPU.

### Parámetros Globales (Uniforms)
- `uniform float u_time`: Factor de progresión temporal derivado del frame.
- `uniform vec2 u_resolution`: Dimensiones del lienzo en píxeles (1920x1080).
- `uniform vec2 u_mouse`: Vector de coordenadas normalizadas de interacción.
- `varying vec2 vUv`: Coordenadas de mapeo UV transferidas del Vertex al Fragment Shader.

---

## 🧪 2. Fragment Shader: Degradado Fluido Procedural con Ruido Simplex

```glsl
uniform float u_time;
varying vec2 vUv;

// Generador Simplex Noise de 2D
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
           -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy) );
  vec2 x0 = v -   i + dot(i, C.xx) ;
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0) ) + i.x + vec3(0.0, i1.x, 1.0) );
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
  m = m*m; m = m*m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 a0 = x - floor(x + 0.5);
  vec3 g = a0.xyx * vec3(m.x, m.y, m.z) + h.xyz * vec3(m.x, m.y, m.z);
  return 130.0 * dot(m, g);
}

void main() {
  vec2 uv = vUv;
  float n1 = snoise(uv * 2.5 + vec2(u_time * 0.12, u_time * 0.18));
  float n2 = snoise(uv * 1.8 - vec2(u_time * 0.08, u_time * 0.14));

  // Paleta de Color Cinemática
  vec3 darkGreen = vec3(0.039, 0.372, 0.274); // #0A5F46
  vec3 cream = vec3(0.956, 0.945, 0.917);     // #F4F1EA
  vec3 deepGraphite = vec3(0.105, 0.105, 0.105); // #1B1B1B

  vec3 col = mix(deepGraphite, darkGreen, n1 * 0.5 + 0.5);
  col = mix(col, cream, clamp(n2 * 0.4, 0.0, 1.0));

  gl_FragColor = vec4(col, 1.0);
}
```

---

## ⚡ 3. Catálogo de Transiciones WebGL Cinemáticas

| Transición | Descripción Matemática | Caso de Uso Óptimo |
| :--- | :--- | :--- |
| **`glitch()`** | Desplazamiento horizontal aleatorio con aberración cromática RGB | Momentos de quiebre narrativo, revelación de datos o saltos temporales |
| **`lightLeak()`** | Destello lumínico cálido con gradiente de exposición y mezcla aditiva | Transición suave entre planos de archivo y planos rodados |
| **`zoomBlur()`** | Desenfoque radial con punto de fuga central y escala exponencial | Avance hacia el núcleo de un mapa o cambio de época histórica |
| **`whipPan()`** | Barrido horizontal ultrarrápido con motion blur direccional | Conexión continua entre dos locaciones geográficas |

---

## 🛡️ 4. Reglas GSAP para Renderizado Headless (Evitar Pantallas Negras)
1. **Línea de Tiempo Pausada:** `const tl = gsap.timeline({ paused: true }); window.__timelines.main = tl;`
2. **Uso Exclusivo de `autoAlpha`:** Previene la contaminación de opacidad entre capas (`tl.set("#scene2", { autoAlpha: 1 }, 3.0)`).
3. **Inyección Forzada del Primer Ancla:** Declarar explícitamente `tl.set("#firstAnchor", { opacity: 1 }, 0.0)`.
