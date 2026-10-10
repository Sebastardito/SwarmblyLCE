"""Anclaje de las cifras citadas en los documentos (preregistro R14 1.3.2).

Cada entrada dice: «este documento debe contener esta cifra, y la cifra se
calcula aquí desde los JSON guardados». Si alguien edita una cifra a mano, o
si una re-corrida cambia los datos sin actualizar el texto, la prueba
``tests/test_doc_figures.py`` falla. Cubre las cifras vigentes de F1a y R13
en los documentos de resultados, la SWIP y STATUS.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _s(x: float, sign: bool = True) -> str:
    return (f"{x:+.3f}" if sign else f"{x:.3f}").replace("-", "−")


def _pair(d: dict, plus: bool = True) -> str:
    """'−0.256 [−0.317, −0.194]', '+0.156 [−0.067, +0.378]': siempre con signo."""
    lo, hi = d["ci95"]
    return f"{_s(d['mean'])} [{_s(lo)}, {_s(hi)}]"


def expected() -> list[tuple[str, str]]:
    an = json.loads((ROOT / "results" / "bench_r13" / "analysis.json").read_text(encoding="utf-8"))
    r13 = json.loads((ROOT / "results" / "bench_r13" / "results.json").read_text(encoding="utf-8"))["summary"]
    total = _pair(an["a3_minus_a2"])
    out: list[tuple[str, str]] = []
    for doc in ("docs/RESULTS_2026-10-09_R13_pilot_ES.md", "docs/RESULTS_2026-10-09_R13_pilot_EN.md"):
        out.append((doc, total))
        for g in ("gemma2:2b", "qwen2.5:3b", "llama3.2:3b"):
            out.append((doc, _pair(an["a3_minus_a2_by_digester"][g])))
            out.append((doc, f"{r13['a3_by_digester'][g]:.3f}"))
        for t in ("simple", "cross", "updated", "contradiction"):
            out.append((doc, _pair(an["a3_minus_a2_by_type"][t], plus=False)))
        for t in ("deleted", "unanswerable"):
            out.append((doc, _pair(an["a3_minus_a2_by_type"][t], plus=True)))
        out.append((doc, _pair(an["n1_a3_minus_a2_without_stale"])))
        out.append((doc, _pair(an["a3_minus_a0_answerable"], plus=True)))
        out.append((doc, _pair(an["a2_minus_a0_answerable"], plus=True)))
        for g, v in an["a4_minus_a3_diagonal"].items():
            out.append((doc, _s(v)))
        for k, v in an["gold_in_context_answerable"].items():
            if k != "n_questions":
                out.append((doc, f"{100 * v:.1f} %"))
        out.append((doc, f"{r13['mean_by_arm']['A3']:.3f}"))
        out.append((doc, f"{r13['mean_by_arm']['A4']:.3f}"))
    swip = "swips/SWIP-XXXX-local-cognitive-extension.md"
    out.append((swip, total))
    out.append((swip, _pair(an["a3_minus_a0_answerable"], plus=True)))
    f1 = an["f1a_n1"]
    out.append((swip, f"+{f1['all']['mean']:.3f} by question, 95 % CI [{f1['all']['ci95'][0]:.3f}, {f1['all']['ci95'][1]:.3f}]"))
    out.append((swip, f"+{f1['without_stale']['mean']:.3f} [{f1['without_stale']['ci95'][0]:.3f}, {f1['without_stale']['ci95'][1]:.3f}]"))
    out.append(("docs/STATUS.md", total))
    return out


def missing() -> list[tuple[str, str]]:
    bad = []
    for doc, needle in expected():
        text = " ".join((ROOT / doc).read_text(encoding="utf-8").split())
        if needle not in text:
            bad.append((doc, needle))
    return bad


if __name__ == "__main__":
    m = missing()
    for d, n in m:
        print(f"FALTA en {d}: {n}")
    raise SystemExit(1 if m else 0)
