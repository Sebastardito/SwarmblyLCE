"""run_derive — regenera todas las cifras derivadas desde las salidas crudas.

Prerregistro R14 sec.1.3.1: un solo comando, sin modelos, que recalcula las
cifras publicadas y termina con código distinto de cero si alguna no
coincide. Recalcula desde las celdas crudas:

  1. F1a: ganancia media por pregunta (bootstrap agrupado, semilla fija);
  2. F1b: deltas de ρ por usuario desde las entradas guardadas;
  3. adaptador y social: sus resúmenes desde los datos guardados;
  4. corrida confirmatoria 2: re-ejecuta ``decide.py`` sobre las salidas
     guardadas y compara los veredictos;
  5. regenera ``results/BENCH_REPORT.md`` y lo compara byte a byte con el
     versionado.

    python3 -m lce_validation.run_derive
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

FAILURES: list[str] = []


def _boot_ci(values, B=10_000, seed=20261005):
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.array([rng.choice(values, n, replace=True).mean()
                      for _ in range(B)])
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _check(name: str, got, want, tol=1e-6):
    if got is None or want is None or abs(got - want) > tol:
        FAILURES.append(f"{name}: derivado {got} != guardado {want}")
        return False
    return True


def derive_hc1() -> None:
    p = ROOT / "results" / "bench_hc1_scale" / "results.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    by_q: dict[tuple, list[float]] = {}
    for c in d["cells"]:
        by_q.setdefault((c["user"], c["q"]), []).append(c["with"] - c["without"])
    q_gains = np.array([float(np.mean(v)) for v in by_q.values()])
    lo, hi = _boot_ci(q_gains)
    s = d["summary"]
    _check("F1a mean_by_question", float(q_gains.mean()),
           s.get("mean_gain_by_question"))
    _check("F1a ci_lo", lo, s.get("gain_ci95_by_question", [None])[0])
    _check("F1a ci_hi", hi, s.get("gain_ci95_by_question", [None, None])[1])
    _check("F1a n_questions", len(by_q), s.get("n_questions"))


def derive_rho() -> None:
    p = ROOT / "results" / "bench_rho" / "results.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    deltas = [u["delta_pct"] for u in d["users"].values()]
    _check("F1b worst", max(deltas), d["summary"].get("worst_delta_pct"))
    _check("F1b median", sorted(deltas)[len(deltas) // 2],
           d["summary"].get("median_delta_pct"))


def derive_run2() -> None:
    p = ROOT / "results" / "2026-10-05_C1C2_run2" / "results_real.json"
    if not p.exists():
        return
    import lce_validation.decide as decide
    d = json.loads(p.read_text(encoding="utf-8"))
    got = decide.decide(d)
    for k, v in (d.get("verdicts") or {}).items():
        g = got.get(k)
        if g is None:
            FAILURES.append(f"run2 {k}: decide ya no emite este veredicto")
        elif str(g.get("verdict")) != str(v.get("verdict")):
            FAILURES.append(f"run2 {k}: derivado {g.get('verdict')} != "
                            f"guardado {v.get('verdict')}")


def derive_r13() -> None:
    """R13: re-califica cada celda con la rúbrica actual y recomputa el
    resumen con la MISMA función que usa run_r13 (``summarize``), que no
    sobrescribe digestores (E1). Las celdas de corridas anteriores guardaban
    la respuesta truncada a 200 caracteres; solo esas pueden diferir al
    re-calificar y se cuentan aparte."""
    p = ROOT / "results" / "bench_r13" / "results.json"
    if not p.exists():
        return
    from lce_validation.run_r13 import score_answer, summarize
    d = json.loads(p.read_text(encoding="utf-8"))
    cells = d["cells"]
    bad = [c for c in cells if score_answer(c["q"], c["answer"]) != c["ok"]]
    if any(len(c["answer"]) != 200 for c in bad):
        FAILURES.append(f"R13: {sum(len(c['answer']) != 200 for c in bad)} celdas "
                        "no se re-califican igual (rúbrica cambiada o celda editada)")
    got = summarize(cells, d["digesters"])
    want = d.get("summary", {})
    for k, v in got.items():
        if want.get(k) != v:
            FAILURES.append(f"R13 {k}: derivado {v} != guardado {want.get(k)}")

def derive_report() -> None:
    import lce_validation.bench_report as br
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "BENCH_REPORT.md"
        # regenerar apuntando la salida al temporal
        saved = br.OUT
        br.OUT = tmp
        try:
            rc = br.main()
        finally:
            br.OUT = saved
        if rc != 0:
            FAILURES.append("report: el generador falló")
            return
        want = (ROOT / "results" / "BENCH_REPORT.md").read_text(encoding="utf-8")
        got = tmp.read_text(encoding="utf-8")
        if got != want:
            FAILURES.append("report: regenerado != versionado (deriva de cifras)")


def main() -> int:
    derive_hc1()
    derive_rho()
    derive_run2()
    derive_r13()
    derive_report()
    if FAILURES:
        print("✘ DERIVA DETECTADA:")
        for f in FAILURES:
            print("  -", f)
        return 1
    print("✔ todas las cifras derivadas coinciden con las guardadas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
