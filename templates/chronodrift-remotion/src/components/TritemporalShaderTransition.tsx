import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

export interface TritemporalShaderTransitionProps {
  transitionFrame: number;
  durationFrames?: number;
  fromEpoch: string;
  toEpoch: string;
}

export const TritemporalShaderTransition: React.FC<TritemporalShaderTransitionProps> = ({
  transitionFrame,
  durationFrames = 30,
  fromEpoch,
  toEpoch
}) => {
  const frame = useCurrentFrame();
  const relFrame = frame - transitionFrame;

  if (relFrame < 0 || relFrame > durationFrames) {
    return null;
  }

  const progress = relFrame / durationFrames;
  const flashOpacity = interpolate(progress, [0, 0.4, 1.0], [0, 0.75, 0], { extrapolateRight: 'clamp' });
  const chromaticOffset = Math.sin(progress * Math.PI) * 16;
  const blurAmount = Math.sin(progress * Math.PI) * 8;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 50,
        mixBlendMode: 'screen',
        backdropFilter: `blur(${blurAmount}px)`
      }}
    >
      {/* Destello de Vórtice Temporal */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, rgba(0, 229, 255, 0.8) 0%, rgba(124, 77, 255, 0.4) 40%, rgba(0,0,0,0) 70%)',
          opacity: flashOpacity
        }}
      />
      {/* Franja de aberración cromática */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: `${chromaticOffset}px`,
          right: `${-chromaticOffset}px`,
          bottom: 0,
          borderLeft: '4px solid #00e5ff',
          borderRight: '4px solid #ffb300',
          opacity: flashOpacity
        }}
      />
    </div>
  );
};
