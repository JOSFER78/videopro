# Flow Music & Generative Audio: Prompting, Psicoacústica y Masterización DSP

## 1. Gramática de Prompts para Flow Music
Estructura recomendada para fondos de alta inmersión (walking tours, documentales, BSO continua):
`[Función/Género] + [Timbres/Capas] + [Afinación Clave (432Hz/528Hz)] + [Espacio 3D/Binaural] + [Micro-ASMR Foley] + [Tempo Lento] + [Restricciones Negativas]`

- **Regla de oro**: Redactar en inglés técnico para máxima respuesta timbral (`warm 432Hz sub drones`, `lush soothing synthesizer pads`, `binaural spatial audio`, `cobblestone footsteps panning`, `zero drums or harsh beats`).
- **Seamless Loops**: Componer en tonalidades estables (D Minor, C Major) con transitorios suaves y colas de reverb largas para crossfade exponencial (S-curve) con FFmpeg (`acrossfade=d=6:c1=exp:c2=exp`).

## 2. Psicoacústica y Frecuencias Clave
- **432Hz**: Afinación armónica natural, reduce fatiga auditiva y ritmo cardíaco en escuchas prolongadas.
- **528Hz**: Tono de claridad mental, óptimo para documentales históricos y transiciones tritemporales.
- **Binaural Beats**: Alpha (8–12Hz) para presencia relajada en tours; Theta (4–8Hz) para relajación profunda / hipnosis.
- **Micro-ASMR 3D**: Pasos sobre adoquines húmedos, brisa urbana sutil, crujidos orgánicos con paneo binaural dinámico (L->R).

## 3. Cadena DSP de Procesamiento en 6 Etapas
1. **Acondicionamiento y De-Artifacts**:
   - High-Pass elíptico en 20Hz (18-24 dB/oct).
   - De-harshing espectral dinámico en 3.5kHz – 7kHz (-1.5 a -3dB) para remover aspereza digital de la IA.
   - Trabajo interno a 32-bit float / 96kHz.
2. **EQ Tonal y Mono-Sub**:
   - Mono-summing estricto < 80Hz para evitar cancelaciones de fase.
   - Notch / Bell -1.8dB en 250Hz (mud zone).
   - Air Shelf Baxandall +2.0dB > 12kHz.
3. **Saturación Analógica Psicoacústica**:
   - Armónicos de 2º y 3º orden (cinta Studer / tubo triodo, THD < 0.1%) para recrear el 'fundamento perdido'.
4. **Espacialización y Crossfeed**:
   - **Cascos de Lujo (Audiófilos / Planares / Open-Back)**: Algoritmo de crossfeed Bauer (BS2B) con retardo de 250-350µs atenuado en agudos para eliminar la fatiga 'in-the-head' y simular sala de escucha tratada.
   - **Cascos Normales (TWS / IEMs / Consumo)**: Mid/Side widener suave (> 1kHz) + Centro sólido.
5. **Micro-ASMR & Dinámica**:
   - Compresión paralela (Upward Compression) mezclada al 8–12% para realzar micro-detalles sin aplastar transitorios.
   - Bus compressor con ratio 1.5:1, ataque lento (30ms) y reducción máx. de 1dB.
6. **Perfiles Duales de Masterización**:
   - **Audiophile Luxury**: FLAC/WAV 24-bit 96kHz | -16 a -18 LUFS | DR13+ | True Peak -1.5 dBFS | BS2B activo.
   - **Universal Consumer**: AAC 320kbps / WAV 16-bit 48kHz | -14.0 LUFS | DR10-11 | True Peak -1.0 dBFS.

## 4. Script de Masterización Rápida FFmpeg
```bash
# Audiophile Master:
ffmpeg -y -i input.wav -af "highpass=f=20:p=2,equalizer=f=250:t=q:w=1.2:g=-1.8,equalizer=f=14000:t=h:g=2.0,bs2b=profile=default,loudnorm=I=-16.0:LRA=12:TP=-1.5" -ar 96000 -c:a flac output_audiophile.flac

# Universal Consumer Master:
ffmpeg -y -i input.wav -af "highpass=f=25:p=2,equalizer=f=250:t=q:w=1.2:g=-2.2,equalizer=f=3500:t=q:w=2.0:g=-1.0,equalizer=f=12000:t=h:g=1.5,stereowiden=w=1.1:de=0.8,loudnorm=I=-14.0:LRA=9:TP=-1.0" -ar 48000 -c:a aac -b:a 320k output_consumer.m4a
```
