import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { KineticSubtitles, KineticChunk } from './components/KineticSubtitles';
import { ModernHUDOverlay } from './components/ModernHUDOverlay';

export interface ShotConfig {
  shot_index: number;
  shot_id: string;
  act: string;
  time_window: string;
  duration_sec: number;
  narration_es: string;
  hud_overlay_telemetry: {
    location: string;
    timestamp_code: string;
    telemetry: string;
    lower_third: string;
  };
}

export interface DocumentaryCompositionProps {
  title?: string;
  totalDurationSec?: number;
  shots?: ShotConfig[];
  subtitleChunks?: KineticChunk[];
  highlightColor?: string;
  textColor?: string;
}

export const DocumentaryComposition: React.FC<DocumentaryCompositionProps> = ({
  title = 'El Umbral Cuántico: La Revolución Silenciosa del Silicio',
  totalDurationSec = 120.0,
  shots = [],
  subtitleChunks = [],
  highlightColor = '#FFD700',
  textColor = '#FFFFFF'
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const currentTimeSec = frame / fps;

  // Determine active shot based on accumulated time
  let accumulatedSec = 0;
  let activeShot: ShotConfig = shots[0] || {
    shot_index: 1,
    shot_id: 'SHOT_01_QUANTUM_CRYOSTAT_DIVE',
    act: 'Acto I: La Grieta en la Realidad',
    time_window: '00:00 - 00:05',
    duration_sec: 5.0,
    narration_es: 'En este instante, a doscientos setenta y tres grados bajo cero...',
    hud_overlay_telemetry: {
      location: 'Laboratorio Subterráneo Gran Sasso, Italia',
      timestamp_code: '00:00:00:00',
      telemetry: 'TEMP: 10.2 mK | VACUUM: 10^-9 mbar | COHERENCE: 99.98%',
      lower_third: 'ARQUITECTURA TOPOLÓGICA DE QÚBITS MONOCRISTALINOS'
    }
  };

  for (const shot of shots) {
    if (currentTimeSec >= accumulatedSec && currentTimeSec < accumulatedSec + shot.duration_sec) {
      activeShot = shot;
      break;
    }
    accumulatedSec += shot.duration_sec;
  }

  const hudInfo = activeShot.hud_overlay_telemetry || {};

  return (
    <AbsoluteFill style={{ backgroundColor: '#05070B' }}>
      {/* 1. Fondo de Escena Cinemático / Gradiente Profundo */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse at 50% 45%, #0d1524 0%, #05070B 100%)'
        }}
      />

      {/* 2. Capa de Textura y Grano Fílmico Kodak Vision3 500T */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.05,
          backgroundImage: 'radial-gradient(#FFFFFF 1px, transparent 1px)',
          backgroundSize: '4px 4px',
          pointerEvents: 'none'
        }}
      />

      {/* 3. Overlay HUD Moderno y Badges Temporales Diegéticos */}
      <ModernHUDOverlay
        actTitle={activeShot.act}
        location={hudInfo.location}
        timeWindow={activeShot.time_window}
        shotId={activeShot.shot_id}
        shotIndex={activeShot.shot_index}
        totalShots={shots.length || 24}
        telemetry={hudInfo.telemetry}
        lowerThird={hudInfo.lower_third}
        timestampCode={hudInfo.timestamp_code}
        primaryCyan="#00E5FF"
        accentGold={highlightColor}
        accentPurple="#B388FF"
      />

      {/* 4. Subtítulos Cinéticos Dinámicos Vox / MrBeast (Oro #FFD700 / Blanco #FFFFFF) */}
      <KineticSubtitles
        chunks={subtitleChunks}
        highlightColor={highlightColor}
        textColor={textColor}
        fontSize={width >= 3840 ? 76 : 42}
        bottomPositionPx={width >= 3840 ? 220 : 120}
      />
    </AbsoluteFill>
  );
};
