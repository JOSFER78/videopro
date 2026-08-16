import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { ChronoDriftHUD } from './components/ChronoDriftHUD';
import { TritemporalShaderTransition } from './components/TritemporalShaderTransition';
import { BuildingSpatialAnchor } from './components/BuildingSpatialAnchor';

export interface ChronoDriftCompositionProps {
  cityKey: string;
  cityName: string;
  country: string;
  coordinates: string;
  totalDurationSec: number;
  shots: Array<{
    shot_index: number;
    shot_id: string;
    epoch: string;
    duration_sec: number;
    hud_overlay: {
      title: string;
      telemetry: string;
      fact_text: string;
      citation: string;
    };
  }>;
}

export const ChronoDriftComposition: React.FC<ChronoDriftCompositionProps> = ({
  cityKey = 'tokyo',
  cityName = 'Tokio',
  country = 'Japón',
  coordinates = '35.6762° N, 139.6503° E',
  totalDurationSec = 42.0,
  shots = []
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTimeSec = frame / fps;

  // Determinar plano actual según tiempo acumulado
  let accumulatedSec = 0;
  let activeShot = shots[0] || {
    shot_index: 1,
    shot_id: '01_STRATOSPHERE_TIME_DIVE',
    epoch: 'TRANSITION_1630',
    duration_sec: 4.5,
    hud_overlay: {
      title: 'INICIO DE VUELO TRITEMPORAL',
      telemetry: 'ALT: 850m | VEL: 140 km/h',
      fact_text: 'Anclaje fotogramétrico 6-DoF y cartografía histórica.',
      citation: 'ChronoDrift Engine'
    }
  };

  let shotStartFrame = 0;
  for (const shot of shots) {
    if (currentTimeSec >= accumulatedSec && currentTimeSec < accumulatedSec + shot.duration_sec) {
      activeShot = shot;
      shotStartFrame = Math.floor(accumulatedSec * fps);
      break;
    }
    accumulatedSec += shot.duration_sec;
  }

  // Cálculo dinámico de año según la época
  let currentYear = 2026;
  if (activeShot.epoch.includes('16') || activeShot.epoch.includes('18')) {
    const num = parseInt(activeShot.epoch.replace(/\D/g, ''), 10);
    currentYear = num || 1626;
  } else if (activeShot.epoch.includes('2226')) {
    currentYear = 2226;
  }

  // Altitud y velocidad simuladas por plano
  let altMeters = 50.0;
  let speedKmh = 90.0;
  if (activeShot.shot_index === 1) {
    altMeters = 850 - (frame / (activeShot.duration_sec * fps)) * 815;
    speedKmh = 140;
  } else if (activeShot.shot_index === 2) {
    altMeters = 1.8 + (frame / (activeShot.duration_sec * fps)) * 13.2;
    speedKmh = 110;
  } else if (activeShot.shot_index === 3) {
    altMeters = 2.5 + (frame / (activeShot.duration_sec * fps)) * 1.5;
    speedKmh = 85;
  } else if (activeShot.shot_index === 4) {
    altMeters = 25 + (frame / (activeShot.duration_sec * fps)) * 60;
    speedKmh = 75;
  } else if (activeShot.shot_index === 5) {
    altMeters = 85 + (frame / (activeShot.duration_sec * fps)) * 165;
    speedKmh = 95;
  } else if (activeShot.shot_index === 6) {
    altMeters = 250 + (frame / (activeShot.duration_sec * fps)) * 50;
    speedKmh = 125;
  } else {
    altMeters = 300 + (frame / (activeShot.duration_sec * fps)) * 200;
    speedKmh = 90;
  }

  // Comprobar si el ducking de voz está activo (primeros 3.5s de cada plano)
  const relTimeInShot = currentTimeSec - (shotStartFrame / fps);
  const isDucking = relTimeInShot >= 0.5 && relTimeInShot <= 4.0;

  return (
    <AbsoluteFill style={{ backgroundColor: '#07090e' }}>
      {/* 1. Fondo de vídeo o gradiente cinematográfico fotogramétrico */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse at 50% 40%, #161b26 0%, #07090e 100%)'
        }}
      />

      {/* 2. Capa de Grano Cinematográfico Kodak Vision3 500T */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.04,
          backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)',
          backgroundSize: '3px 3px',
          pointerEvents: 'none'
        }}
      />

      {/* 3. Transición de Shaders de Match-Cut (Fotograma 630 = ~10.5s) */}
      <TritemporalShaderTransition
        transitionFrame={Math.floor(10.5 * fps)}
        durationFrames={30}
        fromEpoch="PAST_1626"
        toEpoch="PRESENT_2026"
      />

      {/* 4. Transición a la Era Futura (Fotograma 1350 = ~22.5s) */}
      <TritemporalShaderTransition
        transitionFrame={Math.floor(22.5 * fps)}
        durationFrames={30}
        fromEpoch="PRESENT_2026"
        toEpoch="FUTURE_2226"
      />

      {/* 5. Anclaje Espacial 3D a Edificios Históricos & Futuros (Plano 2, 4 y 6) */}
      {activeShot.shot_index === 2 && (
        <BuildingSpatialAnchor
          buildingName={`${cityName} Historic Core`}
          epoch={`PAST_${currentYear}`}
          yearBuilt={currentYear}
          heightMeters={24.5}
          osmHeritageTag="OSM:heritage=monument_class_1"
          historicalFact={activeShot.hud_overlay?.fact_text || 'Estructuras de madera de roble y adoquines originales.'}
          screenXPercent={42}
          screenYPercent={52}
          fps={fps}
          startFrame={shotStartFrame + 20}
          durationFrames={Math.floor(activeShot.duration_sec * fps) - 40}
        />
      )}

      {activeShot.shot_index === 4 && (
        <BuildingSpatialAnchor
          buildingName={`${cityName} Financial Monolith`}
          epoch="PRESENT_2026"
          yearBuilt={2026}
          heightMeters={380.0}
          osmHeritageTag="OSM:building=commercial"
          historicalFact={activeShot.hud_overlay?.fact_text || 'Cañones de cristal y acero sismorresistente con fachadas low-E.'}
          screenXPercent={58}
          screenYPercent={38}
          fps={fps}
          startFrame={shotStartFrame + 20}
          durationFrames={Math.floor(activeShot.duration_sec * fps) - 40}
        />
      )}

      {activeShot.shot_index === 6 && (
        <BuildingSpatialAnchor
          buildingName={`Neo-${cityName} Hyper-Arcology`}
          epoch="FUTURE_2226"
          yearBuilt={2226}
          heightMeters={1200.0}
          osmHeritageTag="IPCC/MIT:arcology_resilience_grid"
          historicalFact={activeShot.hud_overlay?.fact_text || 'Arcología de titanio y nanotubos de grafeno con microclimas cerrados.'}
          screenXPercent={52}
          screenYPercent={32}
          fps={fps}
          startFrame={shotStartFrame + 20}
          durationFrames={Math.floor(activeShot.duration_sec * fps) - 40}
        />
      )}

      {/* 6. HUD 3D Flotante de Telemetría */}
      <ChronoDriftHUD
        currentYear={currentYear}
        cityName={cityName}
        country={country}
        coordinates={coordinates}
        altitudeMeters={Math.max(1.0, altMeters)}
        speedKmh={speedKmh}
        shotId={activeShot.shot_id}
        shotIndex={activeShot.shot_index}
        totalShots={shots.length || 7}
        scientificCitation={activeShot.hud_overlay?.citation || 'Estudios de Resiliencia Urbana'}
        factText={activeShot.hud_overlay?.fact_text || 'Grounding geoespacial tritemporal.'}
        isDuckingActive={isDucking}
        fps={fps}
      />
    </AbsoluteFill>
  );
};
