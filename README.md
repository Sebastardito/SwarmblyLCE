# Swarmbly LCE — Local Cognitive Extension

[![Licencia: AGPL-3.0-or-later](https://img.shields.io/badge/licencia-AGPL--3.0--or--later-blue.svg)](LICENSE)
![Estado: borrador](https://img.shields.io/badge/estado-borrador-orange.svg)

**Una extensión local-first para [Swarmbly](https://github.com/Sebastardito/Swarmbly-AI): memoria personal, aprendizaje del modelo del usuario y transferencia ligera de conocimiento entre nodos, sin deformar el protocolo.**

Swarmbly fragmenta el problema y no el modelo. Sus workers son deliberadamente casi sin estado, y el cliente es la única unidad que conserva memoria. La LCE propone qué hacer con esa memoria: una wiki legible y anclada a las fuentes del usuario, un adaptador ligero que aprende de él solo su manera de hablar y de trabajar (nunca sus hechos), y un intercambio opcional de pequeñas cápsulas de conocimiento escrito cuya memoria sobrevive por uso a la desaparición de los nodos que las originaron.

> **Estado: borrador, nada medido.** Ningún mecanismo de este repositorio se ha medido todavía. Cada uno llega con su hipótesis, su experimento y su condición de abandono, enunciados antes de construir. No revisado por pares.

- **Whitepaper (v0.1, borrador):** [`docs/WHITEPAPER_LCE_ES.md`](docs/WHITEPAPER_LCE_ES.md) — fundamento, homologías aceptadas y descartadas, evidencia adversa, arquitectura, hipótesis, limitaciones. Versión en inglés: pendiente, sobre el texto aprobado.
- **Especificación y arquitectura (v0.1, borrador):** [`docs/SPEC_LCE_ES.md`](docs/SPEC_LCE_ES.md) — componentes, esquemas, reglas normativas (RFC 2119), parámetros.
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

## Lo que no se afirma

Que el modelo personal aprenda hechos; olvido verificable en los pesos salvo regenerando; que la diversidad de familias de modelo garantice errores independientes; que la red se vuelva más inteligente por comunicarse; que la extensión resuelva el problema de incentivo de la computación voluntaria. El whitepaper, sección 12, desarrolla cada una.

## Licencia

Código: AGPL-3.0-or-later (ver [`LICENSE`](LICENSE) y [`NOTICE`](NOTICE)). Textos: CC BY 4.0. Metadatos de cita en [`CITATION.cff`](CITATION.cff).

---

## English summary

**Swarmbly LCE** is a local-first extension to the Swarmbly decentralized inference protocol. Each user keeps, on their own device, a human-readable memory anchored to their sources and a lightweight adapter that learns only their voice and procedures, never facts; nodes may optionally exchange small signed knowledge capsules on demand. Workers keep serving their base model, so verification is untouched. The design is derived from evidence on knowledge injection, model collapse, conformity and correlated errors across model families, and from population-genetic and cultural-evolution instruments. **Status: draft; nothing has been measured.** The protocol-facing proposal is the English SWIP in `swips/`; the Spanish whitepaper and specification are in `docs/`, with English versions to follow.

*Sebastián A. Espinoza-Ulloa · Independent Researcher · [ORCID 0000-0003-1497-356X](https://orcid.org/0000-0003-1497-356X)*
