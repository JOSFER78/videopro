import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER_DIR = os.path.join(BASE_DIR, "server")
WEB_DIR = os.path.join(BASE_DIR, "web")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
REFERENCES_DIR = os.path.join(BASE_DIR, "references")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Model paths & virtualenvs
VIBEVOICE_PYTHON = "/home/ubuntu/vibevoice-venv/bin/python"
VIBEVOICE_ROOT = "/home/ubuntu/VibeVoice"
MODELS_DIR = "/home/ubuntu/models"
STORAGE_ROOT = "/var/www/pro/webasset"

os.makedirs(OUTPUTS_DIR, exist_ok=True)
