---
status: current
lang: en
kind: exploratory
---

# Results — R11 pilot (the fair adapter)

**9 de octubre de 2026 · preregistro `PREREGISTRATION_BENCH_R1X_ES.md` sección 3, con
Enmienda 5 · PILOTO EXPLORATORIO: no dispara la condición de muerte, pero
fija su dirección**

## Figures

12 adaptadores qwen2.5-3b (3 usuarios × 2 semillas × repaso sí/no), lote de
6–17 pares SOLO de claims entrenables (I1), 300 iteraciones, evaluación de
CUATRO brazos sobre tareas re-redactadas. granite-3.1-2b **saltada**: su
digestor produjo solo 4 claims entrenables por usuario (defecto del digestor
a reportar, no del adaptador).

| Brazo (media por usuario) | mara | julian | carmen |
|---|---|---|---|
| base | 0.12 | 0.19 | 0.02 |
| recuperación + Γ | 0.54 | 0.55 | 0.52 |
| adaptador | 0.11 | 0.07 | 0.10 |
| adaptador + recuperación | 0.28 | 0.21 | 0.13 |

**H-C6 (adaptador − recuperación+Γ):** mara −0.435, julian −0.477, carmen
−0.429 — las tres cotas del IC por debajo de cero. **0/3 usuarios cumplen el
margen (+0.10 con cota > 0).**

**Fuga I1:** adaptador − base = −0.367 (n=60) — dirección SEGURA (el
adaptador no responde hechos mejor que el base), pero fuera de la
equivalencia ±0.10: entrenar estilo hace OLVIDAR hechos del modelo base
(interferencia catastrófica visible, la patología que la CLS predice).

## Reading

La recuperación+Γ domina al adaptador por ~45 puntos en este régimen (lotes
pequeños, 300 iteraciones, una familia). La condición de muerte del
preregistro («si el adaptador no supera a la recuperación por el margen
preregistrado, la capa 2 se retira») NO se dispara aquí (piloto), pero la
dirección es inequívoca y coincide con la expectativa del propio whitepaper
(«la recuperación captura la mayor parte del beneficio»). La confirmatoria
(≥30 tareas, ambas familias con el rendimiento del digestor corregido, LC6)
decidiría muy probablemente el retiro de la capa 2 — un negativo publicable
que simplifica el diseño sin tocarlo: memoria + proyección quedan intactas.

*Texto CC BY 4.0.*

*English summary: the R11 pilot is NOT a fair adapter test yet (E6 of the review): the adapter collapsed onto its training batch; ~half the tasks are invalid; no CIs; the retrieval+Γ arm lacked Γ; I1 used general-knowledge items. Its negative is not publishable. The confirmatory needs the redesigned batch and tasks.*
