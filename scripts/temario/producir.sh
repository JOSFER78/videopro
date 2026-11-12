#!/bin/bash
# Monta un episodio de principio a fin a partir de su guion, su voz ya generada y sus imágenes ya asignadas.
#
#   scripts/temario/producir.sh <CODIGO> <carpeta_voz> <carpeta_salida>
#
# <carpeta_voz> contiene <CODIGO>.wav y <CODIGO>.wav.marcas.json (los escribe voz_guion.py).
# En <carpeta_salida>/<CODIGO>/ deja el vídeo, los cortes verticales y las hojas de revisión;
# en entregas/<CODIGO>/ (dentro del repositorio) las miniaturas y el texto para YouTube.
# Se detiene al primer fallo: guion inválido, texto que no cabe en pantalla, imagen que falta…
set -euo pipefail
COD="$1"; VOZ="$2"; OUT="$3/$COD"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$RAIZ"
GUION="data/serie_historia/guiones/$COD.json"
CONFIG="templates/atlas/$COD.config.json"
mkdir -p "$OUT/shorts" "entregas/$COD"

python3 scripts/temario/validar_guion.py "$GUION"
ffmpeg -v error -y -i "$VOZ/$COD.wav" -af loudnorm=I=-16:TP=-1.5 -ar 44100 "$OUT/voz.wav"
python3 scripts/temario/construir_config.py "$GUION" "$VOZ/$COD.wav.marcas.json" data/serie_historia/temario.json "$CONFIG"
(cd templates/atlas && node render.js "$COD.config.json" "$OUT/master.mp4" --audio "$OUT/voz.wav" --jobs 4)
python3 scripts/temario/revisar_video.py "$OUT/master.mp4" "$VOZ/$COD.wav.marcas.json" "$OUT/revision" 30
(cd templates/atlas && node miniatura.js "$COD.config.json" "$RAIZ/entregas/$COD/miniatura.png")
python3 scripts/temario/paquete_youtube.py "$GUION" "$CONFIG" "entregas/$COD/youtube.md"
python3 scripts/temario/cortes_shorts.py "$OUT/master.mp4" "$CONFIG" "$OUT/shorts"
ffmpeg -v error -y -i "$OUT/master.mp4" -c:v libx264 -crf 23 -preset medium -c:a copy "$OUT/$COD.mp4"
echo "HECHO $COD: $OUT/$COD.mp4 — falta mirar las hojas $OUT/revision_*.jpg"
