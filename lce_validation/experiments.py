"""Backend-driven experiments of the whitepaper (section 11.2).

Every function takes the backend(s) explicitly. With ``MockBackend`` the
results validate the plumbing and are labelled ``mock`` downstream; only
``run_real.py`` with real models produces candidate evidence.

* ``build_wiki``      — layers 0–1 end to end on the fixture corpus.
* ``c1_memory``       — H-C1: retrieval over the wiki vs no memory.
* ``c2_projection``   — H-C2 and H-C17: lexicon adherence and bytes added to Γ;
  cross-user homogeneity with vs without projection; cross-family error
  agreement within a request with vs without projection.
* ``c10_selection``   — H-C15 through ``AdapterManager`` (simulation trainer).
* ``canary_check``    — canary terms never reach training data; tail mass and
  identity-violation rate of a backend's glosses.
"""

from __future__ import annotations

import itertools
import json
import re
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from swarmbly_lce.anchors import AnchorVerifier
from swarmbly_lce.backends import PROMPT_MARKERS, Backend
from swarmbly_lce.claims import Maturity
from swarmbly_lce.digest import Digester
from swarmbly_lce.diversity import CanarySet, error_agreement_given_both_wrong, homogeneity
from swarmbly_lce.policy import LearningPolicy
from swarmbly_lce.projection import Projector
from swarmbly_lce.retrieval import BM25Retriever
from swarmbly_lce.sources import SourceSpace
from swarmbly_lce.training import AdapterManager, Example, ExampleBuilder, MockEvaluator, MockTrainer, Recipe
from swarmbly_lce.wiki import Wiki

FIXTURES = Path(__file__).resolve().parent / "fixtures"
DATA = Path(__file__).resolve().parent / "data"

__all__ = ["build_wiki", "c1_memory", "c2_projection", "c10_selection", "canary_check", "FIXTURES", "DATA"]


def _norm(ans: str) -> str:
    return " ".join(re.sub(r"[^\w\s:]", " ", ans.lower()).split()[:8])


def build_wiki(corpus: Path, policy_path: Path, backend: Backend, cycles: int = 4) -> tuple[Wiki, dict[str, Any]]:
    space = SourceSpace(corpus)
    policy = LearningPolicy.load(policy_path)
    wiki = Wiki(policy=policy)
    verifier = AnchorVerifier(space)
    dig = Digester(backend, space, verifier)
    t0 = time.perf_counter()
    dig.digest_all(wiki)
    digest_ms = (time.perf_counter() - t0) * 1000
    # Deterministic linking: consecutive claims of the same source are linked (CONNECTED needs one link).
    by_source: dict[str, list[str]] = {}
    for c in wiki.claims.values():
        by_source.setdefault(c.anchors[0].source, []).append(c.claim_id)
    for ids in by_source.values():
        for a, b in zip(ids, ids[1:]):
            wiki.link(a, b)
    for _ in range(cycles):
        wiki.consolidation_cycle()
    maturity = {m.value: 0 for m in Maturity}
    for c in wiki.claims.values():
        maturity[c.maturity.value] += 1
    stats = {
        "claims": len(wiki.claims),
        "maturity": maturity,
        "trainable": len(wiki.trainable()),
        "digest": dig.stats.__dict__,
        "anchor_verification": {**verifier.stats.__dict__, "rejection_rate": verifier.stats.rejection_rate},
        "digest_ms": digest_ms,
    }
    return wiki, stats


def _answer(backend: Backend, question: str, context: str = "", extra: str = "") -> str:
    prompt = f"{PROMPT_MARKERS['answer']}\nAnswer briefly using the context if it is relevant.\n"
    if extra:
        prompt += f"STYLE: {extra}\n"
    if context:
        prompt += f"CONTEXT: {context}\n"
    prompt += f"QUESTION: {question}\n"
    return backend.generate(prompt, temperature=0.0, max_tokens=96)


