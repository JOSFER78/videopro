"""Lista los planos que cada guion pide recrear con Google Flow y aún no tienen archivo.

    python3 scripts/temario/flow_pendiente.py > data/serie_historia/FLOW_PENDIENTE.md
"""
import json
from pathlib import Path

GUIONES = Path(__file__).resolve().parents[2] / "data" / "serie_historia" / "guiones"


def pendientes(guion: dict) -> list:
    planos, n = [], 0
    for parte in guion["partes"]:
        for frase in parte["frases"]:
            n += 1
            visual = frase.get("visual") or {}
            if visual.get("tipo") == "flow" and not visual.get("archivo"):
                planos.append((n, parte["label"], frase["texto"], visual))
    return planos


def main() -> None:
    print("# Planos pendientes de Google Flow\n")
    print("Se generan en https://flow.google.com con la sesión del usuario, modelo Gemini Omni 1.2 Flash, 16:9, un plano")
    print("cada vez y como mucho 2 repeticiones. Guarda cada clip en `templates/atlas/media/<CÓDIGO>/flow_<frase>.mp4`,")
    print("anota la ruta en `visual.archivo` y `Recreación` en `visual.credito`, y vuelve a montar con `producir.sh`.\n")
    total = 0
    for ruta in sorted(GUIONES.glob("T*-E*.json")):
        guion = json.loads(ruta.read_text(encoding="utf-8"))
        planos = pendientes(guion)
        if not planos:
            continue
        total += len(planos)
        print(f"## {guion['codigo']} — {len(planos)} planos\n")
        for n, parte, texto, visual in planos:
            print(f"**Frase {n}** ({parte}) — «{texto}»\n")
            print(f"- Se ve: {visual.get('que_se_ve', '')}")
            print(f"- Prompt: `{visual.get('prompt_flow', '')}`\n")
    print(f"Total: {total} planos.")


if __name__ == "__main__":
    main()
