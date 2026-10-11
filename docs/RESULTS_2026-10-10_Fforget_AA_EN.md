---
status: current
lang: en
kind: exploratory
---

# Results — forgetting test (F-forget) and A/A reproducibility test

**10 October 2026 · Amendment 6 (c) of `PREREGISTRATION_BENCH_R1X_EN.md`,
committed before running · exploratory tests of mechanism and
reproducibility: they emit no verdict on H-C1 · locked environment (Python
3.11 from the `.venv`) and digests checked against
`lce_validation/data/model_digests.json`**

Raw outputs in `results/bench_forget/` and `results/aa_test/`. The
behavioural figures that follow the pre-registration and the comparison with
R13 are in `results/bench_forget/analysis.json`; `run_derive` recomputes
everything that does not depend on the cached wikis.

## 1. F-forget: does forgetting a source erase what was learnt from it?

For each user (5) and digester (qwen2.5:3b, llama3.2:3b, gemma2:2b) three
wikis were built: W_full, digested with every `.md` source; W_forget, the same
after `Wiki.forget_source("teach/knowledge/borrada.md")`; and W_never,
digested in the same run without that source.

**Structure.** In the 13 valid cells no claim anchored to the forgotten
source remained (S2 = 0) and no claim from other sources was lost or changed
(S3 = 0). The same holds in the sweep that forgets, one at a time, every
source of every W_full: 93 forgets, residue 0 and collateral damage 0. Two
cells (julian and luisa with llama3.2) were refused by S1, because those
wikis had no claim from the deleted source. Since `forget_source` deletes by
anchor, zero is what is expected: S2 and S3 verify that the implementation
does what the specification says on real wikis, not an empirical effect.
**Pre-registered structural verdict: holds.**

**Equivalence with never having digested it.** W_forget matches the W_never
of the same run in 8 of 15 wikis (mean Jaccard 0.943). A post-data analysis,
declared as such, shows where the difference comes from: W_forget matches the
R13 wiki, digested hours earlier without that source, in 15 of 15, while this
run's W_never matches R13's in only 8 of 15. The differences are in W_never,
that is, in the non-determinism of digestion that AA2 measures (Section 2),
not in forgetting. Forgetting a source leaves the wiki exactly as if it had
never been digested.

**Behaviour.** Abstention on the 5 questions about the deleted source, with
R13's prompt, retrieval and rubric (3 digesters × 3 responders, without the
refused cells, as the pre-registration requires):

| Wiki | Abstention |
|---|---|
| W_full | 0.359 |
| W_forget | 0.718 |
| W_never | 0.718 |

forget − full = **+0.356 [+0.222, +0.489]** and forget − never = +0.000
(bootstrap clustered by question). B1 (the full wiki abstains at least 0.10
less than the one that never saw the source) and B2 (forgetting is
behaviourally complete) are met. 89.7 % of the answers with W_forget and
W_never are word-for-word identical. The summary written by the run included
the two refused cells (full 0.444, forget 0.756, never 0.756); neither the
effect nor the conclusion changes.

**Reading.** This is what R13's `deleted` type could not measure (N2): here
the wiki had learnt from the source, forgot it and behaves as if it had never
had it. There are 5 questions, so power is low and the result is about
mechanism, not magnitude. Nor is it a comparison with RAG: in RAG, forgetting
a source means removing the file from the index. What F-forget shows is that
the wiki, which transforms sources into claims, does not lose that property.

## 2. A/A reproducibility (R14 1.2–1.4)

| Test | Result | Criterion |
|---|---|---|
| AA1 generation at T = 0 (R13 arm A2 repeated, 378 answers) | 100 % identical; accuracy Δ 0.0000 | **passes** |
| AA2 digestion (W_never against the R13 wikis) | 8 of 15 identical sets; mean Jaccard 0.943 | **fails** (requires ≥ 14 of 15) |
| AA3 seed at T = 0.7 (qwen2.5:3b, 20 topics × 3 seeds × 2 repetitions) | native endpoint 100 % identical (effective); OpenAI-compatible 80 % (not effective) | the native seed can be adopted by amendment |
| AA4 homogeneity across repetitions | mean Δ −0.0011 [−0.0067, +0.0047] | **passes** (≤ 0.01) |

**R14's re-run criterion is not closed.** Answer generation is fully
reproducible, but digestion not always: 7 of 15 wikis differ in a few claims
despite temperature 0. The pattern is notable: this run's W_full reproduced
the R13 wikis exactly (15 of 15, once the deleted source is removed), and the
W_never, digested right afterwards with the same prompts, is the one that
differs. It is compatible with the server's prompt cache altering decoding at
temperature 0, but that is a hypothesis. Closing R14 requires deterministic
digestion (the native endpoint with a seed, which AA3 shows to be effective,
or a canonicalisation of claims), by amendment. AA4 shows that the stochastic
measure (homogeneity) is stable even though individual samples from the
OpenAI-compatible endpoint do not repeat.

## 3. Declared deviations

1. The `bench_forget` summary included in the behaviour the two cells that S1
   refuses; the figures that follow the pre-registration are recomputed in
   `analysis.json` and the code now excludes them for future runs.
2. The comparison of W_forget with the R13 wikis was not pre-registered; it is
   reported as a post-data analysis.
3. The run script was adjusted before starting to accept the name
   `nomic-embed-text:latest` (commit `eca8f88`; `586eb21` in the provenance, before the weights purge: see `COMMIT_MAP_2026-10-10.md`); it affects no measure.

*Text CC BY 4.0.*

*Cifras ancladas: +0.489 [+0.333, +0.644].*

*Cifras ancladas: 0.289.*

*Cifras ancladas: 0.778.*

*Cifras ancladas: 12 of 15.*

*Cifras ancladas: 88.9 %.*

*Cifras ancladas: 0 of 15.*

*Cifras ancladas: 369.*
