import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';

export interface KineticWord {
  word: string;
  clean_word: string;
  start: number;
  end: number;
  duration_cs?: number;
  is_key_word?: boolean;
}

export interface KineticChunk {
  chunk_index: number;
  shot_index: number;
  time_window: string;
  start: number;
  end: number;
  words: KineticWord[];
  full_text: string;
  primary_highlight_word?: string;
}

export interface KineticSubtitlesProps {
  chunks: KineticChunk[];
  highlightColor?: string; // e.g. '#FFD700'
  textColor?: string;      // e.g. '#FFFFFF'
  fontFamily?: string;
  fontSize?: number;
  bottomPositionPx?: number;
}

export const KineticSubtitles: React.FC<KineticSubtitlesProps> = ({
  chunks = [],
  highlightColor = '#FFD700',
  textColor = '#FFFFFF',
  fontFamily = "'League Spartan', 'Liberation Sans', sans-serif",
  fontSize = 64,
  bottomPositionPx = 180
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeSec = frame / fps;

  // Find active chunk
  const activeChunk = chunks.find(
    (ch) => currentTimeSec >= ch.start && currentTimeSec <= ch.end
  );

  if (!activeChunk) {
    return null;
  }

  // Chunk entry transition
  const chunkStartFrame = Math.floor(activeChunk.start * fps);
  const relChunkFrame = Math.max(0, frame - chunkStartFrame);
  const chunkScale = spring({
    frame: relChunkFrame,
    fps,
    config: { damping: 14, stiffness: 160 }
  });
  const chunkOpacity = interpolate(relChunkFrame, [0, 4], [0, 1], {
    extrapolateRight: 'clamp'
  });

  return (
    <div
      style={{
        position: 'absolute',
        bottom: `${bottomPositionPx}px`,
        left: '50%',
        transform: `translateX(-50%) scale(${chunkScale})`,
        opacity: chunkOpacity,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50,
        pointerEvents: 'none'
      }}
    >
      {/* Translucent Rounded Pill Box */}
      <div
        style={{
          background: 'rgba(10, 14, 23, 0.88)',
          border: '2px solid rgba(255, 255, 255, 0.12)',
          boxShadow: '0 16px 48px rgba(0, 0, 0, 0.75), 0 0 24px rgba(255, 215, 0, 0.15)',
          borderRadius: '24px',
          padding: '16px 36px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '14px',
          alignItems: 'center',
          justifyContent: 'center',
          backdropFilter: 'blur(20px)',
          maxWidth: '85vw'
        }}
      >
        {activeChunk.words.map((w, idx) => {
          const isWordActive =
            currentTimeSec >= w.start && currentTimeSec <= w.end;
          const wordStartFrame = Math.floor(w.start * fps);
          const relWordFrame = Math.max(0, frame - wordStartFrame);

          // Kinetic pop animation when active
          const wordPopScale = isWordActive
            ? spring({
                frame: relWordFrame,
                fps,
                config: { damping: 10, stiffness: 200 }
              }) * 1.12
            : 1.0;

          const isKey = w.is_key_word;
          const wordColor = isWordActive
            ? highlightColor
            : isKey
            ? 'rgba(255, 215, 0, 0.85)'
            : textColor;

          return (
            <span
              key={`${activeChunk.chunk_index}-${idx}`}
              style={{
                fontFamily,
                fontSize: `${fontSize}px`,
                fontWeight: isWordActive || isKey ? 900 : 700,
                color: wordColor,
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                transform: `scale(${wordPopScale})`,
                display: 'inline-block',
                transition: 'color 0.08s ease, transform 0.08s ease',
                textShadow: isWordActive
                  ? `0 0 24px ${highlightColor}, 0 2px 8px rgba(0,0,0,0.9)`
                  : '0 2px 8px rgba(0,0,0,0.85)'
              }}
            >
              {w.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};
