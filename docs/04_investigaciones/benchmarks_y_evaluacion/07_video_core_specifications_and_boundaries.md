# Video Core Technical Specifications (Hermesvideopro Skill)

## 2. Estándares de Programación (Video-as-Code) and Composición 3D
- **Deterministic Frame-Based Animation**: Must use `useCurrentFrame()`; disabled ms-based logic.
- **Interpolation vs. Spring**:
  - `interpolate()` for linear/scale animations.
  - `spring()` for realistic motion; configure `mass`, `stiffness`, `damping` for organic rebounds.
- **Layering**: Use `<AbsoluteFill>` for absolute layers; wrap time-based layers in `<Sequence>`.
- **HyperShader Effects**: Limit to 2‑3 high-energy transitions; map energy to specific shaders (calma/editorial, profesional/corporativo, energía‑alta/glitch).
- **autoAlpha for Non-Anchors**: Use `autoAlpha` instead of `visibility` to prevent black screens.

## 3. Ingeniería de Sonido, Pacing y Sincronismo
- **Word-Level Transcription**: Use `takes_packed.md` + ElevenLabs Scribe; inject 30-200 ms padding.
- **Phase-Click Mitigation**: Apply mandatory 30 ms cross-fade at every cut.
- **Audio Ducking Hierarchy**:
  - Main narration: +10 dB.
  - Background music: duck to –20 dB to –25 dB on voice detection.
  - Foley (paper, typewriter, shutter): subtle, frame-synced.
- **Strict Word Boundaries**: Cuts only at silences/pauses; never split a word.

## 4. Arquitectura de Automatización y QA Loop
- **Conversational State**: Pass `previous_interaction_id`; require `store:true` for persistence.
- **Prompt Isolation**: One concrete change per request; append “Keep everything else the same”.
- **Lip-Sync**: Enclose dialogue in double quotes `""`.
- **Image Role Mapping**: `<FIRST_FRAME>` for start frame; `<IMAGE_REF_N>` for references only.
- **Auto-Evaluation**: Generate `timeline_view` with Playwright; capture 1920×1080 video.
- **Brand Integration**: Colors → `#F4F1EA` (no pure #FFFFFF); fonts → Monospace (JetBrains Mono); TTS voice vars from `voice.json`.

> Tip: All new technical blocks are modular; add pitfalls or trigger conditions as needed in the main skill file.