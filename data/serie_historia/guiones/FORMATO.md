# Formato de guion

Un archivo por episodio: `data/serie_historia/guiones/<CODIGO>.json` (p. ej. `T1-E03.json`).
El guion manda sobre todo lo demás: de él salen la voz, las imágenes que se buscan, los rótulos y los
tiempos. Se valida con `python3 scripts/temario/validar_guion.py <archivo>`.

```json
{
  "codigo": "T1-E03",
  "canal": "Temario",
  "tema": "Historia de la humanidad",
  "mapa": {"bounds": [-24, -38, 56, 40]},
  "partes": [
    {
      "label": "Rayas cruzadas",
      "titulo": "Un garabato de 73.000 años",
      "idea": "Cueva de Blombos, Sudáfrica",
      "frases": [
        {
          "texto": "En el episodio anterior salimos de África. ¿Recuerdas cuánto ADN neandertal llevamos encima?",
          "emocion": 0.5,
          "visual": {"tipo": "archivo", "que_se_ve": "cráneo Manot 1, visto en el episodio 2", "busqueda": "Manot 1 skull"}
        },
        {
          "texto": "Un dos por ciento. Hoy retrocedemos más: a una cueva de Sudáfrica, hace setenta y tres mil años.",
          "visual": {"tipo": "archivo", "que_se_ve": "entrada de la cueva de Blombos", "busqueda": "Blombos Cave"},
          "lugar": {"nombre": "Cueva de Blombos", "pais": "Sudáfrica", "lon": 21.2225, "lat": -34.4144},
          "anios_atras": 73000
        }
      ]
    }
  ],
  "indice": {"kicker": "Quédate con esto", "conclusion": "Una frase, la idea del episodio."},
  "miniatura": {"antetitulo": "…", "gancho": ["…", "…"], "que_se_ve": "…"},
  "fuentes": [{"afirmacion": "…", "url": "https://…"}]
}
```

## Campos de cada frase

| Campo | Para qué |
|---|---|
| `texto` | Lo que dice la voz. Una frase o dos cortas, **como mucho 32 palabras**. |
| `pronunciacion` | Opcional. El mismo texto escrito como suena, si hay cifras, siglas o nombres extranjeros. |
| `emocion` | 0,45–0,55 narrativo; 0,7–0,9 asombro. Opcional (0,5). |
| `visual` | Qué se ve mientras se dice. `tipo`: `archivo` (foto o vídeo real: da `busqueda`), `flow` (recreación: da `prompt_flow` en inglés) o se omite para mantener la imagen anterior. Siempre `que_se_ve`. |
| `lugar` | Si la frase nombra un sitio nuevo: aparece en el minimapa. |
| `anios_atras` | Si la frase sitúa un momento: la aguja del eje viaja allí. |
| `dato` | `{rotulo, valor, unidad, comparacion}`. El único número grande de la parte. |
| `pausa` | Pregunta que se muestra en un silencio **antes** de esta frase. La frase da la respuesta. |
| `aprendido` | 3–8 palabras que quedan en la tarjeta «Aprendido» al acabar la frase. |

## Reglas

1. **Cuatro partes**; la última se llama `Repaso`. Entre 900 y 1.150 palabras de locución en total
   (unos 7–8 minutos). El episodio 0 es la excepción: 1.800–2.100 palabras.
2. **Abre recuperando el episodio anterior con una pregunta** y respóndela en la frase siguiente.
3. **Una idea por parte.** Cada parte lleva un solo `dato` como mucho, y antes de él una `pausa`.
4. **Cada parte que no es el repaso termina con un `aprendido`**; como mucho tres en el episodio, y
   deben coincidir con los `aprendido` del temario.
5. **La imagen es de lo que se dice.** Cambia de imagen cada una a tres frases. Cada `que_se_ve` es
   algo concreto y nombrable (el objeto, el yacimiento, el museo, el mapa), no «gente antigua».
6. Prioriza `archivo`. Usa `flow` solo para lo que no puede existir en foto (una escena de hace
   50.000 años) y, como mucho, cuatro veces por episodio, una de ellas el plano especial de 15 s.
7. **Solo hechos del temario o con fuente propia** en `fuentes`. Cifras redondas y dichas como se
   dicen en voz alta («trescientos mil años», no «315 ± 34 ka»).
8. Rótulos (`label`, `titulo`, `idea`, `rotulo`, `aprendido`) cortos y que no repitan la locución.
9. Cierra el repaso con las ideas del episodio y una frase que abra el siguiente.
10. Segunda persona, frases cortas, sin muletillas ni «en este vídeo veremos».
