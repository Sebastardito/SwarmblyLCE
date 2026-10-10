---
status: current
lang: en
---

# Consolidated pre-registration — benchmarks R14, R13 and R11 of Swarmbly LCE

**5 October 2026 · written BEFORE any real run of these benchmarks**

This document freezes the designs of the next three phases of the LCE
validation plan — hypotheses, rubrics, margins, budgets and refusal
conditions — before a single datum exists. It refers to whitepaper LCE v0.1
(Sections 11.1–11.5) and to the already published results (confirmatory run
2; exploratory benchmarks F1a–F1d with their declared scope). Any later
change is recorded as a numbered amendment in Section 7; a silent change
does not count.

**Covered:** R14 (reproducibility — the environment everything else runs
on), R13 (the decisive question of H-C1: does an anchored wiki beat a simple
memory?), R11 (the fair adapter: H-C6, H-C10 and forgetting by
regeneration), and the closure of H-C2 (ρ against its gain), folded into
R13. **R12 (the social plane) is pre-registered separately** once the canary
set is verified by native speakers, because its blocker is calendar time,
not compute.

Spanish: `PREREGISTRATION_BENCH_R1X_ES.md`.

---

## 1. R14 — Reproducibility (applies to everything else)

### 1.1 Frozen environment

1. The repository freezes a dependency lock file with exact versions and the
   Python version (3.11).
2. Ollama model digests (the five families and `nomic-embed-text`) go from
   being recorded to being a CHECK: the run STOPS if a model does not match
   the pre-registered one, and the refusal is recorded as an infrastructure
   failure, not as a result.

### 1.2 Sampling

1. **Temperature 0** for every measure that does not depend on diversity:
   multiple-choice items, H-C1 and R13 answers, lexicon adherence, identity
   probes.
2. For measures that DO depend on diversity (cross-user homogeneity), the
   raw samples are stored and the analysis assumes no pairing by seed
   (bootstrap over topics, as in run 2).
3. Adopting a server with an effective seed (candidate: llama.cpp) requires
   a pre-registered **A/A test** first: the mean difference between two
   identical runs must be ≤ 0.01 on the stochastic measures. Only if it
   passes is it adopted, recorded as an amendment.

### 1.3 Regeneration and figure anchoring

1. A single command (`python -m lce_validation.run_derive`, to be built)
   regenerates ALL tables of the RESULTS documents from the stored raw
   outputs, without models, and exits non-zero if any figure mismatches.
2. The figure blocks of the RESULTS documents become GENERATED from the JSON
   (never hand-edited), and a CI test compares each published figure with
   its JSON (the `test_published_figures_recompute` pattern of Swarmbly).
3. A shared `provenance()` helper records in every benchmark: Ollama
   version, model digests, git commit and the SHA-256 of this
   pre-registration.
4. **R14 closure criterion:** a fresh clone reproduces the tables
   byte-identical from the raw outputs; on re-running, deterministic arms
   come out identical and stochastic ones stay within the A/A noise (±0.01).

### 1.4 Publication

Release v0.1.1 on GitHub and Zenodo deposit (software DOI), with the raw
outputs included and this pre-registration cited.

---

## 2. R13 — Decisive H-C1: does the anchored wiki beat a simple memory?

### 2.1 The question

"Does memory help?" is answered (F1a: +0.477 per question, 95 % CI [+0.407,
+0.543]). The new question is: **does an anchored, typed, versioned wiki
beat the simple alternatives — the full document in context and raw-chunk
RAG — and on which question types?**

### 2.2 Arms (same token budget T per question; T is reported)

| Arm | What the answering model receives |
|---|---|
| A0 — no memory | the question only |
| A1 — full document | the user's complete sources, truncated to the budget |
| A2 — raw RAG | the k nearest fragments by embeddings (same embeddings as the wiki) |
| A3 — LCE wiki | anchored claims retrieved from the wiki (BM25), with type and maturity |
| A4 — wiki + Γ | A3 plus the projection into the contract (the full LCE product) |

