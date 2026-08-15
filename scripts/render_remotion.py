#!/usr/bin/env python3
"""
render_remotion.py — Renderizado de Composiciones Remotion con VideoStorageManager.
==================================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Ejecuta el renderizado programático de composiciones Remotion (.tsx) utilizando
la estructura canónica de VideoStorageManager. Configura automáticamente tsconfig.json,
dirige la salida a exports/ (out/), aísla la caché en .tmp/ y registra el MP4 final en manifest.json.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from video_storage_manager import (
        MIN_ASSET_SIZE_BYTES,
        VideoStorageManager,
    )
except ImportError:
    from scripts.video_storage_manager import (
        MIN_ASSET_SIZE_BYTES,
        VideoStorageManager,
    )


def configure_remotion_tsconfig(src_dir: Path) -> Path:
    """Asegura que tsconfig.json esté correctamente configurado para JSX/React en Remotion."""
    tsconfig_path = src_dir / "tsconfig.json"
    if not tsconfig_path.exists():
        default_config = {
            "compilerOptions": {
                "target": "es2022",
                "module": "commonjs",
                "jsx": "react-jsx",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
            }
        }
        tsconfig_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
    else:
        try:
            with open(tsconfig_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            compiler_opts = config.setdefault("compilerOptions", {})
            if compiler_opts.get("jsx") != "react-jsx":
                compiler_opts["jsx"] = "react-jsx"
                with open(tsconfig_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
        except Exception as exc:
            print(f"[WARN] Error al verificar tsconfig.json: {exc}", file=sys.stderr)
    return tsconfig_path


def render_remotion_composition(
    project_ref: Optional[Union[str, Path]] = None,
    composition_id: str = "Main",
    entry_point: Optional[str] = None,
    output_filename: str = "final.mp4",
    props: Optional[Dict[str, Any]] = None,
    crf: int = 28,
    concurrency: int = 4,
    gl_backend: str = "angle",
) -> Dict[str, Any]:
    """
    Ejecuta el renderizado de una composición de Remotion y registra el máster exportado.

    Args:
        project_ref: Slug, ID de proyecto o ruta del proyecto canónico.
        composition_id: ID de la composición en Remotion (default: "Main").
        entry_point: Archivo de entrada de Remotion (e.g. "src/index.ts" o "src/Root.tsx").
        output_filename: Nombre del archivo de salida MP4 en exports/ (default: "final.mp4").
        props: Diccionario de props serializables JSON para pasar a la composición.
        crf: Factor de calidad CRF (default: 28).
        concurrency: Número de hilos/procesos paralelos para Remotion.
        gl_backend: Backend OpenGL para Puppeteer ("angle", "egl", "swangle", etc.).

    Returns:
        Dict con el registro del archivo exportado.
    """
    storage = VideoStorageManager(project_ref=project_ref, auto_create=True)
    src_dir = storage.src_dir
    exports_dir = storage.exports_dir
    temp_dir = storage.temp_dir
    cache_dir = temp_dir / ".remotion-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Configurar tsconfig.json en src/
    configure_remotion_tsconfig(src_dir)

    # Determinar entry point de Remotion
    if entry_point:
        entry_path = Path(entry_point).resolve()
    else:
        candidates = [
            src_dir / "index.ts",
            src_dir / "index.tsx",
            src_dir / "Root.tsx",
            src_dir / "Composition.tsx",
        ]
        entry_path = next((c for c in candidates if c.exists()), candidates[0])

    out_file = exports_dir / output_filename
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Iniciando Renderizado Remotion para Proyecto: {storage.project_id} ({storage.version})")
    print(f"   Composición: {composition_id}")
    print(f"   Entry Point: {entry_path}")
    print(f"   Salida MP4:  {out_file}")

    # Escribir props a un JSON temporal si fueron provistas
    props_json_path = None
    if props:
        props_json_path = temp_dir / "remotion_props.json"
        with open(props_json_path, "w", encoding="utf-8") as f:
            json.dump(props, f, indent=2, ensure_ascii=False)

    # Construir comando remotion render
    remotion_cmd = [
        "npx", "remotion", "render",
        str(entry_path),
        composition_id,
        str(out_file),
        f"--crf={crf}",
        f"--concurrency={concurrency}",
        f"--gl={gl_backend}",
    ]

    if props_json_path and props_json_path.exists():
        remotion_cmd.append(f"--props={props_json_path}")

    env = os.environ.copy()
    env["REMOTION_CACHE_DIR"] = str(cache_dir)

    print(f"   Comando: {' '.join(remotion_cmd)}")
    
    try:
        res = subprocess.run(
            remotion_cmd,
            cwd=str(storage.version_dir),
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Render de Remotion completado.")
    except subprocess.CalledProcessError as err:
        print(f"❌ Error en ejecucion de Remotion render: {err.stderr}", file=sys.stderr)
        raise RuntimeError(f"Remotion render falló: {err.stderr}") from err

    # Validación de salida >5KB
    if not out_file.exists() or out_file.stat().st_size < MIN_ASSET_SIZE_BYTES:
        raise ValueError(
            f"❌ El archivo renderizado '{out_file}' no existe o incumple la Regla de Oro >5KB. "
            f"Tamaño: {out_file.stat().st_size if out_file.exists() else 0} B."
        )

    # Registrar el máster exportado en el manifiesto
    export_record = storage.register_export(
        file_path=out_file,
        export_type="master" if output_filename == "final.mp4" else "scene_render",
        crf=crf,
        extra={"composition_id": composition_id, "engine": "remotion"}
    )

    storage.update_phase(
        "phase_5_render_and_composition",
        "completed",
        composition=composition_id,
        master_output=str(out_file)
    )

    print(f"✅ Render Remotion registrado con éxito en project_manifest.json ({out_file.stat().st_size} B).")
    return dict(export_record)


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="render_remotion.py",
        description="Ejecuta el renderizado de composiciones Remotion con VideoStorageManager.",
    )
    parser.add_argument("--project", "-p", help="Slug, ID o ruta del proyecto canónico", default=None)
    parser.add_argument("--composition", "-c", help="ID de la composición (default: Main)", default="Main")
    parser.add_argument("--entry", "-e", help="Ruta al archivo entry de Remotion (e.g. src/index.ts)", default=None)
    parser.add_argument("--output", "-o", help="Nombre del archivo de salida en exports/ (default: final.mp4)", default="final.mp4")
    parser.add_argument("--crf", type=int, help="Calidad CRF de codificación (default: 28)", default=28)
    parser.add_argument("--concurrency", type=int, help="Número de hilos paralelos (default: 4)", default=4)
    parser.add_argument("--json", action="store_true", help="Imprimir dictamen en formato JSON")
    return parser


def main() -> int:
    parser = _build_cli_parser()
    args = parser.parse_args()

    try:
        result = render_remotion_composition(
            project_ref=args.project,
            composition_id=args.composition,
            entry_point=args.entry,
            output_filename=args.output,
            crf=args.crf,
            concurrency=args.concurrency,
        )
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"❌ Error en render_remotion: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
