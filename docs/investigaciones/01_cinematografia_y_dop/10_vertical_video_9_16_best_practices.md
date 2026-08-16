Best practices for vertical (9:16) video production in Hermes:

- Use 1080x1920 resolution; pad with `pad=1080:1920:(ow-iw)/2:(oh-ih)/2` to avoid stretching.
- Compute clip durations from narration length; round to one decimal.
- Validate all assets are >5KB before processing.
- Use `ffprobe` to verify duration and size; abort if >50MB.
- Ensure amix output label matches map; rename if needed.
- Add `-loglevel error` to suppress warnings.
- Keep a concat list file for ffmpeg.