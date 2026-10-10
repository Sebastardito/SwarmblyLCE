---
status: current
lang: en
kind: exploratory
---

# Results — R13 exploratory pilot (the decisive question of H-C1)

**9 October 2026 · pre-registration `PREREGISTRATION_BENCH_R1X_EN.md` with
Amendment 1 · EXPLORATORY PILOT run: no pre-registered verdicts**

**What the pilot says in one line.** The five-arm pipeline works end to end
and the per-type rubric behaves (abstention on unanswerable ≈ 0.95). The
decisive comparison is NOT yet fair: the arms ran with unequal budgets (A1
913 tokens, A2 206, A3 111) and the wiki lost to raw RAG almost everywhere —
but its per-token efficiency equals RAG's (0.380 vs 0.375 per 100 tokens),
pointing to the wiki's retrieval policy, not its representation, as the
defect to fix.

Models: digesters and responders qwen2.5:3b, llama3.2:3b, gemma2:2b. Raw
outputs in `results/bench_r13/results.json` (SHA in the commit).

## 1. Figures

Accuracy per arm (91 questions × 3 responders; A3/A4 crossed):

| Arm | Accuracy | Mean tokens |
|---|---|---|
| A0 no memory | 0.117 | 47 |
| A1 full document | **0.813** | 913 |
| A2 raw RAG | 0.773 | 206 |
| A3 wiki | 0.454 | 111 |
| A4 wiki + Γ | 0.476 | 138 |

Per question type (A1 / A2 / A3):

| Type | A1 | A2 | A3 | Reading |
|---|---|---|---|---|
| simple | 0.88 | 0.78 | 0.42 | the wiki loses simple facts |
| cross | 0.67 | **0.80** | 0.20 | RAG combines two sources better |
| updated | 0.73 | **1.00** | 0.22 | RAG is perfect on updated facts; the wiki retrieves the old claim |
| contradiction | 0.33 | 0.20 | 0.22 | all low |
| deleted | 0.53 | 0.80 | 0.56 | RAG abstains more than the wiki |
| unanswerable | 0.93 | 0.93 | 0.98 | all abstain well |

Crossed design: A3 diagonal 0.458 vs crossed 0.421 — a foreign digester costs
~4 points; a small effect that needs the confirmatory run to decide the
digester gate.

## 2. Honest reading (what it proves and what it does not)

**What the pilot proves.** The complete pipeline (digestion → anchoring →
wiki → retrieval → five arms → per-type rubric → token accounting) runs
without errors, abstention works, and the between-arm differences are large
and stable.

**What it does NOT prove (identified confounds, all fixable before the
confirmatory run):**

1. **Unequal budgets.** A3 received 111 tokens of context against 206 (A2)
   and 913 (A1). The pre-registration requires the same budget; the pilot
   did not equalise it and the ordering A1 > A2 > A3 correlates with context
   size. The per-token efficiency (A3 0.380 ≈ A2 0.375) suggests the gap
   closes substantially at equal budget.
2. **The wiki's retrieval policy is the defect.** On `updated`, the wiki
   holds TWO claims (old and new) and recency-blind BM25 retrieves the old
   one (0.22 vs 1.00 for RAG). The epistemic layer (maturity, versioning)
   exists but the pilot did not use it at retrieval time. Fix: retrieval
   preferring the most recent claim of the same fact first, then maturity,
   with the budget equalised to RAG's.
3. **A4 (wiki+Γ) worsens factual types** (updated 0.20, contradiction 0.13)
   — consistent with the accuracy cost of Γ measured in run 2; re-measured
   with equal budget and corrected retrieval.

## 3. Consequence for the plan

The pilot does NOT trigger the death condition (it is exploratory and
budget-unequal), but it makes clear that the confirmatory run without the
two fixes would trigger it for the wrong reason. Amendment 2 freezes: (a)
equal context budget for all arms (200 tokens, the pilot's RAG budget); (b)
recency-aware wiki retrieval (most recent claim of the same fact first, then
maturity); (c) a quick re-pilot with the already cached wikis before the
≥250-question confirmatory run.

*Text CC BY 4.0.*
