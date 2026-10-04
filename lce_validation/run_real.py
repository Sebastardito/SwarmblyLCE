"""Run C1 and C2 against real models through an OpenAI-compatible endpoint (e.g. Ollama).

    python -m lce_validation.run_real --models qwen2.5:3b,llama3.2:3b,gemma2:2b
    python -m lce_validation.run_real --url http://localhost:11434/v1 --models ... --embed-model nomic-embed-text

The first model is used to digest the corpus and to write; all models are
used as replicas of different families for the error-agreement metric. The
script refuses to run if any model is unreachable, and labels its output
``backend_kind = real``. Results go to results_real.json and REPORT_REAL.md.

Scope must be declared with any result: fixture corpus of one synthetic user,
three projected users, ten factual questions. This is a first measurement of
the instruments on real models, not a test of the LCE's hypotheses at scale.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from swarmbly_lce.backends import BackendUnavailable, OpenAICompatBackend
from swarmbly_lce.report import run_header

from . import experiments as E


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="http://localhost:11434/v1")
    ap.add_argument("--models", required=True, help="comma-separated; at least two families")
    ap.add_argument("--embed-model", default="")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    args = ap.parse_args(argv)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if len(models) < 2:
        ap.error("at least two models of different families are required")
    backends = [OpenAICompatBackend(model=m, base_url=args.url, embed_model=args.embed_model) for m in models]
    for b in backends:
        try:
            b.generate("Reply with OK.", max_tokens=4)
        except BackendUnavailable as exc:
            print(f"model {b.model} unreachable: {exc}", file=sys.stderr)
            return 2
    families = {b.family for b in backends}
    if len(families) < 2:
        print("all models resolve to one family; the error-agreement metric needs distinct families", file=sys.stderr)
        return 2
    lead = backends[0]
    wiki, wstats = E.build_wiki(E.FIXTURES / "corpus", E.FIXTURES / "policy.json", lead)
    results = {
        "header": run_header("real", ",".join(models), url=args.url, embed_model=args.embed_model or "hash-fallback"),
        "build_wiki": wstats,
        "C1": E.c1_memory(lead, wiki),
        "C2": E.c2_projection(backends, lead),
        "canary": E.canary_check(lead, wiki),
        "scope": "fixture corpus (1 synthetic user), 3 projected users, 10 factual questions; unverified canary",
    }
    out = Path(args.out)
    (out / "results_real.json").write_text(json.dumps(results, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    c2 = results["C2"]
    lines = ["# lce_validation — real-model run", "", f"Models: {', '.join(models)} · {results['header']['utc']}", "",
             f"Scope: {results['scope']}.", "",
             f"- Wiki: {wstats['claims']} claims; anchor rejection rate {wstats['anchor_verification']['rejection_rate']:.2f}; "
             f"malformed digester outputs {wstats['digest']['malformed']}.",
             f"- C1 (H-C1): accuracy with memory {results['C1']['acc_with_memory']:.2f} vs without {results['C1']['acc_without_memory']:.2f}.",
             f"- C2 (H-C2): lexicon adherence {c2['lexicon_adherence']}; projection bytes {c2['projection_bytes_mean']:.0f}.",
             f"- C2 (H-C17): cross-user homogeneity {c2['homogeneity_with_projection']:.3f} with projection vs "
             f"{c2['homogeneity_without_projection']:.3f} without; cross-family error agreement "
             f"{c2['error_agreement_with_projection']['mean']} with vs {c2['error_agreement_without_projection']['mean']} without.",
             f"- Canary (unverified): tail mass {results['canary']['tail_mass']:.2f}; identity violations {results['canary']['identity_violation_rate']:.2f}.",
             ""]
    (out / "REPORT_REAL.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
