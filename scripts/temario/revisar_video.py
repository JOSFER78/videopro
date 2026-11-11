#!/usr/bin/env python3
"""
Saca un fotograma del vídeo por cada frase de la locución y los junta en hojas, para comprobar a ojo
que la imagen corresponde a lo que se dice en ese segundo.

    python3 scripts/temario/revisar_video.py <video.mp4> <marcas.json> <prefijo_salida> [por_hoja]

Escribe <prefijo>_1.jpg, _2.jpg… con cada fotograma numerado, e imprime «nº · segundo · frase».
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    video, marcas, prefijo = argv[1], json.load(open(argv[2], encoding="utf-8")), argv[3]
    por_hoja = int(argv[4]) if len(argv) > 4 else 20
    tmp = Path(tempfile.mkdtemp(prefix="revisar-"))
    archivos = []
    for i, m in enumerate(marcas, 1):
        t = (m["start"] + m["end"]) / 2
        destino = tmp / f"{i:03d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-vf",
                        f"scale=480:270,drawtext=text='{i:02d}':x=8:y=6:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.75",
                        str(destino)], check=True)
        archivos.append(destino)
        print(f"{i:02d} · {t:6.1f}s · {m.get('texto', '')[:92]}")
    columnas = 5
    for h in range(0, len(archivos), por_hoja):
        grupo = archivos[h:h + por_hoja]
        orden = ["ffmpeg", "-v", "error", "-y"]
        for a in grupo:
            orden += ["-i", str(a)]
        if len(grupo) == 1:
            filtro = "[0:v]copy"
        else:
            disposicion = "|".join(f"{(i % columnas) * 480}_{(i // columnas) * 270}" for i in range(len(grupo)))
            filtro = "".join(f"[{i}:v]" for i in range(len(grupo))) + f"xstack=inputs={len(grupo)}:layout={disposicion}:fill=black"
        salida = f"{prefijo}_{h // por_hoja + 1}.jpg"
        subprocess.run(orden + ["-filter_complex", filtro, "-frames:v", "1", salida], check=True)
        print(salida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
