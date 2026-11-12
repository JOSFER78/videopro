# Encargo: nombre del canal, comprobado de verdad

Canal de YouTube que explica grandes temas en forma de serie (primer tema: la historia de la humanidad). Lo que lo distingue: en pantalla siempre se ve dónde estás (índice, mapa, eje del tiempo), cada parte es pregunta → explicación → conclusión, hay recapitulaciones, y todo debe quedar clarísimo. Voz maestra en inglés; público también hispanohablante. Diseño sobrio, de agencia; nada infantil ni escolar.

## Por qué se repite el encargo

Los nombres propuestos antes (Meridian, Ariadne, Folio, Lumen…) fallaron: la clienta intentó coger @Meridian y @Ariadne en YouTube y no están disponibles, y además hay docenas de canales con esos nombres. La comprobación anterior (mirar si youtube.com/@Nombre da 404) no sirve por sí sola: YouTube bloquea identificadores reservados o inactivos, y las palabras sueltas corrientes están casi todas cogidas.

## Qué nombre buscamos

- **Distintivo**: una palabra inventada o poco común, o una combinación de dos palabras, que casi nadie use. Es la única forma de que el identificador esté libre y de que el canal se encuentre al buscarlo.
- Fácil de pronunciar y de escribir tras oírlo, en inglés y en español. De 5 a 12 letras si es una palabra; dos palabras cortas si es una combinación.
- Que sugiera orientación, claridad, mapa, pregunta o «entenderlo por fin». No hace falta que lo diga literalmente.
- Sin significados incómodos en inglés ni en español. Que sirva para cualquier tema, no solo historia.
- No vale: nombres de persona, palabras de diccionario muy comunes, nombres que ya usa un canal de divulgación.

## Comprobación obligatoria

Para cada candidato ejecuta:

```
cd /home/user/videopro && python3 scripts/canal/comprobar_nombre.py "Nombre"
```

El script mira si hay canal público en @Nombre y en ocho variantes (@NombreExplains, @NombreDocs…), y lista los canales que el buscador de YouTube devuelve con ese nombre. **Solo puedes proponer un nombre si**: (a) @Nombre no tiene canal público, (b) como mucho una de las variantes existe, y (c) el buscador devuelve como mucho 2 canales que lleven ese nombre, ninguno de divulgación ni con más de 1.000 suscriptores. Si no lo cumple, descártalo y prueba otro. Espera encontrar muchos descartes: prueba al menos 25 candidatos.

Además, para tus finalistas, haz una búsqueda web del nombre (máximo 6 búsquedas en total) para ver si es una marca conocida, una empresa de medios o educación, o una palabra con un significado malo en algún idioma. El registro de marca oficial no se puede comprobar aquí: dilo.

Aun así, deja claro en tu entrega que la disponibilidad real del identificador solo la confirma YouTube al intentar cogerlo.

## Entrega

Escribe en español el archivo que se te indique, con:
1. Tus **5 mejores nombres que pasan la comprobación**, cada uno con: qué significa o de dónde sale, por qué encaja con el canal, cómo se pronuncia en inglés y en español, un lema (EN + ES), el resultado literal resumido del script, lo que encontraste en la búsqueda web y su riesgo.
2. La lista de todos los que probaste y descartaste, con el motivo en pocas palabras.
3. Tu favorito y por qué.

No hagas commit. No toques otros archivos. Informe final de 8 líneas como máximo.
