OBJETIVO: dejar hecho y probado de principio a fin el primer tema del canal «Temario» (nombre provisional): «Historia de la humanidad», con calidad de los mejores canales de divulgación y un formato propio: cada vídeo es un libro con índice, donde siempre se ve dónde estás, qué has aprendido y qué viene.

Repo josfer78/videopro, rama claude/epic-sagan-49cg73. Lee antes data/serie_historia/PROMPT_PILOTO_15MIN.md (reglas de guion, imagen, Flow y voz) y templates/atlas/ (plantilla, render.js, miniatura.js, ejemplo). Trabaja sin preguntarme; si algo te bloquea, dilo y sigue con lo demás.

CÓMO TRABAJAR: tú orquestas. Reparte en subagentes Opus (guion, verificación de datos, revisión crítica) y Sonnet (búsqueda de imágenes, configuración, paquetes de YouTube), en paralelo cuando no dependan entre sí. Dales encargos cerrados y comprueba tú lo que devuelven. Flow y el render los llevas tú, de uno en uno.

TERMINADO SIGNIFICA (todo comprobable):
1. TEMARIO. data/serie_historia/temario.json con 3 temporadas: T1 «De dónde venimos» (episodio 0 + 9), T2 y T3 con episodios titulados. Cada episodio: una idea, 3-4 partes, lugar, fecha, dato comparativo, pregunta de pausa, «aprendido» y fuentes con URL. Código estable (T1-E03).
2. GUIONES. Los 10 de la T1 completos: locución, qué se ve en cada frase y de dónde sale. Cada cifra y fecha contrastada; lo no contrastado, fuera.
3. VÍDEOS. Primero E00 «El mapa» (15 min) y E01, completos y revisados; después E02-E09 mientras queden créditos y tiempo. De los que no lleguen, deja guion, imágenes y configuración listos y dime cuáles.
4. SEGUIMIENTO. Página web estática docs/temario/index.html: temporadas y episodios, qué se aprende en cada uno, 3 preguntas de repaso con respuesta oculta y casillas de «visto» guardadas en el navegador. Mismo diseño que los vídeos.
5. PAQUETE DE YOUTUBE por vídeo, sin publicar: 3 títulos, descripción con marcas de tiempo por parte (mismos nombres que en pantalla), fuentes, créditos con licencia, comentario fijado con la pregunta, 3 miniaturas y un corte vertical por parte para Shorts.
6. INFORME: qué es real y qué recreado, créditos gastados, qué quedó fuera y por qué, qué cambiarías.

LISTÓN DE CALIDAD (compruébalo en cada vídeo):
- La imagen corresponde a lo que se dice en ese segundo: extrae un fotograma por frase y míralo.
- Una idea por parte y una sola cifra nueva en pantalla a la vez. Rótulos de 1-5 palabras que no repiten la locución.
- Cada parte: pregunta de pausa antes del dato y cierre con «Aprendido». Cada episodio abre recuperando el anterior con una pregunta y cierra con el índice.
- Índice, minimapa y eje se mueven solo cuando la locución se refiere a ellos y nunca desaparecen.
- render.js pasa su comprobación. La voz, transcrita con Whisper, coincide con el guion.
- Nada parece plantilla: cada episodio tiene imágenes, datos y recorrido propios. Diseño de agencia, nunca infantil ni de diapositivas.

REGLAS:
- Guion antes que imágenes. Descarga solo lo que el guion pide, de fuentes libres, con licencia y crédito anotados y en pantalla.
- Google Flow desde el navegador con mi sesión iniciada (si no lo está, párate y dímelo; no pidas contraseñas). Omni Flash 1.2, un plano cada vez, máximo 2 repeticiones. Sirve para dar vida a imágenes reales de dominio público (se mueven cámara y luz, nunca el objeto), para un plano especial de 15 s por episodio y para recrear lo que no existe. No subas imágenes con derechos: descríbelas y genera una original. Toda recreación lleva «Recreación» en el crédito.
- Voz natural y con emoción; nunca plana.
- No publiques nada. No cambies el nombre del canal ni el orden de la T1.
- Si la plantilla no hace algo que el formato necesita, amplíala y mantén sus comprobaciones.
- Commit en la rama al cerrar cada episodio.

Empieza por el punto 1 y enséñame el temario y el guion del E00 antes de generar ningún vídeo.
