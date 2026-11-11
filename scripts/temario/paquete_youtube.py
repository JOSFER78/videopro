#!/usr/bin/env python3
"""
Genera el texto para YouTube de un episodio (no publica nada).

    python3 scripts/temario/paquete_youtube.py <guion.json> <config.json> <salida.md>

Usa el bloque `youtube` del guion ({titulos: [3], descripcion, comentario}) y los tiempos reales de la
configuración ya montada, para que las marcas de tiempo lleven los mismos nombres que se ven en pantalla.
Solo librería estándar.
"""

import json
import sys


def mmss(seg):
    seg = int(seg)
    return f"{seg // 60}:{seg % 60:02d}"


def marcas(config):
    """Marcas de tiempo por parte. YouTube exige que la primera sea 0:00 y al menos 10 s entre marcas."""
    salida, ultimo = [], None
    for i, parte in enumerate(config["parts"]):
        t = 0 if i == 0 else parte["at"]
        if ultimo is not None and t - ultimo < 10:
            continue
        salida.append((t, parte["label"]))
        ultimo = t
    return salida


def paquete(guion, config):
    yt = guion.get("youtube") or {}
    titulos = yt.get("titulos") or []
    if len(titulos) != 3 or not yt.get("descripcion") or not yt.get("comentario"):
        raise ValueError("el guion necesita 'youtube': {titulos: [3], descripcion, comentario}")
    largos = [t for t in titulos if len(t) > 70]
    if largos:
        raise ValueError(f"títulos de más de 70 caracteres: {largos}")
    creditos, recreaciones = [], 0
    for parte in guion["partes"]:
        for frase in parte["frases"]:
            v = frase.get("visual") or {}
            if v.get("tipo") == "flow" and v.get("archivo"):
                recreaciones += 1
            if v.get("credito") and v.get("archivo"):
                linea = v["credito"] + (f" — {v['pagina']}" if v.get("pagina") else "")
                if linea not in creditos:
                    creditos.append(linea)
    tiempos = marcas(config)
    lineas = [f"# {guion['codigo']} · texto para YouTube", "", "## Títulos (elegir uno)", ""]
    lineas += [f"{i + 1}. {t}" for i, t in enumerate(titulos)]
    lineas += ["", "## Descripción", "", yt["descripcion"], "", "Partes:"]
    lineas += [f"{mmss(t)} {nombre}" for t, nombre in tiempos]
    lineas += ["", f"{config['channel']} · {config['series']} · {config['season']}", "", "Fuentes:"]
    lineas += [f"- {f['afirmacion']}: {f['url']}" for f in guion.get("fuentes", [])]
    lineas += ["", "Imágenes:"] + [f"- {c}" for c in creditos]
    lineas += ["", "## Comentario fijado", "", yt["comentario"], "", "## Al subirlo", ""]
    lineas.append("- Marcar «contenido alterado o sintético»: " + (
        f"SÍ ({recreaciones} recreaciones generadas)." if recreaciones else "no hace falta (no hay recreaciones generadas)."))
    lineas.append("- La voz es sintética: indícalo en la descripción si el canal no lo dice ya.")
    if len(tiempos) < 3:
        lineas.append("- AVISO: menos de 3 marcas válidas; YouTube no mostrará capítulos.")
    return "\n".join(lineas) + "\n"


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    guion, config = (json.load(open(p, encoding="utf-8")) for p in argv[1:3])
    open(argv[3], "w", encoding="utf-8").write(paquete(guion, config))
    print(argv[3])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
