---
name: flow-realista
description: Úsala cuando haya que generar o animar en Google Flow (Gemini Omni 1.2 Flash, Veo 3.1 Lite, Nano Banana) imágenes o clips de realismo documental para el canal de historia (objetos de museo, yacimientos, paisajes, recreaciones históricas) manteniendo el mismo aspecto entre planos y entre episodios.
---

# Flow realista: vídeo e imagen documental en Google Flow

Esta skill es para el canal documental de historia. Los clips van dentro de un marco ("stage") en un vídeo explicativo y deben parecer **fotografía y rodaje documental real**, nunca "hecho con IA". Cubre cuatro trabajos:
(a) animar una foto real de dominio público moviendo solo cámara y luz; (b) still ultrarrealista de algo sin foto libre;
(c) recreación histórica de 8–15 s; (d) mismo aspecto en los 10–14 clips de un episodio y entre episodios.

Regla general: si algo no está en "Datos comprobados", no lo des por hecho. La interfaz cambia y los modelos se retiran. Antes de un lote grande, abre `https://support.google.com/flow/answer/16352836` y comprueba que nada se ha movido.

## 1. Datos comprobados

Comprobado el 11-11-2026. En la tabla, "suscripción" significa Google AI Plus, Pro o Ultra.

| Dato | Valor | Fuente |
|---|---|---|
| Web de Flow | `https://flow.google.com` (`labs.google/fx/tools/flow` redirige ahí con 308) | comprobación HTTP directa; https://support.google.com/flow/answer/16353333 |
| Omni Flash 1.2: modos | Text to Video, Frames to Video (solo web), Ingredients/References to Video, Video to Video; 16:9 y 9:16 | https://support.google.com/flow/answer/16352836 |
| Omni Flash 1.2: duración | 3–10 s sin suscripción; 3–15 s con suscripción | https://support.google.com/flow/answer/16352836 |
| Omni Extend | Solo con suscripción y Omni Flash 1.2, solo web; añade 3–10 s; admite hasta 3 imágenes de referencia; en clips extendidos no se pueden aplicar los modos insert, remove ni camera edit | https://support.google.com/flow/answer/16352836 · https://support.google.com/flow/answer/16935718 |
| Omni 360p | Cuesta un tercio que 720p; con suscripción, los clips de 360p se escalan a 1080p (a 4K solo en Ultra) | https://support.google.com/flow/answer/16352836 |
| Créditos Omni 1.2 | Hasta 10 s: 1 crédito/s a 360p y 3 créditos/s a 720p. De 11 a 15 s: 2 créditos/s a 360p y 6 créditos/s a 720p. Extend: 1 crédito/s (360p) o 3 créditos/s (720p) por segundo añadido | https://support.google.com/flow/answer/16526234 |
| Escalado de vídeo | Hasta 1080p (suscripción): 0 créditos hasta 10 s y 1 crédito/s a partir de ahí. 4K (solo Ultra): 50 créditos fijos hasta 10 s y 5 créditos/s a partir de ahí | https://support.google.com/flow/answer/16526234 |
| Veo 3.1 Lite | Text to Video y Frames to Video (solo inicial, o inicial + final): 4, 6 u 8 s. Ingredients: solo 8 s. Sin Video to Video ni Extend. 720p | https://support.google.com/flow/answer/16352836 |
| Coste de Veo 3.1 Lite | 10 créditos por clip (5 en Ultra) | https://support.google.com/flow/answer/16526234 |
| Retiradas | Veo Extend se retiró el 5-11-2026. Veo 3.1 Fast, Veo 3.1 Quality y Omni Flash 1.1 se retiran el 5-12-2026. Google recomienda Omni Flash 1.2 o Veo 3.1 Lite | https://support.google.com/flow/answer/16352836 |
| Modelos de imagen | Nano Banana Pro (el que aparece por defecto en la caja de prompt), Nano Banana 2.1 y Nano Banana 2 Lite | https://support.google.com/flow/answer/16352836 · https://support.google.com/flow/answer/16729550 |
| Coste de imagen | No gasta créditos; hay un límite diario por modelo. Nano Banana Pro: 20/100/500 al día (sin plan / Plus y Pro / Ultra). Nano Banana 2.1 y 2 Lite comparten 400/1000/1000. Las generaciones fallidas o bloqueadas no cuentan | https://support.google.com/flow/answer/16729550 |
| Escalado de imagen | 2K: hasta 200 al día en todos los planes. 4K: solo Ultra, hasta 200 al día | https://support.google.com/flow/answer/16729550 |
| Video to Video ("Edit & refine") | Sube un vídeo de hasta 60 s y 1 GB (.mov, .mp4, .avi o .wmv); si dura más de 30 s se recorta a 30. Se edita un tramo de hasta 10 s (15 s con suscripción), con hasta 3 turnos de conversación. Cuesta lo mismo por segundo que una generación. Solo en algunos países | https://support.google.com/flow/answer/16935718 |
| Guardar un fotograma | Pausa el vídeo, pasa el ratón por encima y pulsa "Save frame". El fotograma sirve como ingrediente, frame inicial o frame final | https://support.google.com/flow/answer/16935718 |
| Créditos por plan | 50 créditos diarios para todos, más estos mensuales: Plus 200, Pro 1000, Ultra 10.000 o 25.000. No se acumulan de un mes a otro | https://support.google.com/flow/answer/16526234 |
| Hora punta | Sin suscripción puede que no se pueda generar vídeo entre las 14:00 y las 17:00 UTC, aproximadamente | https://support.google.com/flow/answer/16526234 |
| Límites de ritmo | Mensajes "You're requesting generations too quickly" y "We noticed some unusual activity". Para el segundo: reintenta pasados un par de minutos y desactiva VPN o proxy | https://support.google.com/flow/answer/16353333 |
| Marca de agua | Todo lo que generan Veo, Omni y Nano Banana lleva SynthID (invisible). La marca visible se activa o desactiva en "Visible watermarking" | https://support.google.com/flow/answer/16353333 |
| Etiquetas de control | `<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_0>` y `<VIDEO_REF_0>` están **obsoletas** ("deprecated and unsupported in future models"). Google pide describir con lenguaje natural para qué sirve cada imagen | https://aistudio.google.com/docs/omni |
| Negativos en Omni | No hay un campo aparte: se escriben dentro del prompt ("Do not do X"). Contra los cortes de plano: "In a single continuous shot", "No scene cuts" | https://aistudio.google.com/docs/omni |
| Negativos en Veo | Se describe lo que se quiere en lugar de negar: "a desolate landscape with no buildings or roads", no "no man-made structures" | https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 |
| Personas reales | En Omni no se pueden subir ni editar imágenes de ciertas personas reconocibles | https://aistudio.google.com/docs/omni |
| Plantilla fotorrealista (Gemini imagen) | "A photorealistic [type of shot] of a [subject] in a [setting]. [Light]. Shot from a [camera angle] with a [lens type]." | https://aistudio.google.com/docs/image-generation |
| Divulgación en YouTube | El contenido realista generado o alterado se declara al subirlo, en YouTube Studio, apartado Attributes, opción "AI use". En contenido fotorrealista la etiqueta aparece en el reproductor | https://support.google.com/youtube/answer/14328491 |

