"""
interactive_episode.py — Episodios interactivos con decisiones (historia en segunda persona).

Un episodio es un vídeo principal que termina en una decisión, más un vídeo corto por cada opción.
Este módulo no genera vídeo: convierte el guion (JSON) en los trabajos que consume el pipeline real
(`app/services/task.py`, escenas con `mode`/`prompt`/`text`/`duration`) y cuenta los votos de los
comentarios para decidir el siguiente episodio.

Solo usa la librería estándar, para poder probarse sin el resto de dependencias.
"""

import json
import re
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# Límites de YouTube y de Flow que condicionan el formato
MAX_END_SCREEN_CHOICES = 4      # una pantalla final admite hasta 4 elementos
END_SCREEN_SECONDS = 20         # la pantalla final ocupa los últimos 5-20 s del vídeo
MAX_FLOW_CLIP_SECONDS = 15      # Omni Flash 1.2 con suscripción: clips de 3 a 15 s

POV_PREFIX = "First-person POV, handheld camera at eye level, no visible face of the protagonist. "


class EpisodeError(ValueError):
    """El guion del episodio no cumple el formato interactivo."""


@dataclass
class Scene:
    text: str                       # locución del plano
    prompt: str                     # descripción visual
    mode: str = "google_flow"       # google_flow | flux | stock | real_photo
    duration: float = 8.0
    emotion: str = ""               # acotación de voz: (con misterio), (con urgencia)...

    def to_task_scene(self, image_reference: str = "") -> Dict[str, object]:
        """Escena en el formato que lee get_video_materials() de task.py."""
        prompt = self.prompt
        if self.mode == "google_flow" and not prompt.startswith(POV_PREFIX):
            prompt = POV_PREFIX + prompt
        narration = f"{self.emotion} {self.text}".strip() if self.emotion else self.text
        return {
            "mode": self.mode,
            "prompt": prompt,
            "text": narration,
            "duration": self.duration,
            "image_reference": image_reference,
        }


@dataclass
class Option:
    key: str                        # letra que vota el público: A, B, C, D
    label: str
    outcome_title: str
    scenes: List[Scene] = field(default_factory=list)


@dataclass
class Episode:
    episode_id: str
    title: str
    question: str                   # la decisión que cierra el vídeo principal
    sources: List[str]              # fuentes históricas: lo que distingue esto de contenido genérico
    scenes: List[Scene]
    options: List[Option]
    image_reference: str = ""       # imagen ancla para mantener el mismo mundo entre planos


def _scene_from_dict(raw: dict, where: str) -> Scene:
    for key in ("text", "prompt"):
        if not str(raw.get(key, "")).strip():
            raise EpisodeError(f"{where}: falta '{key}'")
    scene = Scene(
        text=raw["text"].strip(),
        prompt=raw["prompt"].strip(),
        mode=raw.get("mode", "google_flow"),
        duration=float(raw.get("duration", 8.0)),
        emotion=raw.get("emotion", "").strip(),
    )
    if scene.mode == "google_flow" and not 3 <= scene.duration <= MAX_FLOW_CLIP_SECONDS:
        raise EpisodeError(
            f"{where}: un plano de Flow dura entre 3 y {MAX_FLOW_CLIP_SECONDS} s, no {scene.duration}"
        )
    return scene


def parse_episode(raw: dict) -> Episode:
    """Valida el guion y lo convierte en un Episode. Lanza EpisodeError con el motivo."""
    for key in ("episode_id", "title", "question"):
        if not str(raw.get(key, "")).strip():
            raise EpisodeError(f"falta '{key}'")
    if not raw.get("sources"):
        raise EpisodeError("falta 'sources': cada episodio debe citar de dónde salen los hechos")
    if not raw.get("scenes"):
        raise EpisodeError("el vídeo principal no tiene escenas")

    raw_options = raw.get("options") or []
    if not 2 <= len(raw_options) <= MAX_END_SCREEN_CHOICES:
        raise EpisodeError(
            f"una decisión necesita entre 2 y {MAX_END_SCREEN_CHOICES} opciones, no {len(raw_options)}"
        )

    options: List[Option] = []
    for raw_opt in raw_options:
        key = str(raw_opt.get("key", "")).strip().upper()
        if not re.fullmatch(r"[A-D]", key):
            raise EpisodeError(f"clave de opción no válida: '{raw_opt.get('key')}' (usa A, B, C o D)")
        if key in {o.key for o in options}:
            raise EpisodeError(f"opción repetida: {key}")
        if not raw_opt.get("scenes"):
            raise EpisodeError(f"la opción {key} no tiene escenas de desenlace")
        options.append(Option(
            key=key,
            label=str(raw_opt.get("label", "")).strip() or key,
            outcome_title=str(raw_opt.get("outcome_title", "")).strip() or f"{raw['title']} — {key}",
            scenes=[_scene_from_dict(s, f"opción {key}, escena {i + 1}")
                    for i, s in enumerate(raw_opt["scenes"])],
        ))

    return Episode(
        episode_id=raw["episode_id"].strip(),
        title=raw["title"].strip(),
        question=raw["question"].strip(),
        sources=[str(s) for s in raw["sources"]],
        scenes=[_scene_from_dict(s, f"escena {i + 1}") for i, s in enumerate(raw["scenes"])],
        options=options,
        image_reference=raw.get("image_reference", ""),
    )


def load_episode(path: str) -> Episode:
    return parse_episode(json.loads(Path(path).read_text(encoding="utf-8")))


