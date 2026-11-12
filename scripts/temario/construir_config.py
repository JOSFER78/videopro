#!/usr/bin/env python3
"""
Convierte un guion (JSON) y los tiempos reales de la voz en la configuración de templates/atlas.

    python3 scripts/temario/construir_config.py <guion.json> <marcas.json> <temario.json> <salida.json>

El guion manda: cada frase dice qué se ve, dónde ocurre, cuándo, y si lleva dato, pausa o «aprendido».
Este programa solo coloca cada cosa en el segundo en que la voz la dice. Solo librería estándar.

Guion:
  {codigo, canal, tema, mapa: {bounds}, cola, miniatura,
   partes: [{label, titulo, idea, kicker,
     frases: [{texto, visual: {archivo, credito, focus, zoom}, lugar: {nombre, pais, lon, lat},
               anios_atras, dato: {rotulo, valor, unidad, comparacion}, pausa, pausa_seg,
               aprendido, asoma, indice}]}],
   indice: {kicker, conclusion}}
Marcas: [{start, end}] — una por frase, en orden.
"""

import json
import sys

EJE_HISTORIA = {
    "from": 300000, "to": 10, "title": "Eje cronológico", "note": "años atrás · escala logarítmica",
    "ticks": [{"yearsAgo": y, "label": l} for y, l in [
        (300000, "300.000"), (100000, "100.000"), (30000, "30.000"), (10000, "10.000"), (3000, "3.000"),
        (1000, "1.000"), (300, "300"), (100, "100"), (30, "30"), (10, "hoy")]],
}
MUNDO = [-170, -56, 180, 76]


class GuionError(ValueError):
    pass


def frases_de(guion):
    return [(pi, f) for pi, parte in enumerate(guion["partes"]) for f in parte["frases"]]


def temporada_de(temario, codigo):
    numero = int(codigo.split("-")[0][1:])
    for temporada in temario["temporadas"]:
        if temporada["temporada"] == numero:
            return temporada
    raise GuionError(f"el temario no tiene la temporada de {codigo}")


