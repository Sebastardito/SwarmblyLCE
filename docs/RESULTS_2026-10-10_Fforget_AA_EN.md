---
status: current
lang: en
kind: exploratory
---

# Results — F-forget and A/A reproducibility

**10 de octubre de 2026 · Enmienda 6 (c) de `PREREGISTRATION_BENCH_R1X_ES.md` ·
exploratorias de mecanismo y reproducibilidad: no emiten veredictos sobre
H-C1 · corridas con el entorno bloqueado (Python 3.11 del `.venv`) y digests
verificados contra `lce_validation/data/model_digests.json`**

## F-forget: ¿olvidar borra lo aprendido de la fuente?

Tres wikis por celda (5 usuarios × 3 digestores): W_full (todas las
fuentes), W_forget (tras `Wiki.forget_source` de `borrada.md`), W_never
(digerida sin esa fuente).

| Medida | Resultado |
|---|---|
| S2 residuo (claims de la fuente borrada que sobreviven) | **0** en las 15 celdas y en los 93 olvidos del barrido |
| S3 daño colateral (claims de otras fuentes perdidas) | **0** en todo |
| S4 equivalencia forget/never | 8/15 conjuntos idénticos; Jaccard medio 0.943; contextos entregados idénticos 0.72 |
| Abstención en las 5 preguntas `deleted` | full 0.444 → forget **0.756** (forget − full = **+0.311 [0.200, 0.444]**) |
| forget vs never (B2) | Δ 0.000 (dentro de ±0.10) ✓ |

**Verdict structural: holds** — el olvido elimina exactamente lo
aprendido de la fuente y nada más, y en conducta la wiki que olvidó
abstiene en las preguntas sobre lo borrado igual que la que nunca lo
digirió. Esto es lo que el tipo `deleted` de R13 debía medir y no podía
(N2): aquí sí mide olvido real, y la wiki lo pasa.

## A/A de reproducibilidad (R14 1.2–1.4)

| Prueba | Resultado | Criterio |
|---|---|---|
| AA1 generación T=0 (brazo A2 repetido, 378 respuestas) | 100 % idénticas, Δ exactitud 0.0000 | **pasa** |
| AA2 digestión determinista (W_never vs wikis R13) | **8/15** conjuntos idénticos; Jaccard medio 0.943 | **falla** (requiere ≥14/15) |
| AA3 semilla T=0.7 (qwen2.5, 20 temas × 3 semillas × 2 repeticiones) | endpoint nativo 100 % idénticas (**efectiva**); compatible OpenAI 80 % (**no efectiva**) | nativa adoptable por enmienda |
| AA4 medida estocástica (homogeneidad entre repeticiones) | Δ media −0.0011 [−0.0067, 0.0047] | **pasa** (≤0.01) |

**El criterio de re-corrida de R14 NO queda cerrado (AA2).** La generación
de respuestas es perfectamente reproducible, pero la DIGESTIÓN no lo es
corrida a corrida: 7 de 15 wikis difieren en un puñado de claims a pesar de
temperatura 0. Para cerrar R14 hace falta una digestión determinista —el
endpoint nativo con semilla (AA3 nativa) o una canonicalización de claims—,
que queda como siguiente paso, por enmienda. AA4 muestra que las MEDIDAS
estocásticas (homogeneidad) son estables aunque las muestras puntuales no
lo sean.

*Texto CC BY 4.0.*
