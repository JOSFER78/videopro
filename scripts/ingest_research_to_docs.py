#!/usr/bin/env python3
"""
scripts/ingest_research_to_docs.py — Sistema Automatizado de Ingesta y Documentación de Investigaciones
Permite procesar, formatear y archivar investigaciones técnicas en los 5 macro-pilares de docs/.
"""

import os
import sys
import re
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INV_DIR = os.path.join(DOCS_DIR, "04_investigaciones")

AREAS_MAP = {
    "visual": "visual_y_3d",
    "3d": "visual_y_3d",
    "shaders": "visual_y_3d",
    "dop": "visual_y_3d",
    "camara": "visual_y_3d",
    "actores": "visual_y_3d",
    "audio": "audio_y_foley",
    "musica": "audio_y_foley",
    "foley": "audio_y_foley",
    "psicoacustica": "audio_y_foley",
    "ducking": "audio_y_foley",
    "remotion": "motion_y_codigo",
    "motion": "motion_y_codigo",
    "vox": "motion_y_codigo",
    "mapas": "motion_y_codigo",
    "hyperframes": "motion_y_codigo",
    "benchmark": "benchmarks_y_evaluacion",
    "costes": "benchmarks_y_evaluacion",
    "latencia": "benchmarks_y_evaluacion",
    "comparativa": "benchmarks_y_evaluacion"
}

def auto_detect_area(title: str, content: str) -> str:
    text = f"{title} {content}".lower()
    for kw, area in AREAS_MAP.items():
        if kw in text:
            return area
    return "visual_y_3d"

def sanitize_filename(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s-]+', '_', s)
    return s[:60]

def ingest_research(title: str, content: str, area: str = None, author: str = "Hermes Research Agent") -> str:
    if not area or area not in ["visual_y_3d", "audio_y_foley", "motion_y_codigo", "benchmarks_y_evaluacion"]:
        area = auto_detect_area(title, content)
    
    target_folder = os.path.join(INV_DIR, area)
    os.makedirs(target_folder, exist_ok=True)
    
    fn = f"{sanitize_filename(title)}.md"
    file_path = os.path.join(target_folder, fn)
    
    # Formatear el documento según el Estándar de Ingeniería
    doc_header = f"""# 🔬 {title}

> **Pilar:** `docs/04_investigaciones/{area}/`  
> **Fecha de Ingesta:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  
> **Autor / Fuente:** {author}  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA ACTIVA

---

"""
    full_content = doc_header + content.strip() + "\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    # Actualizar README del área
    readme_path = os.path.join(target_folder, "README.md")
    entry_line = f"- 📄 [`{title}`]({fn}): Ingestado el {datetime.utcnow().strftime('%Y-%m-%d')}\n"
    
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            r_content = f.read()
        if fn not in r_content:
            with open(readme_path, "a", encoding="utf-8") as f:
                f.write(entry_line)
    else:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"# 📂 {area.replace('_', ' ').title()}\n\n{entry_line}")
            
    print(f"✅ Investigación ingesta con éxito en: {file_path}")
    return file_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingestar investigaciones en docs/04_investigaciones/")
    parser.add_argument("--title", "-t", required=True, help="Título de la investigación")
    parser.add_argument("--area", "-a", choices=["visual_y_3d", "audio_y_foley", "motion_y_codigo", "benchmarks_y_evaluacion"], help="Área destino")
    parser.add_argument("--file", "-f", help="Ruta a archivo con el contenido")
    parser.add_argument("--content", "-c", help="Texto directo de la investigación")
    
    args = parser.parse_args()
    
    content = ""
    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.content:
        content = args.content
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("❌ Error: Debes proporcionar --content, --file o pasar el contenido por stdin.")
        sys.exit(1)
        
    ingest_research(args.title, content, args.area)
