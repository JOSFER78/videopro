# 📜 PIPELINE AUTÉNTICO VOX: HOMOGRAFÍA 3D, CAPAS TÁCTILES Y FOLEY DIEGÉTICO

Fuente de Verdad extraída de `app/services/vox_authentic_pipeline.py` y `docs/04_investigaciones/motion_y_codigo/` en VideoPro (`/home/ubuntu/workspace/pro/hermes/10_videopro`).

---

## 📐 1. MATEMÁTICAS DE HOMOGRAFÍA 3D (PERSPECTIVA DE DOCUMENTOS)

Para transformar un documento o mapa plano en un plano 3D en perspectiva física (ej. apoyado en una mesa con cámara a 45°):

```python
import numpy as np
from typing import List, Tuple

def find_perspective_coeffs(dst_pts: List[Tuple[float, float]], src_pts: List[Tuple[float, float]]) -> List[float]:
    """
    Calcula los 8 coeficientes de homografía para transformación 3D en perspectiva con PIL.
    dst_pts: coordenadas de destino [(x0,y0), (x1,y1), (x2,y2), (x3,y3)]
    src_pts: coordenadas de origen [(0,0), (w,0), (w,h), (0,h)]
    """
    matrix = []
    for p1, p2 in zip(dst_pts, src_pts):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.matrix(matrix, dtype=float)
    B = np.array(src_pts).reshape(8)
    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8).tolist()
```

---

## 🎨 2. TÉCNICAS VISUALES DE PAPEL Y DOCUMENTOS DE ARCHIVO

1. **Textura de Papel Kraft / Crema Cálido:**
   - Evitar el blanco `#FFFFFF`.
   - Utilizar crema `#F4F1EA` o papel kraft envejecido `#E8DFD1` con ruido gaussiano suave.
2. **Rotación Física Natural:**
   - Todo documento, ficha o recorte debe tener una leve inclinación aleatoria entre **-2.5° y +2.5°** para evitar la sensación de alineación digital rígida.
3. **Resaltado Flúor Animado (*Highlighter Effect*):**
   - Color amarillo flúor: `RGBA(255, 235, 59, 160)` o cian `RGBA(0, 229, 255, 140)`.
   - Modo de fusión: *Multiply* sobre el texto para conservar la legibilidad de la tinta original.
   - Borde irregular con jitter de 1-2px para simular el trazo manual de un rotulador real.
4. **Sello Oficial y Marcas de Archivo (*Classified Stamp*):**
   - Sellos rojos o negros descoloridos (`RGBA(200, 30, 30, 210)`), rotados a 12° con textura de tinta desgastada.

---

## 🔊 3. SINCRONIZACIÓN DE FOLEY DIEGÉTICO (FRAME-ACCURATE)

Cada interacción gráfica en pantalla debe estar acompañada de su correspondiente micro-evento sonoro:

| Evento Visual | Efecto de Sonido (Foley) | Offset de Sincronía |
| :--- | :--- | :--- |
| **Aparición de Documento** | `paper_slide_fast.wav` / `paper_drop.wav` | Frame exacto de inicio |
| **Trazo de Resaltador** | `marker_stroke.wav` (roce sutil de fieltro) | Durante la animación del trazo |
| **Aparición de Sello** | `rubber_stamp_thud.wav` | Frame de impacto visual |
| **Evolución Temporal/Fecha** | `clock_tick_subtle.wav` / `analog_click.wav` | Cada cambio de dígito |
| **Transición de Escena** | `whoosh_organic_air.wav` | -6 frames antes del corte |
