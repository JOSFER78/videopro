"""
Forced Alignment Engine with Deterministic Levenshtein Distance & DTW
====================================================================
Aligns ASR (Whisper) word-level transcriptions against the canonical original script.
Guarantees 100% fidelity to the canonical script while preserving sub-second timing,
completely eliminating ASR hallucinations, drops, and misspellings.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


def normalize_token(text: str) -> str:
    """Normalize text for phonetic/orthographic similarity comparison."""
    if not text:
        return ""
    text = text.lower()
    # Normalize unicode (decompose accents for consistent comparison)
    text = unicodedata.normalize('NFKD', text)
    # Strip all non-alphanumeric chars
    text = re.sub(r'[^a-z0-9]', '', text)
    return text


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute standard Levenshtein edit distance between two strings."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    v0 = list(range(len(s2) + 1))
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0 = list(v1)

    return v0[len(s2)]


def token_similarity(s1: str, s2: str) -> float:
    """Return similarity in range [0.0, 1.0]."""
    n1 = normalize_token(s1)
    n2 = normalize_token(s2)
    if not n1 and not n2:
        return 1.0
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 1.0
    # Prefix match bonus (e.g. cuantic vs cuantico)
    if n1.startswith(n2) or n2.startswith(n1):
        shorter = min(len(n1), len(n2))
        longer = max(len(n1), len(n2))
        if shorter >= 3 and (longer - shorter) <= 2:
            return 0.85

    dist = levenshtein_distance(n1, n2)
    max_len = max(len(n1), len(n2))
    return max(0.0, 1.0 - (dist / max_len))


@dataclass
class CanonicalToken:
    word: str
    clean_word: str
    shot_index: int = 0
    time_window: str = ""
    is_key_word: bool = False
    start: Optional[float] = None
    end: Optional[float] = None
    confidence: float = 1.0
    aligned_asr_word: Optional[str] = None


@dataclass
class ASRWord:
    word: str
    clean_word: str
    start: float
    end: float
    probability: float = 1.0


@dataclass
class AlignmentResult:
    aligned_tokens: List[CanonicalToken]
    total_canonical_words: int
    total_asr_words: int
    matched_words: int
    hallucinated_asr_dropped: int
    interpolated_words: int
    average_confidence: float
    alignment_rate: float


class LevenshteinForcedAligner:
    """
    Deterministic Dynamic Time Warping & Levenshtein alignment engine.
    Matches ASR timestamps to Canonical script tokens.
    """

    def __init__(self, match_threshold: float = 0.50, insertion_penalty: float = 0.75, deletion_penalty: float = 0.75):
        self.match_threshold = match_threshold
        self.insertion_penalty = insertion_penalty
        self.deletion_penalty = deletion_penalty

    def parse_script(self, script_data: Any) -> List[CanonicalToken]:
        """
        Parse script from raw string or escaleta structure.
        """
        tokens: List[CanonicalToken] = []

        if isinstance(script_data, list):
            # Check if it's a list of shots
            for shot in script_data:
                shot_idx = shot.get("shot_index", 0)
                time_win = shot.get("time_window", "")
                text = shot.get("narration_es") or shot.get("text", "")
                shot_tokens = self._tokenize_text(text, shot_index=shot_idx, time_window=time_win)
                tokens.extend(shot_tokens)
        elif isinstance(script_data, dict):
            if "shots" in script_data:
                for shot in script_data["shots"]:
                    shot_idx = shot.get("shot_index", 0)
                    time_win = shot.get("time_window", "")
                    text = shot.get("narration_es") or shot.get("text", "")
                    shot_tokens = self._tokenize_text(text, shot_index=shot_idx, time_window=time_win)
                    tokens.extend(shot_tokens)
            else:
                text = script_data.get("text", "")
                tokens = self._tokenize_text(text)
        elif isinstance(script_data, str):
            tokens = self._tokenize_text(script_data)

        return tokens

    def _tokenize_text(self, text: str, shot_index: int = 0, time_window: str = "") -> List[CanonicalToken]:
        raw_words = text.strip().split()
        tokens = []
        # Key high-impact word patterns for kinetic styling (scientific terms, numbers, uppercase, dramatic concepts)
        key_words_regex = re.compile(r'(cuántic|átom|silicio|fusión|microsegund|milen|realidad|obsolet|luz|energ|frontera|conciencia|infinit|dilema|especie|cero|grados|laboratorio|tokamak|iter|búnker|tiempo|destino)', re.IGNORECASE)

        for w in raw_words:
            clean = normalize_token(w)
            is_key = bool(key_words_regex.search(w)) or len(w) > 8 or w.isupper()
            tokens.append(CanonicalToken(
                word=w,
                clean_word=clean,
                shot_index=shot_index,
                time_window=time_window,
                is_key_word=is_key
            ))
        return tokens

    def parse_asr_result(self, asr_data: Any) -> List[ASRWord]:
        """
        Parse raw Whisper segments or word list into standardized ASRWord items.
        """
        asr_words: List[ASRWord] = []

        if isinstance(asr_data, dict):
            segments = asr_data.get("segments", [])
            for seg in segments:
                words = seg.get("words", [])
                if words:
                    for w in words:
                        word_str = w.get("word", "").strip()
                        if word_str:
                            asr_words.append(ASRWord(
                                word=word_str,
                                clean_word=normalize_token(word_str),
                                start=float(w.get("start", 0.0)),
                                end=float(w.get("end", 0.0)),
                                probability=float(w.get("probability", 1.0))
                            ))
                else:
                    # If word timestamps were not extracted, split segment text
                    seg_text = seg.get("text", "").strip().split()
                    seg_start = float(seg.get("start", 0.0))
                    seg_end = float(seg.get("end", 0.0))
                    seg_dur = max(0.1, seg_end - seg_start)
                    if seg_text:
                        word_dur = seg_dur / len(seg_text)
                        for i, w_str in enumerate(seg_text):
                            asr_words.append(ASRWord(
                                word=w_str,
                                clean_word=normalize_token(w_str),
                                start=seg_start + i * word_dur,
                                end=seg_start + (i + 1) * word_dur,
                                probability=0.9
                            ))
        elif isinstance(asr_data, list):
            for item in asr_data:
                if isinstance(item, dict):
                    asr_words.append(ASRWord(
                        word=item.get("word", ""),
                        clean_word=normalize_token(item.get("word", "")),
                        start=float(item.get("start", 0.0)),
                        end=float(item.get("end", 0.0)),
                        probability=float(item.get("probability", 1.0))
                    ))
                elif isinstance(item, ASRWord):
                    asr_words.append(item)

        return asr_words

    def align(self, script_data: Any, asr_data: Any, total_audio_duration: Optional[float] = None) -> AlignmentResult:
        """
        Execute full dynamic programming alignment.
        """
        canonical_tokens = self.parse_script(script_data)
        asr_words = self.parse_asr_result(asr_data)

        N = len(canonical_tokens)
        M = len(asr_words)

        if N == 0:
            return AlignmentResult([], 0, M, 0, M, 0, 0.0, 0.0)

        if M == 0:
            # No ASR words at all -> fallback distribute across total_audio_duration
            dur = total_audio_duration or 120.0
            step = dur / N
            for i, tok in enumerate(canonical_tokens):
                tok.start = round(i * step, 3)
                tok.end = round((i + 1) * step, 3)
                tok.confidence = 0.5
            return AlignmentResult(canonical_tokens, N, 0, 0, 0, N, 0.5, 0.0)

        # Dynamic Programming Matrix
        dp = [[0.0] * (M + 1) for _ in range(N + 1)]
        backtrack = [[(0, 0)] * (M + 1) for _ in range(N + 1)]

        for i in range(1, N + 1):
            dp[i][0] = dp[i - 1][0] + self.deletion_penalty
            backtrack[i][0] = (i - 1, 0)

        for j in range(1, M + 1):
            dp[0][j] = dp[0][j - 1] + self.insertion_penalty
            backtrack[0][j] = (0, j - 1)

        for i in range(1, N + 1):
            tok = canonical_tokens[i - 1]
            for j in range(1, M + 1):
                asr = asr_words[j - 1]
                sim = token_similarity(tok.clean_word, asr.clean_word)
                match_cost = 1.0 - sim

                cost_match = dp[i - 1][j - 1] + match_cost
                cost_del = dp[i - 1][j] + self.deletion_penalty
                cost_ins = dp[i][j - 1] + self.insertion_penalty

                best_cost = cost_match
                best_op = (i - 1, j - 1)

                if cost_del < best_cost:
                    best_cost = cost_del
                    best_op = (i - 1, j)

                if cost_ins < best_cost:
                    best_cost = cost_ins
                    best_op = (i, j - 1)

                dp[i][j] = best_cost
                backtrack[i][j] = best_op

        # Backtrack to find alignment path
        curr_i = N
        curr_j = M
        path: List[Tuple[Optional[int], Optional[int]]] = []

        while curr_i > 0 or curr_j > 0:
            prev_i, prev_j = backtrack[curr_i][curr_j]
            can_idx = curr_i - 1 if curr_i > prev_i else None
            asr_idx = curr_j - 1 if curr_j > prev_j else None
            path.append((can_idx, asr_idx))
            curr_i, curr_j = prev_i, prev_j

        path.reverse()

        matched_asr_indices = set()
        matched_canonical_count = 0
        total_conf = 0.0

        for can_idx, asr_idx in path:
            if can_idx is not None and asr_idx is not None:
                tok = canonical_tokens[can_idx]
                asr = asr_words[asr_idx]
                sim = token_similarity(tok.clean_word, asr.clean_word)
                if sim >= self.match_threshold:
                    tok.start = asr.start
                    tok.end = asr.end
                    tok.confidence = sim
                    tok.aligned_asr_word = asr.word
                    matched_asr_indices.add(asr_idx)
                    matched_canonical_count += 1
                    total_conf += sim

        hallucinated_count = M - len(matched_asr_indices)

        self._interpolate_missing_timestamps(canonical_tokens, total_audio_duration)

        interpolated_count = N - matched_canonical_count
        avg_conf = (total_conf / matched_canonical_count) if matched_canonical_count > 0 else 0.0
        align_rate = (matched_canonical_count / N) * 100.0 if N > 0 else 0.0

        return AlignmentResult(
            aligned_tokens=canonical_tokens,
            total_canonical_words=N,
            total_asr_words=M,
            matched_words=matched_canonical_count,
            hallucinated_asr_dropped=hallucinated_count,
            interpolated_words=interpolated_count,
            average_confidence=round(avg_conf, 3),
            alignment_rate=round(align_rate, 2)
        )

    def _interpolate_missing_timestamps(self, tokens: List[CanonicalToken], total_duration: Optional[float] = None) -> None:
        """
        Interpolates missing timestamps smoothly using character-weighted distribution
        between verified anchor points.
        """
        n = len(tokens)
        if n == 0:
            return

        max_dur = total_duration or (tokens[-1].end if tokens[-1].end else 120.0)

        anchor_indices = [i for i, tok in enumerate(tokens) if tok.start is not None and tok.end is not None]

        if not anchor_indices:
            step = max_dur / n
            for i, tok in enumerate(tokens):
                tok.start = round(i * step, 3)
                tok.end = round((i + 1) * step, 3)
                tok.confidence = 0.4
            return

        first_anchor = anchor_indices[0]
        if first_anchor > 0:
            anchor_start = tokens[first_anchor].start or 0.5
            start_bound = 0.0
            avail_dur = max(0.2, anchor_start - start_bound)
            chars = sum(len(tokens[i].word) for i in range(first_anchor))
            curr = start_bound
            for i in range(first_anchor):
                w_dur = avail_dur * (len(tokens[i].word) / max(1, chars))
                tokens[i].start = round(curr, 3)
                tokens[i].end = round(curr + w_dur, 3)
                tokens[i].confidence = 0.6
                curr += w_dur

        for idx in range(len(anchor_indices) - 1):
            left_idx = anchor_indices[idx]
            right_idx = anchor_indices[idx + 1]
            gap_size = right_idx - left_idx - 1

            if gap_size > 0:
                t_start = tokens[left_idx].end
                t_end = tokens[right_idx].start
                if t_end <= t_start:
                    t_end = t_start + 0.3 * gap_size

                avail_dur = t_end - t_start
                chars = sum(len(tokens[i].word) for i in range(left_idx + 1, right_idx))
                curr = t_start
                for i in range(left_idx + 1, right_idx):
                    w_dur = avail_dur * (len(tokens[i].word) / max(1, chars))
                    tokens[i].start = round(curr, 3)
                    tokens[i].end = round(curr + w_dur, 3)
                    tokens[i].confidence = 0.7
                    curr += w_dur

        last_anchor = anchor_indices[-1]
        if last_anchor < n - 1:
            anchor_end = tokens[last_anchor].end or (max_dur - 1.0)
            avail_dur = max(0.5, max_dur - anchor_end)
            trailing_range = range(last_anchor + 1, n)
            chars = sum(len(tokens[i].word) for i in trailing_range)
            curr = anchor_end
            for i in trailing_range:
                w_dur = avail_dur * (len(tokens[i].word) / max(1, chars))
                tokens[i].start = round(curr, 3)
                tokens[i].end = round(curr + w_dur, 3)
                tokens[i].confidence = 0.6
                curr += w_dur

        for i in range(n):
            if tokens[i].start is None:
                tokens[i].start = 0.0
            if tokens[i].end is None or tokens[i].end <= tokens[i].start:
                tokens[i].end = tokens[i].start + 0.25
            if i > 0 and tokens[i].start < tokens[i - 1].start:
                tokens[i].start = tokens[i - 1].end
                tokens[i].end = max(tokens[i].start + 0.15, tokens[i].end)
