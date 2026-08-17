import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';

export interface ModernHUDOverlayProps {
  actTitle?: string;
  location?: string;
  timeWindow?: string;
  shotId?: string;
  shotIndex?: number;
  totalShots?: number;
  telemetry?: string;
  lowerThird?: string;
  timestampCode?: string;
  primaryCyan?: string;
  accentGold?: string;
  accentPurple?: string;
}

export const ModernHUDOverlay: React.FC<ModernHUDOverlayProps> = ({
  actTitle = 'Acto I: La Grieta en la Realidad',
  location = 'Gran Sasso Subterranean Lab, Italia',
  timeWindow = '00:00 - 00:05',
  shotId = 'SHOT_01_QUANTUM_CRYOSTAT_DIVE',
  shotIndex = 1,
  totalShots = 24,
  telemetry = 'TEMP: 10.2 mK | VACUUM: 10^-9 mbar | COHERENCE: 99.98%',
  lowerThird = 'ARQUITECTURA TOPOLÓGICA DE QÚBITS MONOCRISTALINOS',
  timestampCode = '00:00:00:00',
  primaryCyan = '#00E5FF',
  accentGold = '#FFD700',
  accentPurple = '#B388FF'
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const is4K = width >= 3840;
  const fontScale = is4K ? 2.0 : 1.0;
  const padding = is4K ? 64 : 36;

  // Spring animations on shot entry
  const hudOpacity = interpolate(frame % (fps * 5), [0, 15], [0, 1], {
    extrapolateRight: 'clamp'
  });
  const reticleScale = spring({
    frame: frame % (fps * 5),
    fps,
    config: { damping: 14, stiffness: 120 }
  });

  const rollAngle = Math.cos(frame * 0.02) * 3;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        fontFamily: "'Share Tech Mono', 'Liberation Mono', monospace",
        color: primaryCyan,
        opacity: hudOpacity,
        pointerEvents: 'none',
        padding: `${padding}px`,
        boxSizing: 'border-box',
        overflow: 'hidden',
        zIndex: 40
      }}
    >
      {/* 1. TOP-LEFT: Diegetic Temporal Badge */}
      <div
        style={{
          position: 'absolute',
          top: `${padding}px`,
          left: `${padding}px`,
          background: 'rgba(7, 9, 14, 0.85)',
          borderLeft: `6px solid ${accentGold}`,
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          padding: `${16 * fontScale}px ${24 * fontScale}px`,
          borderRadius: `${4 * fontScale}px`,
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 36px rgba(0,0,0,0.6)'
        }}
      >
        <div
          style={{
            fontSize: `${12 * fontScale}px`,
            color: accentGold,
            letterSpacing: '0.14em',
            fontWeight: 800
          }}
        >
          ● {actTitle.toUpperCase()}
        </div>
        <div
          style={{
            fontSize: `${22 * fontScale}px`,
            fontWeight: 900,
            color: '#FFFFFF',
            letterSpacing: '-0.02em',
            margin: `${4 * fontScale}px 0`
          }}
        >
          {location}
        </div>
        <div
          style={{
            fontSize: `${11 * fontScale}px`,
            color: primaryCyan,
            opacity: 0.9,
            letterSpacing: '0.06em'
          }}
        >
          WINDOW: {timeWindow} | CODE: {shotId}
        </div>
      </div>

      {/* 2. TOP-RIGHT: Telemetry & SMPTE Timecode */}
      <div
        style={{
          position: 'absolute',
          top: `${padding}px`,
          right: `${padding}px`,
          background: 'rgba(7, 9, 14, 0.85)',
          borderRight: `6px solid ${primaryCyan}`,
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          padding: `${16 * fontScale}px ${24 * fontScale}px`,
          borderRadius: `${4 * fontScale}px`,
          textAlign: 'right',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 36px rgba(0,0,0,0.6)'
        }}
      >
        <div
          style={{
            fontSize: `${12 * fontScale}px`,
            color: accentPurple,
            letterSpacing: '0.12em',
            fontWeight: 800
          }}
        >
          AUDIO EBU R128 (-14 LUFS) // DUCKING -18dB
        </div>
        <div
          style={{
            fontSize: `${20 * fontScale}px`,
            fontWeight: 900,
            color: '#FFFFFF',
            margin: `${4 * fontScale}px 0`
          }}
        >
          TC: {timestampCode}
        </div>
        <div
          style={{
            fontSize: `${11 * fontScale}px`,
            color: primaryCyan,
            letterSpacing: '0.04em'
          }}
        >
          KODAK VISION3 500T // 4K 60FPS CINEMA
        </div>
      </div>

      {/* 3. BOTTOM-LEFT: Lower-Third Scientific Metadata */}
      <div
        style={{
          position: 'absolute',
          bottom: `${padding}px`,
          left: `${padding}px`,
          background: 'rgba(7, 9, 14, 0.85)',
          borderLeft: `6px solid ${accentPurple}`,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          padding: `${16 * fontScale}px ${24 * fontScale}px`,
          maxWidth: is4K ? '950px' : '520px',
          borderRadius: `${4 * fontScale}px`,
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 36px rgba(0,0,0,0.6)'
        }}
      >
        <div
          style={{
            fontSize: `${13 * fontScale}px`,
            color: accentGold,
            letterSpacing: '0.12em',
            fontWeight: 800
          }}
        >
          INFRAESTRUCTURA & CIENCIA // {lowerThird}
        </div>
        <div
          style={{
            fontSize: `${11 * fontScale}px`,
            color: '#FFFFFF',
            marginTop: `${6 * fontScale}px`,
            lineHeight: 1.4,
            opacity: 0.95
          }}
        >
          TELEMETRÍA: {telemetry}
        </div>
        <div
          style={{
            fontSize: `${10 * fontScale}px`,
            color: primaryCyan,
            marginTop: `${4 * fontScale}px`,
            opacity: 0.8
          }}
        >
          CANONICAL DOP 7-LAYER // DETERMINISTIC LEVENSHTEIN ALIGNED
        </div>
      </div>

      {/* 4. BOTTOM-RIGHT: Sequence Progress */}
      <div
        style={{
          position: 'absolute',
          bottom: `${padding}px`,
          right: `${padding}px`,
          background: 'rgba(7, 9, 14, 0.85)',
          borderRight: `6px solid ${primaryCyan}`,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          padding: `${16 * fontScale}px ${24 * fontScale}px`,
          borderRadius: `${4 * fontScale}px`,
          textAlign: 'right',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 12px 36px rgba(0,0,0,0.6)'
        }}
      >
        <div
          style={{
            fontSize: `${11 * fontScale}px`,
            color: primaryCyan,
            letterSpacing: '0.14em',
            fontWeight: 800
          }}
        >
          SECUENCIA DE TOMA
        </div>
        <div
          style={{
            fontSize: `${22 * fontScale}px`,
            fontWeight: 900,
            color: '#FFFFFF',
            margin: `${4 * fontScale}px 0`
          }}
        >
          SHOT [{shotIndex.toString().padStart(2, '0')}/{totalShots.toString().padStart(2, '0')}]
        </div>
        <div
          style={{
            width: `${180 * fontScale}px`,
            height: `${6 * fontScale}px`,
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            borderRadius: '3px',
            overflow: 'hidden',
            marginTop: `${6 * fontScale}px`,
            display: 'inline-block'
          }}
        >
          <div
            style={{
              width: `${(shotIndex / totalShots) * 100}%`,
              height: '100%',
              backgroundColor: accentGold,
              transition: 'width 0.3s ease'
            }}
          />
        </div>
      </div>

      {/* 5. CENTER: 6-DoF Tactical Reticle */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) scale(${reticleScale}) rotate(${rollAngle}deg)`,
          width: `${160 * fontScale}px`,
          height: `${160 * fontScale}px`,
          border: '1.5px solid rgba(0, 229, 255, 0.25)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 30px rgba(0, 229, 255, 0.12)'
        }}
      >
        <div
          style={{
            width: `${6 * fontScale}px`,
            height: `${6 * fontScale}px`,
            backgroundColor: accentGold,
            borderRadius: '50%',
            boxShadow: `0 0 10px ${accentGold}`
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: `${-20 * fontScale}px`,
            width: `${35 * fontScale}px`,
            height: '2px',
            backgroundColor: primaryCyan
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: '50%',
            right: `${-20 * fontScale}px`,
            width: `${35 * fontScale}px`,
            height: '2px',
            backgroundColor: primaryCyan
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: `${-20 * fontScale}px`,
            left: '50%',
            width: '2px',
            height: `${35 * fontScale}px`,
            backgroundColor: primaryCyan
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: `${-20 * fontScale}px`,
            left: '50%',
            width: '2px',
            height: `${35 * fontScale}px`,
            backgroundColor: primaryCyan
          }}
        />
      </div>
    </div>
  );
};
