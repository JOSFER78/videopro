# Hermes Video Factory Verification Checklist

## Verification Steps

1. [ ] Activate virtual environment with required dependencies
2. [ ] Verify scenes.json contains 'text' field (not 'vo_text') for each scene
3. [ ] Confirm audio files exist in /audio/scenes/ for all scenes
4. [ ] Confirm image assets exist in /assets/images/ for all scenes
5. [ ] Check /out/short.mp4 file exists and has reasonable size (>50KB)
6. [ ] Validate video plays and duration matches expected timing
7. [ ] Review console for Python errors during execution

## Common Issues

- **Field Name Mismatch**: KeyError: 'text' occurs when scenes.json uses 'vo_text' but build.py expects 'text'. Fix by ensuring render_from_plan.py outputs 'text' field.

- **Missing Dependencies**: Install missing packages via pip install -e . or pip install required modules.

- **FFmpeg Not Found**: Install FFmpeg for MoviePy operations.

- **Asset Generation Failures**: Verify internet connectivity for image/audio generation APIs.

- **Audio Generation Issues**: Check edge_tts voice names and internet connection.

## Quick Test Command

```bash
cd /path/to/hermes-video-factory
python render_from_plan.py test_plan.json && python build.py --format 9:16 --no-captions
```

If successful, output video will be at out/short.mp4.