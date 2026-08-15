# Consolidated Skill Location

This document explains where to find the complete skill resources for `videopro`.

## Canonical Skill Location (used by Hermes)
The official skill definition that Hermes loads is located at:
```
~/.hermes/skills/creative/videopro/SKILL.md
```

## Working Copy (Project Workspace)
A complete working copy of all skill resources is maintained in the project workspace for easy access and development:
```
/home/ubuntu/workspace/pro/02-apps-escritorio/hermes-video-factory/_SKILL_VIDEO_COMPLETO/
```

### What's in the Working Copy
The `_SKILL_VIDEO_COMPLETO/` directory contains:
- All pipeline scripts (`build.py`, `render_from_plan.py`, `project_manager.py`, etc.)
- Reference documents (e.g., `HOLLYWOOD_PREPRODUCTION_WORKFLOW.md`)
- Template files and example configurations
- All linked scripts and resources referenced by the skill

## How to Use
When developing or debugging video pipelines:
1. Work from the workspace copy: `_SKILL_VIDEO_COMPLETO/`
2. Make changes to scripts or resources as needed
3. To update the canonical skill, copy changes back to `~/.hermes/skills/video-production/videopro/` or submit a skill patch via the appropriate maintenance process

## Important Notes
- The skill definition in `~/.hermes/skills/...` is the **source of truth** for Hermes
- The workspace copy is a **convenience mirror** for development
- Always verify changes work in the canonical location before considering them complete