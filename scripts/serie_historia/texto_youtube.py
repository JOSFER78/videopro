#!/usr/bin/env python3
"""
Escribe el texto para YouTube de un episodio (títulos, descripción con marcas de tiempo, fuentes, créditos de imagen y
comentario fijado) a partir del guion y de la configuración ya montada. No publica nada.

    python3 scripts/serie_historia/texto_youtube.py <guion.json> <config_atlas.json> <salida.md>
"""
import json
import sys


def main(guion_path, config_path, out_path):
    G = json.load(open(guion_path, encoding="utf8"))
    C = json.load(open(config_path, encoding="utf8"))
    Y = G["youtube"]
    mmss = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    L = [f"# {G['titulo']} — texto para YouTube (no publicado)", "",
         "> Al subirlo: marcar **«contenido alterado o sintético»** (la voz es sintética).", "",
         "## Títulos (tres opciones)", ""]
    L += [f"{i}. {t}" for i, t in enumerate(Y["titulos"], 1)]
    L += ["", "## Descripción", "", "```", *Y["descripcion"], "", "CAPÍTULOS"]
    for part, p in zip(C["parts"], G["partes"]):
        at = 0 if part is C["parts"][0] else part["at"]
        n = f"{p['step']}. " if p.get("step") else ""
        L.append(f"{mmss(at)} {n}{p['titulo']}")
    L += ["", "FUENTES"]
    vistos = []
    for p in G["partes"]:
        for u in p.get("fuentes", []):
            if u not in vistos:
                vistos.append(u)
    L += [f"· {u}" for u in vistos]
    L += ["", "IMÁGENES"]
    cred = []
    for p in G["partes"]:
        for v in p.get("visuales", []):
            linea = f"· {v['credito_pantalla']} — {v['origen']}"
            if linea not in cred:
                cred.append(linea)
    L += cred
    L += ["", *Y["pie"], "```", "", "## Comentario fijado", "", Y["comentario_fijado"], "",
          "## Notas de contraste de datos", ""]
    L += [f"- {n}" for n in G.get("notas_de_contraste", [])]
    open(out_path, "w", encoding="utf8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