Tokens sent are reported per arm and per question: they are exposure and ρ.

### 2.3 Question types (fixed before running)

1. **Simple fact** — one key in one source.
2. **Cross-document** — the answer requires combining two sources.
3. **Updated fact** — a newer source corrects an older one; correct = the
   current value.
4. **Contradiction** — two current sources disagree; correct = the current
   version or explicitly flagging the disagreement.
5. **Deleted source** — the user forgot the source; correct = ABSTAIN
   (answering with the deleted fact = error, worse than being wrong).
6. **No answer in memory** — the sources do not answer the question; correct
   = ABSTAIN.

Rubric per type (normative part of this document):

| Type | Correct | Incorrect |
|---|---|---|
| 1, 2 | gold key present | absent or wrong |
| 3 | current value | old value |
| 4 | current version OR disagreement flagged | old version without flagging |
| 5, 6 | abstention (or "not in my sources") | any answer with content |

### 2.4 Data

1. **Frozen own users**: the five benchmark-corpus users (frozen SHA),
   extended with a version 2 per user that adds: an updated source, a
   contradiction, a deleted source and an unanswerable question. The
   generator is frozen in the data commit.
2. **Public subset**: LongMemEval or LoCoMo, chosen after verifying its
   licence; the choice, the SHA-256 of the subset and its licence are fixed
   in Amendment 1, before running. It answers the criticism that the author
   writes the synthetic users.

### 2.5 Crossed design

- **3 digesters × 3 responders** (qwen2.5:3b, llama3.2:3b, gemma2:2b — the
  three families with the highest gain in F1a) for arm A3: it separates
  digester quality from answering ability and decides the digester gate with
  data, not with confounded correlations.
- Arms A0–A2 use the 3 responders. A4 uses the A3 cross plus Γ.

### 2.6 Size and statistics

- **≥250 paired questions** (every question goes through every arm), with
  **≥30 per type** for per-type intervals.
- Primary statistic: paired difference **A3 − A2** (wiki − raw RAG) per
  question, with a bootstrap clustered by question (10,000 resamples, seed
  20261005). Secondary: A3 − A1, A4 − A3, and the per-type breakdown.
- Declared power: with discordant pairs ≈ 30 %, n = 250 detects a difference
  of 0.10 with comfortable margin.

### 2.7 Decision rules

| Hypothesis | Holds | Dies | Otherwise |
|---|---|---|---|
| R13-H1: the wiki beats raw RAG | 95 % CI of A3−A2 > 0 overall | point estimate ≤ 0 | inconclusive |
| R13-H2: the wiki wins on updates and forgetting | CI > 0 on types 3 and 5 | point ≤ 0 on both | inconclusive |
| R13-H3 (digester gate): a floor on anchored claims explains utility | utility falls below the proposed floor in the crossed design | no monotone relation even crossed | the gate is withdrawn as a rule |
| H-C1 global death | — | raw RAG ≥ wiki overall AND the wiki does not win on 3 and 5 | the design is simplified (publishable) |

### 2.8 C2-bis (same run)

Placebo matched in instruction AMOUNT (not only form) and ≥5 users differing
in ≥2 traits. H-C17a holds if the homogeneity reduction by projection
exceeds the placebo with a 95 % CI > 0. It closes the main qualification of
run 2.

### 2.9 Closure of H-C2: ρ against its gain (same run)

With the wikis digested in R13 and Swarmbly's dispatch path (real planner +
packer, parametrisable path), the pair **(adherence gain with Γ, Δρ)** is
measured per task. Pre-registered tradeoff rule: **the projection survives
if the fraction of tasks with gain > 0 AND Δρ ≤ 10 % is ≥ 0.8**; the full
per-task scatter is reported. No additional thresholds.

### 2.10 Refusals

Refuse if: a model digest mismatches; fewer than 3 responders answer; any
wiki has < 5 anchored claims; fewer than 200 analysable questions; more than
10 % of answers cannot be scored.

