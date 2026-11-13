# Cómo continuar este proyecto en otra conversación

> **ACTUALIZACIÓN 12-11-2026 (noche). Manda sobre lo que viene debajo.**
> - **Canal:** el canal ya no es Panlogia. Ahora se llama **Kilocuatrocientos** (@kilocuatrocientos, https://www.youtube.com/@kilocuatrocientos). Está publicado con cabecera, avatar, nombre y descripción numerada del 01 al 07.
> - **Siguiente trabajo:** está en `plan/GOAL_kilocuatrocientos.md`. Incluye la marca fijada, el equipo (orquestador Opus y agentes Sonnet), el tope de 4000 créditos de Flow y los entregables, en orden: manual de marca, plantilla de gráficos, intro de productora, tráiler y episodio 1.
> - **Referencias de marca:**
>   - `data/serie_historia/canal/marca/kilo400/` (cabecera g7.jpg, logo l1.jpg)
>   - `data/serie_historia/canal/marca/pub/kilo400/avatar.jpg`
> - **Mesa local:** http://localhost:4173. Se arranca con `.claude/launch.json` («mesa»).
> - **Navegador:** usar el de Claude, con una pestaña propia por agente. Otra sesión trabajó a la vez en Flow y en Studio, y se pisaban.
> - **YouTube Studio no deja leer archivos locales.** Para subir imágenes, se cargan desde la URL de flow-content y se componen en un canvas dentro de la página.

Este archivo resume el estado para que una sesión nueva de Claude (por ejemplo, en el ordenador de la dueña del proyecto) siga donde se quedó la anterior. Rama: `claude/epic-sagan-49cg73`.

## Qué es el proyecto

Un canal de YouTube **universal** que explica grandes temas en forma de serie. Primer tema: la historia de la humanidad. La dueña habla español, escribe deprisa y con erratas: respóndele en español, claro y breve.

## Reglas que ha fijado ella (no cambiarlas sin preguntar)

- **No desarrollar nada (guiones, vídeos) hasta acordar el concepto con ella.** Se pule de forma interactiva.
- **No trabajar solo:** orquestar agentes Opus para investigar y analizar, y supervisarlos.
- **Pocas opciones, bien explicadas e investigadas.** Nada de listas largas.
- **Datos reales primero.** Investigar y contrastar antes de montar la serie.
- El canal debe ser **la explicación más clara de internet**: que la gente retenga con visuales, preguntas, conclusiones y ubicación.
- **Formato fijo de serie:** piloto que enseña el índice, capítulos numerados, índice arriba, eje abajo, mapa, pregunta y conclusión en cada parte, dos recapitulaciones, láminas finales con preguntas.
- Capítulos de 15-20 minutos o más. Ningún capítulo dedicado a un solo hallazgo. Sorpresas verdaderas, involuciones con su porqué, cosas inventadas, olvidadas y reinventadas.
- **Voz maestra en inglés**; otros idiomas como pistas de audio. Música y efectos de sonido.
- **Imagen:** fotos y vídeos reales, mejorados con Google Flow desde el navegador con su sesión. Ella ha dicho que se pueden subir a Flow como inspiración aunque no haya permiso; se le avisó del riesgo (condiciones de Google y avisos de derechos en YouTube).
- **Nombre del canal:** universal, que suene a nombre propio, sin «map». Mostrarle siempre los cambios en la Mesa de ideas, no solo en el chat.
- No publicar nada.

## Estado del nombre del canal

- Descartados: Temario, Ariadne, Meridian (no disponibles o muy usados), Lucidario (suena español), frases como Then It Clicked (no son nombres propios), todo lo que lleve «map».
- **Cerrado: Panlogia.** El canal ya está creado en YouTube (comprobado el 12-11-2026 en su Chrome): identificador `@panlogia` reservado, nombre visible «Panlogia ,always see where you are», en la cuenta de Google davidsevilla101. Pendiente menor, si ella quiere: quitar el espacio antes de la coma o dejar el nombre en «Panlogia» a secas (YouTube Studio). Marca registrada sin comprobar.
- Reservas: Holomundi, Omnimundi.
- Para comprobar un nombre: `python3 scripts/canal/comprobar_nombre.py "Nombre"`. Un identificador sin canal público NO garantiza que esté libre; solo lo confirma YouTube.

## La Mesa de ideas (el «mod»)

Página privada donde ella comenta la propuesta: https://claude.ai/artifact/5NYewBQLd1iFrLeLFe42Ez
Fuente: `data/serie_historia/canal/mesa-de-ideas.html`. Para actualizarla desde otra conversación, publicar ese archivo pasando esa dirección como `url` (leerla antes). Ella comenta con la herramienta de comentarios y los envía a Claude; no hay aviso automático, así que conviene leer los comentarios cuando diga «ya».

Contenido actual de la mesa: nombre del canal cerrado (Panlogia), descripción, estilo visual, tono, sonido, qué es el canal, formato fijo, tres títulos de serie (recomendado: «The Human Story»), piloto + 14 capítulos con lo que explica cada uno, maquetas de miniatura y pantallas, y una parte de capítulo de ejemplo.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Investigación (8 bloques con fuentes) | `data/serie_historia/investigacion/B1…B8` |
| Verificación de los 35 datos clave | `data/serie_historia/investigacion/V1_verificacion.md` |
| Competencia, identidad, arquitectura de 14 capítulos, manual narrativo | `data/serie_historia/canal/A…D` |
| Rondas de nombres | `data/serie_historia/canal/E, N1, N2, N3` |
| Informe de estado | `data/serie_historia/INFORME.md` |
| Concepto anterior (rechazado por aburrido): guiones, plantilla, página | `data/serie_historia/guiones/`, `templates/atlas/`, `docs/temario/` |
| Guía para usar Google Flow | `.claude/skills/flow-realista/` |

Los vídeos del concepto anterior (E01-E05) no están en git; se le enviaron por el chat de la sesión original.

## Siguiente paso

1. Nombre del canal: cerrado (Panlogia, `@panlogia`). Solo queda el retoque opcional del nombre visible.
2. Seguir puliendo en la mesa: título de la serie, capítulos, tono.
3. Solo cuando ella lo apruebe: piloto corto. En su ordenador sí se puede abrir Flow con su navegador.
