#!/usr/bin/env python3
"""
Hoja de contactos de las imágenes de un guion, para revisarlas a ojo antes de montar.

    python3 scripts/temario/hoja_contactos.py <guion.json> <salida.jpg>

Cada miniatura lleva el número de la primera frase que la usa. Imprime además la lista
«frase → archivo ← lo que debería verse», que es con lo que se compara. Requiere ffmpeg.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[2] / "templates" / "atlas"


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    guion = json.load(open(argv[1], encoding="utf-8"))
    usos, n = [], 0
    for parte in guion["partes"]:
        for frase in parte["frases"]:
            n += 1
            v = frase.get("visual") or {}
            if v.get("archivo"):
                usos.append((n, v["archivo"], v.get("que_se_ve", ""), frase["texto"]))
    vistos, unicos = set(), []
    for uso in usos:
        if uso[1] not in vistos and (ATLAS / uso[1]).exists():
            vistos.add(uso[1])
            unicos.append(uso)
    for n, archivo, que, texto in usos:
        falta = "" if (ATLAS / archivo).exists() else "  (FALTA EL ARCHIVO)"
        print(f"{n:02d} {os.path.basename(archivo)[:34]:34} ← {que[:58]}{falta}")
    if not unicos:
        print("ninguna imagen asignada")
        return 1
    orden = ["ffmpeg", "-v", "error", "-y"]
    for _, archivo, _, _ in unicos:
        orden += ["-i", str(ATLAS / archivo)]
    columnas = 4
    filtro = "".join(
        f"[{i}:v]scale=480:270:force_original_aspect_ratio=increase,crop=480:270,"
        f"drawtext=text='{unicos[i][0]:02d}':x=10:y=8:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.7[t{i}];"
        for i in range(len(unicos)))
    disposicion = "|".join(f"{(i % columnas) * 480}_{(i // columnas) * 270}" for i in range(len(unicos)))
    if len(unicos) == 1:
        filtro += "[t0]copy"
    else:
        filtro += "".join(f"[t{i}]" for i in range(len(unicos))) + f"xstack=inputs={len(unicos)}:layout={disposicion}:fill=black"
    subprocess.run(orden + ["-filter_complex", filtro, "-frames:v", "1", argv[2]], check=True)
    print(f"{argv[2]}: {len(unicos)} imágenes distintas en {len(usos)} frases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
