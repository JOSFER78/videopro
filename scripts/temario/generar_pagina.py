#!/usr/bin/env python3
"""
Genera la página de seguimiento del espectador a partir del temario.

    python3 scripts/temario/generar_pagina.py data/serie_historia/temario.json docs/temario/index.html

Página estática y autónoma: temporadas y episodios, lo que se aprende en cada uno, preguntas de repaso
con la respuesta oculta y casillas de «visto» que se guardan en el navegador. Solo librería estándar.
"""

import html
import json
import sys

e = html.escape

CSS = """
@font-face{font-family:"Serif";src:url("fonts/instrument-serif-latin-400-normal.woff2")}
@font-face{font-family:"Serif";font-style:italic;src:url("fonts/instrument-serif-latin-400-italic.woff2")}
@font-face{font-family:"Sans";font-weight:400;src:url("fonts/inter-latin-400-normal.woff2")}
@font-face{font-family:"Sans";font-weight:600;src:url("fonts/inter-latin-600-normal.woff2")}
:root{--bg:#0c0d0f;--card:#141619;--line:rgba(255,255,255,.16);--ink:#f3f1ec;--dim:#9a9ca2;--faint:#5a5c62;--hot:#ff4b33}
*{box-sizing:border-box;margin:0}
body{background:var(--bg);color:var(--ink);font-family:"Sans",system-ui,sans-serif;font-size:17px;line-height:1.5;font-variant-numeric:tabular-nums}
.wrap{max-width:1080px;margin:0 auto;padding:48px 24px 96px}
.caps{text-transform:uppercase;letter-spacing:.14em;font-weight:600;font-size:13px}
.serif{font-family:"Serif",Georgia,serif;font-weight:400}
header .ch{color:var(--hot)}
h1{font-family:"Serif",Georgia,serif;font-weight:400;font-size:clamp(44px,8vw,84px);line-height:1;margin:10px 0 14px;letter-spacing:-.01em}
header p{color:var(--dim);max-width:640px}
.total{margin-top:28px;display:flex;align-items:center;gap:16px}
.bar{flex:1;height:4px;background:var(--faint);position:relative}
.bar i{position:absolute;left:0;top:0;bottom:0;background:var(--hot);width:0;transition:width .3s}
.count{font-weight:600;white-space:nowrap}
section{margin-top:64px}
.shead{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;border-top:2px solid var(--ink);padding-top:14px}
.shead .n{color:var(--hot)}
.shead h2{font-family:"Serif",Georgia,serif;font-weight:400;font-size:clamp(30px,5vw,46px);line-height:1.05;flex:1;min-width:240px}
.lens{color:var(--dim);margin:8px 0 6px;max-width:720px}
.sbar{display:flex;align-items:center;gap:14px;margin:14px 0 4px}
.ep{border-top:1px solid var(--line)}
.ep summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:54px 1fr auto 34px;gap:14px;align-items:center;padding:16px 0}
.ep summary::-webkit-details-marker{display:none}
.ep .code{font-weight:600;font-size:14px;letter-spacing:.06em;color:var(--dim)}
.ep .t{font-family:"Serif",Georgia,serif;font-size:clamp(22px,3.4vw,30px);line-height:1.15}
.ep .w{color:var(--dim);font-size:14px;text-align:right;white-space:nowrap}
.ep.seen .code{color:var(--hot)}
.ep.seen .t{color:var(--dim)}
.chk{appearance:none;width:26px;height:26px;border:2px solid var(--faint);background:transparent;cursor:pointer;display:grid;place-items:center}
.chk:checked{background:var(--hot);border-color:var(--hot)}
.chk:checked::after{content:"";width:11px;height:6px;border-left:3px solid #fff;border-bottom:3px solid #fff;transform:rotate(-45deg) translateY(-2px)}
.chk:focus-visible,summary:focus-visible,.ans summary:focus-visible{outline:2px solid var(--hot);outline-offset:3px}
.body{padding:0 0 26px 68px;display:grid;gap:22px}
.idea{font-family:"Serif",Georgia,serif;font-size:24px;line-height:1.25;max-width:720px}
.meta{display:flex;flex-wrap:wrap;gap:8px 26px;color:var(--dim);font-size:15px}
.meta b{color:var(--ink);font-weight:600}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.box h3{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin-bottom:10px;font-weight:600}
.box ul{list-style:none;padding:0;display:grid;gap:8px}
.box li{padding-left:18px;position:relative}
.box li::before{content:"";position:absolute;left:0;top:.62em;width:8px;height:2px;background:var(--hot)}
.ans{border:1px solid var(--line);background:var(--card);padding:10px 14px}
.ans+.ans{margin-top:8px}
.ans summary{cursor:pointer;display:block;padding:0}
.ans p{color:var(--dim);margin-top:8px;border-top:1px solid var(--line);padding-top:8px}
.ans summary::after{content:"Ver respuesta";display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--hot);font-weight:600;margin-top:4px}
.ans[open] summary::after{content:"Ocultar"}
.src{font-size:14px;color:var(--dim)}
.src a{color:var(--dim)}
.soon{font-size:12px;letter-spacing:.12em;text-transform:uppercase;border:1px solid var(--faint);color:var(--dim);padding:2px 8px;font-weight:600}
footer{margin-top:72px;color:var(--faint);font-size:14px;border-top:1px solid var(--line);padding-top:18px}
@media(max-width:700px){.ep summary{grid-template-columns:44px 1fr 30px}.ep .w{display:none}.body{padding-left:0}.cols{grid-template-columns:1fr}}
"""

