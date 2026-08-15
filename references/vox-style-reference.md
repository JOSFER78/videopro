# Vox‑Style Visual System – Reference Sheet

## Design Tokens
| Token | Value | Usage |
|-------|-------|-------|
| Primary text | `#111111` | Main copy, headings |
| Accent orange | `#FF6600` | Highlights, accent stripe |
| Paper background | `#F9F9F9` | Paper‑cutout base |
| Paper border | `#BBBBBB` | Stroke on cut edges |
| Badge background | `#222222` | Technical badge background |
| Badge text | `#FFFFFF` | Text inside badge |
| Corner radius | `8px` | Rounded paper corners |
| Stroke width | `2px` | Outline thickness |
| Drop shadow | `0 4px 6px rgba(0,0,0,0.15)` | Depth for floating elements |
| Heading font | `Helvetica Neue, Arial, sans-serif` | Title & headings |
| Body font | `Georgia, serif` | Body copy & subtitles |
| Layout width | `800px` | Base container width |
| Layout margin | `40px` | Side margins |

### Color Palette (CSS Variables)
```css
:root {
  --c-primary-text: #111111;
  --c-accent-orange: #FF6600;
  --c-paper-bg: #F9F9F9;
  --c-paper-border: #BBBBBB;
  --c-badge-bg: #222222;
  --c-badge-text: #FFFFFF;
  --c-corner-radius: 8px;
  --c-stroke-width: 2px;
  --c-shadow: rgba(0,0,0,0.15);
  --font-heading: Helvetica Neue, Arial, sans-serif;
  --font-body: Georgia, serif;
}
```

## SVG Template Snapshots
All assets live in `assets/` and share structural conventions:

| File | viewBox | Key Elements | Size |
|------|---------|--------------|------|
| `lower-third.svg` | `0 0 800 200` | Triangular fold, orange stripe, badge | < 10 KB |
| `lower-third-alt.svg` | `0 0 800 200` | “LIVE” pill tag, updated typography | < 10 KB |
| `callout-badge.svg` | `0 0 260 80` | Dark body, orange trim, label | < 10 KB |
| `callout-badge-alt.svg` | `0 0 260 80` | Warning icon, “ATENCIÓN TÉCNICA” | < 10 KB |
| `floating-element.svg` | `0 0 200 200` | Swoosh path + accent dot | < 10 KB |
| `floating-element-alt.svg` | `0 0 200 200` | Outer ring + geometric accent | < 10 KB |

### Consistency Rules
- Every SVG must contain `xmlns="http://www.w3.org/2000/svg"`.
- Must include a proper `viewBox="0 0 {W} {H}"`.
- Must end with `</svg>` (no trailing whitespace after).
- Use CSS variables defined in `:root` for colors and dimensions.
- Target final file size < 10 KB after minification.
- Export scripts (`verify-svgs.py`) validate these constraints.

## p5.js Sketch Overview
- **Location**: `p5js/sketch.js` + `p5js/index.html`.
- **Canvas**: 1280×720, 60 fps target.
- **Animation Loop**: updates floating elements, pulses badge, renders lower‑third.
- **Interaction**: `S` → save PNG, `R` → reseed randomness.
- **Export**: `saveCanvas('vox-motion', 'png')`.

---

*Generated on 2026‑07‑31 by Hermes Agent (default profile).*