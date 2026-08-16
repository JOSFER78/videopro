# Remotion Automation – Session Reference

## Overview
Generates a Remotion composition from a strict `scenes.json` schema and associated data mapping. Used to automatically produce video compositions with layers, Vox overlays, and dynamic data binding.

## Key Files
- **`src/scenes.json`** – Defines scenes, durations, easing, transitions, layers, assets, and Vox definitions.
- **`src/scenes_schema.json`** – JSON‑Schema (draft‑2020‑12) that validates the structure.
- **`data/data_mapping.json`** – Registers assets, layer configs, Vox overlays, and source‑field mappings.
- **`scripts/validate_scenes.py`** – Validates schema and runs semantic checks.
- **`scripts/generate_composition_fixed.py`** – Emits `src/generated/Composition.tsx`.
- **`src/generated/Composition.tsx`** – Output React/TypeScript component.

## Workflow Steps
1. **Validate** `src/scenes.json` with `scripts/validate_scenes.py`. Fix any warnings (e.g., `total_frames` mismatch).
2. **Generate** component via `scripts/generate_composition_fixed.py`.
3. **Compile** `Composition.tsx` (ensure `"jsx": "react-jsx"` in `tsconfig.json`).
4. **Import** the generated component into your Remotion project (e.g., in `src/Composition.tsx`).

## Troubleshooting
- **Total frames mismatch**: Update `total_frames` in `scenes.json` to match the sum of `sequence_start + duration_frames` for all scenes.
- **Missing asset references**: Ensure asset files (e.g., `assets/icons/grid.svg`) exist and are correctly referenced in `data/data_mapping.json` or directly in `scenes.json`.
- **JSX compilation errors**: Add `"jsx": "react-jsx"` to `tsconfig.json` under `compilerOptions` if not present.
- **Style overrides**: Inline styles from JSON may need adjustment for specific Remotion versions (e.g., CSS property names).

## Example Scene Entry
```json
{
  "id": "scene_dimensions",
  "sequence_start": 0,
  "duration_frames": 240,
  "easing": "easeInOut",
  "transition_in": { "type": "fade", "frames": 15 },
  "transition_out": { "type": "fade", "frames": 15 },
  "layers": [
    {
      "layer_id": "bg_grid",
      "type": "background",
      "z_index": 0,
      "asset_ref": "icon_grid",
      "style": {
        "backgroundColor": "#0a0d14",
        "backgroundImage": "radial-gradient(circle at 50% 40%, #161f33 0%, #080b11 100%)",
        "gridPattern": "radial-gradient(#00f0ff22 1px, transparent 1px)",
        "gridSize": "40px 40px",
        "gridOpacity": 0.4
      }
    }
    // ... other layers
  ]
}
```