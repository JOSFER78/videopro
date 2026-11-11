#!/usr/bin/env python3
"""
Une las temporadas en data/serie_historia/temario.json y comprueba que el temario es coherente.

    python3 scripts/temario/unir_temario.py

Lee temario_t1.json y temario_t2_t3.json. Falla, sin escribir nada, si un episodio no tiene idea,
si una fecha o cifra no lleva fuente con URL, si los códigos se repiten o si el orden no es cronológico (salvo que el episodio lo explique en
'nota_orden').
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "data" / "serie_historia"
CABECERA = {
    "canal": "Temario",
    "tema": "Historia de la humanidad",
    "presentacion": "Toda la historia humana, una idea cada vez. Cada episodio parte de un objeto real, "
                    "te dice dónde y cuándo ocurrió, y termina con un repaso. Marca lo que vas viendo.",
}


def comprobar(temporadas):
    problemas, vistos = [], set()
    for t in temporadas:
        anterior = None
        for ep in t["episodios"]:
            c = ep["codigo"]
            if c in vistos:
                problemas.append(f"{c}: código repetido")
            vistos.add(c)
            if not c.startswith(f"T{t['temporada']}-E"):
                problemas.append(f"{c}: no pertenece a la temporada {t['temporada']}")
            if not ep.get("titulo") or not ep.get("idea"):
                problemas.append(f"{c}: falta título o idea")
            fuentes = ep.get("fuentes") or []
            if not fuentes or any(not str(f.get("url", "")).startswith("http") for f in fuentes):
                problemas.append(f"{c}: falta fuente con URL")
            es_mapa = c.endswith("E00")
            atras = (ep.get("cuando") or {}).get("anios_atras")
            if not es_mapa:
                if not atras or atras <= 0:
                    problemas.append(f"{c}: 'anios_atras' debe ser mayor que cero")
                elif anterior is not None and atras > anterior and not ep.get("nota_orden"):
                    problemas.append(f"{c}: rompe el orden cronológico")
                else:
                    anterior = atras
                lugar = (ep.get("ancla") or {}).get("lugar") or {}
                if not isinstance(lugar.get("lon"), (int, float)) or not isinstance(lugar.get("lat"), (int, float)):
                    problemas.append(f"{c}: el ancla no tiene coordenadas")
            if t["temporada"] == 1:
                if len(ep.get("repaso") or []) != 3:
                    problemas.append(f"{c}: deben ser 3 preguntas de repaso")
                if not 3 <= len(ep.get("partes") or []) <= 4:
                    problemas.append(f"{c}: deben ser 3 o 4 partes")
                if not ep.get("pregunta_pausa") or not ep.get("aprendido") or not ep.get("dato"):
                    problemas.append(f"{c}: falta pregunta de pausa, 'aprendido' o dato")
    return problemas


def main():
    t1 = json.load(open(BASE / "temario_t1.json", encoding="utf-8"))
    resto = json.load(open(BASE / "temario_t2_t3.json", encoding="utf-8"))
    temporadas = [t1] + resto["temporadas"]
    problemas = comprobar(temporadas)
    if problemas:
        print("Temario incoherente:\n  " + "\n  ".join(problemas))
        return 1
    json.dump({**CABECERA, "temporadas": temporadas}, open(BASE / "temario.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("temario.json:", ", ".join(f"T{t['temporada']} {len(t['episodios'])} episodios" for t in temporadas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