**Sin comprobar**. No lo presentes como dato:
- **Ingredientes en Flow.** La ayuda de Flow no da un máximo. La API de Omni admite hasta 6 imágenes, pero eso no tiene por qué valer para la interfaz.
- **Duración total con Extend.** La API dice 30 s y la guía de DeepMind dice 40 s. Flow no lo indica.
- **Tarifa de 11–15 s.** No queda claro si la tarifa alta se aplica a todo el clip o solo a los segundos que pasan de 10. Mira el saldo antes y después de la primera vez.
- **Créditos de un vídeo fallido.** La ayuda no dice si se devuelven. Compruébalo en el historial de créditos (Plus, Pro y Ultra).
- **Datos técnicos de salida.** No hay datos oficiales en Flow sobre fps, resolución exacta en píxeles ni presets de cámara.
- **Audio.** No está confirmado que Flow acepte archivos de audio como referencia. Lo documentado son las "Voices", que solo funcionan con Ingredients.

## 2. Flujo de trabajo

Pasos comunes (los indica la ayuda de Flow): abre un proyecto, pulsa el nombre del modelo en la caja de prompt y elige **Image** o **Video**. En vídeo, elige **Frames** o **Ingredients** y ajusta proporción, número de salidas, modelo y duración. Para traer un asset del proyecto, escribe `@` y su nombre, o usa "Add". Escribe los prompts en inglés: es el único idioma con soporte completo documentado en Omni.

