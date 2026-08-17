# 🗺️ Cartografía Táctil y Motion Graphics Estilo Vox & Johnny Harris

> **Pilar:** Animación Cartográfica & Documental Táctil  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA  

---

## 1. Pipeline de Mapas 4K y Textura de Papel Físico

Para lograr la estética documental analógica característica de Vox Media y Johnny Harris:

1. **Mapas Base 4K Vectoriales ($3840 \times 2160\text{ px}$)**:
   - Exportación limpia de capas de países, hidrografía, relieve y topografía desde QGIS u OpenStreetMap Overpass API.
2. **Linear Color Key**:
   - Eliminación del fondo digital plano (`#000000` o `#FFFFFF`) con clave de color lineal para dejar entrever la textura de papel analógico base (`#F4F1EA`, `#F6F3EA` o tono crema cálido `RGB 248, 243, 230`).
3. **Tratamiento Satelital y Viñeteado**:
   - Desaturación al 40%, reducción de contraste digital y viñeteado elíptico perimetral para centrar la mirada.
   - Fórmula de viñeteado continuo de estudio en NumPy (elimina *digital harshness*):
     $$\text{dist}(x, y) = \frac{\sqrt{(x - cx)^2 + (y - cy)^2}}{\sqrt{cx^2 + cy^2}}$$
     $$\alpha_{\text{vignette}} = \left(\text{clip}\left(\frac{\text{dist} - 0.38}{0.62}, 0, 1\right)^{2.2}\right) \times 160.0$$

---

## 2. Trazado de Rutas Punteadas y Efectos de Trazo (Dash=78)

### Parámetros Canónicos de Trazo
- **Efecto de Escritura**: `Trim Paths` animado en **3.0 segundos** ($90\text{ frames}$ a 30fps / $180\text{ frames}$ a 60fps) con curva de desaceleración suave `bezier(0.34, 1.56, 0.64, 1)`.
- **Patrón Punteado (*Dash Pattern*)**: `Dash = 78` puntos de espaciado regular (o longitud `22px` con brecha `12px` en canvas escalado).
- **Grosor de Línea (*Stroke Width*)**: `4.5 px` a resolución 4K nativa (`6.0 px` con borde sombreado de `7.0 px`).
- **Pulso en Punta Activa**: Radio elástico oscilante en la coordenada del cabezal de trazado:
  $$r_{\text{pulse}} = 14 + \sin(\text{prog} \cdot 10\pi) \cdot 5$$

### Algoritmo de Desgaste Procedural de Bordes (*Roughen Edges*)
Efecto analógico estilo *createdaley* implementado en NumPy/PIL para romper la perfección vectorial:
```python
def apply_roughen_edges(image: Image.Image, border: float = 3.3, sharpness: float = 4.58, complexity: int = 10) -> Image.Image:
    w, h = image.size
    alpha = np.array(image.split()[-1], dtype=np.float32)
    y, x = np.ogrid[:h, :w]
    noise = np.zeros((h, w), dtype=np.float32)
    for octave in range(1, complexity + 1):
        freq = 0.015 * (1.8 ** octave)
        weight = 1.0 / (octave ** 0.8)
        noise += (np.sin(x * freq + octave * 1.5) * np.cos(y * freq + octave * 2.3) * weight) * border
        
    dist_x = np.minimum(x, w - x)
    dist_y = np.minimum(y, h - y)
    dist_edge = np.minimum(dist_x, dist_y)
    
    edge_zone = dist_edge < (border * 4.0)
    alpha[edge_zone] = np.clip((alpha[edge_zone] + noise[edge_zone] * sharpness * 15.0), 0, 255)
    image.putalpha(Image.fromarray(alpha.astype(np.uint8)))
    return image
```

---

## 3. DaVinci Resolve Fusion + QGIS: La Regla del Z-Shift `+0.001`

### Eliminación Definitiva de Z-Fighting en 3D
Cuando el mapa satelital base y la máscara vectorial de fronteras/relieve coexisten en el mismo plano tridimensional ($Z = 0$):
- **Causa**: El motor de renderizado nodal de DaVinci Fusion / Three.js produce parpadeos de textura (*Z-fighting*) por indeterminación de profundidad en coma flotante.
- **Solución Canónica Obligatoria**: En el nodo `Imageplane3D` de la capa de contorno/máscara superior, desplazar la traslación $Z$ hacia adelante por exactamente **`+0.001`**.
- **Herramienta Paint (Stroke Tool)**: Modo de trazado continuo con espaciado (*Spacing*) calibrado entre **`0.75` y `0.80`** (nunca multi-stroke desordenado).

---

## 4. Transformaciones Proyectivas 3D (Homografía en Python/PIL)

Para simular el plano de periódico o documento inclinado en un espacio tridimensional:
```python
def find_perspective_coeffs(pa, pb):
    """Calcula coeficientes de transformación proyectiva (8 parámetros) de pb a pa."""
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = np.matrix(matrix, dtype=float)
    B = np.array(pb).reshape(8)
    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)
```

---

## 5. Diseño de HUD Documental y Elementos Gráficos

1. **Top-Left HUD Pill**:
   - `[ ● EXPEDIENTE #0X // UBICACIÓN // AÑO ]` con punto de grabación rojo `#EF4444` y borde cian `#38BDF8`.
2. **Lower-Third Glassmorphism Card**:
   - Fondo `rgba(15, 23, 42, 0.92)` con borde `#38BDF8`, barra de acento vertical amarillo flúor `#FACC15`, título de 32px en negrita, subtítulo de 18px y badge de fuente oficial (`FUENTE: ARCHIVO HISTÓRICO`).
3. **Retículas de Detalle y Tracking**:
   - Anillo exterior amarillo/rojo de radio 36px, mirilla en cruz de 4 segmentos (longitud 20px) y directriz en ángulo de $45^\circ$ hacia tarjeta de telemetría.
4. **Resaltado de Texto Flúor (*Kinetic Highlighter*)**:
   - Capa de subrayado animado `rgba(250, 204, 21, 0.45)` o `(255, 235, 59, 165)` con bordes redondeados y sello `DESCLASIFICADO` en rojo `#DC2626` rotado a $-14^\circ$.

---

## 6. Foley Sonoro Diegético Sincronizado

- **Whoosh de Transición ($0.7\text{s}$)**: Ruido blanco con envolvente sinusoidal $\sin^2(\pi t / 0.7)$.
- **Sonido de Papel / Marcado**: Frecuencia media a $3200\text{ Hz}$ con modulación aleatoria.
- **Impacto Sub-grave de Sello ($0.25\text{s}$)**: Tono senoidal puro a $90\text{ Hz}$ con decaimiento exponencial $e^{-28t}$.
- **Tic-tac de Precisión Horológica ($0.08\text{s}$)**: Frecuencia de $1800\text{ Hz}$ con decaimiento rápido $e^{-90t}$.
