import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def test_skill_md_exists():
    assert (SKILL_DIR / "SKILL.md").exists()


def test_references_exist():
    refs = list((SKILL_DIR / "references").glob("*.md"))
    assert len(refs) >= 5


def test_scripts_exist():
    scripts = list((SKILL_DIR / "scripts").glob("*"))
    assert any(s.name == "verify-assets.py" for s in scripts)


def test_templates_exist():
    assert (SKILL_DIR / "templates").exists()
