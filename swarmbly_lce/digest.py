"""Digester: proposes claims from source spans (SPEC 6.3).

The digester is the only place where a model writes into the wiki, and what
it writes are *proposals*: every proposed claim is anchored to a span by
offsets, then verified by :class:`~swarmbly_lce.anchors.AnchorVerifier`. A
claim whose anchor does not verify stays DIGESTED and can never be trained on.

The model is asked for JSON. Malformed output is not repaired creatively: the
span is skipped and counted, because a digester that invents structure is the
failure this layer exists to contain.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .anchors import AnchorVerifier
from .backends import PROMPT_MARKERS, Backend
from .claims import Claim, ClaimType, Maturity, Provenance, Transmission
from .errors import InvariantViolation
from .sources import SourceSpace, Span
from .wiki import Wiki

__all__ = ["Digester", "DigestStats", "locate_quote"]

PROMPT = (
    PROMPT_MARKERS["extract"] + "\n"
    "Extract atomic claims from the passage. For each, return its exact character offsets in the passage "
    "and one type among: fact, user_claim, opinion, belief, hypothesis, experience, preference, style, procedure. "
    "Use user_claim/opinion/belief for what the author asserts or believes; style/preference/procedure for how the author "
    "writes, prefers or works. Return JSON: {{\"claims\": [{{\"text\": ..., \"type\": ..., \"start\": int, \"end\": int}}]}}.\n"
    "PASSAGE:\n{passage}\n"
)

PROMPT_QUOTE = (
    PROMPT_MARKERS["extract"] + "\n"
    "Extract atomic claims from the passage. For each, copy the exact words of the passage that support it as "
    "'quote' (a verbatim substring, unchanged), and give one type among: fact, user_claim, opinion, belief, hypothesis, "
    "experience, preference, style, procedure. Use user_claim/opinion/belief for what the author asserts or believes; "
    "style/preference/procedure for how the author writes, prefers or works. Write the claim in the passage's language. "
    "Return JSON: {{\"claims\": [{{\"text\": ..., \"type\": ..., \"quote\": ...}}]}}.\n"
    "PASSAGE:\n{passage}\n"
)

_JSON = re.compile(r"\{.*\}", re.S)
_WS = re.compile(r"\s+")


def locate_quote(passage: str, quote: str) -> tuple[int, int] | None:
    """Offsets of ``quote`` in ``passage``, computed by code (never by the model).

    Exact match first; then a match that tolerates differences in whitespace and
    letter case only. Anything looser (paraphrase, reordering) is not a quote.
    """
    q = quote.strip().strip("\"'«»“”")
    if len(q) < 4:
        return None
    i = passage.find(q)
    if i >= 0:
        return i, i + len(q)
    pat = r"\s+".join(re.escape(w) for w in _WS.split(q) if w)
    m = re.search(pat, passage, re.I)
    return (m.start(), m.end()) if m else None


@dataclass
class DigestStats:
    spans: int = 0
    malformed: int = 0
    proposed: int = 0
    added: int = 0
    skipped_policy: int = 0
    quote_not_found: int = 0


@dataclass
class Digester:
    backend: Backend
    space: SourceSpace
    verifier: AnchorVerifier
    stats: DigestStats = field(default_factory=DigestStats)
    # "offsets": the model returns character offsets (v0.1). "quote": the model returns a
    # verbatim quote and the code locates it; small models count characters poorly.
    anchor_mode: str = "offsets"

    def _parse(self, raw: str) -> list[dict]:
        m = _JSON.search(raw)
        if not m:
            raise ValueError("no JSON object in digester output")
        data = json.loads(m.group(0))
        items = data.get("claims", [])
        if not isinstance(items, list):
            raise ValueError("'claims' is not a list")
        return items

    def digest_span(self, wiki: Wiki, span: Span) -> list[Claim]:
        self.stats.spans += 1
        rule = wiki.policy.rule_for(span.source)
        if not rule.wiki:
            self.stats.skipped_policy += 1
            return []
        try:
            prompt = (PROMPT_QUOTE if self.anchor_mode == "quote" else PROMPT).format(passage=span.text)
            items = self._parse(self.backend.generate(prompt, temperature=0.0, max_tokens=1024))
        except (ValueError, json.JSONDecodeError):
            self.stats.malformed += 1
            return []
        out: list[Claim] = []
        for it in items:
            try:
                text = str(it["text"]).strip()
                ctype = ClaimType(str(it.get("type", "fact")).strip().lower())
                if self.anchor_mode == "quote":
                    loc = locate_quote(span.text, str(it.get("quote", "")))
                    if loc is None:
                        self.stats.quote_not_found += 1
                        continue
                    s, e = loc
                else:
                    s, e = int(it["start"]), int(it["end"])
            except (KeyError, ValueError, TypeError):
                self.stats.malformed += 1
                continue
            if not text or not (0 <= s < e <= len(span.text)):
                self.stats.malformed += 1
                continue
            self.stats.proposed += 1
            if ctype == ClaimType.EXPERIENCE and not rule.retain_episodic:
                self.stats.skipped_policy += 1
                continue
            # A style claim from text the user did not write is kept (it describes the
            # source) but can never become trainable: LearningPolicy.allows_type requires
            # authored_by_user for style (SPEC 7.2.1).
            anchor = wiki.new_anchor(span.source, span.start + s, span.start + e)
            distance = 0 if (ctype in {ClaimType.STYLE, ClaimType.PREFERENCE, ClaimType.PROCEDURE} and rule.authored_by_user) else 1
            claim = Claim(text=text, type=ctype, anchors=[anchor], maturity=Maturity.DIGESTED,
                          provenance=Provenance(epistemic_distance=distance, transmission_path=Transmission.VERTICAL))
            self.verifier.verify(claim)
            try:
                out.append(wiki.add(claim))
                self.stats.added += 1
            except InvariantViolation:
                self.stats.skipped_policy += 1
        return out

    def digest_source(self, wiki: Wiki, rel: str) -> list[Claim]:
        wiki.register_source(rel, self.space.file_hash(rel))
        claims: list[Claim] = []
        for span in self.space.spans(rel):
            claims.extend(self.digest_span(wiki, span))
        return claims

    def digest_all(self, wiki: Wiki) -> list[Claim]:
        claims: list[Claim] = []
        for f in self.space.files():
            claims.extend(self.digest_source(wiki, f.rel))
        return claims
