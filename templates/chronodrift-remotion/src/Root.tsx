import React from 'react';
import { Composition } from 'remotion';
import { ChronoDriftComposition } from './Composition';
import { DocumentaryComposition } from './DocumentaryComposition';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="DocumentalUmbralCuantico120s"
        component={DocumentaryComposition}
        durationInFrames={7200} // 120 segundos a 60 fps
        fps={60}
        width={3840}
        height={2160}
        defaultProps={{
          title: 'El Umbral Cuántico: La Revolución Silenciosa del Silicio',
          totalDurationSec: 120.0,
          shots: [],
          subtitleChunks: [],
          highlightColor: '#FFD700',
          textColor: '#FFFFFF'
        }}
      />
      <Composition
        id="ChronoDriftMaster"
        component={ChronoDriftComposition}
        durationInFrames={2520} // 42 segundos a 60 fps
        fps={60}
        width={3840}
        height={2160}
        defaultProps={{
          cityKey: 'tokyo',
          cityName: 'Tokio',
          country: 'Japón',
          coordinates: '35.6762° N, 139.6503° E',
          totalDurationSec: 42.0,
          shots: []
        }}
      />
      <Composition
        id="ChronoDriftShorts"
        component={ChronoDriftComposition}
        durationInFrames={900} // 15 segundos a 60 fps
        fps={60}
        width={2160}
        height={3840}
        defaultProps={{
          cityKey: 'tokyo',
          cityName: 'Tokio',
          country: 'Japón',
          coordinates: '35.6762° N, 139.6503° E',
          totalDurationSec: 15.0,
          shots: []
        }}
      />
    </>
  );
};
