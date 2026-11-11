# Episodio 0 · «El mapa» — informe de entrega

Piloto de 14 min 20 s, 1080p, en español. No se ha publicado ni subido nada.

## Qué hay y dónde

| Pieza | Ruta |
|---|---|
| Guion con fuentes, créditos y licencias | `data/serie_historia/ep00_el_mapa.json` |
| Configuración de la plantilla (tiempos reales de la voz) | `templates/atlas/ep00_el_mapa.json` |
| Texto para YouTube | `data/serie_historia/ep00/ep00_youtube.md` |
| Tres miniaturas | `data/serie_historia/ep00/ep00_miniatura_{1,2,3}.png` |
| Vídeo y pista de voz | entregados en la sesión (no están en git: pesan demasiado) |
| Material visual | `templates/atlas/media/ep00/` (carpeta ignorada por git; el origen de cada archivo está en el guion) |

Para rehacerlo: `python3 scripts/serie_historia/montar_episodio.py <guion> <carpeta_wav> voz.wav templates/atlas/ep00_el_mapa.json`
y después `cd templates/atlas && node render.js ep00_el_mapa.json salida.mp4 --audio voz.wav --jobs 4`.

## Planos reales y recreados

- **47 planos, los 47 reales** (fotos, documentos históricos y un vídeo de la NASA). **Ninguna recreación.**
- **Google Flow: 0 clips, 0 créditos gastados.** En la máquina donde se ejecutó esta sesión (contenedor en la nube) Flow
  no tenía sesión de Google iniciada; no se pidieron credenciales ni se intentó entrar. El reparto previsto
  (60–70 % real, 30–40 % Flow) queda por tanto en 100 % real.
- El «plano especial» se resolvió con metraje real: la Tierra de noche del satélite Suomi NPP (NASA), 9,8 s, recortado
  para quitar los rótulos y el logotipo del vídeo original. No es el plano de 15 s hecho con Flow que pedía el encargo.

Planos que ganarían con Flow cuando haya sesión (todos «dar vida» a una imagen de dominio público o CC0, cámara lenta, objeto rígido):
órbita lenta sobre la tablilla del Met; travelling sobre el mapa de Juan de la Cosa hasta América; luz rasante sobre el
Augusto de Prima Porta; y el plano especial de la hoguera a la ciudad.

## Voz

- Chatterbox Multilingual en local (CPU), voz por defecto del modelo, `exaggeration` 0,5 en lo narrativo y 0,8 en las
  nueve cifras y momentos de asombro; `cfg_weight` 0,35 / 0,3. Ritmo final bajado un 6 % (tempo 0,94).
- 126 frases generadas una a una y **transcritas con Whisper**. 47 se repitieron (hasta 6 intentos) porque la
  transcripción no coincidía: palabras deformadas, coletillas añadidas al final o cifras mal dichas (una decía
  «sesenta horas» en lugar de «trescientas»).
- **No he podido escuchar el audio**: lo que está comprobado es que cada frase dice el texto, no cómo suena. La
  naturalidad y la emoción hay que juzgarlas de oído. Es la voz por defecto del modelo, sin voz de referencia en
  español, así que puede tener algo de acento.
