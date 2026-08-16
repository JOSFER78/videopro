# 🎙️ Guía Maestra: Kokoro HD TTS, Voces en Español & Foley Director

> **Ubicación:** `docs/investigaciones/nodos_capacidades/kokoro-tts-foley/01_guia_maestra_kokoro_y_foley_director.md`  
> **Servicio de Voz:** Kokoro HD TTS (Local CPU `$0` en puerto `:7892`)  
> **Calidad:** 24kHz High-Fidelity / 48kHz Resampled Master  
> **Efectos y Mezcla:** Foley Director & FFmpeg Sidechain Ducking (`-22dB`)  

---

## 1. Visión General del Sistema de Audio & Voz

El pipeline de voz y sonido de **VideoPro** opera de forma 100% autónoma y local en el VPS, eliminando costes recurrentes por APIs de terceros y garantizando una calidad cinematográfica profesional:

```mermaid
graph TD
    A[Guion / Locución VO] --> B[Kokoro HD TTS :7892 (Local CPU $0)]
    B --> C[Voz Master 24kHz/48kHz WAV]
    D[Shotlist / Foley Director] --> E[Librería Foley 48kHz + SFX]
    F[Flow Music 432Hz/528Hz BSO] --> G[Mezclador Automatizado FFmpeg]
    C --> G
    E --> G
    G -->|Sidechain Ducking -22dB| H[Master Final Estéreo -14 LUFS]
```

---

## 2. Catálogo de Voces en Español (Kokoro HD)

Kokoro HD ofrece síntesis de voz natural y expresiva con soporte fonético optimizado para español neutro e ibérico:

| Voz / Perfil | Tono & Estilo | Uso Óptimo en VideoPro | Frecuencia de Muestreo |
| :--- | :--- | :--- | :--- |
| **`ef_dora` (Dora)** | Femenina, cálida, documental, ritmo pausado | Documentales históricos, Walking Tours, Narración poética | 24kHz WAV nativo |
| **`em_santiago` (Santiago)** | Masculina, profunda, autoritaria, cinematográfica | Tráilers, CHRONODRIFT épico, Ciencia y Exploración | 24kHz WAV nativo |
| **`em_alex` (Alex)** | Masculina, dinámica, cercana, divulgativa | NANOVERSE, Edutainment, Tecnología y Futuro | 24kHz WAV nativo |

### Llamada al Servicio Local Kokoro vía Python
```python
import httpx
import soundfile as sf
import io

def synthesize_kokoro_voice(text: str, voice_name: str = "em_santiago", output_path: str = "locucion.wav"):
    url = "http://localhost:7892/v1/audio/speech"
    payload = {
        "model": "kokoro",
        "input": text,
        "voice": voice_name,
        "response_format": "wav",
        "speed": 0.95  # Ritmo ligeramente pausado para documental
    }
    
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
            
    print(f"Locución generada con éxito en: {output_path}")
```

---

## 3. Foley Director & Generación de SFX Ambientales

El **Foley Director** es el módulo encargado de mapear los eventos visuales del shotlist con efectos sonoros espaciales y texturas ambientales:

- **Pass-By SFX**: Efectos de viento y Doppler cuando la cámara FPV pasa cerca de muros, árboles o vehículos.
- **Surface Textures (ASMR)**: Pasos sobre grava, adoquines mojados, crujidos de madera.
- **Atmospheric Room Tone**: Reverberación y tono de sala acústico adaptado a la época (catedral gótica, calle estrecha, nave espacial).

---

## 4. FFmpeg Sidechain Ducking Automatizado (-22dB)

Para asegurar que la música de fondo (Flow Music) nunca compita con la voz del narrador, se aplica una compresión por cadena lateral (*sidechain ducking*) automática:

```bash
# Mezcla de Voz + Música con Sidechain Ducking de -22dB
ffmpeg -y \
  -i locucion_master.wav \
  -i bso_ambient_432hz.wav \
  -filter_complex "\
    [1:a][0:a]sidechaincompress=\
      threshold=0.08:\
      ratio=5:\
      attack=20:\
      release=350:\
      makeup=1.0[music_ducked]; \
    [0:a][music_ducked]amix=inputs=2:duration=longest:weights=1.0 0.75[mix_out]; \
    [mix_out]loudnorm=I=-14.0:LRA=9:TP=-1.0[master_lufs] \
  " -map "[master_lufs]" -c:a pcm_s24le master_audio_completo.wav
```

---

## 5. Reglas de Descarte y Calidad

- 🚫 **Descartar audios a 8kHz o 16kHz**: Todas las locuciones deben procesarse a 24kHz nativo y remuestrearse a 48kHz para la mezcla.
- 🚫 **Descartar música sin ducking en escenas con voz**: La música sin atenuar reduce la inteligibilidad y eleva la tasa de abandono del espectador en YouTube.
- 🚫 **Descartar clipping en picos**: Mantener siempre un True Peak máximo de `-1.0 dBFS`.

---

## 6. Documentos y Referencias Relacionadas

- [Plan Maestro Flow Music & BSO](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/nodos_capacidades/flowmusic-via-playwright/00_plan_maestro_flow_music.md)
- [Capacidades Maestras e Infraestructura](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/nodos_capacidades/capacidades_maestras.md)
- [Metodología Documental Cinematográfica](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/01_metodologia_documental_cinematografica.md)
