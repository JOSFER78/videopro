# 🎬 WORKFLOW DOCUMENTAL: ARQUITECTURA DE 7 PLANOS POR ESCENA & SINCRONIZACIÓN VO-FIRST

Este documento define el estándar de producción cinematográfica para documentales científicos y tecnológicos en **Hermes Video Engine** utilizando **Google Flow (Gemini Omni Flash / Nano Banana Pro)** y **VibeVoice / Edge-TTS**.

---

## 🏛️ 1. FILOSOFÍA DE PRODUCCIÓN: PLANIFICACIÓN & PRE-RENDER

1. **Cero Improvisación Visual**:
   - Nunca renderizar clips de vídeo aislados sin haber cerrado previamente el guion, el desglose de planos (storyboard) y las duraciones exactas del audio.
2. **Audio Dicta el Montaje (VO-First)**:
   - La locución grabada (`vo_scene_*.wav`) es el ancla temporal de la línea de tiempo. Cada plano se corta o se transiciona en concordancia con los acentos, pausas y métricas de la voz.
3. **Consistencia Visual Fotorrealista (Netflix Standard)**:
   - Para mantener la identidad de personajes, naves, arquitectura y texturas a lo largo de todo el metraje, se generan primero **Keyframes Maestros** con `Nano Banana Pro` que actúan como `<FIRST_FRAME>` y `<IMAGE_REF_0..N>` en las llamadas a `Gemini Omni Flash`.

---

## 📐 2. ARQUITECTURA DE 7 PLANOS POR ESCENA DOCUMENTAL

Cada bloque temático o escena de ~10 segundos se desglosa en una secuencia fluida de al menos **7 planos cinemáticos**:

```text
[Plano 1: Gran Plano General] ──► [Plano 2: Infraestructura/Medio] ──► [Plano 3: Sujeto/Acción]
                                                                              │
[Plano 6: Subjetivo POV] ◄── [Plano 5: Macro Telemetría] ◄── [Plano 4: Primer Plano Visera]
           │
           ▼
[Plano 7: Revelación Panorámica / Transición]
```

### Detalle de los 7 Planos:

| # | Tipo de Plano | Óptica y Encuadre | Movimiento de Cámara | Función Narrativa |
|---|---|---|---|---|
| **1** | **Gran Plano General (EWS)** | 24mm Anamórfico, f/4.0 | Orbiting lento / Drone Descent | Establece la escala planetaria, geografía o entorno exterior. |
| **2** | **Plano General Medio (WS)** | 35mm Prime, f/2.8 | Slow Push-in con paralaje | Muestra la infraestructura activa, domos, transporte o bases. |
| **3** | **Plano Medio (MS)** | 50mm Prime, f/1.8 | Tracking lateral suave | Presenta a los científicos, robots o sistemas en plena operación. |
| **4** | **Primer Plano (CU)** | 85mm Portrait, f/1.4 | Enfoque selectivo (Rack Focus) | Rostro humano, visera presurizada con reflejos HUD y emoción. |
| **5** | **Macro Telemetría (ECU)** | 100mm Macro, f/2.8 | Enfoque milimétrico estático | Sensores, reactores de fusión, interfaces holográficas, datos. |
| **6** | **Plano Subjetivo (POV)** | 28mm Wide, f/2.0 | Cámara al hombro estabilizada | Perspectiva en primera persona del operador o rover. |
| **7** | **Revelación Panorámica (Reveal)** | 35mm Anamórfico, f/2.0 | Crane / Jib Up con Tilt | Conclusión visual de la escena que enlaza con el siguiente bloque. |

---

## 🎨 3. MASTER COLOR & LIGHTING SCIENCE (MARTE 2200)

Para asegurar la uniformidad en todas las tomas generadas en Google Flow:

- **Paleta de Color Unificada**:
  - *Rust Oxide*: `#8C3823` (Regolito y cañones marcianos).
  - *Martian Dust*: `#C46845` (Tormentas y polvo en suspensión).
  - *Carbon Titanium*: `#1F2326` (Estructuras de hábitats y fuselaje).
  - *Cryo-Cyan HUD*: `#2AD4D4` (Interfaces gráficas y telemetría Vox).
  - *Solar Amber*: `#EAA844` (Iluminación interior y reactores Sabatier).
- **Textura Fílmica**:
  - Grano fino analógico Kodak Vision3 500T 35mm.
  - Perfil de color ARRI Alexa LF con curvas Log-C.
  - Iluminación solar marciana real (590 W/m2), con sombras duras y atmósfera delgada.

---

## 🎙️ 4. MATRIZ DE SINCRONIZACIÓN DE AUDIO & FOLEY

1. **Pista 1: Locución (Voiceover)**:
   - Normalizada a -14 LUFS (EBU R128).
   - Generada con `VibeVoice` (`es-emilio.wav`) o `Edge-TTS` (`es-ES-AlvaroNeural`).
2. **Pista 2: Música BGM (Flow Music / Lyria 3.5)**:
   - Atenuación automática (*sidechain ducking*) de -18 dB durante la presencia de voz.
3. **Pista 3: Efectos SFX y Foley Diegético**:
   - Pulsos electromagnéticos, despresurización de esclusas, servos de rover y crujido de regolito sincronizados en los timecodes exactos de cada corte de plano.
