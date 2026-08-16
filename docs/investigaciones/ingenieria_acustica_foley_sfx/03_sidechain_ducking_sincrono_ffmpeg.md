# 🎚️ Audio Ducking Procedural en FFmpeg (`sidechaincompress`)

> **Área:** `docs/investigaciones/ingenieria_acustica_foley_sfx/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

```bash
ffmpeg -y \
  -i voiceover.mp3 \
  -i background_music.mp3 \
  -filter_complex \
  "[0:a]asplit=2[vo_main][vo_side]; \
   [1:a]volume=1.0[bgm_base]; \
   [bgm_base][vo_side]sidechaincompress=threshold=0.05:ratio=12.5:attack=10:release=120[bgm_ducked]; \
   [vo_main][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=3[out_audio]" \
  -map "[out_audio]" \
  -c:a aac -b:a 192k output_mixed_ducked.aac
```
