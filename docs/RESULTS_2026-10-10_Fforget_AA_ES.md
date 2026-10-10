---
status: current
lang: es
kind: exploratory
---

# Resultados — prueba de olvido (F-forget) y prueba A/A de reproducibilidad

**10 de octubre de 2026 · Enmienda 6 (c) de `PREREGISTRATION_BENCH_R1X_ES.md`,
confirmada antes de correr · pruebas exploratorias de mecanismo y
reproducibilidad: no emiten veredictos sobre H-C1 · entorno bloqueado (Python
3.11 del `.venv`) y digests verificados contra
`lce_validation/data/model_digests.json`**

Salidas crudas en `results/bench_forget/` y `results/aa_test/`. Las cifras de
conducta conformes al preregistro y la comparación con R13 están en
`results/bench_forget/analysis.json`; `run_derive` recalcula todo lo que no
depende de las wikis en caché.

## 1. F-forget: ¿olvidar una fuente borra lo aprendido de ella?

Para cada usuario (5) y digestor (qwen2.5:3b, llama3.2:3b, gemma2:2b) se
construyeron tres wikis: W_full, digerida con todas las fuentes `.md`;
W_forget, la misma tras `Wiki.forget_source("teach/knowledge/borrada.md")`; y
W_never, digerida en la misma corrida sin esa fuente.

**Estructura.** En las 13 celdas válidas no quedó ninguna claim anclada a la
fuente olvidada (S2 = 0) y no se perdió ni cambió ninguna claim de otras
fuentes (S3 = 0). Lo mismo en el barrido que olvida, una por una, cada fuente
de cada W_full: 93 olvidos, residuo 0 y daño colateral 0. Dos celdas
(julian y luisa con llama3.2) se rechazaron por S1, porque esas wikis no
tenían ninguna claim de la fuente borrada. Como `forget_source` borra por
anclaje, cero es lo esperado: S2 y S3 verifican que la implementación hace lo
que la especificación dice sobre wikis reales, no un efecto empírico.
**Veredicto estructural preregistrado: se sostiene.**

**Equivalencia con no haberla digerido nunca.** W_forget coincide con la
W_never de la misma corrida en 8 de 15 wikis (Jaccard medio 0.943). Un
análisis posterior a los datos, declarado como tal, aclara de dónde viene la
diferencia: W_forget coincide en 15 de 15 con la wiki de R13, digerida horas
antes y sin esa fuente, mientras que la W_never de esta corrida coincide con
la de R13 solo en 8 de 15. Las diferencias están en W_never, es decir, en el
no determinismo de la digestión que mide AA2 (sección 2), no en el olvido.
Olvidar una fuente deja la wiki exactamente como si nunca se hubiera
digerido.

**Conducta.** Abstención en las 5 preguntas sobre la fuente borrada, con el
prompt, la recuperación y la rúbrica de R13 (3 digestores × 3 respondedores,
sin las celdas rechazadas, como pide el preregistro):

| Wiki | Abstención |
|---|---|
| W_full | 0.359 |
| W_forget | 0.718 |
| W_never | 0.718 |

forget − full = **+0.356 [+0.222, +0.489]** y forget − never = +0.000
(bootstrap agrupado por pregunta). B1 (la wiki completa se abstiene al menos
0.10 menos que la que nunca vio la fuente) y B2 (el olvido es completo en
conducta) se cumplen. El 89.7 % de las respuestas con W_forget y W_never son
idénticas palabra por palabra. El resumen que escribió la corrida incluía las
dos celdas rechazadas (full 0.444, forget 0.756, never 0.756); el efecto y la
conclusión no cambian.

**Lectura.** Esto es lo que el tipo `deleted` de R13 no podía medir (N2):
aquí la wiki sí había aprendido de la fuente, la olvidó y se comporta como si
nunca la hubiera tenido. Son 5 preguntas, así que la potencia es baja y el
resultado es de mecanismo, no de magnitud. Tampoco es una comparación con el
RAG: en un RAG, olvidar una fuente es quitar el archivo del índice. Lo que
F-forget muestra es que la wiki, que transforma las fuentes en claims, no
pierde esa propiedad.

## 2. A/A de reproducibilidad (R14 1.2–1.4)

| Prueba | Resultado | Criterio |
|---|---|---|
| AA1 generación a T = 0 (brazo A2 de R13 repetido, 378 respuestas) | 100 % idénticas; Δ exactitud 0.0000 | **pasa** |
| AA2 digestión (W_never frente a las wikis de R13) | 8 de 15 conjuntos idénticos; Jaccard medio 0.943 | **falla** (requiere ≥ 14 de 15) |
| AA3 semilla a T = 0.7 (qwen2.5:3b, 20 temas × 3 semillas × 2 repeticiones) | endpoint nativo 100 % idénticas (efectiva); compatible con OpenAI 80 % (no efectiva) | la semilla nativa es adoptable por enmienda |
| AA4 homogeneidad entre repeticiones | Δ media −0.0011 [−0.0067, +0.0047] | **pasa** (≤ 0.01) |

**El criterio de re-corrida de R14 no queda cerrado.** La generación de
respuestas es reproducible por completo, pero la digestión no siempre lo es:
7 de 15 wikis difieren en unas pocas claims pese a la temperatura 0. El
patrón es llamativo: la W_full de esta corrida reprodujo exactamente las
wikis de R13 (15 de 15, quitando la fuente borrada), y la W_never, digerida
justo después con los mismos prompts, es la que difiere. Es compatible con
que la caché de prompts del servidor altere la decodificación a temperatura
0, pero eso es una hipótesis. Cerrar R14 requiere una digestión determinista
(el endpoint nativo con semilla, que AA3 muestra efectivo, o una
canonicalización de claims), por enmienda. AA4 muestra que la medida
estocástica (homogeneidad) es estable aunque las muestras individuales del
endpoint compatible con OpenAI no se repitan.

## 3. Desviaciones declaradas

1. El resumen de `bench_forget` incluyó en la conducta las dos celdas que S1
   rechaza; las cifras conformes al preregistro se recalculan en
   `analysis.json` y el código ya las excluye para corridas futuras.
2. La comparación de W_forget con las wikis de R13 no estaba preregistrada;
   se reporta como análisis posterior a los datos.
3. El script de corrida se ajustó antes de empezar para aceptar el nombre
   `nomic-embed-text:latest` (commit `586eb21`); no afecta a ninguna medida.

*Texto CC BY 4.0.*
