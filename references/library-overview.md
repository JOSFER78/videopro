# Vox Animation Components Library

A curated collection of React components that bring Vox-style animations to Remotion videos.

## Problem Solved
Before this library, Remotion developers had to manually implement:
- Complex spring-based animations
- SVG stroke-dash techniques
- Picture-in-picture overlays with spring exits
- Animated data presentations

## Solution
This library provides reusable, well-typed components that handle these complex animations with minimal setup, following Vox design principles.

## Core Features

### 1. Spring Animation System
- Predefined spring configs (`gentle`, `snappy`, `bouncy`, `smooth`, `stiff`)
- `useVoxSpring` hook for easy spring creation
- Scale, opacity, position, and rotation animation helpers

### 2. SVG Drawing Utilities
- Stroke-dash animation with customizable easing
- Multi-path staggered entrance effect
- 12 predefined easing functions

### 3. Picture-in-Picture Overlays
- 9 position options (4 corners + center variations)
- Size presets (small, medium, large, full)
- Spring enter/exit animations with configurable durations
- Backdrop-filter support for blurred backgrounds

### 4. Data Card Components
- Animated data presentation with staggered entrances
- Multiple styling variations (glassmorphism, outlined, accent-colored)
- Grid layout with automatic spacing and alignment

## Installation
Just import from the package and you're ready to go:

```tsx
import { VoxDataCard, VoxStaggeredDraw } from 'remotion/App/Components';
```

## Dependencies
- Remotion 4.x
- React 18+

No additional npm packages required.