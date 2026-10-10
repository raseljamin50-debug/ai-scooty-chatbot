"""
Finds which question in the knowledge base a customer message means.

Why not let the AI model decide?  A tiny model (Qwen 0.6B) can easily mix things up.
So the *matching* is done by plain, predictable code (TF-IDF over the 50+ paraphrases
of every question).  The model is only used afterwards to phrase the already-chosen
answer nicely (see llm.py), and it is never allowed to add facts.

Result of a match:
  confident -> we are sure which question it is        -> answer it
  suggest   -> we are not sure (maybe 2 questions fit) -> ask "did you mean ...?"
  none      -> nothing in the knowledge base fits       -> out-of-scope message
"""
import json
import re
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .text_utils import normalize, tokens

CONFIDENT_SCORE = 0.62      # at/above this (and clear winner) -> answer directly
SUGGEST_SCORE = 0.40        # at/above this -> ask "did you mean ...?"
MIN_MARGIN = 0.06           # winner must beat the runner-up by this much
STRONG_BOOST = 0.20         # bonus when a "strong keyword" of the question is present
GENERIC_INTENT_SHARE = 0.30  # a word used by >30% of questions is "generic"
MIN_COVERAGE = 0.80         # share of the question's meaning-words the answer must explain
SUGGEST_COVERAGE = 0.60
MIN_TOKENS = 3              # one or two loose words ("where is dhaka") are never enough to answer
_DEFINITION = re.compile(r"^(what is|what are|whats|define|meaning of) (a|an) ")
# harmless extra words people add; ignored when matching
FILLER = {"sir", "madam", "mam", "bro", "brother", "bhai", "vai", "apu", "sis", "dear",
          "really", "actually", "kindly", "pls", "plz", "quick", "question",
          "sorry", "anyway", "well", "ok", "yes"}


@dataclass
class MatchResult:
    status: str                       # "confident" | "suggest" | "none"
    intent_id: str | None = None
    score: float = 0.0
    candidates: list = field(default_factory=list)   # [(intent_id, score), ...] best first


