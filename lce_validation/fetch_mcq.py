"""Draw the fixed MCQ item set for the error-agreement instrument (run ONCE, before any model call).

    python -m lce_validation.fetch_mcq                      # 1500 items, seed 20261005
    python -m lce_validation.fetch_mcq --n 1500 --seed 20261005 --out lce_validation/data/mmlu_test_1500.json

Source: MMLU (Hendrycks et al., 2021), Hugging Face dataset ``cais/mmlu``,
config ``all``, split ``test``; MIT licence. Items are drawn uniformly without
replacement with ``numpy.random.default_rng(seed)`` over the row indices
reported by the Hugging Face datasets-server, then fetched one by one through
its public ``/rows`` endpoint (standard library only, no ``datasets`` or
``pyarrow`` needed). The script prints the SHA-256 of the file it writes;
``run_real`` records that hash in every result.

The pre-registration fixes the seed and the size. Re-drawing with another seed
after seeing results is a protocol deviation and must be declared.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

API = "https://datasets-server.huggingface.co/rows"
DATASET, CONFIG, SPLIT = "cais/mmlu", "all", "test"
DEFAULT_OUT = Path(__file__).resolve().parent / "data" / "mmlu_test_1500.json"


def _get(offset: int, length: int = 1, retries: int = 4) -> dict:
    q = urllib.parse.urlencode({"dataset": DATASET, "config": CONFIG, "split": SPLIT, "offset": offset, "length": length})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:  # network errors are retried, then raised
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"datasets-server unreachable at offset {offset}: {last}")


def select_indices(num_rows: int, n: int, seed: int) -> list[int]:
    rng = np.random.default_rng(seed)
    return sorted(int(i) for i in rng.choice(num_rows, size=n, replace=False))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=20261005)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    if out.exists():
        print(f"{out} already exists; the item set is drawn once. Delete it explicitly to re-draw (a declared deviation).")
        return 1
    first = _get(0)
    num_rows = int(first["num_rows_total"])
    idx = select_indices(num_rows, args.n, args.seed)
    items = []
    for k, i in enumerate(idx, 1):
        row = _get(i)["rows"][0]["row"]
        items.append({"idx": i, "subject": row["subject"], "question": row["question"],
                      "choices": list(row["choices"]), "answer": "ABCD"[int(row["answer"])]})
        if k % 50 == 0:
            print(f"  {k}/{len(idx)}")
        time.sleep(0.05)
    payload = {"source": f"huggingface.co/datasets/{DATASET}", "config": CONFIG, "split": SPLIT, "licence": "MIT",
               "citation": "Hendrycks, D., et al. (2021). Measuring massive multitask language understanding. ICLR 2021.",
               "num_rows_total": num_rows, "n": len(items), "seed": args.seed,
               "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "items": items}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(items)} items)\nsha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
