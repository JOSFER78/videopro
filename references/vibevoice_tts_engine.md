# 🎙️ Motor de Voz VibeVoice 1.5B Local y Sincronización VO-First

## 1. Visión General del Motor TTS

VideoPro integra el modelo neural **`microsoft/VibeVoice-1.5b`** ejecutado localmente en el VPS a coste $0.00 USD con la voz de referencia en español **`es-emilio`**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DE AUDIO & PROSODIA VIBEVOICE               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Ingesta de Guion y Etiquetas de Emoción:                                 │
│    "(con entusiasmo) La misión ha comenzado con éxito..."                  │
│                                                                             │
│ 2. Aislamiento de Proceso & File Locking:                                   │
│    fcntl.flock('/tmp/vibevoice_synthesis.lock', LOCK_EX)                    │
│    Venv: /home/ubuntu/vibevoice-venv/bin/python                             │
│    Modelo: microsoft/VibeVoice-1.5b | Voz: es-emilio                        │
│                                                                             │
│ 3. Control de Dinámica y Expresividad:                                      │
│    --cfg_scale 1.3 (Rango 1.0 - 2.5) -> Estabilidad vs Inflexión Emocional  │
│                                                                             │
│ 4. Transcodificación y Normalización FFmpeg:                                │
│    -af volume=1.0,atempo=1.0 -> WAV 24kHz / MP3 44.1kHz                    │
│                                                                             │
│ 5. Sincronización VO-First & Ducking Multicapa:                             │
│    VO (-14 LUFS) + BGM (-18dB Ducking con sidechaincompress) + Foley 30ms │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Parámetros de Expresividad y Prosodia

### Guía Libre de Clasificador (CFG Scale):
- **`cfg_scale = 1.0 - 1.2`**: Narración sobria, factual, documental histórico pausado.
- **`cfg_scale = 1.3 - 1.5` (Recomendado por Defecto)**: Tono cálido, natural, con inflexiones dinámicas vivas en castellano neutro.
- **`cfg_scale = 1.8 - 2.5`**: Alta intensidad dramática, ganchos de alta retención para Shorts/TikTok.

### Etiquetas de Control Emocional:
El preprocesador detecta etiquetas en el guión e inyecta modulaciones contextuales:
- `(con entusiasmo)`: Eleva el tono y acelera sutilmente el ritmo fonético (+8%).
- `(con seriedad)` / `(solemne)`: Baja el centro tonal y añade pausas de respiración más marcadas.
- `(susurrando)` / `(en confidencia)`: Reduce la compresión dinámica y acentúa frecuencias altas (micro-ASMR).

---

## 3. Concurrencia Segura y Bloqueo de Proceso

Para evitar que múltiples solicitudes saturen la VRAM o CPU del VPS, la síntesis se sincroniza a través de un cerrojo a nivel de kernel:

```python
import fcntl
import subprocess

LOCK_FILE = "/tmp/vibevoice_synthesis.lock"

def synthesize_with_lock(text: str, output_path: str, cfg_scale: float = 1.3):
    with open(LOCK_FILE, "w") as lock_f:
        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
        try:
            cmd = [
                "/home/ubuntu/vibevoice-venv/bin/python",
                "-m", "vibevoice.cli",
                "--model", "microsoft/VibeVoice-1.5b",
                "--voice", "es-emilio",
                "--text", text,
                "--cfg_scale", str(cfg_scale),
                "--output", output_path
            ]
            subprocess.run(cmd, check=True)
        finally:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
```

---

## 4. Regla Áurea: Whisper Timestamps vs. Guion Aprobado

> **NUNCA PINTAR EL TEXTO TRANSCRITO POR WHISPER.**  
> Whisper ASR se utiliza **EXCLUSIVAMENTE** para extraer las marcas de tiempo (`timestamps`) exactas a nivel de palabra ($\text{word\_timestamps}=\text{True}$).
> El texto visible en pantalla (subtítulos ASS / Remotion) proviene estrictamente del guión aprobado.

```
       [Guion Aprobado] ──────────────────────┐
                                              ▼
  [Locución narration.mp3] ──► [Whisper] ──► [Timestamps (ms)] ──► [Karaoke ASS / Remotion]
                                             (Solo Marcas t_0, t_1)  (Texto del Guion)
```

### Sincronización Timeline-Anchored (VO-First):
1. Se sintetiza el audio completo de la escena (`narration.mp3`).
2. Se mide la duración exacta con `ffprobe` o `AudioFileClip`.
3. El timeline visual (`scenes.json`) adapta los 7 planos para que la suma exacta de las tomas coincida con la duración del audio, con un margen de seguridad de `+0.1s` para evitar cortes abruptos.
