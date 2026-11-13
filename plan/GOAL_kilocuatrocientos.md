# GOAL · Kilocuatrocientos: manual de marca + tráiler + intro + episodio 1

Presupuesto máximo: 4000 créditos de Flow (vídeo). Las imágenes no gastan créditos: probar todo en imagen antes de animar.

## Equipo
- **Orquestador (Opus):** reparte, supervisa, analiza y aprueba. No da nada por bueno sin verlo (fotogramas, capturas, transcripción). Lleva la cuenta de créditos.
- **Agentes Sonnet:** hacen el trabajo, cada uno con una tarea cerrada, archivos de entrada y lo que debe entregar.
- Skills: `canal-episodio`, `flow-realista`, `orquesta`.
- Flow, YouTube Studio y la Mesa se usan **solo desde el navegador de Claude**, una pestaña propia por agente. Nunca se comparte pestaña.
- Nada se publica en YouTube sin el «sí» de la dueña.

## Referencia de marca (ya cerrada, está publicada en el canal Kilocuatrocientos de YouTube)
- **Nombre:** KILOCUATROCIENTOS. «KILO» va en blanco y negrita; «CUATROCIENTOS» va en verde grisáceo y fino, a la misma altura. KILO no debe dominar.
- **Eslogan:** EL MISMO CEREBRO. OTRO MUNDO. Solo en tamaños grandes; nunca en el avatar.
- **Símbolo:** un haz de líneas finas paralelas, de verde menta a verde grisáceo, que llega plano desde la izquierda y sube en vertical a la derecha. Representa el cerebro, que no cambia, frente al mundo, que se dispara.
- **Colores:** antes de fijar los hex definitivos, tomarlos de las imágenes de referencia.
  - Fondo carbón: ~#14171A
  - Verde menta (acento): ~#6FE3B0
  - Verde grisáceo (texto secundario): ~#A9BCAF
  - Blanco frío: ~#ECEEEA
  - Gris de apoyo: ~#6E6F76
  - Nada de naranja, crema ni dorado.
- **Letra:** sans condensada alta para los títulos (probar Oswald 700/300 o similar, la que más se parezca) y sans geométrica espaciada para rótulos y eslogan (Montserrat). Verificar contra la cabecera.
- **Guía en pantalla:**
  - Dónde estás: mapa con el contorno de Natural Earth y un punto menta.
  - Cuándo: eje de puntos de CUÁNDO a HOY.
  - Dato real, con su fuente.
  - Retos.
  - Qué tiene que ver contigo.
  - Iconos de línea fina.
  - Paneles de cristal oscuro.
- **Imagen:** maquetas hiperrealistas en tilt-shift (montañas y valle frente a ciudad de noche), generadas con Nano Banana 2.1.
- **Archivos de referencia:**
  - Avatar publicado: `data/serie_historia/canal/marca/kilo400/avatar_publicado.png`
  - Cabecera publicada (2048×1152): `data/serie_historia/canal/marca/kilo400/cabecera_publicada_2048.jpg`
  - Cabecera base de Flow: `data/serie_historia/canal/marca/kilo400/banner/g7.jpg`
  - Logo: `data/serie_historia/canal/marca/kilo400/logo/l1.jpg`

## Entregables (cada uno se enseña en http://localhost:4173 antes de seguir)
1. **Manual de marca en la Mesa**, en una página nueva «Marca Kilocuatrocientos»:
   - Logo y avatar.
   - Paleta con hex y usos.
   - Tipografías con su escala de tamaños.
   - Iconos.
   - Paneles en pantalla (mapa, eje, dato, reto, Hoy).
   - Miniaturas tipo «EP. 01 /».
   - Plantilla de capítulo.
   - Ejemplos aplicados generados con Nano Banana 2.1, nada dibujado a mano.
   - Las páginas antiguas de colores y letras se marcan como superadas.
2. **Plantilla de gráficos en movimiento** (HTML → vídeo) con esa marca:
   - Quieta hasta que cambia el tema.
   - Mapa de Natural Earth.
   - Captura revisada de cada pantalla.
3. **Intro de productora (4–6 s)**:
   - El haz de líneas llega plano, se dispara hacia arriba y forma el logo.
   - Sonido potente: golpe grave, subida y cierre limpio.
   - Dos propuestas a 360p; solo la elegida se escala.
4. **Tráiler del canal (60 s)**: es la presentación del canal, no de una serie. Debe dejar claro que aquí se explica **cualquier tema** en series (temporadas y capítulos); la historia de la humanidad es solo la primera. Mostrar varios temas posibles.
   - Gancho: «Llevas un cerebro de 1,4 kilos que no ha crecido en 300.000 años».
   - Cómo es un episodio por dentro (las 7 claves de la descripción).
   - Termina con la intro y «Suscríbete».
   - Voz en inglés como pista maestra y pista en español; música y efectos.
5. **Episodio 1** de la primera serie (la historia de la humanidad), siguiendo el flujo de `canal-episodio` con la nueva marca:
   - Primero una prueba de un capítulo (1–3 min) para su visto bueno.
   - Después el episodio completo.
   - Datos con fuente y control de calidad.

## Reglas
- Español claro y breve con la dueña; pocas opciones y bien hechas.
- Todo lo visual, generado (Flow, Nano Banana 2.1). Las capas de datos en HTML siguen la marca.
- Cada fase termina con algo que ella pueda ver y marcar en la Mesa. No se avanza sin su «me vale».
- Al acabar cada fase, apuntar en el registro los créditos gastados y lo que queda de los 4000.