Antes de gastar créditos, revisa siempre esto:
1. **Derechos.** La imagen que subes es de dominio público, CC o generada por el canal (ver sección 7).
2. **Proporción.** La imagen ya está recortada a 16:9, sin bordes, marcos, texto ni logos. Flow solo genera en 16:9 y 9:16.
3. **Prompt completo.** Lleva el Bloque de estilo y el bloque negativo pegados al final.
4. **Duración.** Es la mínima que pide el guion: más segundos, más deriva y más coste.
5. **Lotes.** Número de salidas: 1 para borradores de vídeo, 2–4 para imágenes (las imágenes no gastan créditos).

Qué modelo elegir:

| Necesidad | Modelo y modo | Por qué |
|---|---|---|
| Still de objeto o lugar | Nano Banana Pro (Image) | No gasta créditos, solo límite diario |
| Borrador de vídeo | Omni Flash 1.2, 360p | Un tercio del coste de 720p y escalado a 1080p gratis hasta 10 s (suscripción) |
| Clip de 8 s sin suscripción y sin escalado | Veo 3.1 Lite, 720p | 10 créditos fijos |
| Plano de más de 10 s, Extend o Video to Video | Omni Flash 1.2 | Veo 3.1 Lite no lo soporta |

### (a) Animar una foto real (busto, cráneo fósil, tablilla)
1. Busca la foto en un fondo libre (Wikimedia Commons, Met Open Access, Smithsonian Open Access…). Anota licencia, autor y URL. Usa la mayor resolución disponible.
2. Recórtala a 16:9 fuera de Flow (la guía de Omni pide imágenes de alta resolución). Si es vertical, amplía el fondo con Nano Banana ("extend the neutral background to 16:9, do not alter the object") y comprueba que el objeto queda idéntico.
3. Ve a Video → **Frames** → modelo **Omni Flash 1.2** y arrastra la foto a "+ Add start frame". No pongas frame final si buscas un movimiento simple.
4. Elige 16:9, una salida, **6–8 s** y **360p**.
5. Prompt: la plantilla 4.1 más el Bloque de estilo, el bloque de vídeo y el negativo.
6. Genera, pasa la Lista anti-IA (sección 5) y, si pasa, escálalo a 1080p (gratis con suscripción hasta 10 s).
7. Alternativa barata a 720p: **Veo 3.1 Lite**, Frames, 8 s (10 créditos). Con Veo, escribe el negativo en positivo (sección 3).

### (b) Still ultrarrealista sin foto libre
1. Ve a **Image** → **Nano Banana Pro**, 16:9, 4 salidas.
2. Añade como ingrediente la imagen de estilo del canal correspondiente (`@estilo_objeto` o `@estilo_lugar`, sección 3).
3. Usa la plantilla 4.2 (objeto) o 4.3 (lugar). Describe forma, material, color y desgaste reales según la bibliografía, no "un cráneo antiguo" sin más.
4. Elige la mejor de las 4 y retócala con edición conversacional, cambiando una sola cosa por turno ("make the lighting softer, keep everything else the same").
5. Escálala a **2K** y guárdala en la colección del episodio. Si va a animarse, ya es el frame inicial del trabajo (a).

### (c) Recreación histórica de 8–15 s
1. Primero crea el fotograma clave con Image → Nano Banana Pro y la plantilla 4.4: personas de espaldas o lejos, y la imagen de estilo como ingrediente. Repite hasta que pase la Lista anti-IA. Una imagen no gasta créditos; un vídeo sí.
2. Ve a Video → **Frames** → **Omni Flash 1.2** y pon el fotograma clave como "start frame". Elige **360p** y 8–10 s (o 15 s con suscripción, ver 4.5).
3. Usa **un solo movimiento de cámara** y una acción simple de las figuras. Añade "In a single continuous shot. No scene cuts."
4. Valídalo a 360p, escálalo a 1080p y descárgalo.
5. **Ingredients** (en lugar de Frames) solo si necesitas que un objeto concreto aparezca idéntico en varios planos. Sube el objeto sobre fondo liso, como recomienda la ayuda de Flow, y di en el prompt qué papel tiene.

### (d) Mismo aspecto en 10–14 clips
Sigue la sección 6. En resumen:
- todos los planos parten de stills hechos con la misma imagen de estilo y el mismo bloque;
- los planos encadenados empiezan en el último fotograma bueno del anterior ("Save frame");
- el color final se iguala en postproducción.

