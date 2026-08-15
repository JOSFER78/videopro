# Visual Redesign – Asset Swap & Filter Removal

## What was changed
- **Removed** `filter: 'hue-rotate(90deg)'` from `src/compositions/PogacarSuperMaster60s.tsx` line 82.
- **Replaced** stock image `assets/pogacar_tour.jpg` with real photo `assets/pogacar_giro.jpg`.
- **Verified** presence of supporting assets:
  - `pogacar_victory.jpg`
  - `pogacar_cutout.png`
  - `pogacar_cutout.png` (duplicate removed)
  - `pogacar_tour.jpg` (kept for alternate scenes)
- **Checked** all other `filter:` usages across TSX files; none remain that distort color.

## Step‑by‑step recap
1. **Edit TSX** – swap `staticFile('assets/pogacar_tour.jpg')` → `staticFile('assets/pogacar_giro.jpg')` and delete `filter: 'hue-rotate(90deg)'`.
2. **Confirm file existence** in `public/assets/` (run `search_files` or `ls`).
3. **Search for remaining filters**: `grep -R "filter:" --include="*.tsx" --include="*.js" --include="*.jsx" --include="*.ts" .`
4. **Re‑build** (`npm run build`) and validate output.

## Pitfalls & fixes
- **Wrong asset name** → 404; double‑check spelling and case.
- **Missing filter** → color cast returns; run the `grep` search to ensure none left.
- **Low‑resolution image** → pixelation; use ≥1920 px width.

## Related skill
- `video-editor-pro` – core video production framework.

## References
- `templates/visual-redesign-starter/manifest.json` – starter manifest for new visual projects.