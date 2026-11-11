#!/usr/bin/env python3
"""
Corta un episodio ya montado en un vídeo vertical (1080x1920) por parte, para Shorts.

    python3 scripts/temario/cortes_shorts.py <episodio.mp4> <config.json> <carpeta_salida>

No vuelve a renderizar la plantilla: recoloca en vertical las zonas del vídeo horizontal (escenario,
minimapa, dato y eje cronológico) y rotula arriba el episodio y la parte. Las partes de menos de 20 s
se saltan y las de más de 3 minutos se avisan (YouTube no las trata como Short). Requiere ffmpeg.
"""

import json
import subprocess
import sys
from pathlib import Path

# Zonas de templates/atlas en el vídeo de 1920x1080: (x, y, ancho, alto)
ESCENARIO = (64, 150, 1444, 700)
MAPA = (1532, 150, 324, 392)
DATO = (1532, 558, 324, 292)
EJE = (64, 880, 1792, 150)
FONDO = "0x0c0d0f"


def texto(s):
    return s.replace("\\", "").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def filtro(titulo_episodio, etiqueta_parte, titulo_parte):
    c = lambda z: f"crop={z[2]}:{z[3]}:{z[0]}:{z[1]}"
    return (
        f"color=c={FONDO}:s=1080x1920[bg];"
        f"[0:v]split=4[a][b][c][d];"
        f"[a]{c(ESCENARIO)},scale=1080:-2[st];"
        f"[b]{c(MAPA)},scale=520:-2[mp];"
        f"[c]{c(DATO)},scale=520:-2[dt];"
        f"[d]{c(EJE)},scale=1040:-2[ax];"
        f"[bg][st]overlay=0:400:shortest=1[v1];[v1][mp]overlay=20:960[v2];[v2][dt]overlay=540:960[v3];[v3][ax]overlay=20:1640[v4];"
        f"[v4]drawtext=font='Inter':text='{texto(titulo_episodio)}':x=40:y=150:fontsize=34:fontcolor=0xff4b33,"
        f"drawtext=font='Inter':text='{texto(etiqueta_parte)}':x=40:y=208:fontsize=30:fontcolor=0x9a9ca2,"
        f"drawtext=font='Inter':text='{texto(titulo_parte)}':x=40:y=262:fontsize=68:fontcolor=0xf3f1ec[v]"
    )


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    video, config, salida = argv[1], json.load(open(argv[2], encoding="utf-8")), Path(argv[3])
    salida.mkdir(parents=True, exist_ok=True)
    episodio = config["episodes"][config["episode"] - 1]
    numero = episodio.get("n") or f"{config['episode']:02d}"
    titulo_episodio = f"{config['channel']} · {numero} {episodio['title']}".upper()
    partes = config["parts"]
    hechos = 0
    for i, parte in enumerate(partes):
        inicio = parte["at"]
        fin = partes[i + 1]["at"] if i + 1 < len(partes) else config["duration"]
        dur = fin - inicio
        if dur < 20:
            print(f"parte {i + 1} «{parte['label']}»: {dur:.0f} s, demasiado corta; se salta")
            continue
        if dur > 180:
            print(f"AVISO parte {i + 1} «{parte['label']}»: {dur:.0f} s, pasa de 3 minutos")
        destino = salida / f"{i + 1:02d}_{parte['label'].lower().replace(' ', '_')}.mp4"
        orden = ["ffmpeg", "-y", "-v", "error", "-ss", f"{inicio:.2f}", "-t", f"{dur:.2f}", "-i", video,
                 "-filter_complex", filtro(titulo_episodio, f"Parte {i + 1} de {len(partes)}", parte.get("title") or parte["label"]),
                 "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "160k", "-t", f"{dur:.2f}", str(destino)]
        if subprocess.run(orden).returncode != 0:
            print(f"ERROR al cortar la parte {i + 1}")
            return 1
        hechos += 1
        print(f"{destino}  {dur:.0f} s")
    print(f"{hechos} cortes verticales")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
