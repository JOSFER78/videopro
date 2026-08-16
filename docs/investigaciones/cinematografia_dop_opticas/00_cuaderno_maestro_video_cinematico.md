# CUADERNO MAESTRO — Producción de Vídeo (Video Pro / Hermes)

Fuente única de conocimiento consolidado para TODO el proceso de vídeo: investigación, pre-producción, Google Flow (CDP), Remotion, render, audio/karaoke y entrega Telegram.

## Rutas canónicas
| Elemento | Ruta |
|----------|------|
| Skill maestra | `~/.hermes/skills/creative/videopro/SKILL.md` |
| Pipeline almacenamiento | `references/storage-pipeline.md` |
| Plantilla manifiesto | `templates/project-manifest.json` |
| Proyecto ejecución | `/home/ubuntu/workspace/pro/02-apps-escritorio/hermes-video-factory/` |
| Motor principal | `build.py` (comprime desde scenes.json + vo_durations.json) |
| Plan → scenes | `render_from_plan.py` |
| Estructura | `project_manager.py create` → `projects/YYYY/MM/YYYY-MM-DD_<slug>/v1/` |
| Director creativo | `creative_director.py` (roles: vox_box, documental_epic, plastilina, humor_meme) |
| IA generativa | `google_flow.py` |
| Telegram | `hermes_video_bot.py`, `notify_telegram.py` |
| Remotion | `/home/ubuntu/remotion_app/src/components/` |

## Flujo canónico
INVESTIGACIÓN (BBC/PwC) → PRE-PRODUCCIÓN (Hollywood $1B) → GUION & STORYBOARD → ASSETS → GENERACIÓN IA (Google Flow) → PROGRAMACIÓN (Remotion) → EDICIÓN (FFmpeg) → AUDIO (TTS/karaoke) → RENDER (build.py) → QA → ENTREGA (Telegram)

## Google Flow vía CDP — lecciones
- Prereq: Chrome con `--remote-debugging-port=9222 --remote-allow-origins=*`, login `josferestuido@gmail.com`, Playwright connect_over_cdp.
- **NO usar selectores CSS** (clases `sc-*` dinámicas). Usar texto visible, roles, ARIA.
- reCAPTCHA = contenteditable div → saltar.
- Selector modelo: botón `ULTRA` → dropdown → opción innerText `Gemini Omni Flash` vía page.evaluate().
- Selector generar: `button:has-text("Crear"/"Generar"/"Create"/"Generate")` o `[aria-label*="Crear"]`.
- Selector descargar: `button:has-text("Descargar"/"Download")` o `[aria-label*="Download"]`.
- Espera generación: botón Descargar / `<video>` / textos "generado|completado|listo|download|descarg"; fallback 120s.
- Upload "Añadir archivo multimedia": esperar 5s tras click.
- Motores: Gemini Omni Flash (video+edición, PREFERIDO), Veo 3.1 (fotorrealismo), Nano Banana 2 Lite (imágenes 4K).
- Comandos: `google_flow.py image|video|batch` con `--engine omni_flash|veo`, `--model nanobanana|veo-3.1-generate-preview`.

## Remotion — composición desde scenes.json
1. Validar scenes.json contra scenes_schema.json (`scripts/validate_scenes.py`).
2. Corregir total_frames = suma duraciones.
3. `scripts/generate_composition_fixed.py` → `src/generated/Composition.tsx`.
4. tsconfig: `"jsx": "react-jsx"`.
5. Importar en `src/Composition.tsx`.
Pitfalls: total_frames mismatch, assets inexistentes, JSX react-jsx, estilos inline version-dependent.

## Componentes Vox (Remotion)
Import: `from 'remotion/App/Components'` — VoxScaleSpring/VoxFadeSpring/VoxSlideSpring/VoxRotateSpring/VoxMultiSpring (configs gentle/snappy/bouncy/smooth/stiff), VoxSVGDraw/VoxStaggeredDraw/VoxEasing (12 easings), VoxPictureInPicture/SimplePiP/SlidePiP (4 esquinas+centro, 4 tamaños), VoxDataCard/VoxSlideDataCard/VoxDataCardGrid.

## Render & FFmpeg
- build.py: verify_assets_real() + abort_on_missing_assets() (exit 2), NUNCA placeholder_png.
- Evitar RGB 0,0,0 puro en sintetizados (blackdetect falso) — usar RGB 36,48,72.
- MoviePy 2.x: with_volume_scaled() / with_volume_scaling() (nunca multiply_volume).
- Shot plans audio: shot.get('audio', shot.get('vo', shot.get('audio_file', ''))) + os.path.basename().
- Compresión final: `ffmpeg -i in.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k out.mp4` (<50MB Telegram).

## Audio
- TTS: `python3 -m edge_tts --voice es-ES-AlvaroNeural --text "..." --write-media narration.mp3 --write-subtitles narration.vtt` (+ `--rate +18%` para ajustar a 30s). Instalar en venv (PEP 668).
- Música: Suno/HeartMuLa → bgm.mp3, −18/−22 dB sobre voz.
- Karaoke: timestamps palabra `[{"word","start","end"}]` (Stable-TS/MFA), componente KaraokeSubtitles.tsx + diagnóstico sync.
- SFX: assets/sfx/ .wav sincronizados a keyframes.

## Estilos visuales
1. Vox Box/Diorama 2.5D; 2. Papercut Kraft; 3. Plastilina 12fps; 4. Biological Hyperreal; 5. Documental Épico; 6. Humor Meme.

## Investigación (BBC/PwC)
RESEARCH_DOSSIER.md: fuentes primarias, fact-check ≥2 fuentes, registro evidencia (verificado/hipótesis/especulativo), anti-alucinación. Narrativa 3 actos (0-15% hook, 15-75% desarrollo, 75-100% síntesis).

## Pre-producción (Hollywood $1B)
Briefing: formato (16:9 4K / 9:16 / 1:1), público, tonalidad, ritmo, estilo, duración. scenes.json con scene_id, timestamps, duration, voiceover_text, visual_prompt, motion_graphics, audio_sfx.

## QA & Entrega
- ffprobe: duración/resolución/fps/streams; inspección visual keyframes.
- Telegram: SIEMPRE enviar MP4 + notificación; >50MB → 413, comprimir CRF28+aac96k.
- Mini App: /var/www/videomastery/ estática, API /pro/videomastery-api/ → Flask 9130.

## Reglas de oro
1. Una sola skill: videopro. 2. Cero placeholders, assets >5KB, cero alucinaciones. 3. Autonomía total. 4. Entregar archivo final. 5. Google Flow: selectores texto/ARIA nunca CSS dinámico. 6. Remotion: validar→generar→react-jsx. 7. Notificar MP4 por Telegram al terminar.
