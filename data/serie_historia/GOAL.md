OBJETIVO: dejar hecho y probado de principio a fin el primer tema del canal «Temario» (nombre provisional): «Historia de la humanidad», con calidad de los mejores canales de divulgación y un formato que nadie más tiene: cada vídeo es un libro con índice, donde siempre se ve dónde estás, qué has aprendido y qué viene.

Repo josfer78/videopro, rama claude/epic-sagan-49cg73. Lee antes data/serie_historia/PROMPT_PILOTO_15MIN.md (reglas de guion, imagen, Flow y voz) y templates/atlas/ (plantilla, render.js, miniatura.js y el ejemplo). Trabaja sin preguntarme; si algo te bloquea de verdad, dilo y sigue con lo demás.

TERMINADO SIGNIFICA (todo comprobable):
1. TEMARIO ESCRITO. data/serie_historia/temario.json con 3 temporadas: T1 «De dónde venimos» (episodio 0 + 9), T2 y T3 con sus episodios titulados. Cada episodio: una idea única, 3-4 partes, lugar, fecha, dato comparativo, pregunta de pausa, «aprendido» y fuentes con URL. Código estable por episodio (T1-E03).
2. GUIONES. Los 10 de la T1 completos, con locución, qué se ve en cada frase y de dónde sale. Cada cifra y fecha contrastada con fuente; lo no contrastado, fuera.
3. VÍDEOS. Por este orden: E00 «El mapa» (15 min) y E01 completos y revisados; después E02-E09 mientras queden créditos de Flow y tiempo. Si no llegas a todos, deja listos guion, imágenes y configuración de los que falten y dime cuáles.
4. SEGUIMIENTO PARA EL ESPECTADOR. Una página web estática (docs/temario/index.html) con las temporadas y episodios, lo que se aprende en cada uno, 3 preguntas de repaso por episodio con respuesta oculta, y casillas de «visto» que se guardan en el navegador. Mismo diseño que los vídeos.
5. PAQUETE DE YOUTUBE por vídeo (sin publicar): 3 títulos, descripción con marcas de tiempo por parte (mismos nombres que en pantalla), fuentes, créditos de imagen con licencia, comentario fijado con la pregunta, 3 miniaturas y el corte vertical de cada parte para Shorts.
6. INFORME FINAL: qué es real y qué recreado en cada vídeo, créditos gastados, qué quedó fuera y por qué, y qué cambiarías.

LISTÓN DE CALIDAD (compruébalo en cada vídeo antes de darlo por bueno):
- La imagen corresponde a lo que se dice en ese segundo. Revísalo extrayendo un fotograma por cada frase y mirándolo.
- Una idea por parte y como mucho una cifra nueva en pantalla a la vez. Rótulos de 1-5 palabras que no repiten la locución.
- Cada parte tiene pregunta de pausa antes de revelar el dato, y cierra con «Aprendido». Cada episodio abre recuperando el anterior con una pregunta y cierra con el índice.
- El índice superior, el minimapa y el eje cronológico se mueven solo cuando la locución se refiere a ellos, y nunca desaparecen.
- render.js pasa la comprobación de maquetación. La voz, transcrita con Whisper, coincide con el guion.
- Nada parece plantilla: cada episodio tiene imágenes, datos y recorrido propios. Diseño sobrio de agencia, nunca infantil ni de diapositivas.

REGLAS:
- Guion antes que imágenes. Descarga solo los archivos que el guion pide, de fuentes libres, con licencia y crédito anotados y en pantalla. Nada «por si acaso».
- Google Flow desde el navegador con mi sesión ya iniciada (si no lo está, párate y dímelo; no pidas contraseñas). Omni Flash 1.2, un plano cada vez, máximo 2 repeticiones. Úsalo para dar vida a imágenes reales de dominio público (se mueven la cámara y la luz, nunca el objeto), para un plano especial de 15 s por episodio y para recrear lo que no existe. No subas a Flow imágenes con derechos: descríbelas y genera una original. Toda recreación lleva «Recreación» en el crédito.
- Voz natural y con emoción; nunca una voz plana.
- No publiques ni subas nada. No cambies el nombre del canal ni el orden de la T1.
- Si la plantilla no hace algo que el formato necesita, amplíala y mantén sus comprobaciones.
- Haz commit en la rama al cerrar cada episodio.

Empieza por el punto 1 y enséñame el temario y el guion del E00 antes de generar ningún vídeo.