def c1_memory(backend: Backend, wiki: Wiki, questions_path: Path = FIXTURES / "questions.json", k: int = 3) -> dict[str, Any]:
    qs = json.loads(questions_path.read_text(encoding="utf-8"))["questions"]
    retr = BM25Retriever().index(wiki.claims.values())
    with_mem, without = [], []
    for item in qs:
        hits = retr.search(item["q"], k=k)
        ctx = " ".join(h.text for h in hits)
        a1 = _answer(backend, item["q"], ctx)
        a0 = _answer(backend, item["q"])
        with_mem.append(item["gold"].lower() in a1.lower())
        without.append(item["gold"].lower() in a0.lower())
    acc1, acc0 = float(np.mean(with_mem)), float(np.mean(without))
    return {"hypothesis": "H-C1", "n": len(qs), "acc_with_memory": acc1, "acc_without_memory": acc0, "gain": acc1 - acc0}


def _write(backend: Backend, topic: str, gamma: dict[str, Any]) -> str:
    lex = gamma.get("lexicon", {})
    preferred = [t for t, v in lex.items() if v == "preferred"]
    prompt = (f"{PROMPT_MARKERS['write']}\nWrite two sentences about the topic. Follow the contract fields if present.\n"
              f"TOPIC: {topic}\n")
    if gamma.get("register"):
        prompt += f"REGISTER: {gamma['register']}\n"
    if preferred:
        prompt += f"LEXICON: {', '.join(preferred)}\n"
    if gamma.get("style_seed"):
        prompt += f"STYLE_SEED: {gamma['style_seed']}\n"
    return backend.generate(prompt, temperature=0.0, max_tokens=160)


def c2_projection(families: Sequence[Backend], digest_backend: Backend, users_dir: Path = FIXTURES / "users",
                  users_policy: Path = FIXTURES / "users_policy.json", queries_path: Path = FIXTURES / "open_queries.json",
                  factual_path: Path = FIXTURES / "factual.json") -> dict[str, Any]:
    topics = json.loads(queries_path.read_text(encoding="utf-8"))["topics"]
    writer = families[0]
    projections = {}
    for udir in sorted(p for p in users_dir.iterdir() if p.is_dir()):
        wiki, _ = build_wiki(udir, users_policy, digest_backend)
        res = Projector().project("escribe sobre " + " ".join(topics), list(wiki.claims.values()))
        projections[udir.name] = res
    # (a) adherence and bytes
    adherence, bytes_added = [], []
    for name, res in projections.items():
        g = res.projection.gamma_fields()
        preferred = [t for t, v in g.get("lexicon", {}).items() if v == "preferred"]
        bytes_added.append(res.projection.size_bytes())
        for t in topics:
            out = _write(writer, t, g).lower()
            if preferred:
                adherence.append(np.mean([p.lower() in out for p in preferred]))
    # (b) H-C17 cross-user homogeneity
    hom_with, hom_without = [], []
    for t in topics:
        outs_with = [_write(writer, t, projections[u].projection.gamma_fields()) for u in projections]
        outs_without = [_write(writer, t, {}) for _ in projections]
        hom_with.append(homogeneity(writer.embed(outs_with)))
        hom_without.append(homogeneity(writer.embed(outs_without)))
    # (c) within-request cross-family error agreement with vs without projection
    fq = json.loads(factual_path.read_text(encoding="utf-8"))["questions"]
    some_proj = next(iter(projections.values())).projection.as_text()

    def correct(ans: str, gold: str) -> bool:
        return ans.startswith("CORRECT::") or gold.lower() in ans.lower()

    def agreement(extra: str) -> dict[str, Any]:
        answers = {b.family: [_norm(_answer(b, q["q"], extra=extra)) for q in fq] for b in families}
        rows = []
        for fa, fb in itertools.combinations(sorted(answers), 2):
            a, b = answers[fa], answers[fb]
            # Map correct answers to a sentinel so that only wrong answers are compared.
            aa = ["__gold__" if correct(x, q["gold"]) else x for x, q in zip(a, fq)]
            bb = ["__gold__" if correct(x, q["gold"]) else x for x, q in zip(b, fq)]
            rows.append({"pair": f"{fa}|{fb}", "agree_given_both_wrong": error_agreement_given_both_wrong(aa, bb, ["__gold__"] * len(fq))})
        vals = [r["agree_given_both_wrong"] for r in rows if r["agree_given_both_wrong"] is not None]
        return {"pairs": rows, "mean": float(np.mean(vals)) if vals else None}

    return {
        "hypothesis": "H-C2, H-C17",
        "users": len(projections),
        "projection_bytes_mean": float(np.mean(bytes_added)) if bytes_added else 0.0,
        "lanes": {u: [r.lane_initial.name, r.lane_final.name] for u, r in projections.items()},
        "lexicon_adherence": float(np.mean(adherence)) if adherence else None,
        "homogeneity_with_projection": float(np.mean(hom_with)),
        "homogeneity_without_projection": float(np.mean(hom_without)),
        "error_agreement_without_projection": agreement(""),
        "error_agreement_with_projection": agreement(some_proj),
        "prediction": "projection lowers cross-user homogeneity and leaves within-request error agreement unchanged",
    }


