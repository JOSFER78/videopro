#!/usr/bin/env python3
"""
learning_memory_tool.py
=======================
Herramienta de Auditoría Forense y Memoria Continua de Aprendizaje para VideoPro.
Evalúa proyectos frente a las 10 Reglas Forenses (R01 a R10), calcula scores,
detecta anomalías en el montaje y se integra con el motor de auto-mejora continua.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Añadir raíz de VideoPro al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from scripts.workflow_learner import WorkflowLearner, GOLDEN_RULES_CATALOG
except ImportError:
    # Fallback si se ejecuta desde otra ubicación
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from workflow_learner import WorkflowLearner, GOLDEN_RULES_CATALOG


class LearningMemoryTool:
    """
    Herramienta de auditoría forense, control de calidad y memoria de aprendizaje para VideoPro.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = BASE_DIR / "storage" / "learning_memory"
            if not self.storage_dir.exists():
                fallback = Path(os.path.expanduser("~/.hermes/skills/creative/videopro/learning_memory"))
                if fallback.exists():
                    self.storage_dir = fallback

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.learner = WorkflowLearner(
            storage_dir=self.storage_dir.parent if self.storage_dir.name == "learning_memory" else self.storage_dir,
            learning_dir=self.storage_dir
        )
        self.critiques_file = self.storage_dir / "project_critiques.json"
        self.lessons_file = self.storage_dir / "lessons_catalog.json"

    def audit_project(self, project_manifest_path_or_dict: Union[str, Path, dict]) -> Dict[str, Any]:
        """
        Audita un proyecto contra el catálogo de 10 Reglas de Oro y retorna el veredicto estructurado.
        """
        try:
            manifest_data, project_dir = self.learner.load_manifest(project_manifest_path_or_dict)
            audit_res = self.learner.audit_project(manifest_data, project_dir)
            anomalies_res = self.learner.detect_montage_anomalies(manifest_data, project_dir)

            return {
                "project_id": audit_res["project_id"],
                "archetype_id": audit_res["archetype_id"],
                "score": audit_res["overall_score"],
                "passed": audit_res["passed"],
                "total_penalties": audit_res["total_penalties"],
                "violations_count": audit_res["violations_count"],
                "critical_violations_count": audit_res["critical_violations_count"],
                "violations": [
                    f"[{v.get('rule_id')}] {v.get('name')}: {'; '.join(v.get('details', []))}"
                    for v in audit_res.get("violations", [])
                ],
                "detailed_violations": audit_res.get("violations", []),
                "anomalies": anomalies_res.get("anomalies", []),
                "rules_checked": audit_res["rules_checked"],
                "category_scores": audit_res["category_scores"],
                "audited_at": audit_res["audited_at"]
            }
        except Exception as ex:
            return {
                "project_id": "unknown",
                "score": 0.0,
                "passed": False,
                "error": str(ex),
                "violations": [f"Error de ejecución en auditoría: {ex}"],
                "rules_checked": len(GOLDEN_RULES_CATALOG)
            }

    def optimize_project(self, project_manifest_path_or_dict: Union[str, Path, dict], archetype_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Audita el proyecto y auto-parchea el workflow correspondiente a la versión v+1.
        """
        return self.learner.audit_and_optimize_post_execution(
            project_manifest_path_or_dict,
            archetype_id=archetype_id,
            auto_patch=True
        )

    def get_lessons(self) -> List[Dict[str, Any]]:
        """Obtiene el catálogo de lecciones aprendidas."""
        if self.lessons_file.exists():
            try:
                with open(self.lessons_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def get_critiques(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de evaluaciones de proyectos."""
        if self.critiques_file.exists():
            try:
                with open(self.critiques_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []


def main():
    parser = argparse.ArgumentParser(description="Learning Memory QA Tool & Forensic Auditor")
    parser.add_argument("--audit", type=str, help="Ruta al project_manifest.json o directorio del proyecto")
    parser.add_argument("--optimize", type=str, help="Audita y auto-parchea el workflow del arquetipo a v+1")
    parser.add_argument("--archetype", type=str, help="ID explícito del arquetipo de workflow")
    parser.add_argument("--list-rules", action="store_true", help="Listar las 10 Reglas de Oro")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    args = parser.parse_args()

    tool = LearningMemoryTool()

    if args.list_rules:
        if args.json:
            print(json.dumps(GOLDEN_RULES_CATALOG, indent=2, ensure_ascii=False))
        else:
            print("📋 10 REGLAS FORENSES DE APRENDIZAJE VIDEOPRO (R01 A R10):")
            for r in GOLDEN_RULES_CATALOG:
                print(f"  [{r['id']}] {r['name']} (Severidad: {r['severity']}, Penalización: -{r['penalty']} pts)")
                print(f"     • {r['description']}")
        return

    if args.optimize:
        res = tool.optimize_project(args.optimize, archetype_id=args.archetype)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(tool.learner.export_report_markdown(res))
        return

    if args.audit:
        res = tool.audit_project(args.audit)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"\n📊 RESULTADO DE AUDITORÍA QA FORENSE: Score {res.get('score', 0.0)}/100.0 (Aprobado: {res.get('passed', False)})")
            print(f"   • Proyecto: {res.get('project_id')}")
            print(f"   • Arquetipo: {res.get('archetype_id')}")
            print(f"   • Penalizaciones Totales: -{res.get('total_penalties', 0.0)} pts")
            if res.get("violations"):
                print("\n⚠️ Violaciones Detectadas:")
                for v in res["violations"]:
                    print(f"   - {v}")
            else:
                print("   🎉 Cero violaciones detectadas.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
