import React from 'react';
import { interpolate, useCurrentFrame, spring } from 'remotion';
import { AudioSpectrumWaveform } from './AudioSpectrumWaveform';

export interface ChronoDriftHUDProps {
  currentYear: number;
  cityName: string;
  country: string;
  coordinates: string;
  altitudeMeters: number;
  speedKmh: number;
  shotId: string;
  shotIndex: number;
  totalShots: number;
  scientificCitation: string;
  factText: string;
  isDuckingActive?: boolean;
  primaryCyan?: string;
  secondaryOrange?: string;
  accentPurple?: string;
  fps?: number;
}

export const ChronoDriftHUD: React.FC<ChronoDriftHUDProps> = ({
  currentYear,
  cityName,
  country,
  coordinates,
  altitudeMeters,
  speedKmh,
  shotId,
  shotIndex,
  totalShots = 7,
  scientificCitation,
  factText,
  isDuckingActive = false,
  primaryCyan = '#00e5ff',
  secondaryOrange = '#ffb300',
  accentPurple = '#b388ff',
  fps = 60
}) => {
  const frame = useCurrentFrame();

  // Animaciones de entrada e interpolación dinámica
  const hudOpacity = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: 'clamp' });
  const reticleScale = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });
  
  // Modulación de horizonte artificial según el fotograma
  const pitchAngle = Math.sin(frame * 0.04) * 6;
  const rollAngle = Math.cos(frame * 0.03) * 4;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        fontFamily: "'JetBrains Mono', 'Share Tech Mono', monospace",
        color: primaryCyan,
        opacity: hudOpacity,
        pointerEvents: 'none',
        padding: '56px',
        boxSizing: 'border-box',
        overflow: 'hidden',
        textShadow: '0 0 12px rgba(0, 229, 255, 0.45)'
      }}
    >
      {/* 1. RETÍCULA CENTRAL 6-DoF CON HORIZONTE ARTIFICIAL */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) scale(${reticleScale}) rotate(${rollAngle}deg)`,
          width: '180px',
          height: '180px',
          border: `1.5px solid rgba(0, 229, 255, 0.35)`,
          borderRadius: '50%',
          boxShadow: '0 0 35px rgba(0, 229, 255, 0.18)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {/* Punto de Mira Central */}
        <div style={{ width: '6px', height: '6px', backgroundColor: secondaryOrange, borderRadius: '50%', boxShadow: `0 0 10px ${secondaryOrange}` }} />
        
        {/* Marcadores de Horizonte Pitch / Roll */}
        <div style={{ position: 'absolute', top: '50%', left: '-30px', width: '50px', height: '2px', backgroundColor: primaryCyan }} />
        <div style={{ position: 'absolute', top: '50%', right: '-30px', width: '50px', height: '2px', backgroundColor: primaryCyan }} />
        <div style={{ position: 'absolute', top: '-30px', left: '50%', width: '2px', height: '50px', backgroundColor: primaryCyan }} />
        <div style={{ position: 'absolute', bottom: '-30px', left: '50%', width: '2px', height: '50px', backgroundColor: primaryCyan }} />
        
        {/* Graduación Angular Pitch */}
        <div style={{ position: 'absolute', top: '25%', left: '20%', right: '20%', height: '1px', backgroundColor: 'rgba(0, 229, 255, 0.25)' }} />
        <div style={{ position: 'absolute', bottom: '25%', left: '20%', right: '20%', height: '1px', backgroundColor: 'rgba(0, 229, 255, 0.25)' }} />
      </div>

      {/* 2. PANEL SUPERIOR IZQUIERDO: CRONOMETRO & LOCALIZACIÓN */}
      <div
        style={{
          position: 'absolute',
          top: '64px',
          left: '64px',
          background: 'rgba(7, 9, 14, 0.82)',
          borderLeft: `5px solid ${secondaryOrange}`,
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '20px 32px',
          borderRadius: '4px',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.6)'
        }}
      >
        <div style={{ fontSize: '13px', color: secondaryOrange, letterSpacing: '0.14em', fontWeight: 700 }}>
          CHRONODRIFT 6-DoF // {cityName.toUpperCase()} [{country.toUpperCase()}]
        </div>
        <div style={{ fontSize: '38px', fontWeight: 900, color: '#ffffff', letterSpacing: '-0.03em', margin: '4px 0' }}>
          {currentYear} <span style={{ fontSize: '18px', color: primaryCyan, fontWeight: 500 }}>CE</span>
        </div>
        <div style={{ fontSize: '13px', color: primaryCyan, opacity: 0.92, letterSpacing: '0.04em' }}>
          COORDS: {coordinates} | 60 FPS UHD
        </div>
      </div>

      {/* 3. PANEL SUPERIOR DERECHO: TELEMETRÍA DE AUDIO & MOTOR */}
      <div
        style={{
          position: 'absolute',
          top: '64px',
          right: '64px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: '12px'
        }}
      >
        <div
          style={{
            background: 'rgba(7, 9, 14, 0.82)',
            borderRight: `5px solid ${primaryCyan}`,
            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            padding: '20px 32px',
            borderRadius: '4px',
            textAlign: 'right',
            backdropFilter: 'blur(16px)',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.6)'
          }}
        >
          <div style={{ fontSize: '13px', color: accentPurple, letterSpacing: '0.12em', fontWeight: 700 }}>
            AUDIO MASTER: EBU R128 (-14.0 LUFS)
          </div>
          <div style={{ fontSize: '16px', fontWeight: 800, color: '#ffffff', margin: '4px 0' }}>
            118 BPM <span style={{ color: secondaryOrange, fontSize: '13px' }}>[FLOW CHILLHOP]</span>
          </div>
          <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.75)' }}>
            DUCKING: -18.0 dB | TRUE PEAK: -1.0 dBTP
          </div>
        </div>

        {/* Visualizador de Espectro Dinámico 118 BPM */}
        <AudioSpectrumWaveform
          bpm={118}
          isDuckingActive={isDuckingActive}
          duckingDb={-18.0}
          masterLufs={-14.0}
          truePeakDb={-1.0}
          primaryCyan={primaryCyan}
          secondaryOrange={secondaryOrange}
          accentPurple={accentPurple}
          fps={fps}
        />
      </div>

      {/* 4. PANEL INFERIOR IZQUIERDO: SHOT PROGRESS & DATOS CIENTÍFICOS */}
      <div
        style={{
          position: 'absolute',
          bottom: '64px',
          left: '64px',
          background: 'rgba(7, 9, 14, 0.82)',
          borderLeft: `5px solid ${accentPurple}`,
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '20px 32px',
          maxWidth: '650px',
          borderRadius: '4px',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.6)'
        }}
      >
        <div style={{ fontSize: '13px', color: accentPurple, letterSpacing: '0.12em', fontWeight: 700 }}>
          CANONICAL SHOT [{shotIndex}/{totalShots}]: {shotId}
        </div>
        <div style={{ fontSize: '15px', color: '#ffffff', marginTop: '6px', lineHeight: 1.45 }}>
          {factText}
        </div>
        <div style={{ fontSize: '12px', color: primaryCyan, marginTop: '8px', opacity: 0.85 }}>
          ANCLAJE: {scientificCitation}
        </div>
      </div>

      {/* 5. PANEL INFERIOR DERECHO: DINÁMICA DE VUELO (ALTITUD & VELOCIDAD) */}
      <div
        style={{
          position: 'absolute',
          bottom: '64px',
          right: '64px',
          background: 'rgba(7, 9, 14, 0.82)',
          borderRight: `5px solid ${primaryCyan}`,
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '20px 32px',
          borderRadius: '4px',
          textAlign: 'right',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.6)'
        }}
      >
        <div style={{ fontSize: '13px', color: primaryCyan, letterSpacing: '0.14em', fontWeight: 700 }}>
          FLIGHT TELEMETRY (BAROMETRIC AGL)
        </div>
        <div style={{ fontSize: '28px', fontWeight: 900, color: '#ffffff', margin: '4px 0' }}>
          ALT: <span style={{ color: secondaryOrange }}>{altitudeMeters.toFixed(1)} M</span> | SPD: <span style={{ color: primaryCyan }}>{speedKmh.toFixed(0)} KM/H</span>
        </div>
        <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.75)' }}>
          PITCH: {pitchAngle.toFixed(1)}° | ROLL: {rollAngle.toFixed(1)}° | ZERO VEO 3
        </div>
      </div>
    </div>
  );
};
