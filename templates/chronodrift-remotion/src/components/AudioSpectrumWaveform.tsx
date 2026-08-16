import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

export interface AudioSpectrumWaveformProps {
  bpm?: number;
  isDuckingActive?: boolean;
  duckingDb?: number;
  masterLufs?: number;
  truePeakDb?: number;
  primaryCyan?: string;
  secondaryOrange?: string;
  accentPurple?: string;
  fps?: number;
}

export const AudioSpectrumWaveform: React.FC<AudioSpectrumWaveformProps> = ({
  bpm = 118,
  isDuckingActive = false,
  duckingDb = -18.0,
  masterLufs = -14.0,
  truePeakDb = -1.0,
  primaryCyan = '#00e5ff',
  secondaryOrange = '#ffb300',
  accentPurple = '#b388ff',
  fps = 60
}) => {
  const frame = useCurrentFrame();
  const numBars = 16;
  const beatFrames = (60 / bpm) * fps; // ~30.5 frames per beat at 118 BPM, 60fps

  // Modulación rítmica a 118 BPM
  const beatPhase = (frame % beatFrames) / beatFrames;
  const kickPulse = Math.pow(Math.max(0, 1 - beatPhase * 1.8), 2);

  const bars = Array.from({ length: numBars }).map((_, i) => {
    const freqMod = Math.sin(frame * 0.15 + i * 0.45);
    const harmonic = Math.cos(frame * 0.08 + i * 0.25);
    let heightFactor = 0.25 + 0.45 * Math.abs(freqMod) + 0.3 * Math.abs(harmonic);
    
    // Inyectar pulso en frecuencias graves (barras 0-4)
    if (i < 4) {
      heightFactor += kickPulse * 0.5;
    }
    
    // Reducción si el ducking está activo
    if (isDuckingActive) {
      heightFactor *= 0.45;
    }

    const clampedHeight = Math.min(1.0, Math.max(0.1, heightFactor));
    return clampedHeight * 36; // Altura en px (max 36px)
  });

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: '3px',
        padding: '6px 12px',
        background: 'rgba(7, 9, 14, 0.75)',
        border: '1px solid rgba(0, 229, 255, 0.2)',
        borderRadius: '3px',
        backdropFilter: 'blur(8px)',
        fontFamily: "'JetBrains Mono', 'Share Tech Mono', monospace"
      }}
    >
      {/* Indicador de Ducking */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          marginRight: '8px',
          paddingRight: '8px',
          borderRight: '1px solid rgba(255, 255, 255, 0.12)'
        }}
      >
        <div style={{ fontSize: '9px', color: isDuckingActive ? secondaryOrange : primaryCyan, fontWeight: 700 }}>
          {isDuckingActive ? `DUCK ${duckingDb}dB` : 'FLOW 118 BPM'}
        </div>
        <div style={{ fontSize: '8px', color: 'rgba(255, 255, 255, 0.6)' }}>
          {masterLufs} LUFS | {truePeakDb} dBTP
        </div>
      </div>

      {/* Barras de Espectro */}
      {bars.map((barHeight, idx) => {
        const isBass = idx < 4;
        const color = isBass ? secondaryOrange : (idx > 12 ? accentPurple : primaryCyan);
        return (
          <div
            key={idx}
            style={{
              width: '4px',
              height: `${barHeight}px`,
              backgroundColor: color,
              borderRadius: '1px',
              boxShadow: `0 0 6px ${color}88`,
              transition: 'height 0.05s ease-out'
            }}
          />
        );
      })}
    </div>
  );
};
