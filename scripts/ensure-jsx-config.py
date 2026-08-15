#!/usr/bin/env python3
"""
Ensure tsconfig.json includes the 'jsx' setting required for generated
Composition.tsx files. This script updates the configuration automatically.
"""

import json
import os
import sys
from pathlib import Path

def main():
    # Locate tsconfig.json in the project root
    project_root = Path(__file__).resolve().parent.parent
    tsconfig_path = project_root / "tsconfig.json"

    if not tsconfig_path.exists():
        print(f"No tsconfig.json found at {tsconfig_path}. Create one with {{\"jsx\": \"react-jsx\"}}")
        return 1

    # Load existing config
    with open(tsconfig_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Ensure "compilerOptions" exists
    compiler_opts = config.setdefault("compilerOptions", {})

    # Setjsx to react-jsx if not already set
    if compiler_opts.get("jsx") != "react-jsx":
        compiler_opts["jsx"] = "react-jsx"
        print(f"Updated {tsconfig_path} with jsx: react-jsx")
        # Write back changes
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return 0
    else:
        print("jsx is already set to react-jsx.")
        return 0

if __name__ == "__main__":
    sys.exit(main())