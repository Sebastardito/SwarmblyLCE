# Swarmbly LCE — Local Cognitive Extension

[![Licencia: AGPL-3.0-or-later](https://img.shields.io/badge/licencia-AGPL--3.0--or--later-blue.svg)](LICENSE)
![Estado: borrador](https://img.shields.io/badge/estado-borrador-orange.svg)
[![Whitepaper DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23150478.svg)](https://doi.org/10.5281/zenodo.23150478)

**Una extensión local-first para [Swarmbly](https://github.com/Sebastardito/Swarmbly-AI): memoria personal, aprendizaje del modelo del usuario y transferencia ligera de conocimiento entre nodos, sin deformar el protocolo.**

Swarmbly fragmenta el problema y no el modelo. Sus workers son deliberadamente casi sin estado, y el cliente es la única unidad que conserva memoria. La LCE propone qué hacer con esa memoria: una wiki legible y anclada a las fuentes del usuario, un adaptador ligero que aprende de él solo su manera de hablar y de trabajar (nunca sus hechos), y un intercambio opcional de pequeñas cápsulas de conocimiento escrito cuya memoria sobrevive por uso a la desaparición de los nodos que las originaron.

> **Estado: borrador, nada medido.** Ningún mecanismo de este repositorio se ha medido todavía. Cada uno llega con su hipótesis, su experimento y su condición de abandono, enunciados antes de construir. El repositorio incluye una implementación de referencia y un arnés cuyos instrumentos pasan en simulación; eso valida las medidas, no la extensión. No revisado por pares.

- **Whitepaper (v0.1, borrador; Zenodo [10.5281/zenodo.23150478](https://doi.org/10.5281/zenodo.23150478)):** [`docs/WHITEPAPER_LCE_ES.md`](docs/WHITEPAPER_LCE_ES.md) ([PDF](docs/WHITEPAPER_LCE_ES.pdf)) · English: [`docs/WHITEPAPER_LCE_EN.md`](docs/WHITEPAPER_LCE_EN.md) ([PDF](docs/WHITEPAPER_LCE_EN.pdf)) — fundamento, homologías aceptadas y descartadas, evidencia adversa, arquitectura, hipótesis, limitaciones.
- **Especificación y arquitectura (v0.1, borrador):** [`docs/SPEC_LCE_ES.md`](docs/SPEC_LCE_ES.md) · English: [`docs/SPEC_LCE_EN.md`](docs/SPEC_LCE_EN.md) — componentes, esquemas, reglas normativas (RFC 2119), parámetros, correspondencia con el código (sección 21).
- **Diagrama de arquitectura:** [`docs/ARCHITECTURE_LCE.html`](docs/ARCHITECTURE_LCE.html).
- **Implementación de referencia:** [`swarmbly_lce/`](swarmbly_lce/) · **arnés de validación:** [`lce_validation/`](lce_validation/) ([README](lce_validation/README.md)) · **pruebas:** [`tests/`](tests/), una por invariante I1–I8.
- **Propuesta para el protocolo (SWIP, revisión 2):** [`swips/SWIP-XXXX-local-cognitive-extension.md`](swips/SWIP-XXXX-local-cognitive-extension.md) — la parte visible en la red, en inglés, con el formato de `CONTRIBUTING.md` del repositorio Swarmbly.
- **Bibliografía anotada:** [`docs/REFERENCES_LCE.md`](docs/REFERENCES_LCE.md) — 65 entradas con su uso en el diseño y su estado de verificación.
- **Estado de la documentación:** [`docs/STATUS.md`](docs/STATUS.md).
- **Borradores de trabajo:** [`_archive/drafts/`](_archive/drafts/) — las versiones conceptuales 0.2 a 0.4 y la revisión 1 del SWIP, conservadas como registro.

## La arquitectura en una línea por plano

| Plano | Dónde vive | Qué hace |
|---|---|---|
| **Local** | dispositivo del usuario | fuentes inmutables → wiki anclada, tipada y versionada (aprende rápido) → adaptador LoRA con repaso, regenerado desde base + wiki (aprende despacio) |
| **Inferencia** | Swarmbly, sin cambios en el núcleo | la personalización entra solo por el contrato Γ; los workers sirven su modelo base; la verificación queda intacta; respuesta plural desde el consenso E16 |
| **Social** | opcional, bajo demanda | cápsulas firmadas de ≤ 16 KiB, pull y nunca gossip; variación solo con evidencia humana nueva; persistencia por uso y réplicas derivadas de una tolerancia |

## Ocho invariantes

I1 hechos en la wiki, comportamiento en los pesos · I2 los workers sirven el modelo base · I3 acumular, nunca reemplazar · I4 la variación viene de personas · I5 la prevalencia es una etiqueta, no un criterio de adopción · I6 cada adaptador desde base + wiki, con repaso y prueba nueva · I7 la diversidad se presupuesta y se reporta · I8 lo no declarado no entrena.

## Código

Requiere Python 3.10 o superior; la única dependencia obligatoria es numpy.

```bash
pip install -e '.[dev]'          # extras: crypto (Ed25519), yaml, mlx (LoRA en Apple Silicon)
python -m pytest                 # 83 pruebas, incluida una por invariante
python -m lce_validation.run_all # siete instrumentos + experimentos con backend simulado
```

La herramienta de línea de órdenes `swarmbly-lce` cubre el ciclo local: `init` crea las carpetas de fuentes y una política en la que nada entrena por defecto; `ingest --sources DIR [--backend ollama --model qwen2.5:3b]` digiere y ancla; `cycle` avanza la madurez; `status`, `project "petición"` (muestra lo que saldría hacia Γ y en qué carril), `forget FUENTE`, `export-md`, `replicas --eps 1e-3`, `capsule keygen|make|verify` y `validate`.

Los resultados con `MockBackend` o por simulación **no son evidencia**. La primera corrida con modelos reales está preregistrada en [`docs/PREREGISTRATION_C1_C2_ES.md`](docs/PREREGISTRATION_C1_C2_ES.md) ([EN](docs/PREREGISTRATION_C1_C2_EN.md)), escrita antes de medir. Las corridas reales se hacen con `python -m lce_validation.run_real --models qwen2.5:3b,llama3.2:3b,gemma2:2b` contra Ollama u otro servidor compatible con OpenAI, y se reportan con su alcance.

## Lo que no se afirma

Que el modelo personal aprenda hechos; olvido verificable en los pesos salvo regenerando; que la diversidad de familias de modelo garantice errores independientes; que la red se vuelva más inteligente por comunicarse; que la extensión resuelva el problema de incentivo de la computación voluntaria. El whitepaper, sección 12, desarrolla cada una.

## Licencia

Código: AGPL-3.0-or-later (ver [`LICENSE`](LICENSE) y [`NOTICE`](NOTICE)). Textos: CC BY 4.0. Metadatos de cita en [`CITATION.cff`](CITATION.cff).

**Cómo citar / How to cite:** Espinoza-Ulloa, S. A. (2026). *Local Cognition and Anchored Transmission: A Local-First Cognitive Extension for Swarmbly* (Version 0.1, draft). Zenodo. https://doi.org/10.5281/zenodo.23150478

---

## English summary

**Swarmbly LCE** is a local-first extension to the Swarmbly decentralized inference protocol. Each user keeps, on their own device, a human-readable memory anchored to their sources and a lightweight adapter that learns only their voice and procedures, never facts; nodes may optionally exchange small signed knowledge capsules on demand. Workers keep serving their base model, so verification is untouched. The design is derived from evidence on knowledge injection, model collapse, conformity and correlated errors across model families, and from population-genetic and cultural-evolution instruments. **Status: draft; nothing has been measured.**

Documents: whitepaper [`docs/WHITEPAPER_LCE_EN.md`](docs/WHITEPAPER_LCE_EN.md) (Zenodo: [10.5281/zenodo.23150478](https://doi.org/10.5281/zenodo.23150478)), specification [`docs/SPEC_LCE_EN.md`](docs/SPEC_LCE_EN.md), protocol-facing proposal [`swips/`](swips/), annotated bibliography [`docs/REFERENCES_LCE.md`](docs/REFERENCES_LCE.md); Spanish versions alongside.

Code: `swarmbly_lce` is a reference implementation of the whole specification (Python 3.10+, numpy; optional `cryptography` for Ed25519 and MLX for a real LoRA trainer on Apple Silicon). `lce_validation` is the harness: seven instrument tests that must pass before any measurement is trusted, mock-backend experiments that exercise the pipeline, and `run_real` for runs against real models through Ollama or any OpenAI-compatible server. `pip install -e '.[dev]' && python -m pytest && python -m lce_validation.run_all`. Mock and simulation outputs are never evidence. The first real-model run is pre-registered in [`docs/PREREGISTRATION_C1_C2_EN.md`](docs/PREREGISTRATION_C1_C2_EN.md).

*Sebastián A. Espinoza-Ulloa · Independent Researcher · [ORCID 0000-0003-1497-356X](https://orcid.org/0000-0003-1497-356X)*
