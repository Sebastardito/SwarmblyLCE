# lce_validation — instrument and mock report

> **SIMULATION AND MOCK RUN — NOT EVIDENCE.** Instruments are simulations; experiments use `MockBackend`, which answers by rules and injects the effects being measured. These numbers show that each measurement responds to what it measures. No figure here may be cited as a result about language models or about the LCE.

Version 0.1.0 · seed 0 · 2026-10-04T19:43:29Z

## Instruments

| instrument | hypothesis | prediction | passed |
|---|---|---|---|
| `anchor_gate` | anchoring rule (whitepaper 5.2; SPEC 6.3) | supported claims accepted (>=0.95); fabricated or misanchored claims rejected (acceptance <=0.05) | yes |
| `conformity` | H-C11 | conformist arm loses the minority (<5%); linear arm keeps its mean (~p0) | yes |
| `migration` | H-C8 (instrument only) | simulated F_ST decreases with Nm and tracks 1/(1+4Nm) within a factor of 2 in the band 0.5–2.25 | yes |
| `persistence` | H-C5 / H-C13 (instrument) | simulated loss matches q**r analytics; shared-operator placement is far worse | yes |
| `selection_bias` | H-C15 (instrument) | realised ≈ i·r·σ; selection-set estimate inflated; fresh-set estimate unbiased | yes |
| `collapse` | H-C7 / H-C12 (instrument) | replace erodes the tail; accumulate bounds it; anchored variation preserves or recovers it | yes |

## Mock experiments (plumbing only)

- Wiki on the fixture corpus: 13 claims, 5 trainable, anchor rejection rate 0.00.
- C1: accuracy with memory 0.90 vs without 0.00 (mock answers from context by rule).
- C2: lexicon adherence 1.0; projection bytes 113; cross-user homogeneity 0.826 with projection vs 1.000 without; cross-family error agreement 0.5333333333333333 with vs 0.5333333333333333 without.
- C10 (simulated trainer): 5 accepted adapters over 6 generations, 6 distinct test sets.
- Canary: 8 items, 0 verified; training guard passed.