def build_video_jobs(episode: Episode) -> List[Dict[str, object]]:
    """
    Un trabajo de vídeo por pieza a publicar: el principal y uno por opción.

    Cada trabajo lleva las escenas listas para task.py y, aparte, lo que hay que hacer a mano en
    YouTube Studio: la API de YouTube no permite crear pantallas finales.
    """
    choices = " / ".join(f"{o.key}) {o.label}" for o in episode.options)
    description_footer = "Fuentes:\n" + "\n".join(f"- {s}" for s in episode.sources)

    main = {
        "job_id": f"{episode.episode_id}_main",
        "role": "main",
        "title": episode.title,
        "scenes": [s.to_task_scene(episode.image_reference) for s in episode.scenes],
        # La pantalla final necesita metraje propio: plano fijo con la pregunta en pantalla
        "end_screen_hold_seconds": END_SCREEN_SECONDS,
        "end_screen_text": f"{episode.question}  {choices}",
        "end_screen_links": [f"{episode.episode_id}_{o.key}" for o in episode.options],
        "pinned_comment": f"{episode.question} Vota con una letra: {choices}",
        "description_footer": description_footer,
    }
    jobs = [main]
    for option in episode.options:
        jobs.append({
            "job_id": f"{episode.episode_id}_{option.key}",
            "role": "branch",
            "option": option.key,
            "title": option.outcome_title,
            "scenes": [s.to_task_scene(episode.image_reference) for s in option.scenes],
            "end_screen_hold_seconds": END_SCREEN_SECONDS,
            "end_screen_text": "¿Y si hubieras elegido otra cosa?",
            "end_screen_links": [f"{episode.episode_id}_{o.key}"
                                 for o in episode.options if o.key != option.key],
            "description_footer": description_footer,
        })
    return jobs


def estimate_flow_clips(jobs: Iterable[Dict[str, object]], retries_per_clip: float = 2.0) -> Dict[str, float]:
    """Cuántas generaciones de Flow pide el episodio, contando repeticiones por planos fallidos."""
    clips = sum(1 for job in jobs for sc in job["scenes"] if sc["mode"] == "google_flow")
    seconds = sum(sc["duration"] for job in jobs for sc in job["scenes"] if sc["mode"] == "google_flow")
    return {"flow_clips": clips, "flow_seconds": seconds, "flow_generations": clips * retries_per_clip}


# ---------------------------------------------------------------------------
# Votos
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).upper().strip()


def extract_vote(comment: str, valid_keys: Iterable[str]) -> Optional[str]:
    """
    Letra votada en un comentario, o None si no es un voto claro.

    Cuenta "A", "a)", "Voto B", "opción c", "la B sin duda". No cuenta comentarios que nombran
    dos opciones distintas, ni una letra suelta en mitad de una frase ("a mí me gustó").
    """
    keys = {k.upper() for k in valid_keys}
    text = _normalize(comment)
    if not text:
        return None

    found = set()
    # Comentario que es solo la letra, o empieza por ella seguida de signo: "B", "b)", "A!!", "C - por mar"
    lead = re.match(r"^([A-D])(?:$|\s*[\)\.\:\-!,]+|\s*$)", text)
    if lead:
        found.add(lead.group(1))
    # Letra precedida de una palabra que la marca como voto
    for match in re.finditer(r"\b(?:VOTO|OPCION|ELIJO|LA|EL|ME QUEDO CON LA|ME QUEDO CON EL)\s+([A-D])\b", text):
        found.add(match.group(1))

    found &= keys
    return found.pop() if len(found) == 1 else None


def tally_votes(comments: Iterable[dict], valid_keys: Iterable[str]) -> Dict[str, object]:
    """
    Recuento con un voto por persona (el primero que dejó).

    `comments`: dicts con 'author' y 'text'. Devuelve el recuento, el ganador (None si hay empate
    o no hay votos) y cuántos comentarios no eran votos.
    """
    keys = [k.upper() for k in valid_keys]
    counts = {k: 0 for k in keys}
    voters = set()
    ignored = 0
    for comment in comments:
        vote = extract_vote(str(comment.get("text", "")), keys)
        author = str(comment.get("author", "")).strip()
        if vote is None or not author or author in voters:
            ignored += 1
            continue
        voters.add(author)
        counts[vote] += 1

    top = max(counts.values()) if counts else 0
    leaders = [k for k, v in counts.items() if v == top]
    winner = leaders[0] if top > 0 and len(leaders) == 1 else None
    return {"counts": counts, "winner": winner, "total_votes": len(voters), "ignored": ignored}


def fetch_comments(video_id: str, api_key: str, max_pages: int = 20) -> List[dict]:
    """Comentarios de primer nivel de un vídeo (YouTube Data API v3, commentThreads.list)."""
    comments: List[dict] = []
    page_token = ""
    for _ in range(max_pages):
        params = {
            "part": "snippet", "videoId": video_id, "maxResults": 100,
            "textFormat": "plainText", "order": "time", "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token
        url = "https://www.googleapis.com/youtube/v3/commentThreads?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        for item in data.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": snippet.get("authorChannelId", {}).get("value") or snippet.get("authorDisplayName", ""),
                "text": snippet.get("textDisplay", ""),
            })
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break
    # 'order=time' devuelve primero los más recientes; el recuento quiere el primer voto de cada persona
    comments.reverse()
    return comments
