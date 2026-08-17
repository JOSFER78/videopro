import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Img,
  Sequence
} from 'remotion';

export interface VoxParallaxProps {
  headline: string;
  documentImage: string;
  highlightText?: string;
  staggerFrames?: number;
  paperTextureOpacity?: number;
}

export const VoxParallaxDocument: React.FC<VoxParallaxProps> = ({
  headline,
  documentImage,
  highlightText = '',
  staggerFrames = 3,
  paperTextureOpacity = 0.25,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 1. Animación elástica de la cámara 3D
  const cameraZoom = interpolate(frame, [0, durationInFrames], [1.0, 1.12], {
    extrapolateRight: 'clamp',
  });

  const cameraRotateZ = interpolate(frame, [0, durationInFrames], [-1.5, 0.5], {
    extrapolateRight: 'clamp',
  });

  // 2. Animación de entrada con spring del documento principal (Frame 0)
  const docSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 100 },
  });

  // 3. Stagger psicoacústico: El titular entra desfasado (Frame = staggerFrames)
  const titleFrame = Math.max(0, frame - staggerFrames);
  const titleSpring = spring({
    frame: titleFrame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 120 },
  });

  // 4. Stagger psicoacústico: El resaltador entra después (Frame = staggerFrames * 2)
  const highlightFrame = Math.max(0, frame - staggerFrames * 2);
  const highlightProgress = interpolate(highlightFrame, [0, 15], [0, 100], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#12161a',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        perspective: '1200px',
        overflow: 'hidden',
        fontFamily: "'Inter', sans-serif",
      }}
    >
      {/* Capa Z-0: Contenedor 3D con rotación y zoom suave */}
      <div
        style={{
          transform: `scale(${cameraZoom}) rotateZ(${cameraRotateZ}deg)`,
          transformStyle: 'preserve-3d',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Capa Z-1: Documento / Periódico Antiguo con Sombra Suave */}
        <div
          style={{
            transform: `translateY(${(1 - docSpring) * 60}px) rotateX(8deg)`,
            opacity: docSpring,
            boxShadow: '0 30px 60px rgba(0,0,0,0.65), 0 10px 20px rgba(0,0,0,0.4)',
            borderRadius: '4px',
            backgroundColor: '#f6f3ea',
            padding: '24px',
            maxWidth: '900px',
            position: 'relative',
          }}
        >
          {documentImage ? (
            <Img
              src={documentImage}
              style={{
                width: '100%',
                maxHeight: '520px',
                objectFit: 'cover',
                filter: 'sepia(0.15) contrast(1.05)',
              }}
            />
          ) : (
            <div style={{ height: '400px', width: '700px', backgroundColor: '#e2dcc8' }} />
          )}

          {/* Capa Z-2: Titular Estilo Prensa */}
          <div
            style={{
              marginTop: '16px',
              transform: `translateY(${(1 - titleSpring) * 30}px)`,
              opacity: titleSpring,
            }}
          >
            <h2
              style={{
                color: '#1a1a1a',
                fontSize: '28px',
                fontWeight: 800,
                letterSpacing: '-0.5px',
                margin: 0,
                textTransform: 'uppercase',
              }}
            >
              {headline}
            </h2>

            {/* Capa Z-3: Marcador / Resaltador Amarillo Flúor Animado */}
            {highlightText && (
              <div style={{ marginTop: '8px', position: 'relative', display: 'inline-block' }}>
                <span
                  style={{
                    position: 'absolute',
                    top: '2px',
                    bottom: '2px',
                    left: '-4px',
                    width: `${highlightProgress}%`,
                    backgroundColor: 'rgba(250, 204, 21, 0.45)',
                    zIndex: 1,
                    borderRadius: '2px',
                  }}
                />
                <span
                  style={{
                    position: 'relative',
                    zIndex: 2,
                    fontSize: '18px',
                    color: '#262626',
                    fontWeight: 600,
                  }}
                >
                  {highlightText}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Capa Z-Top: Viñeteado de estudio perimetral */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle, rgba(0,0,0,0) 45%, rgba(0,0,0,0.65) 100%)',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
