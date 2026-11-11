# Prompt maestro — Piloto «La historia de la humanidad en 15 minutos»

Pega este texto como primer mensaje de una sesión de Claude Code que se ejecute **en el equipo donde
está iniciada la sesión de Google** (hace falta el navegador con Google Flow). Rama del repo:
`claude/epic-sagan-49cg73`.

---

## Objetivo

Producir, de principio a fin y sin pedirme nada salvo permisos imprescindibles, el **episodio piloto**
de la serie: toda la historia de la humanidad en **15 minutos (±1)**, en español. El piloto es el
«Episodio 0 · El mapa»: recorre los nueve capítulos de la Temporada 1 a razón de una idea por
capítulo, y sirve de índice de todo lo que vendrá. No lo subas a YouTube ni publiques nada.

Lo que distingue a este canal y no se negocia:

1. **Está organizado como un libro con índice.** En pantalla siempre se ve en qué temporada, episodio
   y parte estamos, dónde ocurrió lo que se cuenta (minimapa) y cuándo (eje cronológico).
2. **Una idea por parte.** Como mucho una cifra nueva en pantalla cada vez. Si un dato no sostiene la
   idea de esa parte, fuera.
3. **Lo que se ve es de lo que se habla.** Cada frase de la locución tiene debajo la imagen real de
   eso mismo (el fósil, el yacimiento, la tablilla, el mapa), no metraje genérico.
4. **Se repasa.** Cada parte cierra con «Aprendido», y el episodio cierra con el índice completo.

## Lo que ya existe en el repo (léelo antes de empezar)

- `templates/atlas/` — la plantilla. `atlas.html` dibuja el índice superior (episodios y partes), el
  escenario con la imagen o el vídeo, el minimapa, el dato comparativo, la tarjeta «Aprendido», la
  pausa «¿…?», el eje cronológico y el índice final. `render.js <config> <salida.mp4> --audio voz.wav`
  genera el vídeo y se niega a hacerlo si algún texto no cabe. `miniatura.js` genera la miniatura.
  `ejemplo_ep1_nuestro_origen.json` es el ejemplo a imitar: mira cómo sincroniza `parts`, `visuals`,
  `map.places`, `data`, `asks`, `learned` y `journey` con los tiempos de la voz.
  `visuals` admite fotos y vídeos (`.mp4`); las rutas son relativas a `templates/atlas/`.
- `app/services/free_media.py` — buscador de material libre (NASA, Internet Archive, Library of
  Congress, Art Institute of Chicago, Openverse). **Solo busca**; devuelve enlace, licencia y crédito.
- `data/serie_historia/serie.json` — mapa de capítulos con una idea por capítulo.

## Orden de trabajo

### 1. Guion (antes de buscar o generar nada)

Escribe `data/serie_historia/ep00_el_mapa.json` con esta forma por parte:
`{label, titulo, idea, locucion, visual: {tipo: "archivo"|"flow", busqueda|prompt, que_se_ve},
lugar: {nombre, pais, lon, lat}, anios_atras, dato: {rotulo, valor, unidad, comparacion},
pregunta_pausa, aprendido, fuentes: [url]}`.

Estructura (≈ 15 min, ≈ 2.000 palabras de locución a ritmo tranquilo):

| Bloque | Duración | Contenido |
|---|---|---|
| Apertura | 0:45 | Una pregunta que se responde al final. Enseña el índice vacío y el eje. |
| 9 capítulos | ~1:25 cada uno | Una idea, un hallazgo o lugar concreto, una fecha, un dato comparativo. |
| Cierre | 1:30 | Las 9 ideas en el índice, respuesta a la pregunta inicial y qué viene en el episodio 1. |

Los nueve capítulos y su idea única: 1 Nuestro origen · 2 Salimos de África · 3 Arte y símbolos ·
4 La agricultura · 5 Ciudades y escritura · 6 Imperios · 7 El mundo se conecta · 8 Ciencia e
industria · 9 El mundo de hoy. Mejora los títulos si encuentras uno con más gancho, pero no cambies
el orden ni añadas capítulos.

Reglas de guion:
- Cada capítulo se ancla en **un objeto o lugar real y nombrable** (un cráneo, una cueva, una
  tablilla, un barco, una máquina, un busto). Nada de generalidades.
- Antes de revelar cada cifra, una pausa de 2–3 s con pregunta («¿Cuántos éramos entonces?»).
- La etiqueta en pantalla nunca repite la frase que se está diciendo: 1–5 palabras.
- **Contrasta cada fecha y cifra con una fuente** (artículo científico, museo, enciclopedia de
  referencia) y guarda la URL en `fuentes`. Si dos fuentes discrepan, usa el rango y dilo.
  Lo que no puedas contrastar, no entra.

### 2. Material visual (solo ahora, y solo lo que pide el guion)

Para cada parte, por este orden de preferencia:

