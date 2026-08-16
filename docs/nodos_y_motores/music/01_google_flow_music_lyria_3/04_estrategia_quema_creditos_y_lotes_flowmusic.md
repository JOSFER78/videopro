# Estrategia de Quema de Créditos y Producción Masiva por Lotes en Flow Music

## 1. El Objetivo: Maximizar el Retorno de Créditos Web Acumulados

Cuando se dispone de un volumen masivo de créditos en **Flow Music (Google Labs FX)** cuya caducidad o limitación web impide usarlos vía API directa, la mejor estrategia de ingeniería no es generar pistas una a una sobre la marcha, sino **construir una Factoría Autónoma de Audio BSO por Lotes (Batch Audio Factory)**.

Esta factoría convierte créditos virtuales en **activos de producción permanentes de máxima fidelidad (24-bit / 96kHz FLAC y 320k AAC)**, organizados y listos para ser consumidos instantáneamente por los motores de renderizado de VideoPro y CHRONODRIFT.

---

## 2. Matriz de Generación por Nichos y Categorías

Para agotar los créditos de forma estructurada y con alto valor comercial/narrativo, el generador por lotes divide la producción en 5 bibliotecas maestras:

```
storage/music/flowmusic/
├── 01_walking_tours_432hz/        # Ambientes urbanos, foley binaural 3D, adoquines, brisa
├── 02_tritemporal_documentary/    # Contrastes pasado-presente-futuro, shimmer pads, chelos analógicos
├── 03_deep_focus_cyberpunk/       # Ondas Theta 6Hz, lluvia ASMR, sintetizadores analógicos oscuros
├── 04_nature_meditation_528hz/    # Frecuencia 528Hz, ríos, pájaros binaurales, campanas tibetanas
└── 05_epic_cinematic_trailers/    # Híbrido orquestal sin percusión estridente, sub-drones de impacto
```

### Tabla de Producción Planificada

| Categoría | BPM | Afinación | Foley / Textura ASMR | Formato Master | Propósito VideoPro |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **City Walking Tours** | 60–75 | 432 Hz | Pasos adoquín, eco urbano, brisa | 24-bit FLAC / AAC | Recorridos FPV 4K de ciudades históricas |
| **Tritemporal History** | 50–65 | 528 Hz | Campanas antiguas, piedra, shimmer | 24-bit FLAC / AAC | Comparativas Pasado vs Presente vs Futuro |
| **Cyberpunk Focus** | 80–90 | 432 Hz | Lluvia sobre cristal, zumbido neón | 24-bit FLAC / AAC | Documentales tech, IA y paisajes nocturnos |
| **Solfeggio Healing** | 45–55 | 528 Hz | Agua fluyendo, viento en hojas | 24-bit FLAC / AAC | Vídeos de meditación, sueño y ASMR |
| **Trailer Atmospheric** | 70–85 | 432 Hz | Sub-boom cinemático, arco de violín | 24-bit FLAC / AAC | Intros de alto impacto y teasers virales |

---

## 3. Arquitectura del Loteador Asíncrono (Batch Worker)

El script `scripts/flow_music_playwright_runner.py` opera como un demonio o tarea CLI con las siguientes características de seguridad y rendimiento:

1. **Throttling Inteligente (Anti-Rate Limit)**:
   - Tiempo de generación en Flow Music: ~20 a 40 segundos por pista.
   - Pausa aleatoria entre generaciones (`jitter` de 5 a 12 segundos) para simular interacción humana orgánica.
   - Tasa media de producción: **60 a 70 pistas completas por hora**.

2. **Control de Errores y Auto-Reconexión**:
   - Si la pestaña de Flow Music muestra un error temporal de Google Labs ("Too many requests" o "Try again later"), el runner espera 30 segundos, refresca la pestaña y reintenta sin detener el lote.
   - En caso de modal informativo o popup de cookies, lo cierra automáticamente mediante el `ModalDismissEngine`.

3. **Masterización DSP en Tiempo Real (Post-Download Hook)**:
   - Cada pista descargada pasa inmediatamente por el procesador `AudiophileAudioProcessor`.
   - Se generan automáticamente **dos versiones por cada crédito quemado**:
     1. `track_audiophile_master.flac` (24-bit 96kHz, rango dinámico intacto, crossfeed Bauer).
     2. `track_universal_master.m4a` (-14.0 LUFS, optimizado para YouTube Shorts y TikTok).

4. **Registro Automático de Metadata**:
   - Cada pista se acompaña de un archivo `.json` con el prompt original, los parámetros de DSP, la tonalidad, el BPM y el hash de verificación para `VideoStorageManager`.

---

## 4. Ejecución del Lote en Segundo Plano

Para lanzar una sesión de quema de créditos masiva en el VPS:

```bash
# Ejecutar un lote de 20 pistas para Walking Tours en segundo plano
python3 scripts/flow_music_playwright_runner.py \
  --batch templates/batch_flow_music_prompts.json \
  --category walking_tours_432hz \
  --tuning 432 \
  --profile audiophile_luxury \
  --max-tracks 20
```

Este proceso corre de forma 100% autónoma en el VPS sin requerir que el usuario mantenga abierta ninguna ventana o realice confirmaciones manuales.
