## 5. Matriz de Desambiguación Tecnológica (Hard Boundaries)

Para evitar errores de sintaxis y cruce de dependencias, debes tratar a cada plataforma de video bajo fronteras operativas estrictas e inquebrantables:

| Criterio | Remotion (React) | HyperFrames (HTML-as-Code) | Google Flow (AI Studio) | Estética Vox / Harris (Aesthetic) |
| :--- | :--- | :--- | :--- | :--- |
| **¿Qué es?** | Un framework de desarrollo basado en React. | Un motor de renderizado declarativo basado en código web plano. | Un estudio creativo en la nube potenciado por modelos de Google DeepMind. | Una dirección de arte y ritmo de montaje periodístico y táctil. |
| **Extensión** | `.tsx` / `.ts`. | `.html`. | Sin archivos locales; se interactúa mediante prompts de texto y activos en la nube. | No tiene formato; es una capa de diseño que se aplica *sobre* las otras herramientas. |
| **Librería de Animación** | `@remotion/transitions`, `interpolate()`, `spring()`. | `GSAP (Timeline pausado)` e `HyperShader` para WebGL. | Generación física fluida guiada por texto, `Lasso Tool` y controles de cámara. | Keyframes manuales en software de edición o parámetros adaptados en código. |
| **Renderizado** | CLI de Remotion (`npx remotion render`). | CLI de HyperFrames (`npx hyperframes render`). | Renderizado en servidores de Google. | Compilación final en MP4 a través de FFmpeg. |
| **Sincronía de Audio** | Componente `<OffthreadVideo>` + API de audio local. | Etiquetas `<video>/<audio>` con atributos de datos + CLI local. | Audio y diálogos generados de forma nativa en el renderizado. | Pistas Foley analógicas mezcladas en línea de tiempo (Rampa de 30ms). |

---

## 6. Flujos de Ejecución y Estructura de Archivos

Dependiendo de la plataforma seleccionada por el usuario o sugerida por el enrutador de tareas, debes estructurar los archivos del espacio de trabajo de la siguiente manera:

### A. Flujo de Trabajo en Remotion (React)

- **Inicialización:** `npx create-video --yes --blank my-video`.
- **Estructura del Proyecto:**
  - `Root.tsx`: Registro de composiciones.
  - `src/LowerThird.tsx`: Componente React animado con `useCurrentFrame()`.
  - `src/TitleCard.tsx`: Componente con animaciones `spring` o lineales.
  - `src/theme.ts`: Centralización de colores y timing.

- **Comando de previsualización:** `npm run dev`.
- **Comando de renderizado:** `npx remotion render <composition-id> out/video.mp4`.

### B. Flujo de Trabajo en HyperFrames (HTML-as-Code)

- **Inicialización:** `npx hyperframes init my-video`.
- **Estructura del Proyecto:** línea de tiempo declarativa en `index.html` con clips y atributos de datos.
- **Comando de previsualización:** `npx hyperframes preview`.
- **Comando de renderizado:** `npx hyperframes render`.

### C. Flujo de Trabajo en Google Flow (Nube)

- **Preproducción:** estructurar la screenplay y catalogar personajes, entornos y props.
- **Exportación:** guardar metadatos del plan localmente para persistencia.
- **Edición con Estado:** emplear la Interactions API enviando parámetros `previous_interaction_id` para realizar pases de edición acumutivos.

---

## 7. Mapeo de la Estética Vox por Plataforma

Debes aprender a traducir las características de la dirección de arte Vox de acuerdo al entorno de código o prompting que estés utilizando:

1. **Animación Asimétrica (Choppy Motion a 12 fps)**
   - En Remotion: mantener la composición maestra en 30fps para fluidez de metraje, y envolver los elementos tipográficos cinéticos en un componente personalizado que redondee el frame actual para forzar el ritmo de 12fps.
   - En HyperFrames: controlar el timing mediante selectores de GSAP o posponer el intervalo de actualización de shaders.
   - En Google Flow: añadir frases de pacing al prompt: `stop motion style, claymation aesthetic, choppy frames`.

2. **Focus Hunt (Búsqueda de Enfoque con Máscara de 300px)**
   - En Remotion / HTML-CSS: superponer un contenedor absoluto con un degradado radial inverso y animar la escala del contenedor para simular el colapso del foco.
   - En Google Flow: usar términos ópticos explícitos: `shallow depth of field, 85mm lens bokeh, sharp focus on the main subject with blurred background`.

3. **Texturas y Fondos de Papel Orgánicos**
   - En Remotion / HTML-CSS: alternar de forma síncrona el fondo con texturas de papel crema cálido (`#F4F1EA`) por medio de imágenes locales.
   - En Google Flow: añadir al prompt instrucciones de textura y color: `on a warm cream paper texture background, paper-cut style collage, tactile newspaper snippets`.