## 3. Bloque de estilo del canal

Pégalo **sin cambiar nada** al final de cada prompt de imagen y de vídeo. Si lo cambias, cambia de versión (`ESTILO v2`) y anótalo en el log.

```text
STYLE: Documentary photograph, natural and unretouched. Full-frame camera, 50mm prime lens at f/4, moderate depth of field, true-to-life colour, neutral white balance, gentle contrast with soft highlight roll-off, fine natural film-like grain, slight lens vignetting. Real materials with honest wear: dust, hairline cracks, chips, uneven patina, fingerprints of age. One clear, motivated light source with soft natural falloff. Muted, earthy palette.
```

Solo para vídeo, añade esta línea detrás:

```text
CAMERA: Slow, steady camera with real weight, as if on a dolly or a tripod head, with true parallax. In a single continuous shot. No scene cuts.
```

Bloque negativo para Omni y Nano Banana (Google documenta en Omni el formato "Do not…"):

```text
Do not add any text, captions, labels, logos or watermarks. Do not add music. Do not bend, morph, melt or reshape any object. Do not change the number of objects or people. Do not add lens flares, glow, bloom, HDR or neon colours. Do not make surfaces glossy or plastic.
```

Con **Veo 3.1 Lite**, su guía pide describir lo que se quiere en lugar de negar. Cambia el negativo por esto:

```text
The image is clean and unbranded, with blank surfaces where no writing exists. The objects keep their exact shape and count throughout. Matte, weathered surfaces. Soft, natural light without flares. Quiet room tone only.
```

Palabras que **no** van en el prompt porque empujan al look de render o de IA: `8K`, `4K`, `ultra HD`, `hyper-realistic`, `masterpiece`, `Unreal Engine`, `octane render`, `cinematic lighting`, `epic`, `flawless`, `perfect`. Tampoco apiles marcas de cámara y lente: una sola indicación óptica concreta basta. La resolución se elige en la interfaz, no en el texto.

### Imagen de estilo (se crea una vez y se reutiliza)
1. En un proyecto fijo "CANAL – Estilo", ve a Image → Nano Banana Pro, 16:9, 4 salidas.
2. Crea dos anclas, cada una con este prompt más el Bloque de estilo:
   - **estilo_objeto**: `A photograph of a weathered terracotta oil lamp on a matte mid-grey museum plinth, soft window light from the left, plain dark grey background.`
   - **estilo_lugar**: `A photograph of a dry stone wall and a dirt track in an open Mediterranean landscape under a thin overcast sky, late afternoon.`
3. Elige la que mejor encarne el canal (color apagado, grano fino, nada brillante). Escálala a 2K y renómbrala exactamente `estilo_objeto` o `estilo_lugar`.
4. Para usarla: escribe `@estilo_objeto` o pulsa "Add to Prompt", y añade al prompt: `Use @estilo_objeto only as a reference for colour, light, grain and lens character; do not copy its subject or background.`
5. En vídeo no la uses como ingrediente directo, porque tiende a colarse en el plano. Úsala solo en los stills que luego serán frame inicial.
6. Guarda los archivos y el prompt de las anclas en el repo, junto al log del canal. Así cualquier episodio futuro parte del mismo sitio.

## 4. Plantillas de prompt

Rellena lo que va entre `[ ]` y añade siempre STYLE (+ CAMERA en vídeo) y el negativo.

### 4.1 Animar una foto real (se mueven la cámara y la luz, el objeto nunca)
```text
The provided image is the exact first frame. The [object] is a solid, inanimate [material] object and stays completely still and unchanged for the whole shot: same shape, same surface, same position. Only the camera and the light move. The camera [slow push-in / slow lateral slide left to right / slow orbit of about 15 degrees] over [6–8] seconds, ending on [detail]. [Light change: a soft window light slowly brightens from the left, moving shadows gently across the surface]. Fine dust particles drift in the air. Sound design: quiet museum room tone. No dialogue.
```
**Ejemplo (busto de Napoleón en mármol, foto de dominio público):**
```text
The provided image is the exact first frame. The marble bust of Napoleon Bonaparte is a solid, inanimate white marble sculpture and stays completely still and unchanged for the whole shot: same shape, same surface, same position. Only the camera and the light move. The camera makes a slow push-in over 8 seconds, ending on the carved eyes and brow. A soft window light slowly brightens from the left, moving shadows gently across the polished marble and revealing small grey veins and chips. Fine dust particles drift in the air. Sound design: quiet museum room tone. No dialogue.
```

