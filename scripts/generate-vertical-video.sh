#!/bin/bash
# generate-vertical-video.sh - create 9:16 vertical MP4 from image clips + narration
# Usage: generate-vertical-video.sh <asset-dir> <audio_vo.mp3> <output.mp4>
set -euo pipefail

if [ $# -lt 3 ]; then
  echo "Usage: $0 <asset-dir> <audio> <output.mp4>" >&2
  exit 1
fi

ASSET_DIR="$1"
AUDIO="$2"
OUTPUT="$3"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

AUDIO_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO" | cut -d. -f1)
SCENES=$(find "$ASSET_DIR" -maxdepth 1 -name 'v_scene_*.png' | sort)
COUNT=$(echo "$SCENES" | wc -l)
if [ "$COUNT" -eq 0 ]; then echo "No v_scene_*.png in $ASSET_DIR" >&2; exit 1; fi

# equal-ish durations, 6 decimal fractions
BASE=$(awk "BEGIN{print $AUDIO_DUR/$COUNT}")
DURATIONS=()
for i in $(seq 1 $COUNT); do
  if [ $i -eq $COUNT ]; then
    DURATIONS+=("0")
  else
    DURATIONS+=("$BASE")
  fi
done

# create clips with padding for 9:16
for i in $(seq 0 $(($COUNT-1))); do
  SCENE=$(echo "$SCENES" | sed -n "$((i+1))p")
  DUR="${DURATIONS[$i]}"
  ffmpeg -y -loglevel error -loop 1 -i "$SCENE" -t "$DUR" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
    -r 25 -an "$TMPDIR/clip_$((i+1)).mp4"
done

# concat list
CONCLIST="$TMPDIR/concat.txt"
> "$CONCLIST"
for i in $(seq 0 $(($COUNT-1))); do
  echo "file '$TMPDIR/clip_$((i+1)).mp4'" >> "$CONCLIST"
done

VIDEO_ONLY="$TMPDIR/video_only.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$CONCLIST" -c copy "$VIDEO_ONLY"
ffmpeg -y -loglevel error -i "$VIDEO_ONLY" -i "$AUDIO" -c:v copy -c:a aac -b:a 128k -shortest "$OUTPUT"

echo "Created: $OUTPUT"
ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$OUTPUT"