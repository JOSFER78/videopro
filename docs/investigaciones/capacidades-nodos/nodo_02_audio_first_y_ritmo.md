# 📘 NODO 02: Motor de Audio-First, Sincronismo y Ritmo de Montaje

> **Rol del Nodo:** Controlar la línea de tiempo matemática basada en el audio del usuario (música instrumental o voz).

---

## 🎯 Reglas Operativas Estrictas:

1. **El Audio es la Ley:**
   * La duración del archivo de audio del usuario rige el corte y final del vídeo de forma absoluta (ej. 177.64s).
   * Se extrae el perfil de transitorios y energía RMS para alinear los cortes visuales con los golpes de bombo/caja o caídas de compás.

2. **Frecuencia de Corte Rápido (Estilo Hollywood / Vox):**
   * **Duración por toma:** Máximo de **2.0 a 3.5 segundos por plano**.
   * **Prohibido:** Planos estáticos o escenas continuas de 10-20 segundos sin cambio de ángulo.

3. **Ventanas de Amortiguación Acústica:**
   * Margen de seguridad de **30 ms a 200 ms** en cada corte para absorber desviaciones de fase y evitar *jump cuts* estridentes.