### 4.2 Still ultrarrealista de un objeto
```text
A photorealistic [close-up / three-quarter view] of [precise object: what it is, material, colour, size, condition, distinctive features] resting on [support] in [setting: museum storeroom / display case / lab bench]. [Light: soft directional light from …]. Shot from a [camera angle] with a [macro / 100mm] lens. A small [scale reference: neutral grey card / museum label without legible text] sits beside it.
```
**Ejemplo (cráneo de Jebel Irhoud, sin foto libre: original generado, rotular "Recreación"):**
```text
A photorealistic three-quarter view of a Middle Stone Age Homo sapiens fossil skull, as found at Jebel Irhoud, Morocco: long, low braincase, a face that is short and flat like a modern human's, a heavy but not continuous brow ridge, mineralised ochre-brown bone with darker patches, fine cracks and missing fragments rebuilt in matte pale plaster, resting on a grey foam block on a lab bench. Soft directional light from a large window on the left. Shot from eye level with a 100mm macro lens. A small neutral grey card sits beside it.
```

### 4.3 Still ultrarrealista de un lugar
```text
A photorealistic [wide / establishing] shot of [place, period, state: ruin or working], [geographic detail: terrain, vegetation, weather]. [Light: time of day, sky]. Shot from [human eye level / low hill] with a [35mm / 28mm] lens. [Signs of real use: mud, puddles, worn paths, moss, soot].
```
**Ejemplo (casa de máquinas Newcomen):**
```text
A photorealistic wide shot of an early 18th-century Newcomen engine house at an English coal mine: a tall, narrow stone building with a massive timber beam protruding from the top of one wall, a brick chimney, a wooden pump rod descending into a shaft, heaps of coal and spoil, muddy cart tracks. Overcast morning light with thin smoke drifting from the chimney. Shot from human eye level with a 35mm lens. Soot stains on the stone, puddles, trampled grass.
```

### 4.4 Recreación histórica con personas (de espaldas o lejos)
```text
A photorealistic [medium-wide] shot from behind / at a distance of [who: role, era, clothing in real fabrics], [action with hands kept simple], in [period setting]. Faces are turned away or too small to read. [Light]. Shot with a [35mm / 50mm] lens at [eye level / over-the-shoulder].
```
**Ejemplo (escriba sumerio presionando una tablilla):**
```text
A photorealistic over-the-shoulder medium shot from behind of a Sumerian scribe, about 2500 BC, with a shaved head and a plain undyed wool kilt, seated cross-legged, pressing a reed stylus into a palm-sized wet clay tablet held in his left hand; rows of wedge-shaped marks are visible but not legible. A mudbrick room with a reed mat and clay jars. Warm daylight from a doorway on the right, dust in the air. Shot with a 50mm lens at shoulder height. His face is turned away from the camera.
```
Para animarlo (Frames, con este still como inicial): `The scribe's right hand slowly presses the stylus into the clay three times; his head and body barely move. The camera stays locked off. Sound design: faint scratching of reed on clay, distant street murmur. No dialogue.`

### 4.5 Plano especial de 15 s (con suscripción: tramo de 11–15 s más caro, ver sección 1)
Úsalo un máximo de una vez por episodio. Haz el borrador siempre a 360p. Un solo movimiento de cámara, en tres tiempos descritos con lenguaje natural.
```text
The provided image is the exact first frame. In a single continuous 15-second shot: first, [start: what we see, camera static or slow]; then, [middle: one camera move continuing in the same direction]; finally, [end: what is revealed, camera settles]. [Elements in motion: smoke, water, a distant figure walking away]. Everything else keeps its shape. Sound design: [ambience]. No dialogue. No scene cuts.
```
**Ejemplo (Newcomen al anochecer; frame inicial: still 4.3 adaptado):**
```text
The provided image is the exact first frame. In a single continuous 15-second shot: first, the camera holds at eye level on the stone engine house while the great timber beam slowly rocks down and up; then, the camera rises steadily like a crane, keeping the beam in frame; finally, it settles high above, revealing the mine yard, coal heaps and a worker with a lantern walking away into the dusk. Thin smoke rises from the chimney; the pump rod moves in rhythm with the beam. Everything else keeps its shape. Sound design: deep wooden creak and hiss of steam on each stroke, wind, distant dog. No dialogue. No scene cuts.
```

