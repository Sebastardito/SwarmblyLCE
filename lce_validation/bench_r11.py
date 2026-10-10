"""R11 — el adaptador justo (H-C6, H-C10, I1), conforme al preregistro §3.

Lote SOLO de afirmaciones TRAINABLES vía ExampleBuilder (I1: nunca hechos),
con y sin repaso (H-C10); dos familias base (qwen2.5-3b, licencia
qwen-research, pesos no distribuidos; granite-3.1-2b, Apache-2.0); dos
semillas; evaluación de CUATRO brazos sobre tareas re-redactadas sin cruce
con el lote, más la prueba de fuga I1 (sin recuperación, el adaptador no
debe responder hechos mejor que el base, equivalencia ±0.10).

LC6 (olvido por regeneración) se difiere a la confirmatoria: requiere el
flujo de olvido completo y se declara en la Enmienda 5.

    python3 -m lce_validation.bench_r11 --users mara,julian,carmen
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from swarmbly_lce.wiki import Wiki  # noqa: E402
from swarmbly_lce.policy import LearningPolicy  # noqa: E402
from swarmbly_lce.training import ExampleBuilder  # noqa: E402
from swarmbly_lce.retrieval import BM25Retriever  # noqa: E402
from swarmbly_lce.backends import OpenAICompatBackend  # noqa: E402
from lce_validation.bench_corpus_gen import USERS as CORPUS  # noqa: E402

MLX_LORA = "/opt/homebrew/bin/mlx_lm.lora"
MLX_GEN = "/opt/homebrew/bin/mlx_lm.generate"
OUT = ROOT / "results" / "bench_r11"
BASE = {"qwen2.5:3b": "Qwen/Qwen2.5-3B-Instruct",
        "granite3.1-dense:2b": "ibm-granite/granite-3.1-2b-instruct"}


def _norm(s: str) -> str:
    s = s.lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ñ", "n")]:
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", s)


def _env() -> dict:
    env = os.environ.copy()
    env["HF_HOME"] = str(ROOT / ".hf_cache")
    return env


def build_tasks(uid: str) -> tuple[list[dict], list[dict]]:
    """Tareas de evaluación re-redactadas (sin cruce con el lote) y las
    factuales para la prueba de fuga I1."""
    style = CORPUS[uid]["style"]
    proc = CORPUS[uid]["procedures"]
    tasks: list[dict] = []
    prefs = re.findall(r"Prefiero el término (.+?) en lugar de (.+?)[.\n]",
                       style)
    for prefer, avoid in prefs:
        tasks.append({"q": f"Corrige esta frase para que suene como yo: "
                           f"«el problema es la {avoid} del sistema»",
                      "gold": [prefer]})
        tasks.append({"q": f"¿Qué término elegirías frente a «{avoid}» en un "
                           f"texto tuyo?", "gold": [prefer]})
    rules = [l.strip() for l in style.splitlines()
             if l.strip() and "Prefiero" not in l and "Escribo" in l
             or l.strip().startswith("Cuando") or l.strip().startswith("En los")]
    for r in rules[:6]:
        tasks.append({"q": "Describe cómo escribes un documento técnico.",
                      "gold": [_norm(r).split()[-1] if _norm(r).split() else r]})
    # tareas de procedimiento (umbrales) desde el documento
    nums = re.findall(r"(\d[\d,\.]*)\s*(?:por ciento|%|muestras|variantes|milisegundos|minutos|paso|puntos)",
                      proc)
    proc_qs = [
        ("¿Qué umbral de cobertura exiges antes de un cambio?", "80"),
        ("¿Cuántas variantes mínimas conserva tu conjunto de trabajo?", "5,000"),
        ("¿En qué ventana podas por desequilibrio de ligamiento?", "50"),
        ("¿Qué p95 de latencia exiges?", "300"),
        ("¿Qué materialidad aplicas a los informes?", "5"),
        ("¿Cuántos participantes mínimos exigen tus criterios?", "50"),
        ("¿Cómo repartes una sesión de 90 minutos?", "40"),
        ("¿Qué pesa el examen final?", "40"),
    ]
    for q, g in proc_qs[:6]:
        tasks.append({"q": q, "gold": [g]})
    factual = json.loads((HERE / "fixtures" / "factual.json").read_text(
        encoding="utf-8"))["questions"]
    factual_user = [
        {"q": f"Según tus notas: {fq['q']}", "gold": fq["gold"]}
        for fq in factual[:5]]
    return tasks, factual_user


def train(base_model: str, rows: list[dict], out_dir: Path, seed: int) -> Path:
    data = out_dir / "data"
    data.mkdir(parents=True, exist_ok=True)
    n_valid = max(2, len(rows) // 5)
    (data / "train.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows[n_valid:])
        + "\n", encoding="utf-8")
    (data / "valid.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows[:n_valid])
        + "\n", encoding="utf-8")
    adapter = out_dir / "adapter"
    cmd = [MLX_LORA, "--model", base_model, "--train", "--data", str(data),
           "--adapter-path", str(adapter), "--iters", "300",
           "--batch-size", "2", "--learning-rate", "1e-4", "--seed", str(seed)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=_env(),
                       timeout=3600)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    return adapter


def generate(prompt: str, adapter: Path | None, base_model: str,
             max_tokens: int = 60) -> str:
    cmd = [MLX_GEN, "--model", base_model, "--prompt", prompt,
           "--max-tokens", str(max_tokens), "--temp", "0.0"]
    if adapter:
        cmd += ["--adapter-path", str(adapter)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=_env(),
                       timeout=600)
    return r.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", default="mara,julian,carmen")
    ap.add_argument("--families", default="qwen2.5:3b,granite3.1-dense:2b")
    ap.add_argument("--seeds", default="20261005,20261006")
    ap.add_argument("--replay", default="yes,no")
    ap.add_argument("--eval-only", action="store_true")
    args = ap.parse_args(argv)

    users = [u.strip() for u in args.users.split(",")]
    fams = [f.strip() for f in args.families.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]
    replays = [r.strip() for r in args.replay.split(",")]
    OUT.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {"cells": [], "trainings": []}
    for fam in fams:
        base_model = BASE[fam]
        for uid in users:
            tasks, factual = build_tasks(uid)
            wiki_path = (ROOT / "results" / "bench_r13" / "wikis_cache"
                         / f"{uid}__{fam}_wiki.json")
            if not wiki_path.exists():
                print(f"digiriendo wiki {uid}×{fam} ...", flush=True)
                from lce_validation.experiments import build_wiki
                bb = OpenAICompatBackend(model=fam,
                                         base_url="http://localhost:11434/v1")
                base_dir = HERE / "fixtures" / "bench_users" / uid
                build_wiki(base_dir, base_dir / "policy.json", bb,
                           anchor_mode="quote", reconcile_types=True,
                           suffixes=frozenset({".md"}))[0].save(wiki_path)
            wiki = Wiki.load(wiki_path, LearningPolicy.load(
                HERE / "fixtures" / "bench_users" / uid / "policy.json"))
            examples = ExampleBuilder(wiki).from_claims()
            rows = [{"messages": [{"role": "user", "content": e.prompt},
                                  {"role": "assistant", "content": e.response}]}
                    for e in examples if e.kind != "preference_pair"]
            if len(rows) < 6:
                print(f"  {uid}×{fam}: lote insuficiente ({len(rows)}), salto")
                continue
            replay_rows = rows + rows[:4] + rows[:4]   # repaso entremezclado
            for replay in replays:
                batch = replay_rows if replay == "yes" else rows
                for seed in seeds:
                    tag = f"{uid}__{fam}__s{seed}__r{replay}"
                    adir = OUT / tag
                    if not args.eval_only:
                        t0 = time.time()
                        try:
                            adapter = train(base_model, batch, adir, seed)
                        except RuntimeError as e:
                            print(f"  {tag}: entrenamiento falló: {e}")
                            report["trainings"].append(
                                {"tag": tag, "ok": False})
                            continue
                        report["trainings"].append(
                            {"tag": tag, "ok": True,
                             "seconds": round(time.time() - t0, 1),
                             "batch": len(batch)})
                        print(f"  {tag}: {len(batch)} pares, "
                              f"{time.time()-t0:.0f}s", flush=True)
                    adapter = adir / "adapter"
                    if not adapter.exists():
                        print(f"  {tag}: adaptador ausente, salto")
                        continue
                    if replay == "no":
                        # H-C10: solo las 6 primeras tareas y 2 brazos
                        eval_tasks = tasks[:6]
                        arms = {"base": None, "adapter": adapter}
                    else:
                        eval_tasks = tasks
                        arms = {"base": None, "adapter": adapter}
                    for t in eval_tasks:
                        ctx = "\n".join(
                            h.text for h in BM25Retriever().index(
                                wiki.claims.values()).search(t["q"], k=3))
                        ans_b = generate(t["q"], None, base_model)
                        ans_r = generate(t["q"] + "\nCONTEXTO:\n" + ctx,
                                         None, base_model)
                        ans_a = generate(t["q"], adapter, base_model)
                        ans_ar = generate(t["q"] + "\nCONTEXTO:\n" + ctx,
                                          adapter, base_model)
                        report["cells"].append({
                            "tag": tag, "q": t["q"], "gold": t["gold"],
                            "base_ok": all(_norm(g) in _norm(ans_b)
                                           for g in t["gold"]),
                            "retrieval_ok": all(_norm(g) in _norm(ans_r)
                                                for g in t["gold"]),
                            "adapter_ok": all(_norm(g) in _norm(ans_a)
                                              for g in t["gold"]),
                            "adapter_retr_ok": all(_norm(g) in _norm(ans_ar)
                                                   for g in t["gold"]),
                            "base": ans_b[:120], "adapter": ans_a[:120]})
                    # I1: fuga de hechos (adaptador SIN recuperación vs base)
                    for f in factual:
                        ans_b = generate(f["q"], None, base_model, 40)
                        ans_a = generate(f["q"], adapter, base_model, 40)
                        report["cells"].append({
                            "tag": tag, "q": f["q"], "gold": f["gold"],
                            "i1": True,
                            "base_ok": all(_norm(g) in _norm(ans_b)
                                           for g in f["gold"]),
                            "adapter_ok": all(_norm(g) in _norm(ans_a)
                                              for g in f["gold"])})

    (OUT / "results.json").write_text(json.dumps(report, ensure_ascii=False,
                                                 indent=2), encoding="utf-8")
    # resumen
    cells = [c for c in report["cells"] if not c.get("i1")]
    by_tag: dict[str, list] = {}
    for c in cells:
        by_tag.setdefault(c["tag"], []).append(c)
    print("\n=== RESUMEN R11 (piloto) ===")
    for tag, cs in sorted(by_tag.items()):
        n = len(cs)
        base = sum(c["base_ok"] for c in cs) / n
        adp = sum(c["adapter_ok"] for c in cs) / n
        adr = sum(c["adapter_retr_ok"] for c in cs) / n
        print(f"  {tag}: base {base:.2f} | adapter {adp:.2f} | "
              f"adapter+retr {adr:.2f} (n={n})")
    i1 = [c for c in report["cells"] if c.get("i1")]
    if i1:
        n = len(i1)
        diff = (sum(c["adapter_ok"] for c in i1) - sum(c["base_ok"] for c in i1)) / n
        print(f"\nI1 (fuga de hechos): adaptador − base = {diff:+.3f} "
              f"(equivalencia ±0.10)")
    print(f"\nresultados: {OUT/'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
