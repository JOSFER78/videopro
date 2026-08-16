import React from 'react';
import { interpolate, spring, useCurrentFrame } from 'remotion';

export interface BuildingSpatialAnchorProps {
  buildingName: string;
  epoch: string;
  yearBuilt: number | string;
  heightMeters: number;
  osmHeritageTag?: string;
  historicalFact: string;
  screenXPercent: number; // 0 to 100
  screenYPercent: number; // 0 to 100
  primaryCyan?: string;
  secondaryOrange?: string;
  accentPurple?: string;
  fps?: number;
  startFrame?: number;
  durationFrames?: number;
}

export const BuildingSpatialAnchor: React.FC<BuildingSpatialAnchorProps> = ({
  buildingName,
  epoch,
  yearBuilt,
  heightMeters,
  osmHeritageTag = 'OSM:historic=monument',
  historicalFact,
  screenXPercent = 50,
  screenYPercent = 45,
  primaryCyan = '#00e5ff',
  secondaryOrange = '#ffb300',
  accentPurple = '#b388ff',
  fps = 60,
  startFrame = 0,
  durationFrames = 180
}) => {
  const frame = useCurrentFrame();
  const relFrame = frame - startFrame;

  if (relFrame < 0 || relFrame > durationFrames) {
    return null;
  }

  // Animación suave de aparición y salida
  const entrance = spring({ frame: relFrame, fps, config: { damping: 14, stiffness: 100 } });
  const exitOpacity = interpolate(
    relFrame,
    [durationFrames - 20, durationFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const opacity = entrance * exitOpacity;
  const lineLength = interpolate(relFrame, [0, 20], [0, 100], { extrapolateRight: 'clamp' });
  const pulse = 1 + Math.sin(relFrame * 0.1) * 0.05;

  return (
    <div
      style={{
        position: 'absolute',
        left: `${screenXPercent}%`,
        top: `${screenYPercent}%`,
        transform: `translate(-50%, -50%) scale(${entrance})`,
        opacity,
        pointerEvents: 'none',
        zIndex: 40,
        fontFamily: "'JetBrains Mono', 'Share Tech Mono', monospace"
      }}
    >
      {/* 1. Punto de Anclaje Fotogramétrico sobre el Edificio */}
      <div
        style={{
          position: 'relative',
          width: '18px',
          height: '18px',
          borderRadius: '50%',
          border: `2px solid ${secondaryOrange}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 0 16px ${secondaryOrange}`,
          transform: `scale(${pulse})`
        }}
      >
        <div
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: '#ffffff'
          }}
        />
        {/* Anillo de Pulso Radar */}
        <div
          style={{
            position: 'absolute',
            inset: '-6px',
            borderRadius: '50%',
            border: `1px solid rgba(255, 179, 0, 0.4)`,
            animation: 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite'
          }}
        />
      </div>

      {/* 2. Línea Guía Vectorial (Leader Line) en Diagonal */}
      <svg
        style={{
          position: 'absolute',
          top: '9px',
          left: '9px',
          width: '140px',
          height: '90px',
          overflow: 'visible',
          pointerEvents: 'none'
        }}
      >
        <polyline
          points={`0,0 45,-35 ${45 + lineLength},-35`}
          fill="none"
          stroke={primaryCyan}
          strokeWidth="1.5"
          strokeDasharray="4 2"
        />
      </svg>

      {/* 3. Tarjeta de Datos Espaciales & Telemetría Histórica */}
      <div
        style={{
          position: 'absolute',
          left: `${9 + 45 + lineLength}px`,
          top: '-70px',
          background: 'rgba(7, 9, 14, 0.88)',
          borderLeft: `4px solid ${primaryCyan}`,
          borderTop: '1px solid rgba(0, 229, 255, 0.3)',
          borderRight: '1px solid rgba(255, 255, 255, 0.08)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '14px 20px',
          borderRadius: '4px',
          backdropFilter: 'blur(12px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.75)',
          minWidth: '280px',
          maxWidth: '360px'
        }}
      >
        {/* Cabecera con Badge de Época y Altura OSM */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 800,
              color: secondaryOrange,
              letterSpacing: '0.12em',
              textTransform: 'uppercase'
            }}
          >
            {epoch} // c. {yearBuilt}
          </span>
          <span
            style={{
              fontSize: '10px',
              color: accentPurple,
              background: 'rgba(179, 136, 255, 0.15)',
              padding: '2px 6px',
              borderRadius: '2px',
              fontWeight: 600
            }}
          >
            ALT: {heightMeters}m AGL
          </span>
        </div>

        {/* Nombre del Edificio / Monumento */}
        <div
          style={{
            fontSize: '16px',
            fontWeight: 800,
            color: '#ffffff',
            letterSpacing: '-0.01em',
            lineHeight: 1.2
          }}
        >
          {buildingName}
        </div>

        {/* Hecho Histórico / Fotogramétrico */}
        <div
          style={{
            fontSize: '11.5px',
            color: 'rgba(255, 255, 255, 0.85)',
            marginTop: '6px',
            lineHeight: 1.4
          }}
        >
          {historicalFact}
        </div>

        {/* Etiqueta OSM */}
        <div
          style={{
            fontSize: '9.5px',
            color: primaryCyan,
            marginTop: '8px',
            opacity: 0.75,
            letterSpacing: '0.04em'
          }}
        >
          {osmHeritageTag}
        </div>
      </div>
    </div>
  );
};
