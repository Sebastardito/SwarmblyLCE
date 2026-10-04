# lce_validation — harness and validation tools

*Español abajo.*

This directory holds the validation harness of the Swarmbly LCE. It follows the method of the Swarmbly whitepaper v2 (section 3): **an instrument is tested before it is used to decide anything**, and simulated or mock results are never evidence.

## Two kinds of runs

| | what it is | output | evidence? |
|---|---|---|---|
| **Instruments** (`instruments.py`) | numpy simulations checking that each measurement detects what it must | `results.json`, `REPORT.md` | **No** — they validate instruments |
| **Mock experiments** (`experiments.py` with `MockBackend`) | the real pipeline (digest → anchors → wiki → projection → Γ) driven by a rule-based backend | same files | **No** — plumbing only |
| **Real runs** (`run_real.py`) | the same experiments against real models (Ollama or any OpenAI-compatible server) | `results_real.json`, `REPORT_REAL.md` | candidate evidence, with its scope declared |

## Instruments and the hypotheses they serve

| instrument | hypothesis (whitepaper 11.1) | passes when |
|---|---|---|
| `anchor_gate` | anchoring rule (5.2) | supported claims accepted ≥ 95 %; fabricated, misanchored or stale-hash claims accepted ≤ 5 % |
| `conformity` | H-C11 | the conformist arm loses a 20 % minority; the linear (utility) arm keeps its mean; the I5 guard flags a threshold rule |
| `migration` | H-C8 (instrument) | simulated F_ST decreases with Nm and tracks 1/(1+4Nm) within a factor of 2 in the band 0.5–2.25 |
| `persistence` | H-C5, H-C13 | simulated annual loss matches q^r; shared-operator placement is far worse |
| `selection_bias` | H-C15 | realised gain ≈ i·r·σ; the selection-set estimate is inflated; a fresh set is unbiased |
| `collapse` | H-C7, H-C12 | replace erodes the tail; accumulate bounds it; anchored variation preserves it |

`run_all` exits with status 1 if any instrument fails.

## Running

```bash
pip install -e '.[dev]'
python -m lce_validation.run_all              # instruments + mock experiments
python -m pytest                              # unit tests, including one test per invariant I1–I8
```

On a machine with Ollama (e.g. Apple Silicon), with at least two model families pulled:

```bash
ollama pull qwen2.5:3b && ollama pull llama3.2:3b && ollama pull gemma2:2b
python -m lce_validation.run_real --models qwen2.5:3b,llama3.2:3b,gemma2:2b
# optional real embeddings for the homogeneity metric:
ollama pull nomic-embed-text
python -m lce_validation.run_real --models qwen2.5:3b,llama3.2:3b,gemma2:2b --embed-model nomic-embed-text
```

Declare the scope with any result: one synthetic user corpus, three projected users, ten factual questions, an **unverified** canary set. The canary items in `data/canary_es-EC.json` are drafts (`verified: false`) until a native speaker confirms each gloss.

---

## Español

Este directorio contiene el arnés de validación de la LCE. Sigue el método del whitepaper v2 de Swarmbly (sección 3): **un instrumento se prueba antes de usarlo para decidir nada**, y los resultados simulados o con `MockBackend` nunca son evidencia.

Los **instrumentos** son simulaciones que comprueban que cada medida detecta lo que debe (tabla de arriba). Los **experimentos con mock** recorren el código real con un backend de reglas y solo validan la tubería. Las **corridas reales** (`run_real.py`) repiten C1 y C2 contra modelos reales vía Ollama u otro servidor compatible con OpenAI, y son las únicas que producen evidencia candidata, siempre con su alcance declarado. `run_all` termina con código 1 si falla cualquier instrumento.

Los ítems del conjunto canario son borradores sin verificar hasta que un hablante nativo confirme cada glosa; con ellos se puede probar el arnés, pero no reportar un resultado.