def construir(guion, marcas, temario):
    frases = frases_de(guion)
    if len(frases) != len(marcas):
        raise GuionError(f"el guion tiene {len(frases)} frases y hay {len(marcas)} marcas de voz")
    for anterior, actual in zip(marcas, marcas[1:]):
        if actual["start"] < anterior["end"]:
            raise GuionError("las marcas de voz se solapan o están desordenadas")

    temporada = temporada_de(temario, guion["codigo"])
    codigos = [e["codigo"] for e in temporada["episodios"]]
    if guion["codigo"] not in codigos:
        raise GuionError(f"{guion['codigo']} no está en el temario")
    con_cero = codigos[0].endswith("E00")
    episodios = [{
        # en el índice de pantalla va el título corto («Nuestro origen»), sin el subtítulo de después de los dos puntos
        "title": e.get("titulo_corto") or e["titulo"].split(":")[0].strip(), "when": (e.get("cuando") or {}).get("texto", ""),
        # el episodio 0 recorre toda la temporada: no ocupa un punto del eje
        "yearsAgo": None if con_cero and i == 0 else (e.get("cuando") or {}).get("anios_atras") or None,
        "n": f"{i if con_cero else i + 1:02d}",
    } for i, e in enumerate(temporada["episodios"])]

    config = {
        "duration": round(marcas[-1]["end"] + guion.get("cola", 6), 2),
        "channel": guion["canal"], "series": guion["tema"],
        "season": f"Temporada {temporada['temporada']} · {temporada['titulo']}",
        "episode": codigos.index(guion["codigo"]) + 1, "episodes": episodios,
        "parts": [], "visuals": [], "map": {"bounds": (guion.get("mapa") or {}).get("bounds", MUNDO), "places": []},
        "data": [], "asks": [], "learned": [], "peek": [],
        "axis": EJE_HISTORIA, "journey": [{"at": 0, "yearsAgo": EJE_HISTORIA["to"]}],
    }

    parte_vista = -1
    indice_en = None
    for (pi, frase), marca in zip(frases, marcas):
        inicio, fin = marca["start"], marca["end"]
        if pi != parte_vista:
            parte = guion["partes"][pi]
            entrada = {"label": parte["label"], "at": 0 if pi == 0 else round(max(0, inicio - 0.3), 2),
                       "title": parte.get("titulo", ""), "idea": parte.get("idea", "")}
            if parte.get("kicker"):
                entrada["kicker"] = parte["kicker"]
            config["parts"].append(entrada)
            parte_vista = pi
            if pi == len(guion["partes"]) - 1 and indice_en is None and not any(f.get("indice") for _, f in frases):
                indice_en = inicio
        if frase.get("indice"):
            indice_en = inicio

        visual = frase.get("visual") or {}
        if not visual.get("archivo") and visual.get("respaldo"):
            # plano de Flow aún sin generar: mientras tanto se ve la imagen real de respaldo
            visual = visual["respaldo"]
        if visual.get("archivo"):
            if not visual.get("credito"):
                raise GuionError(f"imagen sin crédito: {visual['archivo']}")
            v = {"at": round(max(0.4, inicio - 0.3), 2), "src": visual["archivo"], "credit": visual["credito"]}
            for clave in ("focus", "zoom", "start"):
                if clave in visual:
                    v[clave] = visual[clave]
            config["visuals"].append(v)
        if frase.get("lugar"):
            lugar = frase["lugar"]
            config["map"]["places"].append({"at": round(inicio + 0.5, 2), "name": lugar["nombre"], "where": lugar["pais"],
                                            "lon": lugar["lon"], "lat": lugar["lat"]})
        if frase.get("anios_atras"):
            anterior = config["journey"][-1]["at"]
            llegada = round(inicio + 0.8, 2)
            config["journey"].append({"at": llegada, "yearsAgo": frase["anios_atras"],
                                      "travel": round(min(1.8, max(0.3, llegada - anterior)), 2)})
        if frase.get("dato"):
            dato = frase["dato"]
            config["data"].append({"at": round(inicio + dato.get("retraso", 1.0), 2), "label": dato["rotulo"],
                                   "value": dato["valor"], "unit": dato.get("unidad", ""),
                                   "compare": dato.get("comparacion", "")})
        if frase.get("pausa"):
            # la pregunta se muestra en el silencio que la voz deja justo antes de esta frase
            silencio = frase.get("pausa_seg", 2.8)
            config["asks"].append({"at": round(max(0, inicio - silencio), 2), "hold": round(silencio - 0.1, 2),
                                   "kicker": "Pausa y piensa", "text": frase["pausa"]})
        if frase.get("aprendido"):
            config["learned"].append({"at": round(fin + 0.1, 2), "hold": 3.4, "text": frase["aprendido"]})
        if frase.get("asoma"):
            config["peek"].append({"at": round(inicio, 2), "episode": frase["asoma"]})

    if not config["visuals"]:
        raise GuionError("ninguna frase tiene imagen asignada")
    if guion.get("indice"):
        config["index"] = {"at": round(indice_en, 2), "kicker": guion["indice"]["kicker"],
                           "takeaway": guion["indice"]["conclusion"]}
    mini = guion.get("miniatura") or {}
    if mini.get("archivo") or mini.get("ganchos") or mini.get("gancho"):
        ganchos = mini.get("ganchos") or [mini.get("gancho") or [episodios[config["episode"] - 1]["title"]]]
        base = {"seasonNumber": temporada["temporada"], "seasonColor": temporada.get("color", "#ff4b33"),
                "image": mini.get("archivo") or config["visuals"][0]["src"], "kicker": mini.get("antetitulo", "")}
        for clave in ("focus", "zoom", "shift"):
            if clave in mini:
                base[clave] = mini[clave]
        # una miniatura por gancho; la primera línea de cada uno va resaltada
        config["thumbs"] = [{**base, "hook": [{"text": linea, "highlight": i == 0} for i, linea in enumerate(lineas)]}
                            for lineas in ganchos]
    return config


def main(argv):
    if len(argv) != 5:
        print(__doc__)
        return 2
    guion, marcas, temario = (json.load(open(p, encoding="utf-8")) for p in argv[1:4])
    config = construir(guion, marcas, temario)
    json.dump(config, open(argv[4], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{argv[4]}: {config['duration']} s, {len(config['parts'])} partes, {len(config['visuals'])} imágenes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
