# Quick Reference

## 1. Sketch Scene (JSON)
```json
{
  "scenes": [
    {
      "id": "s1",
      "timestamp_start": 0,
      "timestamp_end": 5,
      "duration": 5,
      "visual_prompt": "iPhone 17 Pro Max rear camera module, exploded view, labeled parts",
      "visual_style": "vox_box",
      "audio_prompt": "Narrador: 'Primer paso, retirar los tornillos Phillips #00.'"
    },
    {
      "id": "s2",
      "timestamp_start": 5,
      "timestamp_end": 10,
      "duration": 5,
      "visual_prompt": "Screen adhesive removal with suction cup",
      "visual_style": "vox_box",
      "audio_prompt": "Narrador: 'Ahora usamos una ventosa para levantar la pantalla.'"
    }
    /* Add more scenes until total duration ≈30s */
  ]
}
```

## 2. Generate Assets
- Images: `google_flow.py image "Prompt" -o assets/b-roll-01.jpg --model gemini-omni-flash-preview`
- Voice-over: `edge_tts --text "..." --voice es-ES-ElviraNeural --output assets/voice.wav`
- Sound effects: place .wav files in `assets/sfx/`

## 3. Render Pipeline (FFmpeg)
```bash
# Install FFmpeg (if missing)
sudo apt-get install -y ffmpeg

# Render video from scenes.json
python3 render_from_plan.py --plan my_plan.json

# Compress for Telegram (<50 MB)
ffmpeg -i final_raw.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k final.mp4
```

## 3. Render & Delivery
```bash
# Ensure Telegram CLI installed
sudo apt install telegram-cli

# Send to Telegram
telegram-send --file out/final.mp4 --caption "Vídeo listo! #iPhone17ProMax"
```

## 4. Pitfalls
- **Asset <5KB** → abort with exit 2; verify size before render.
- **Chrome not running on 9222** → launch with `computer_use` and grant permission.
- **Placeholder assets** → must be >5KB; otherwise abort.

# References
- `templates/example_plan.json` – starter scene definitions.
- `scripts/verify_assets.py` – validates size and realness of assets.