JS = """
const KEY="temario:vistos";
let seen={};try{seen=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function paint(){
  let total=0,done=0;
  document.querySelectorAll("section").forEach(s=>{
    const boxes=[...s.querySelectorAll(".chk")],d=boxes.filter(b=>b.checked).length;
    total+=boxes.length;done+=d;
    s.querySelector(".sbar i").style.width=(boxes.length?100*d/boxes.length:0)+"%";
    s.querySelector(".sbar .count").textContent=d+" de "+boxes.length;
  });
  document.querySelector(".total i").style.width=(total?100*done/total:0)+"%";
  document.querySelector(".total .count").textContent=done+" de "+total+" episodios vistos";
}
document.querySelectorAll(".chk").forEach(b=>{
  b.checked=!!seen[b.dataset.code];
  b.closest(".ep").classList.toggle("seen",b.checked);
  b.addEventListener("click",ev=>ev.stopPropagation());
  b.addEventListener("change",()=>{
    seen[b.dataset.code]=b.checked;b.closest(".ep").classList.toggle("seen",b.checked);
    try{localStorage.setItem(KEY,JSON.stringify(seen))}catch(e){}
    paint();
  });
});
paint();
"""


def episodio(ep):
    cuando = (ep.get("cuando") or {}).get("texto", "")
    ancla = ep.get("ancla") or {}
    lugar = ancla.get("lugar") or {}
    completo = bool(ep.get("repaso"))
    partes = []
    if ep.get("idea"):
        partes.append(f'<p class="idea">{e(ep["idea"])}</p>')
    meta = []
    if ancla.get("objeto"):
        meta.append(f'<span><b>Lo verás en</b> {e(ancla["objeto"])}</span>')
    if lugar.get("nombre"):
        meta.append(f'<span><b>Dónde</b> {e(lugar["nombre"])}{", " + e(lugar["pais"]) if lugar.get("pais") else ""}</span>')
    if ep.get("enlaza_con"):
        meta.append(f'<span><b>Vuelve sobre</b> {e(ep["enlaza_con"])}</span>')
    if meta:
        partes.append(f'<div class="meta">{"".join(meta)}</div>')
    if completo:
        aprendido = "".join(f"<li>{e(a)}</li>" for a in ep.get("aprendido", []))
        repaso = "".join(
            f'<details class="ans"><summary>{e(q["pregunta"])}</summary><p>{e(q["respuesta"])}</p></details>'
            for q in ep["repaso"])
        partes.append(f'<div class="cols"><div class="box"><h3>Lo que aprendes</h3><ul>{aprendido}</ul></div>'
                      f'<div class="box"><h3>Repaso</h3>{repaso}</div></div>')
    fuentes = [f for f in ep.get("fuentes", []) if str(f.get("url", "")).startswith("http")]
    if fuentes:
        enlaces = " · ".join(f'<a href="{e(f["url"])}" rel="noopener">{e(f["afirmacion"][:70])}</a>' for f in fuentes[:6])
        partes.append(f'<p class="src">Fuentes: {enlaces}</p>')
    etiqueta = "" if completo else ' <span class="soon">Próximamente</span>'
    return (f'<details class="ep"><summary><span class="code">{e(ep["codigo"].split("-")[1])}</span>'
            f'<span class="t">{e(ep["titulo"])}{etiqueta}</span><span class="w">{e(cuando)}</span>'
            f'<input class="chk" type="checkbox" data-code="{e(ep["codigo"])}" aria-label="Visto: {e(ep["titulo"])}"></summary>'
            f'<div class="body">{"".join(partes)}</div></details>')


def pagina(temario):
    secciones = []
    for t in temario["temporadas"]:
        lente = f'<p class="lens">{e(t["lente"])}</p>' if t.get("lente") else ""
        secciones.append(
            f'<section><div class="shead"><span class="n caps">Temporada {t["temporada"]}</span><h2>{e(t["titulo"])}</h2></div>'
            f'{lente}<div class="sbar"><div class="bar"><i></i></div><span class="count caps"></span></div>'
            f'{"".join(episodio(ep) for ep in t["episodios"])}</section>')
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(temario["canal"])} · {e(temario["tema"])}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<div class="caps"><span class="ch">{e(temario["canal"])}</span> · Tema</div>
<h1>{e(temario["tema"])}</h1>
<p>{e(temario.get("presentacion", ""))}</p>
<div class="total"><div class="bar"><i></i></div><span class="count"></span></div>
</header>
{"".join(secciones)}
<footer>Tu progreso se guarda solo en este navegador. Todas las fechas llevan su fuente enlazada.</footer>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    temario = json.load(open(argv[1], encoding="utf-8"))
    open(argv[2], "w", encoding="utf-8").write(pagina(temario))
    print(f"{argv[2]}: {sum(len(t['episodios']) for t in temario['temporadas'])} episodios")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