class KnowledgeBase:
    def __init__(self, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.brand = data.get("brand", "AI Scooty")
        self.intents = data["intents"]
        self.by_id = {i["id"]: i for i in self.intents}
        self._build_index()

    # ------------------------------------------------------------------ index
    def _build_index(self):
        n = len(self.intents)
        self._para_tokens = []        # per intent: list of token lists
        self._exact = {}              # normalized paraphrase -> intent id
        df = Counter()
        for idx, intent in enumerate(self.intents):
            texts = list(intent["paraphrases"]) + [intent["question"]]
            toks = [tokens(t) for t in texts]
            self._para_tokens.append(toks)
            seen = set()
            for t_list in toks:
                seen.update(t_list)
            df.update(seen)
            for t in texts:
                self._exact.setdefault(normalize(t), intent["id"])

        self.idf = {t: math.log(1 + n / c) for t, c in df.items()}
        self.max_idf = max(self.idf.values()) if self.idf else 1.0
        self.vocab = sorted(self.idf)
        self.generic = {t for t, c in df.items() if c / n > GENERIC_INTENT_SHARE}

        self._intent_vocab = []       # token set per intent
        self._para_vecs = []          # per intent: [(vector, norm)]
        for toks in self._para_tokens:
            vocab_i = set()
            vecs = []
            for t_list in toks:
                vocab_i.update(t_list)
                vec = {t: self.idf[t] for t in set(t_list)}
                norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
                vecs.append((vec, norm))
            self._intent_vocab.append(vocab_i)
            self._para_vecs.append(vecs)

        # words of which at least one must be in the question, otherwise the question is
        # probably about something else (e.g. "what is the weather" is NOT about charging)
        self._require = [set(i.get("require_any", [])) for i in self.intents]
        self._strong = [set(tokens(" ".join(i.get("strong", [])), keep_stopwords=True))
                        | set(i.get("strong", [])) for i in self.intents]

    # ------------------------------------------------------------------ query
    @staticmethod
    def _osa(a: str, b: str) -> int:
        """Edit distance that also counts swapping two neighbouring letters as 1."""
        d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(len(a) + 1):
            d[i][0] = i
        for j in range(len(b) + 1):
            d[0][j] = j
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
                if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                    d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
        return d[-1][-1]

    def _fix_word(self, t: str) -> str:
        """Fix a typo by snapping an unknown word to a known one - but only when it is safe.
        (Careful rules: 'rice' must NOT become 'price', 'cook' must NOT become 'cost'.)"""
        n = len(t)
        if n < 4:
            return t
        best, best_d = None, 99
        for v in self.vocab:
            if v[0] != t[0] or abs(len(v) - n) > 1:
                continue
            dist = self._osa(t, v)
            same_len = len(v) == n
            if n == 4:
                ok = dist == 1 and same_len and sorted(t) == sorted(v)     # only letter swaps
            elif n == 5:
                ok = dist == 1 and same_len                                # one wrong letter / swap
            elif n == 6:
                ok = dist == 1
            else:
                ok = dist <= 2 and (same_len or dist == 1)
            if ok and dist < best_d:
                best, best_d = v, dist
        return best or t

    def _correct(self, toks: list[str]) -> list[str]:
        return [t if t in self.idf else self._fix_word(t) for t in toks]

    def match(self, text: str) -> MatchResult:
        norm = normalize(text)
        if norm in self._exact:
            iid = self._exact[norm]
            return MatchResult("confident", iid, 1.0, [(iid, 1.0)])

        q_tokens = [t for t in self._correct(tokens(text)) if t not in FILLER]
        if not q_tokens:
            return MatchResult("none")
        # "what is a solar panel?" is a general-knowledge question, not about our product
        if _DEFINITION.match(norm) and "scooty" not in q_tokens:
            return MatchResult("none")

        # Unknown words count against the match: they dilute the cosine and lower coverage.
        q_vec = {t: self.idf.get(t, self.max_idf) for t in set(q_tokens)}
        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0
        # the "meaning" words of the question (not generic ones like ai / scooty / what / how)
        q_content = {t: self.idf.get(t, self.max_idf) for t in set(q_tokens) if t not in self.generic}
        content_total = sum(q_content.values())
        has_unknown = any(t not in self.idf for t in q_tokens)

        scored = []
        for idx, intent in enumerate(self.intents):
            best = 0.0
            for vec, norm_p in self._para_vecs[idx]:
                dot = sum(w * vec[t] for t, w in q_vec.items() if t in vec)
                if dot:
                    best = max(best, dot / (q_norm * norm_p))

            strong_hit = bool(self._strong[idx] & set(q_tokens))
            shared = {t for t in q_content if t in self._intent_vocab[idx]}
            if content_total:
                coverage = sum(q_content[t] for t in shared) / content_total
            else:
                coverage = 1.0
            needs = self._require[idx]
            if not shared and not strong_hit:
                best = 0.0
            elif needs and not (needs & set(q_tokens)):
                best = best * 0.5
            else:
                best = best * (0.35 + 0.65 * coverage)
                if strong_hit and best >= 0.15:
                    best = min(1.0, best + STRONG_BOOST * coverage)
            scored.append((intent["id"], round(best, 4), coverage))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_id, top, top_cov = scored[0]
        second = scored[1][1] if len(scored) > 1 else 0.0
        candidates = [(i, s) for i, s, c in scored[:3] if s >= SUGGEST_SCORE * 0.8]

        # A word we have never seen (e.g. "tesla", "iphone") means the person may be asking
        # about something else -> never answer directly, at most ask "did you mean ...?"
        if (top >= CONFIDENT_SCORE and (top - second) >= MIN_MARGIN
                and top_cov >= MIN_COVERAGE and not has_unknown
                and len(q_tokens) >= MIN_TOKENS):
            return MatchResult("confident", top_id, top, candidates)
        if top >= SUGGEST_SCORE and top_cov >= SUGGEST_COVERAGE:
            return MatchResult("suggest", top_id, top, candidates)
        return MatchResult("none", None, top, [])
