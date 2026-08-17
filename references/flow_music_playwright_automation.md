# Referencia Técnica: Automatización Autónoma de Flow Music vía Playwright & CDP

## 1. Contexto y Arquitectura
Esta referencia documenta cómo generar y masterizar pistas de audio BSO y música ambiental en **Google Flow Music / MusicFX** de forma 100% autónoma utilizando Playwright sobre Chrome DevTools Protocol (CDP) en el puerto `9222`.

### Por qué esta vía es la mejor para quemar créditos acumulados:
- **Sesión Activa Persistente**: Reutiliza la sesión web del usuario en `/home/ubuntu/.config/brave-session` (puerto 9222), evitando logins, tokens expirados y bloqueos de seguridad.
- **Sin Coste de API Externa**: Consume directamente los créditos de la cuenta de Google Labs/Flow Music.
- **Mastering DSP Automático**: Pasa cada audio descargado por `audiophile_audio_processor.py` (432Hz/528Hz, Crossfeed Meier, LUFS).

---

## 2. Comandos de Ejecución

### Generación de Pista Individual
```bash
python3 scripts/flow_music_playwright_runner.py \
  --prompt "Ultra-high fidelity ambient walking soundtrack for city tours. Warm 432Hz sub drones, lush soothing synth pads, binaural ASMR footsteps." \
  --tuning 432 \
  --profile audiophile_luxury
```

### Quema Masiva de Créditos por Lotes (Batch Runner)
```bash
python3 scripts/flow_music_playwright_runner.py \
  --batch templates/batch_flow_music_prompts.json \
  --tuning 432 \
  --profile audiophile_luxury
```

---

## 3. Integración en Código Python

```python
from app.services.audio.flowmusic_service import FlowMusicAutomationService

service = FlowMusicAutomationService()

# Generación desatendida de una BSO
result = service.generate_track_sync(
    prompt="Warm 432Hz ambient walking tour in Rome, gentle breeze, binaural 3D",
    filename_prefix="rome_walking_tour",
    tuning_hz=432,
    profile="audiophile_luxury"
)

print(f"Pista Masterizada FLAC: {result['files']['audiophile_flac']}")
print(f"Pista Universal M4A: {result['files']['universal_m4a']}")
```