## 5. Lista anti-IA (pasarla a cada resultado antes de aceptarlo)

Mira el clip entero a velocidad normal, después fotograma a fotograma en los cambios, y ampliado al 200 %.

| Fallo | Qué mirar | Qué cambiar en el prompt |
|---|---|---|
| Manos | Dedos de más o fundidos, herramientas que atraviesan la mano | Plano más abierto o de espaldas, menos acción manual, "hands hold the stylus firmly and simply" |
| Texto basura | Letras o cuneiformes inventados, carteles, firmas | Negativo de texto; describe "marks are visible but not legible"; recorta o tapa en post |
| Objeto que muta | El busto cambia de rasgos, una tablilla cambia de tamaño o forma, aparecen o desaparecen objetos | Repite "stays completely still and unchanged"; acorta la duración; baja el giro de cámara; menos elementos en el plano |
| Piel o material de plástico | Brillo uniforme, poros borrados, mármol de jabón | "matte, weathered, unretouched", desgaste concreto; quita palabras de calidad |
| Luz imposible | Sombras en dos direcciones, contraluz sin fuente, brillo en el borde de todo | "one motivated light source from the [side]"; nombra la ventana o la puerta |
| Sobresaturación o HDR | Cielos turquesa, naranjas chillones, halos | "muted, earthy palette, neutral white balance"; corrige el color en post |
| Cámara flotante | Deriva sin peso, zoom y giro a la vez, temblor digital | Un solo movimiento: "slow push-in only, on a dolly"; o "locked off" |
| Cortes no pedidos | El modelo mete un segundo plano | "In a single continuous shot. No scene cuts." |
| Caras derretidas | Rostros que cambian en movimiento | Personas de espaldas, lejos o de perfil; cámara estática cerca de las figuras |
| Anacronismos | Ropa, herramientas o arquitectura de otra época | Describe materiales y objetos del periodo; compara con fuentes académicas |
| Audio raro | Música, voces inventadas | "No dialogue", negativo de música; en el montaje se sustituye por la locución |
| Encuadre del stage | El sujeto queda bajo el marco del vídeo explicativo | Pide "subject centred with generous empty margins" |

Si un plano falla dos veces, no lo reintentes una tercera. Cambia el enfoque: plano más simple, still con movimiento de cámara en edición, u otro modelo.

## 6. Coherencia entre planos y episodios

1. **Una sola fuente de estilo.** Usa siempre `estilo_objeto` o `estilo_lugar` y el mismo `STYLE` de la sección 3. Anota la versión en el log.
2. **Primero el still, luego el vídeo.** Cada plano nace de un still aprobado (generado o foto real). Así la paleta y la óptica las decides en imagen, que no gasta créditos.
3. **Plantilla fija por tipo de plano.** No improvises la estructura: cambia solo los corchetes.
4. **Óptica coherente.** Para objetos, macro o 100 mm. Para lugares, 28–35 mm. Para personas, 50 mm. No mezcles dentro de una secuencia.
5. **Encadenar planos.** Si un plano debe continuar al anterior, abre el clip bueno, pausa en el último fotograma limpio, pulsa "Save frame" y úsalo como "start frame" del siguiente. Si está disponible y el plano lo justifica, usa **Extend** (Omni 1.2, con suscripción).
6. **Objetos recurrentes.** Si el mismo objeto sale en varios planos, súbelo como ingrediente sobre fondo liso, con el mismo nombre en todo el episodio (`@tablilla_ur`), y di en el prompt qué hace.
7. **Organización.** Un proyecto por episodio y una colección por secuencia (selecciona con Shift+clic o arrastrando un recuadro). Deja las imágenes de estilo en el proyecto fijo del canal.
8. **Color en post.** Aunque todo salga de Flow, iguala el color en el montaje: un único ajuste base o LUT del canal para todos los clips, grano añadido uniforme si hace falta, y el mismo marco. Corrige en post, no regenerando.
9. **Cierre del episodio.** Copia los prompts aprobados a la biblioteca del canal. El siguiente episodio parte de ahí.

## 7. Derechos y transparencia