- Frases en las que la transcripción aún difiere en una palabra (puede ser fallo de la voz o de Whisper; conviene oírlas):
  `c1_04` («del cráneo»), `c1_10` («rincón»), `c2_06` («Huellas»), `c3_01` («marfil de mamut»), `c4_05` («escalera»),
  `c7_10` («ideas»), `c8_11` («Octava idea»), `z14` («lo reciente»), `z17` («nueve ideas»). Los nombres propios
  (Jebel Irhoud, Xi'an, Qin Shi Huang, James Watt) se escribieron como suenan; Whisper no permite confirmarlos.
- **Sin música ni ambiente**: no tenía una pista de licencia libre comprobada.

## Datos: qué se matizó y qué quedó fuera

Cada fecha y cifra tiene su fuente en el guion (`fuentes` y `notas_de_contraste`). Cambios respecto al primer borrador:

- Hombre León: «más de 400 horas» de talla no se pudo abrir en origen; las fuentes consultadas dan 320, 360 y «más de 370». Se dice **«más de trescientas»**.
- Censo Han del año 2: circulan 57,7 y 59,6 millones. Se dice **«casi sesenta millones»** y el rótulo da el rango.
- Tripulación de Magallanes: de 237 a unos 270 según la fuente. Se dice **«unos doscientos cincuenta»**.
- Del primer vuelo al alunizaje hay 65 años y 7 meses, no 66. Se dice **«menos de sesenta y seis»**.
- Omo Kibish se revisó en 2022 a un mínimo de ~233.000 años; la locución dice «los restos más antiguos que se conocían entonces».

Fuera por no poder contrastarlos: los «11.000 días de trabajo» de la torre de Jericó; una cifra concreta de
población de Uruk (solo fuentes secundarias: se dice «decenas de miles»); la velocidad de la Rocket frente a un caballo;
el porcentaje de la humanidad bajo Roma y Han.

Apoyados solo en Wikipedia (las páginas de museo o revista no se pudieron abrir desde aquí): el rango de edad y las
horas de réplica del Hombre León, los cereales cultivados en Jericó, el 85 % de tablillas administrativas de Uruk y la
cifra de 57,7 millones del censo Han.

## Lo que no salió bien

- **Wikimedia Commons limitó las descargas** desde esta máquina. Varias imágenes están a 960–1.280 px de ancho en vez
  de 1.920 (la Rocket, la réplica de la Victoria, las fábricas de 1820, el cráneo, la cueva, la rueda hidráulica y el
  mapa de Ortelius): en pantalla se ven algo blandas. Se pueden sustituir por los originales sin tocar nada más.
- No conseguí un mapa anterior a 1492 (Fra Mauro). El capítulo 7 empieza sobre la mitad del mapa de Juan de la Cosa que
  muestra el Viejo Mundo y se abre hasta América cuando se nombra a Colón.
- La máquina de Watt es un grabado con poca presencia; es el plano más flojo.
- El Tigris y el Éufrates se ven en una imagen de satélite en falso color (lo indica el crédito); no encontré una en color natural.
- El cráneo de Irhoud es el molde del Smithsonian, no el fósil original (lo indica el crédito).
- La apertura son 50 s sobre una sola imagen (la Tierra del Apolo 17).
- Las imágenes verticales van sobre un fondo desenfocado de la propia foto; funciona, pero un recorte del objeto sobre fondo liso quedaría más limpio.
- En el eje, el capítulo 2 se sitúa en 60.000 años (la salida de África) aunque su hallazgo, las huellas, es de hace ~22.000; la aguja sí viaja hasta esa fecha.

## Cambios en la plantilla

- **Episodio panorámico** (`episode: 0`): el tramo abierto del índice superior avanza del 01 al 09 y enseña los tres pasos de cada capítulo.
- **Minimapa que viaja** de una región a otra (`map.views`) y lugares y datos que caducan (`until`).
- **Repaso final progresivo**: cada fila se enciende cuando se nombra y la frase grande cambia (pregunta → respuesta → siguiente episodio).
- **Vídeo por fotogramas**: los clips se funden y llevan rótulos igual que una foto; `--jobs` reparte el render entre núcleos (14 min en ~20 min).
- **Miniatura** para el episodio 0 y con varias propuestas (`thumbs`).
- La comprobación de maquetación sigue en verde, también con el ejemplo original.

## Qué cambiaría

1. Oír la voz antes de dar nada por bueno y, si no convence, grabar 10 s de una voz de referencia en español y regenerar.
2. Hacer con Flow los cuatro planos de arriba y sustituir las imágenes de baja resolución.
3. Añadir música y ambiente con una pista de licencia comprobada.
4. Partir la apertura en dos o tres imágenes.
