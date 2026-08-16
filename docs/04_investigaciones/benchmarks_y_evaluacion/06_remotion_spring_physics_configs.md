# Vox Spring Configuration Reference

This document provides detailed reference for the predefined spring configurations used in the Vox animation components library.

## Spring Configurations

### gentle
- **damping**: 20
- **stiffness**: 100
- **mass**: 1
- **overshootClamping**: false
- **Behavior**: Smooth, fluid entrance. Ideal for subtle animations and background effects.

### snappy
- **damping**: 15
- **stiffness**: 200
- **mass**: 1
- **overshootClamping**: false
- **Behavior**: Fast, responsive feel. Good for interactive elements that require quick feedback.

### bouncy
- **damping**: 8
- **stiffness**: 180
- **mass**: 1
- **overshootClamping**: false
- **Behavior**: Playful, slightly elastic movement. Creates a bouncy effect that feels lively and engaging.

### smooth
- **damping**: 30
- **stiffness**: 80
- **mass**: 1
- **overshootClamping**: true
- **Behavior**: Very relaxed motion with slight overshoot. Best for background transitions where you want a gentle, flowing feel.

### stiff
- **damping**: 25
- **stiffness**: 300
- **mass**: 1
- **overshootClamping**: true
- **Behavior**: Precise, controlled movement with minimal overshoot. Suitable for exact positioning and technical visualizations.