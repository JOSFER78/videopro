# 🎛️ Catálogo Maestro de Capacidades (Capabilities)

Las **Capacidades** definen formalmente el **QUÉ** se hace en el pipeline audiovisual, desacoplado de qué motor o proveedor físico lo ejecuta.

| ID Capacidad | Nombre Formal | Categoría | Requerido | Contrato Entrada | Contrato Salida |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `research` | Investigación Factual & Subagentes | `intelligence` | No | `prompt`, `depth` | `dossier`, `facts` |
| `script` | Dirección Creativa & Guion | `intelligence` | Sí | `theme`, `style`, `duration` | `script`, `scenes` |
| `scene_planning` | Planificación y Ruteo de Escenas | `planning` | Sí | `scenes`, `visual_strategy` | `planned_scenes` |
| `voice_generation` | Síntesis Vocal Neural (TTS) | `audio` | Sí | `text`, `voice_id`, `emotion` | `audio_path`, `sample_rate` |
| `speech_to_text` | Transcripción & Word Timestamps (STT) | `audio` | Sí | `audio_path` | `word_timestamps`, `lang` |
| `image_generation` | Síntesis de Imágenes & Keyframes 4K | `visual` | No | `prompt`, `res`, `aspect_ratio` | `image_path` |
| `video_generation` | Generación de Vídeo DiT / Flow | `visual` | Sí | `prompt`, `image_ref`, `duration` | `video_clip_path`, `has_audio` |
| `music_generation` | Composición Musical & BSO | `audio` | No | `genre`, `duration`, `mood` | `music_path` |
| `foley_sfx` | Efectos Acústicos Foley & Ambiente | `audio` | No | `action_prompt`, `duration` | `sfx_path` |
| `subtitle_generation` | Subtítulos Animados Vox Style | `assembly` | No | `word_timestamps`, `font`, `size`| `ass_path`, `srt_path` |
| `post_processing` | Post-Procesado & Efectos 2.5D | `visual` | No | `clips`, `lut` | `processed_clips` |
| `rendering` | Ensamblaje Máster & Auto-Ducking | `assembly` | Sí | `clips`, `voice`, `bgm`, `subs` | `final_video_path`, `duration` |
| `storage` | Almacenamiento Cloud Zero Egress | `infrastructure` | No | `file_path`, `bucket`, `key` | `storage_url`, `etag` |
| `notification` | Notificación & Webhooks | `infrastructure` | No | `job_id`, `status`, `result_url` | `notified` |
