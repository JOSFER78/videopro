# 📘 NODO 05: Motor de Mezcla de Audio y Foley Físico (3 Capas)

> **Rol del Nodo:** Orquestar la espacialidad acústica, ducking dinámico e inserción de efectos sonoros foley sincronizados.

---

## 🎯 Arquitectura de las 3 Capas de Audio:

1. **Capa 1 - Voz / Locución Principal:**
   * Normalizada a **+10 dB** (True Peak -1.0 dBTP).
   * Claridad en frecuencias medias (1 kHz - 4 kHz) y compresión multibanda suave.

2. **Capa 2 - BGM / Pista Musical:**
   * **Ducking Automático a -22 dB** en presencia de voz.
   * Recuperación rápida a -8 dB en las transiciones entre bloques para mantener la energía.

3. **Capa 3 - Foley SFX Sincronizados:**
   * Efectos mecánicos y orgánicos insertados en cada entrada de rótulo o cambio de escena:
     * Obturador fotográfico mecánico (*Shutter click*).
     * Transición de viento rápido (*Whoosh*).
     * Despliegue de mapa de papel (*Paper rustle*).
     * Clic de engranaje relojero (*Mechanical tick*).
   * **Crossfade de 30 ms** en todos los empalmes para neutralizar chasquidos de fase.
