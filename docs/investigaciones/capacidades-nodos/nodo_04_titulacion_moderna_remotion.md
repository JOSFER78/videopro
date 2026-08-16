# 💎 Nodo 04: Motion Graphics & Titulación Remotion 4.x (Vox / Johnny Harris Style)

## 🎯 Misión del Nodo
Renderizar capas gráficas, animaciones de mapas, documentos de archivo y tipografía cinética utilizando el motor **Remotion 4.x (React 18)** con Video-as-Code. Queda **terminantemente prohibido** el uso de cajas planas primitivas (`drawbox` de FFmpeg).

---

## 🎨 Paleta Cromática y Tokens Oficiales del Cuaderno
* 📜 **Fondo Crema de Papel:** `#F4F1EA` / `#FDF8F0` (nunca blanco puro).
* 🖋️ **Texto Principal:** `#2D2D2D` (gris tinta de imprenta).
* 🟡 **Resaltador Sweep (Highlighter):** Amarillo rotulador `#FFC924` con animación `width: 0% -> 100%` en 0.6s con física `power2.out`.
* 🔴 **Rutas de Mapas y Alerta:** Rojo de tinta `#E7040C` con trazo segmentado (*dash: 78*) y efecto de absorción `blur(1px)`.
* 🌲 **Acentos Topográficos:** Verde Tierra (`#0A5F46`) y Tono Archivo Latte (`#C49B76`).

---

## ⚙️ Reglas de Animación y Composición
1. **Choppy Motion (12-18 fps):**
   * Los gráficos, mapas y recortes se animan a 12 fps con físicas elásticas `spring({ stiffness: 120, damping: 14 })` para mantener la textura táctil analógica sobre el fondo de vídeo fluido.
2. **Loop de Textura de Papel:**
   * Textura de papel arrugado en ciclo de 2.5 cambios por segundo con modo de fusión `overlay` y opacidad al **27%**.
3. **Bordes Rugosos (*Roughen Edges*):**
   * Desgaste de fibra de 3.3px y nitidez 4.58 en recortes de prensa y documentos.
4. **Subtítulos "Burned Karaoke":**
   * Bloques `UPPERCASE bold` de máximo 2 palabras por línea, sincronizados con marcas de tiempo fonéticas.
