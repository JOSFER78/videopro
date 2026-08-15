# 📂 Structure of the Video Production Skill Repository

This repository consolidates the **`videopro`** skill in a single, self‑contained location for quick reference and version control.

## Top‑level Directories

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Core pipeline scripts (`build.py`, `render_from_plan.py`, `project_manager.py`, `creative_director.py`, etc.). |
| `assets/` | Raw media assets (images, video clips, audio files) generated or downloaded by the workflow. |
| `audio/` | Voice‑over, music, and sound‑effect files (e.g., `narration.mp3`, `bgm.wav`). |
| `scenes.json` | JSON definition of scenes (timestamps, prompts, technical metadata). |
| `references/` | Session‑specific notes, error logs, and external API documentation useful for debugging. |
| `out/` | Final rendered videos (`final.mp4`) and delivery artifacts. |
| `project_manifest.json` | Auto‑generated manifest that records project metadata (name, slug, version, paths). |
| `SKILL.md` | The canonical skill definition (the source of truth for Hermes). |

## Quick Startup Flow

1. **Create Project**  
   ```bash
   python3 project_manager.py create "My Video Title"
   ```
   → Creates a timestamped folder under `projects/videos/YYYY/MM/`.

2. **Generate Plan**  
   ```bash
   python3 creative_director.py --topic "Your topic" --style vox_box --duration 30 --language es
   ```
   → Produces `scenes.json` and related metadata.

3. **Render Video**  
   ```bash
   python3 render_from_plan.py --plan <plan.json> --verbose
   ```
   → Produces `out/final.mp4` (verified >5 KB, correct duration).

4. **Deliver via Telegram**  
   ```bash
   python3 notify_telegram.py --file out/final.mp4 --caption "Your video is ready!"
   ```

## Key Files & Their Roles

- **`SKILL.md`** – Canonical definition of the `videopro` skill.
- **`references/storage-pipeline.md`** – Formal storage hierarchy and project lifecycle reference.
- **`templates/project-manifest.json`** – Canonical template for `project_manifest.json`.
- **`scenes.json`** – Scene‑level prompts, timings, and technical data.
- **`build.py`** – Final composition engine; enforces asset validation (>5 KB, no placeholders).
- **`render_from_plan.py`** – Orchestrates asset generation, overlay application, and encoding.
- **`templates/`** – Starter templates (referenced in `SKILL.md`).
- **`scripts/`** – Reusable utilities (`generate_audio.py`, `qa_check.py`, etc.).

## Maintenance Tips

- **Version Control** – Commit changes to this repository; it serves as the single source of truth.
- **Add References** – When you encounter a non‑trivial error or a novel workaround, drop a concise note into `references/<topic>.md`.
- **Support Scripts** – Place deterministic scripts (e.g., fixture generators) under `scripts/` and link them in `SKILL.md`.

---  

*This file (`references/structure.md`) acts as a map for anyone (including future you) to navigate the repository at a glance.*