1. **Foto o vídeo real de uso libre** del objeto o lugar exacto. Busca con `free_media.search()` y en
   Wikimedia Commons (haz pausas de varios segundos entre peticiones; limita el ritmo). Si tengo
   claves de Pexels o Pixabay en `config.toml`, úsalas para paisajes y ambiente.
   Guarda solo los archivos elegidos, en `templates/atlas/media/ep00/`, y anota en el guion licencia y
   crédito. CC BY y CC BY-SA exigen crédito en pantalla: va en el campo `credit` de cada visual.
   No descargues nada «por si acaso».
2. **Recreación con Google Flow** cuando no exista imagen libre, o para dar vida a una imagen real.

Cómo usar Flow (https://labs.google/fx/tools/flow, con mi sesión ya iniciada; si no lo está, párate y
dímelo, no pidas contraseñas):
- Modelo **Omni Flash 1.2** (Veo 3.1 Fast/Quality y Omni Flash 1.1 se retiran el 5-dic-2026).
  Formato 16:9. Clips de 3 a 15 s.
- **Dar vida a una imagen real de dominio público**: súbela como primer fotograma y pide un único
  movimiento de cámara lento. Ejemplo — busto de Napoleón: «slow 15-second orbit around the marble
  bust, museum light sliding across the face, shallow depth of field, dust in the light beam, no
  morphing, the sculpture stays perfectly rigid». Lo que se mueve es la cámara y la luz, nunca el
  objeto: un busto que parpadea es justo lo que hace que un vídeo parezca falso.
- **Imágenes con derechos**: no las descargues ni las subas a Flow. Describe con tus palabras el
  objeto o la escena (que no tiene derechos; los tiene la foto) y genera una imagen original.
- **Un plano especial de 15 s**: reserva uno solo para el momento más fuerte del episodio (propuesta:
  la Tierra de noche encendiéndose ciudad a ciudad, o el paso de una hoguera a una ciudad en un único
  movimiento). Hazlo con cuidado y repítelo hasta que quede bien.
- **Coherencia**: genera primero una lámina de estilo con Nano Banana Pro (documental fotográfico,
  luz natural, grano fino, sin texto) y úsala de referencia en todas las recreaciones. Copia literal
  el mismo bloque de estilo al final de cada prompt y añade «no text, no captions, no logos».
- **Ritmo**: un plano cada vez, sin ráfagas; hay bloqueos por «actividad inusual» con uso
  automatizado. Como mucho 2 repeticiones por plano, salvo el plano especial.
- Toda recreación lleva en `credit` la palabra «Recreación». Apúntame cuántos créditos gastas.

Reparto orientativo: 60–70 % foto/vídeo real, 30–40 % Flow. El piloto debería tener entre 10 y 14
clips de Flow, no más.

### 3. Voz

La voz debe sonar natural y con emoción real; nada de voces planas de lector de pantalla. Usa
Chatterbox Multilingual en local (`pip install chatterbox-tts "setuptools<81"`,
`ChatterboxMultilingualTTS.from_pretrained(device=...)`, `generate(texto, language_id="es",
exaggeration=…, cfg_weight=…)`): `exaggeration` 0,45–0,55 en lo narrativo y 0,7–0,9 en los momentos
de asombro. Genera frase a frase y **transcribe cada audio con Whisper** para confirmar que dice el
texto completo (a veces corta el final). Escribe las fechas y los nombres extranjeros como suenan.
Los tiempos reales de cada frase son los que mandan para sincronizar la plantilla.

### 4. Montaje

Convierte el guion en el archivo de configuración de `templates/atlas/` con los tiempos de la voz y
renderiza. Si el piloto necesita algo que la plantilla no hace (más de un episodio activo en el índice
superior, por ejemplo: en el episodio 0 el tramo abierto debe ir avanzando del 01 al 09), amplía la
plantilla; no lo esquives. Mantén la comprobación de maquetación en verde.

Añade música y ambiente solo si tienes una pista de licencia libre comprobada; si no, entrégalo sin
música y dímelo.

### 5. Miniatura

Con `miniatura.js`: imagen real a sangre, insignia `T1 · E00`, antetítulo corto y un gancho de 2–4
palabras con una cifra. Haz tres variantes con ganchos distintos.

### 6. Texto para YouTube (no publiques)

Genera `ep00_youtube.md` con: tres títulos, descripción con **marcas de tiempo por parte** (los mismos
nombres que salen en pantalla), lista de fuentes, créditos de imagen con licencia, y el comentario
fijado con la pregunta del episodio. Recuerda marcar «contenido alterado o sintético» al subirlo.

## Entrega

1. `ep00_el_mapa.mp4` (1080p, 15 ± 1 min) y las tres miniaturas.
2. El guion con fuentes y créditos, y el texto para YouTube.
3. Un informe breve y honesto: qué planos son reales y cuáles recreados, créditos de Flow gastados,
   qué datos quedaron fuera por no poder contrastarlos, qué no salió bien y qué cambiarías.

Antes de dar nada por terminado: mira el vídeo entero fotograma a fotograma en los cambios de parte y
comprueba que la imagen corresponde a lo que se está diciendo en ese instante.