- **No subas fotos con copyright** como frame ni como ingrediente: fotos de museo con licencia restrictiva, agencias, libros, webs. Describe el objeto con fuentes y genera un original (plantilla 4.2).
- **Dominio público y CC sí**, con crédito en la descripción del vídeo: autor, institución, licencia y URL. Respeta la condición "SA" o "NC" si la hay. Verifica la licencia en la ficha de la obra, no en buscadores.
- **Rotula "Recreación"** en pantalla en todo plano generado que no sea la foto real animada. En la foto animada, indica "Animación a partir de fotografía de [institución]".
- **YouTube.** Al subir, en YouTube Studio, apartado Attributes, marca "AI use: Yes" cuando haya escenas realistas que no ocurrieron así o lugares reales con metraje generado. Los clips de Flow llevan SynthID y YouTube puede etiquetarlos por su cuenta.
- **Nunca** pongas a una persona real a decir o hacer algo que no dijo o hizo. Nada de diálogo sincronizado de personajes históricos reconocibles. Las caras de figuras famosas solo aparecen a través de obras reales (bustos, retratos de dominio público) animadas por cámara. Omni no admite subir imágenes de ciertas personas reconocibles: no intentes rodear el filtro.
- Ante una duda histórica, la recreación se queda en lo genérico (un escriba, un minero) y no se presenta como retrato de alguien concreto.

## 8. Ritmo y créditos

- **Una generación a la vez.** Espera el resultado, revísalo y deja al menos un minuto antes de la siguiente. No lances lotes en paralelo desde varias pestañas.
- **"We noticed some unusual activity".** Para, espera un par de minutos y desactiva VPN o proxy, como indica la ayuda.
- **"You're requesting generations too quickly".** Para al menos 10–15 minutos. Esta pausa es práctica propia, no un dato oficial.
- **Hora punta.** Sin suscripción, evita las 14:00–17:00 UTC (15:00–18:00 en la España peninsular en horario de invierno).
- **Presupuesto por plano.** Un borrador más un máximo de **2 reintentos**, siempre a 360p. Solo el aprobado se escala. Un plano de 8 s a 360p cuesta 8 créditos, así que el peor caso es unos 24 créditos por plano. Un episodio de 12 planos cabe en unos 300 créditos más el plano especial.
- **Antes de un lote**, mira el saldo de créditos (Plus, Pro y Ultra pueden ver el historial de actividad). Los créditos diarios y mensuales no se acumulan.
- **Modelos que se retiran.** No empieces trabajo nuevo con Veo 3.1 Fast, Veo 3.1 Quality ni Omni Flash 1.1: se retiran el 5-12-2026.

**Log por clip**, obligatorio. Lleva un CSV en la carpeta del episodio con una fila por generación (también las rechazadas):

```text
fecha,episodio,plano,modo,modelo,duracion_s,resolucion,estilo_version,imagen_inicial,ingredientes,prompt_id,creditos,veredicto,fallo_anti_ia,nota
2026-11-11,E07,P03,Frames,Omni Flash 1.2,8,360p,ESTILO v1,napoleon_bust_commons.jpg,-,P03a,8,rechazado,objeto muta,bajar orbit a push-in
```

Guarda el texto completo de cada prompt con su `prompt_id`. Para repetir un buen resultado, reutiliza el prompt literal.

## Correcciones a las notas del repo

Las notas de `docs/04_investigaciones/` son borradores. Esto se ha corregido con la documentación oficial:
- **Etiquetas.** `<FIRST_FRAME>` e `<IMAGE_REF_N>` son etiquetas de la API y Google las declara obsoletas. `[# Sources …]` y `[# References …]` no aparecen en la documentación de Google. En Flow se usan los huecos "Add start frame", "Add end frame" e Ingredients, más `@nombre` y lenguaje natural.
- **Parámetros inventados.** `task` es un parámetro de la API, no de Flow, y Google lo da como último recurso. `--engine omni_flash` no existe.
- **Límites incorrectos.** "10 s máximo" es falso: hoy son 3–15 s con suscripción. Las cifras "7 imágenes", "3 pistas de audio" y "1080p 24–60 fps" no aparecen en la ayuda de Flow.
- **Último fotograma.** Extraerlo con FFmpeg funciona, pero Flow ya tiene "Save frame".
- **Vocabulario.** Se mantiene: evitar "8K", "Unreal", "octane" y "hyper-realistic"; personas de espaldas o de perfil; un solo movimiento de cámara por plano. Se descarta: apilar ARRI, Panavision y destellos anamórficos, y la capa "4K UHD, photorealistic raw footage". Chocan con el look documental de museo, y la resolución se elige en la interfaz.
