"""R13 — la pregunta decisiva de H-C1: ¿la wiki anclada supera a una memoria simple?

Corre los cinco brazos del prerregistro consolidado (A0 sin memoria, A1
documento completo, A2 RAG crudo, A3 wiki LCE, A4 wiki + Γ) sobre las
preguntas v1+v2 del corpus de usuarios, con el diseño cruzado 3×3 en los
brazos de wiki, la rúbrica por tipo de pregunta (simple/cross/updated/
contradiction/deleted/unanswerable) y la contabilidad de tokens enviados
por brazo.

MODOS:
  --confirm  corrida CONFIRMATORIA: exige preregistro confirmado, árbol
             limpio, digests verificados y ≥3 respondedores (R14 §1.1);
  (por defecto) PILOTO EXPLORATORIO: corre igual, reporta todo, y declara
  que no emite veredictos preregistrados (Enmienda 1).

Uso:
  python3 -m lce_validation.run_r13 --digesters qwen2.5:3b,llama3.2:3b,gemma2:2b \
      --responders qwen2.5:3b,llama3.2:3b,gemma2:2b
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from swarmbly_lce.backends import OpenAICompatBackend  # noqa: E402
from swarmbly_lce.retrieval import BM25Retriever  # noqa: E402
from lce_validation.experiments import build_wiki  # noqa: E402
from lce_validation.provenance import record as _record  # noqa: E402
from lce_validation import instruments as I  # noqa: E402

PREREG = ROOT / "docs" / "PREREGISTRATION_BENCH_R1X_ES.md"
USERS_DIR = HERE / "fixtures" / "bench_users"
OUT = ROOT / "results" / "bench_r13"

ABSTAIN_RE = I._ABSTAIN_RE


def _norm(s: str) -> str:
    s = s.lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ñ", "n")]:
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", s)


def _tokens(text: str) -> int:
    return len(text.split())


class _Shim:
    """Objeto compatible con el índice BM25 (sentencias crudas o claims
    cacheadas)."""
    from swarmbly_lce.claims import Status as _S
    status = _S.ACTIVE
    _n = 0

    def __init__(self, t: str):
        self.text = t
        _Shim._n += 1
        self.claim_id = f"shim-{_Shim._n}"

    def render_for_retrieval(self) -> str:
        return self.text


def score_answer(q: dict, answer: str) -> bool:
    """Rúbrica de R13 §2.3 por tipo."""
    t = q.get("type", "simple")
    if t in ("deleted", "unanswerable"):
        return I._classify_abstention(answer) == "abstain"
    a = _norm(answer)
    if t == "updated":
        return all(_norm(g) in a for g in q["gold"])
    if t == "contradiction":
        has_gold = all(_norm(g) in a for g in q["gold"])
        flagged = bool(re.search(r"discrep|contradic|desacuerdo|no coincide", a))
        return has_gold or (q.get("allow_flag", False) and flagged)
    return all(_norm(g) in a for g in q["gold"])


def _ask(backend, q: dict, context: str = "", gamma: str = "") -> tuple[str, int]:
    prompt = ("Responde en una o dos oraciones. Si la información no está en "
              "el contexto o en las fuentes, di «no está en mis fuentes» y "
              "nada más.\n")
    if gamma:
        prompt += f"ESTILO DEL USUARIO: {gamma}\n"
    if context:
        prompt += f"FUENTES:\n{context}\n"
    prompt += f"PREGUNTA: {q['q']}\n"
    ans = backend.generate(prompt, temperature=0.0, max_tokens=96)
    return ans, _tokens(prompt + ans)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--digesters", default="qwen2.5:3b,llama3.2:3b,gemma2:2b")
    ap.add_argument("--responders", default="qwen2.5:3b,llama3.2:3b,gemma2:2b")
    ap.add_argument("--url", default="http://localhost:11434/v1")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--users", default=None)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)

    digesters = [m.strip() for m in args.digesters.split(",") if m.strip()]
    responders = [m.strip() for m in args.responders.split(",") if m.strip()]
    users = sorted(p.name for p in USERS_DIR.iterdir() if p.is_dir())
    if args.users:
        keep = {u.strip() for u in args.users.split(",")}
        users = [u for u in users if u in keep]

    prov = _record(PREREG, sorted(set(digesters + responders)),
                   url=args.url, extra={"mode": "confirmatory" if args.confirm
                                        else "exploratory-pilot"})
    if args.confirm and (prov["git_dirty"] or len(responders) < 3):
        print("NEGADA: la corrida confirmatoria exige árbol limpio y ≥3 "
              "respondedores", prov)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    cache_dir = OUT / "wikis_cache"
    cache_dir.mkdir(exist_ok=True)
    backends = {m: OpenAICompatBackend(model=m, base_url=args.url)
                for m in set(digesters + responders)}

    # wikis por (usuario, digestor) + RAG y documento completo
    # (las wikis se cachean en disco: un fallo no pierde las digestiones)
    wikis: dict[tuple, Any] = {}
    docs: dict[str, str] = {}
    stats: dict[str, Any] = {}
    for uid in users:
        base = USERS_DIR / uid
        srcs = []
        for p in sorted((base / "teach").rglob("*.md")):
            if p.name == "borrada.md":
                continue   # la fuente borrada se olvida antes de preguntar
            srcs.append(p.read_text(encoding="utf-8"))
        docs[uid] = "\n\n".join(srcs)
        from swarmbly_lce.wiki import Wiki as _Wiki
        from swarmbly_lce.policy import LearningPolicy as _LP
        for d in digesters:
            cache_file = cache_dir / f"{uid}__{d}_wiki.json"
            if cache_file.exists() and not getattr(args, "no_cache", False):
                wiki = _Wiki.load(cache_file,
                                  _LP.load(base / "policy.json"))
                wikis[(uid, d)] = wiki
                stats[f"{uid}|{d}"] = {"claims": len(wiki.claims),
                                       "cached": True}
                print(f"  wiki {uid}×{d}: {len(wiki.claims)} claims (caché)",
                      flush=True)
                continue
            wiki, st = build_wiki(base, base / "policy.json", backends[d],
                                  anchor_mode="quote", reconcile_types=True)
            wiki.save(cache_file)
            wikis[(uid, d)] = wiki
            stats[f"{uid}|{d}"] = {"claims": st["claims"],
                                   "anchored": st["claims"],
                                   "rejection": st["anchor_verification"]
                                   ["rejection_rate"]}
            print(f"  wiki {uid}×{d}: {st['claims']} claims", flush=True)

    cells = []
    for uid in users:
        base = USERS_DIR / uid
        qs = []
        for fname in ("questions.json", "questions_v2.json"):
            p = base / fname
            if p.exists():
                for q in json.loads(p.read_text(encoding="utf-8"))["questions"]:
                    q = dict(q)
                    q.setdefault("type", "simple")
                    qs.append(q)
        for q in qs:
            # A0: sin memoria, cada respondedor
            for r in responders:
                ans, tok = _ask(backends[r], q)
                cells.append({"user": uid, "arm": "A0", "responder": r,
                              "q": q, "ok": score_answer(q, ans),
                              "tokens": tok, "answer": ans[:200]})
            # A1: documento completo (truncado al presupuesto: 2400 tokens)
            doc = " ".join(docs[uid].split()[:2400])
            for r in responders:
                ans, tok = _ask(backends[r], q, context=doc)
                cells.append({"user": uid, "arm": "A1", "responder": r,
                              "q": q, "ok": score_answer(q, ans),
                              "tokens": tok, "answer": ans[:200]})
            # A2: RAG crudo (BM25 sobre oraciones de las fuentes)
            sents = re.split(r"(?<=[.!?])\s+", docs[uid])
            retr_raw = BM25Retriever().index([_Shim(s) for s in sents])
            ctx2 = "\n".join(h.text for h in retr_raw.search(q["q"], k=6))
            for r in responders:
                ans, tok = _ask(backends[r], q, context=ctx2)
                cells.append({"user": uid, "arm": "A2", "responder": r,
                              "q": q, "ok": score_answer(q, ans),
                              "tokens": tok, "answer": ans[:200]})
            # A3: wiki (cruzado digestor × respondedor)
            for d in digesters:
                wiki = wikis[(uid, d)]
                retr_w = BM25Retriever().index(wiki.claims.values())
                ctx3 = "\n".join(h.text for h in retr_w.search(q["q"], k=3))
                for r in responders:
                    ans, tok = _ask(backends[r], q, context=ctx3)
                    cells.append({"user": uid, "arm": "A3", "digester": d,
                                  "responder": r, "q": q,
                                  "ok": score_answer(q, ans),
                                  "tokens": tok, "answer": ans[:200]})
            # A4: wiki + Gamma (proyección real; diagonal digester=responder)
            from swarmbly_lce.projection import Projector
            for d in digesters:
                if d not in responders:
                    continue
                wiki = wikis[(uid, d)]
                retr_w4 = BM25Retriever().index(wiki.claims.values())
                ctx4 = "\n".join(h.text for h in retr_w4.search(q["q"], k=3))
                proj = Projector().project(q["q"], list(wiki.claims.values()))
                gamma = proj.projection.as_text()
                ans, tok = _ask(backends[d], q, context=ctx4, gamma=gamma)
                cells.append({"user": uid, "arm": "A4", "digester": d,
                              "responder": d, "q": q,
                              "ok": score_answer(q, ans),
                              "tokens": tok, "answer": ans[:200]})
        print(f"  {uid}: {len(qs)} preguntas respondidas por {len(responders)} "
              f"respondedores", flush=True)

    report = {
        "kind": "exploratory-pilot" if not args.confirm else "confirmatory",
        "prereg": str(PREREG), "provenance": prov,
        "digesters": digesters, "responders": responders,
        "wiki_stats": stats, "cells": cells,
    }
    # resumen por brazo (emparejado por pregunta y respondedor)
    by_q: dict[tuple, dict[str, float]] = {}
    for c in cells:
        key = (c["user"], c["q"]["q"], c["responder"])
        by_q.setdefault(key, {})[c["arm"]] = float(c["ok"])
    arms = ["A0", "A1", "A2", "A3", "A4"]
    means = {a: float(np.mean([v.get(a, 0.0) for v in by_q.values()]))
             for a in arms}
    # A3 diagonal (mismo digestor=respondedor) vs cruzado completo
    diag = [c for c in cells if c["arm"] == "A3"
            and c["digester"] == c["responder"]]
    a3_all = [c for c in cells if c["arm"] == "A3"]
    report["summary"] = {
        "questions": len(by_q),
        "mean_by_arm": {a: round(means[a], 3) for a in arms},
        "a3_diagonal_mean": round(float(np.mean([c["ok"] for c in diag])), 3),
        "a3_crossed_mean": round(float(np.mean([c["ok"] for c in a3_all])), 3),
        "tokens_by_arm": {a: round(float(np.mean(
            [c["tokens"] for c in cells if c["arm"] == a])), 1) for a in arms},
        "mode": report["kind"],
    }
    (OUT / "results.json").write_text(json.dumps(report, ensure_ascii=False,
                                                 indent=2), encoding="utf-8")
    s = report["summary"]
    print("\n=== RESUMEN R13 (piloto exploratorio) ===")
    for a in arms:
        print(f"  {a}: exactitud {s['mean_by_arm'][a]:.3f} "
              f"(tokens medios {s['tokens_by_arm'][a]:.0f})")
    print(f"  A3 diagonal: {s['a3_diagonal_mean']:.3f} | A3 cruzado: "
          f"{s['a3_crossed_mean']:.3f}")
    print(f"resultados: {OUT/'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
