#!/usr/bin/env python3
"""
Comprueba que un guion cumple el formato y las reglas de data/serie_historia/guiones/FORMATO.md.

    python3 scripts/temario/validar_guion.py <guion.json> [más guiones…]

Devuelve 0 si todos pasan. Solo librería estándar.
"""

import json
import re
import sys
from pathlib import Path

TEMARIO = Path(__file__).resolve().parents[2] / "data" / "serie_historia" / "temario.json"
MAX_PALABRAS_FRASE = 32


def palabras(texto):
    return len(re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+", texto))


def validar(guion, temario):
    p = []
    codigo = guion.get("codigo", "")
    episodio = next((e for t in temario["temporadas"] for e in t["episodios"] if e["codigo"] == codigo), None)
    if episodio is None:
        return [f"el código {codigo!r} no está en el temario"]
    es_mapa = codigo.endswith("E00")
    for campo in ("canal", "tema", "partes", "indice", "fuentes"):
        if not guion.get(campo):
            p.append(f"falta '{campo}'")
    partes = guion.get("partes") or []
    if not es_mapa and len(partes) != 4:
        p.append(f"deben ser 4 partes, hay {len(partes)}")
    if partes and partes[-1].get("label") != "Repaso":
        p.append("la última parte debe llamarse 'Repaso'")

    total, aprendidos, flows = 0, [], 0
    imagen_puesta = False
    for i, parte in enumerate(partes):
        donde = f"parte {i + 1}"
        for campo, tope in (("label", 3), ("titulo", 7), ("idea", 9)):
            valor = parte.get(campo, "")
            es_repaso = parte.get("label") == "Repaso"
            if not valor and not (es_repaso and campo != "label"):
                p.append(f"{donde}: falta '{campo}'")
            elif palabras(valor) > tope:
                p.append(f"{donde}: '{campo}' tiene más de {tope} palabras")
        frases = parte.get("frases") or []
        if not frases:
            p.append(f"{donde}: sin frases")
            continue
        datos = [f for f in frases if f.get("dato")]
        if len(datos) > 1:
            p.append(f"{donde}: más de un dato")
        sin_cambio = 0
        for j, f in enumerate(frases):
            aqui = f"{donde}, frase {j + 1}"
            n = palabras(f.get("texto", ""))
            total += n
            if n == 0:
                p.append(f"{aqui}: sin texto")
            if n > MAX_PALABRAS_FRASE:
                p.append(f"{aqui}: {n} palabras (máximo {MAX_PALABRAS_FRASE})")
            v = f.get("visual")
            if v:
                sin_cambio = 0
                imagen_puesta = True
                if not v.get("que_se_ve"):
                    p.append(f"{aqui}: la imagen no dice qué se ve")
                if v.get("tipo") == "archivo" and not (v.get("busqueda") or v.get("archivo")):
                    p.append(f"{aqui}: imagen de archivo sin 'busqueda'")
                elif v.get("tipo") == "flow":
                    flows += 1
                    if not v.get("prompt_flow"):
                        p.append(f"{aqui}: recreación sin 'prompt_flow'")
                elif v.get("tipo") not in ("archivo", "flow"):
                    p.append(f"{aqui}: 'tipo' de imagen debe ser archivo o flow")
            else:
                sin_cambio += 1
                if not imagen_puesta:
                    p.append(f"{aqui}: la primera frase del episodio necesita imagen")
                elif sin_cambio > 3:
                    p.append(f"{aqui}: más de tres frases seguidas con la misma imagen")
            if f.get("dato"):
                d = f["dato"]
                if not d.get("rotulo") or not str(d.get("valor", "")):
                    p.append(f"{aqui}: dato sin rótulo o valor")
                if palabras(d.get("comparacion", "")) > 10 or palabras(str(d.get("unidad", ""))) > 4:
                    p.append(f"{aqui}: la comparación del dato pasa de 10 palabras o la unidad de 4 (no caben en la tarjeta)")
                if palabras(d.get("rotulo", "")) > 4:
                    p.append(f"{aqui}: rótulo del dato de más de 4 palabras")
                if not any(x.get("pausa") for x in frases[: j + 1]):
                    p.append(f"{aqui}: el dato necesita antes una pregunta de pausa")
            if f.get("lugar"):
                lugar = f["lugar"]
                if not all(isinstance(lugar.get(k), (int, float)) for k in ("lon", "lat")) or not lugar.get("nombre"):
                    p.append(f"{aqui}: lugar sin nombre o coordenadas")
            if f.get("aprendido"):
                aprendidos.append(f["aprendido"])
                if not 2 <= palabras(f["aprendido"]) <= 9:
                    p.append(f"{aqui}: 'aprendido' debe tener de 2 a 9 palabras")
        if parte.get("label") != "Repaso" and not es_mapa and not any(f.get("aprendido") for f in frases):
            p.append(f"{donde}: no cierra con un 'aprendido'")

    minimo, maximo = (1800, 2100) if es_mapa else (900, 1150)
    if not minimo <= total <= maximo:
        p.append(f"{total} palabras de locución (debe estar entre {minimo} y {maximo})")
    if len(aprendidos) > (9 if es_mapa else 3):
        p.append(f"demasiados 'aprendido': {len(aprendidos)}")
    if flows > (12 if es_mapa else 4):
        p.append(f"demasiadas recreaciones con Flow: {flows}")
    primera = (partes[0].get("frases") or [{}])[0].get("texto", "") if partes else ""
    if not es_mapa and codigo[-2:] != "01" and "?" not in primera + " " + ((partes[0].get("frases") or [{}, {}])[1].get("texto", "") if partes and len(partes[0].get("frases") or []) > 1 else ""):
        p.append("debe abrir recuperando el episodio anterior con una pregunta")
    if not (guion.get("indice") or {}).get("conclusion"):
        p.append("falta la conclusión del índice")
    for f in guion.get("fuentes") or []:
        if not str(f.get("url", "")).startswith("http"):
            p.append(f"fuente sin URL: {f.get('afirmacion', '')[:40]}")
    return p


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    temario = json.load(open(TEMARIO, encoding="utf-8"))
    fallo = False
    for ruta in argv[1:]:
        try:
            guion = json.load(open(ruta, encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"{ruta}: no se puede leer ({exc})")
            fallo = True
            continue
        problemas = validar(guion, temario)
        n = sum(palabras(f.get("texto", "")) for parte in guion.get("partes", []) for f in parte.get("frases", []))
        if problemas:
            fallo = True
            print(f"{ruta}: {len(problemas)} problema(s)\n  " + "\n  ".join(problemas))
        else:
            print(f"{ruta}: correcto ({n} palabras)")
    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