def c10_selection(generations: int = 6, k: int = 5, reliability: float = 0.5, seed: int = 0) -> dict[str, Any]:
    """Runs the real AdapterManager with simulated trainer/evaluator (SIMULATION)."""
    from swarmbly_lce.claims import Anchor, Claim, ClaimType, Provenance
    policy = LearningPolicy.from_mapping({"learning_policy": {"sources": {"s": {"authored_by_user": True, "learn_style": True, "learn_procedure": True}}}})
    wiki = Wiki(policy=policy)
    for i in range(40):
        c = Claim(text=f"Suelo usar la construcción número {i} al escribir informes técnicos.", type=ClaimType.STYLE,
                  anchors=[Anchor("s/f.md", 0, 10, "h", verified=True)], provenance=Provenance(epistemic_distance=0))
        wiki.add(c)
    ids = list(wiki.claims)
    for a, b in zip(ids, ids[1:]):
        wiki.link(a, b)
    for _ in range(4):
        wiki.consolidation_cycle()
    new = ExampleBuilder(wiki).from_claims()
    replay = [Example("replay", f"old {i}", f"old answer {i}") for i in range(20)]
    general = [Example("general", f"gen {i}", f"general {i}") for i in range(20)]
    mgr = AdapterManager(wiki, "base-3b", MockTrainer(seed=seed), MockEvaluator(reliability=reliability, seed=seed))
    import random
    rng = random.Random(seed)
    for _ in range(generations):
        recipes = [Recipe(rank=rng.choice([4, 8, 16]), lr=rng.choice([5e-5, 1e-4, 2e-4]), seed=rng.randrange(10**6)) for _ in range(k)]
        mgr.run_generation(new, replay, general, recipes)
    accepted = [h for h in mgr.history if h["winner"]]
    return {"hypothesis": "H-C15 (simulation through AdapterManager)", "generations": generations, "candidates_per_generation": k,
            "accepted": len(accepted), "distinct_test_sets": len({h["test_id"] for h in mgr.history}),
            "history": mgr.history, "examples_eligible": len(new)}


def canary_check(backend: Backend, wiki: Wiki, canary_path: Path = DATA / "canary_es-EC.json") -> dict[str, Any]:
    canary = CanarySet.load(canary_path)
    examples = ExampleBuilder(wiki).from_claims()
    canary.guard_training(e.response for e in examples)  # raises if violated
    answers = {}
    for item in canary.items:
        q = f"¿Qué significa '{item.term}' en el español de Ecuador?"
        answers[item.term] = _answer(backend, q)
    return {
        "items": len(canary.items),
        "verified_items": sum(i.verified for i in canary.items),
        "tail_mass": canary.tail_mass(answers),
        "identity_violation_rate": canary.identity_violation_rate(answers.values()),
        "training_guard": "passed",
        "note": "items are unverified drafts until a native speaker confirms them; do not report as a result",
    }