---

## 3. R11 — The fair adapter (H-C6, H-C10, LC6)

Runs AFTER R13: the training batch comes from the trainable claims of an
already validated wiki.

### 3.1 Batch and tasks

1. The batch is built ONLY with `ExampleBuilder` from TRAINABLE claims
   (preference, style, procedure) — never facts (I1) — and with interleaved
   replay.
2. The test tasks are reworded and do not cross the batch: **≥30 per user ×
   3 users** (the first three of the corpus), with confidence intervals.
3. The **no-replay** sub-arm (H-C10) trains the same batch without the
   replay examples: one extra configuration per adapter.

### 3.2 Base families and seeds

- Two families: **qwen2.5-3b** (weights not distributed; qwen-research
  licence) and **granite-3.1-2b** (Apache-2.0; verify before freezing —
  amendment).
- **2 training seeds** per adapter; the third runs only if the first two
  disagree by more than 0.05 (MLX is not deterministic; the between-seed
  variance is reported).
- Declared budget: 2 families × 3 users × 2 seeds × 2 (replay) = **24
  trainings** of ≤ 500 iterations.

### 3.3 Arms (same information per arm)

base · retrieval + Γ (BM25 over the user's full wiki) · adapter · adapter +
retrieval.

### 3.4 Decision rules

| Hypothesis | Holds | Dies |
|---|---|---|
| H-C6 | adapter − retrieval has CI lower bound > 0 and mean ≥ +0.10 in ≥2 of 3 users | bound ≤ 0 in 2 of 3 → layer 2 is withdrawn (the roadmap death condition) |
| H-C10 (replay) | the no-replay arm forgets consolidated material EARLIER than the replay arm (later crossing point with replay) | no difference → the CLS homology reverts to vocabulary |
| LC6 (forgetting) | after `forget` of a source and regeneration, the forgotten fact returns to the base level (equivalence ±0.10) and style adherence persists | the fact persists in the adapter → "verifiable forgetting" is withdrawn |
| I1 (leak) | WITHOUT retrieval, the adapter does not answer user facts better than the base (equivalence ±0.10) | the adapter beats the base on facts → I1 violated and the batch is rebuilt |

### 3.5 Public option

A subset of LaMP (the personalization benchmark of OPPU [5]) if its licence
allows and its topics do not overlap the wikis; fixed by amendment with SHA.
It makes the result comparable with the literature.

### 3.6 Instruments tested in simulation BEFORE measuring

The abstention scorer (R13 types 5–6), the contradiction scorer (type 4),
the I1/LC6 equivalence procedure (it must detect an injected leak), the A/A
sampler test, and the generated-figure anchoring (1.3.2). None of them
decides anything before passing its simulation.

---

## 4. What this pre-registration does NOT cover

R12 (social plane) — requires the verified canary; pre-registered
separately. The public-subset choice (R13) and the second base family (R11)
— licence pending; they enter by amendment before running. Style-quality
judging is out of scope: grading is deterministic when the gold allows it,
and an LLM judge is only a secondary measure with human audit of a sample,
from a family different from the responders.

---

## 5. Execution order

R14 (environment and regeneration) → R13 (decisive run + C2-bis + ρ) → R11
(adapter, with batches from the R13 wikis) → R12 (separately). Every
confirmatory run requires a clean tree, verified digests and this committed
pre-registration, as in run 2.

---

## 6. References

[W] Whitepaper LCE v0.1, Sections 11.1–11.5. [5] Tan et al. 2024 (OPPU).
[LaMP] Salemi et al. 2024. [LongMemEval / LoCoMo] licence to confirm
(amendment). [Swarmbly] whitepaper v2, Sections 5 and 15, for the dispatch
path and the definition of ρ.

---

## 7. Amendments

*None yet. Any change is recorded here with date and reason before running;
a silent change does not count.*

*Text CC BY 4.0; code AGPL-3.0-or-later.*
