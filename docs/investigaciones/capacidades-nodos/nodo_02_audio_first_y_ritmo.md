# 🎵 Nodo 02: Audio-First, Sincronismo y Ritmo de Montaje

## 🎯 Misión del Nodo
Garantizar que **la pista de audio mande sobre el tiempo y los cortes**. El montaje no es aleatorio; se calibra a los milisegundos exactos del archivo maestro.

---

## 🛠️ Especificaciones Técnicas
1. **Duración Absoluta:**
   * La pista WAV master (177.64s @ 48 kHz estéreo) define la línea de tiempo total.
2. **Ritmo de Corte:**
   * Cambios de plano o elemento visual cada **1.5 a 3.0 segundos**.
   * Cortes sincronizados con los transitorios de percusión y cambios de compás.
3. **Audio Ducking Dinámico:**
   * Atenuación de la música a **-22.0 dB** durante los momentos de voz/explicación clave y retorno suave (*fade-in* en 250ms) a nivel nominal.
4. **Análisis de Espectro en Tiempo Real:**
   * Generación de datos FFT para el ecualizador visual React/Remotion (`AudioSpectrumWaveform`).
